from __future__ import annotations

import asyncio
import logging
import time
from typing import Iterable, Optional

from pydeye.exceptions import DeviceNotSupported
from pydeye.helper import patch_bitmask, hex_str
from pydeye.interfaces.base import ModbusInterface
from pydeye.sensor import LOG_TRACE, Sensor
from pydeye.state import InverterState, group_sensors, register_map

_LOG = logging.getLogger(__name__)


class BaseInverter:
    """Abstract base class and factory for Deye inverter implementations."""

    adapter: ModbusInterface
    state: InverterState

    port: str = "/dev/tty0"
    baudrate: int = 9600
    server_id: int = 1
    timeout: int = 10
    read_sensors_batch_size: int = 60
    allow_gap: int = 3
    timeouts: int = 0

    def __init__(self, adapter: ModbusInterface) -> None:
        self.adapter = adapter
        self.state = InverterState()

    @staticmethod
    async def create_device(adapter: ModbusInterface) -> BaseInverter:
        """Factory: connect, read device info, and return the correct subclass."""
        basic_info = await adapter.get_basic_info()
        from pydeye.helper import InverterType
        from pydeye.inverters.deye_SUN12KEU import DeyeSUN12KEU

        if basic_info.type in (
            InverterType.LOW_VOLTAGE_THREE_PHASE_HYBRID_INVERTER,
            InverterType.HIGH_VOLTAGE_THREE_PHASE_HYBRID_INVERTER,
            InverterType.HIGH_VOLTAGE_THREE_PHASE_INVERTER_6_12KW,
            InverterType.HIGH_VOLTAGE_THREE_PHASE_INVERTER_20_50WK,
            InverterType.UNDEFINED,  # fall back to 3-phase for unknown devices
        ):
            return DeyeSUN12KEU(adapter)

        raise DeviceNotSupported(f"Unsupported device type: {basic_info.type}")

    async def init(self) -> None:
        """Populate device metadata from holding registers 0-23."""
        basic_info = await self.adapter.get_basic_info()
        self.type = basic_info.type
        self.serial_number = basic_info.serial_number
        self.main_version = basic_info.main_version
        self.hmi_version = basic_info.hmi_version
        self.protocol_version = basic_info.protocol_version
        self.rated_power = basic_info.rated_power
        _LOG.info(
            "Inverter %s %sW %s initialized",
            self.type,
            self.rated_power,
            self.serial_number,
        )

    async def update_status(self) -> None:
        """Subclasses must implement this to refresh measurements."""
        raise NotImplementedError

    # ── New sensor-based API ─────────────────────────────────────────────────

    async def read_sensors(self, sensors: Optional[Iterable[Sensor]] = None) -> None:
        """Read a set of sensors using grouped/batched Modbus requests.

        If *sensors* is None, all tracked sensors in self.state are read.
        """
        if sensors is None:
            sensors = list(self.state.sensors)
        else:
            sensors = list(sensors)

        for sen in sensors:
            if sen not in self.state.values:
                _LOG.warning("Sensor %s is not tracked; call state.track() first", sen.id)

        new_regs: dict[int, int] = {}
        errors: list[Exception] = []

        groups = list(group_sensors(sensors, allow_gap=self.allow_gap, max_group_size=self.read_sensors_batch_size))
        for grp in groups:
            length = grp[-1] - grp[0] + 1
            try:
                t0 = time.perf_counter()
                raw = await asyncio.wait_for(
                    self.adapter.read_holding_registers(grp[0], length),
                    timeout=self.timeout + 1,
                )
                elapsed = time.perf_counter() - t0
                _LOG.debug(
                    "Read %d registers from %d in %.2fs", length, grp[0], elapsed
                )
            except asyncio.TimeoutError:
                err = TimeoutError(f"timeout reading {length} registers from {grp[0]}")
                errors.append(err)
                self.timeouts += 1
                continue
            except Exception as exc:
                errors.append(
                    exc.__class__(
                        f"{exc.__class__.__name__} reading {length} registers from {grp[0]}: {exc}"
                    )
                )
                continue

            new_regs.update(register_map(grp[0], raw))

        self.state.update(new_regs)

        if len(errors) > 1:
            raise ExceptionGroup("errors reading sensors", errors)
        if errors:
            raise errors[0]

    async def write_sensor(self, sensor, value, *, msg: str = "") -> None:
        """Write a value to a read/write sensor, handling bitmask registers correctly."""
        from pydeye.rwsensors import RWSensor
        if not isinstance(sensor, RWSensor):
            raise TypeError(f"{sensor.name} is not a writable sensor")

        regs = sensor.value_to_reg(value, self.state)

        if sensor.bitmask:
            regs = sensor.reg(*regs, msg=f"while setting {value!r}")
            current_raw = await self.adapter.read_holding_registers(sensor.address[0], 1)
            current_val = current_raw[0]
            patched = patch_bitmask(current_val, regs[0], sensor.bitmask)
            regs = (patched, *regs[1:])
            msg = f"[Register {current_val:#06x}→{patched:#06x}]"

        if sensor.trace:
            _LOG.debug(
                "Writing sensor %s=%r registers:%s %s",
                sensor.id,
                value,
                hex_str(regs, address=sensor.address),
                msg,
            )

        for idx, addr in enumerate(sensor.address):
            if idx:
                await asyncio.sleep(0.05)
            await self.adapter.write_register(address=addr, value=regs[idx])
            self.state.registers[addr] = regs[idx]
