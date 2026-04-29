from __future__ import annotations

import logging
from typing import Optional, Union

from pydeye.helper import (
    BOOL_OFF,
    BOOL_ON,
    NumType,
    RegType,
    ValType,
    as_num,
    hex_str,
    int_round,
    slug,
    unpack_value,
)

_LOG = logging.getLogger(__name__)
LOG_TRACE = 5  # custom level below DEBUG


FAULTS: dict[int, str] = {
    1: "F01 DC Bus Over Voltage",
    2: "F02 DC Bus Low Voltage",
    3: "F03 DC Bus Unbalanced",
    4: "F04 DC Bus Unbalanced 2",
    5: "F05 Inverter Soft Start Failed",
    6: "F06 Grid Voltage Sampling Abnormal",
    7: "F07 Internal Fan Fault",
    8: "F08 Bus Voltage Sampling Abnormal",
    9: "F09 Grid Over Current Protection",
    10: "F10 DC Over Current Protection",
    11: "F11 AC Over Current",
    12: "F12 GFCI Device Fault",
    13: "F13 DC Inversed",
    14: "F14 Islanding",
}

HV_FAULTS: dict[int, str] = {
    1: "DC Inversed Failure",
    2: "DC Bus Overvoltage",
    3: "DC Bus Undervoltage",
    4: "DC Bus Unbalanced",
    5: "Inverter Overcurrent",
    6: "Output Voltage High",
    7: "Output Voltage Low",
    8: "Output Frequency High",
    9: "Output Frequency Low",
    10: "PV Overcurrent",
    11: "PV Overvoltage",
    12: "Isolation Failure",
    13: "GFCI Failure",
    14: "Internal Fan Failure",
    15: "AC Overcurrent",
    16: "AC Overvoltage",
    17: "AC Undervoltage",
    18: "AC Overfrequency",
    19: "AC Underfrequency",
    20: "AC Arc Fault",
    21: "Battery Undervoltage",
    22: "Battery Overvoltage",
    23: "Battery Overcurrent",
    24: "Battery Over-temperature",
    25: "Battery Under-temperature",
    26: "BMS Communication Failure",
    27: "Self-Test Failure",
    28: "Relay Adhesion",
    29: "Relay Open Circuit",
    30: "Anti-islanding Failure",
    31: "Inverter Over-temperature",
    32: "Heat Sink Temperature Failure",
    33: "Micro Inverter Communication Failure",
    34: "PV String Polarity Reversal",
    35: "Load Overcurrent",
    36: "DC Overvoltage on Startup",
    37: "DC Disconnect Switch Open",
    38: "AC Disconnect Switch Open",
    39: "Battery Disconnect Switch Open",
    40: "Emergency Stop",
    41: "Ground Fault",
    42: "Weak Grid",
    43: "Grid Phase Failure",
    44: "Grid Frequency Fluctuation",
    45: "Transformer Over-temperature",
    46: "Capacitor Failure",
    47: "Inductor Failure",
    48: "IGBT Failure",
    49: "Communication Failure",
    50: "Hardware Protection",
    51: "Software Protection",
    52: "Configuration Error",
    53: "Calibration Error",
    54: "Memory Failure",
    55: "DSP Failure",
    56: "FPGA Failure",
    57: "Sensor Failure",
    58: "A/D Converter Failure",
    59: "Power Factor Abnormal",
    60: "Harmonic Distortion Abnormal",
    61: "Insulation Resistance Low",
    62: "Leakage Current High",
    63: "Over Load",
    64: "System Fault",
}

INVERTER_STATES: dict[int, str] = {
    0: "standby",
    1: "selfcheck",
    2: "normal",
    3: "alarm",
    4: "fault",
    5: "off",
}


class Sensor:
    """Represents one or more Modbus holding registers as a single measurement."""

    def __init__(
        self,
        address: Union[int, tuple[int, ...]],
        name: str,
        unit: str = "",
        factor: float = 1,
        bitmask: int = 0,
    ) -> None:
        self.address: tuple[int, ...] = (address,) if isinstance(address, int) else tuple(address)
        self.name = name
        self.unit = unit
        self.factor = factor
        self.bitmask = bitmask
        self.trace = False

    @property
    def id(self) -> str:
        return slug(self.name)

    @property
    def source(self) -> str:
        return "@" + ",".join(str(a) for a in self.address)

    def masked(self, regs: RegType) -> RegType:
        if not self.bitmask:
            return regs
        return (regs[0] & self.bitmask,) + regs[1:]

    def reg_to_value(self, regs: RegType) -> ValType:
        regs = self.masked(regs)
        signed = self.factor < 0
        val = unpack_value(regs, signed=signed)
        return int_round(val * abs(self.factor))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.address}, {self.name!r}, {self.unit!r}, {self.factor})"


class Constant(Sensor):
    """A sensor with a fixed value that never reads from a register."""

    def __init__(self, value: ValType, name: str, unit: str = "") -> None:
        super().__init__((), name, unit)
        self.value = value

    def reg_to_value(self, regs: RegType) -> ValType:
        return self.value


class TempSensor(Sensor):
    """Temperature sensor with a configurable offset (default -100).

    Deye convention: raw uint16 × factor + offset = °C.
    """

    def __init__(
        self,
        address: Union[int, tuple[int, ...]],
        name: str,
        unit: str = "°C",
        factor: float = 0.1,
        offset: float = -100,
    ) -> None:
        super().__init__(address, name, unit, factor)
        self.offset = offset

    def reg_to_value(self, regs: RegType) -> ValType:
        regs = self.masked(regs)
        val = unpack_value(regs, signed=False)  # always uint16 for Deye temperatures
        return int_round(val * abs(self.factor) + self.offset)


class BinarySensor(Sensor):
    """Interprets a (masked) register value as an ON/OFF boolean."""

    def __init__(
        self,
        address: Union[int, tuple[int, ...]],
        name: str,
        bitmask: int = 0,
        on: Optional[int] = None,
        off: int = 0,
    ) -> None:
        super().__init__(address, name, "", 1, bitmask)
        self.on_value = on
        self.off_value = off

    def reg_to_value(self, regs: RegType) -> ValType:
        regs = self.masked(regs)
        val = regs[0]
        if self.on_value is not None:
            return BOOL_ON if val == self.on_value else BOOL_OFF
        return BOOL_OFF if val == self.off_value else BOOL_ON


class MathSensor(Sensor):
    """Combines multiple registers with individual scale factors (weighted sum)."""

    def __init__(
        self,
        address: Union[tuple[int, ...], list[int]],
        name: str,
        unit: str = "",
        factors: Optional[Union[tuple[float, ...], list[float]]] = None,
    ) -> None:
        addr = tuple(address)
        factor = factors[0] if factors else 1
        super().__init__(addr, name, unit, factor)
        self.factors: tuple[float, ...] = tuple(factors) if factors else (1,) * len(addr)

    def reg_to_value(self, regs: RegType) -> ValType:
        total: float = 0
        for reg, f in zip(regs, self.factors):
            total += unpack_value((reg,), signed=f < 0) * abs(f)
        return int_round(total)


class SerialSensor(Sensor):
    """Decodes multiple registers into an ASCII serial-number string."""

    def reg_to_value(self, regs: RegType) -> ValType:
        chars = []
        for reg in regs:
            hi = (reg >> 8) & 0xFF
            lo = reg & 0xFF
            if hi:
                chars.append(chr(hi))
            if lo:
                chars.append(chr(lo))
        return "".join(chars).strip("\x00")


class EnumSensor(Sensor):
    """Maps register values to human-readable string options."""

    def __init__(
        self,
        address: Union[int, tuple[int, ...]],
        name: str,
        unit: str = "",
        options: Optional[dict[int, str]] = None,
        bitmask: int = 0,
    ) -> None:
        super().__init__(address, name, unit, 1, bitmask)
        self.options: dict[int, str] = options or {}

    def reg_to_value(self, regs: RegType) -> ValType:
        regs = self.masked(regs)
        val = regs[0]
        res = self.options.get(val)
        if res is None:
            _LOG.warning("%s: unknown register value %s", self.id, val)
            return f"unknown ({val})"
        return res


class SDStatusSensor(Sensor):
    """Decodes SD card status codes."""

    def reg_to_value(self, regs: RegType) -> ValType:
        regs = self.masked(regs)
        val = regs[0]
        if val == 1000:
            return "fault"
        if val == 2000:
            return "ok"
        return f"unknown ({val})"


class InverterStateSensor(Sensor):
    """Decodes inverter operating state."""

    def reg_to_value(self, regs: RegType) -> ValType:
        regs = self.masked(regs)
        return INVERTER_STATES.get(regs[0], f"unknown ({regs[0]})")


class FaultSensor(Sensor):
    """Decodes up to 4 fault registers into a comma-separated fault message."""

    def reg_to_value(self, regs: RegType) -> ValType:
        active = []
        for reg_idx, reg in enumerate(regs):
            for bit in range(16):
                fault_num = reg_idx * 16 + bit + 1
                if reg & (1 << bit):
                    active.append(FAULTS.get(fault_num, f"F{fault_num:02d} Unknown"))
        return ", ".join(active) if active else "None"


class HVFaultSensor(Sensor):
    """Decodes up to 4 fault registers using the extended HV fault code table."""

    def reg_to_value(self, regs: RegType) -> ValType:
        active = []
        for reg_idx, reg in enumerate(regs):
            for bit in range(16):
                fault_num = reg_idx * 16 + bit + 1
                if reg & (1 << bit):
                    active.append(HV_FAULTS.get(fault_num, f"F{fault_num:02d} Unknown"))
        return ", ".join(active) if active else "None"


class ProtocolVersionSensor(Sensor):
    """Formats a register as a 'major.minor' version string."""

    def reg_to_value(self, regs: RegType) -> ValType:
        regs = self.masked(regs)
        hi = (regs[0] >> 8) & 0xFF
        lo = regs[0] & 0xFF
        return f"{hi}.{lo}"


class Sensor16(Sensor):
    """Sensor that may appear at different register addresses across firmware versions.

    primary: address used on older/standard firmware (16-bit).
    alt: address used on newer firmware (also 16-bit, different location).
    Falls back to the alt value when the primary register reads zero.
    """

    def __init__(
        self,
        primary: int,
        alt: int,
        name: str,
        unit: str = "",
        factor: float = 1,
        bitmask: int = 0,
    ) -> None:
        super().__init__((primary, alt), name, unit, factor, bitmask)
        self._primary_idx = 0  # index of primary in self.address

    def reg_to_value(self, regs: RegType) -> ValType:
        signed = self.factor < 0
        primary_val = unpack_value((regs[0],), signed=signed)
        if len(regs) > 1:
            alt_val = unpack_value((regs[1],), signed=signed)
            if primary_val == 0 and alt_val != 0:
                return int_round(alt_val * abs(self.factor))
        return int_round(primary_val * abs(self.factor))


class SensorDefinitions:
    """Container for a named set of sensors, supporting copy and override."""

    def __init__(self) -> None:
        self.all: dict[str, Sensor] = {}

    def __iadd__(self, sensor: Sensor) -> SensorDefinitions:
        self.all[sensor.id] = sensor
        return self

    def __iter__(self):
        return iter(self.all.values())

    def __len__(self) -> int:
        return len(self.all)

    def __getattr__(self, name: str) -> Sensor:
        if name != "all" and "all" in self.__dict__ and name in self.all:
            return self.all[name]
        raise AttributeError(f"No sensor '{name}'")

    def copy(self) -> SensorDefinitions:
        new = SensorDefinitions()
        new.all = dict(self.all)
        return new

    def merge(self, other: SensorDefinitions) -> SensorDefinitions:
        """Merge sensors from another SensorDefinitions in-place."""
        self.all.update(other.all)
        return self

    def override(self, sensor_id: str, **kwargs) -> SensorDefinitions:
        """Override attributes on an existing sensor by id."""
        if sensor_id in self.all:
            for k, v in kwargs.items():
                setattr(self.all[sensor_id], k, v)
        return self

    def get(self, sensor_id: str, default: Optional[Sensor] = None) -> Optional[Sensor]:
        return self.all.get(sensor_id, default)
