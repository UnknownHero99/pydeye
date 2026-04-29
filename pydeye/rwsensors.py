from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Optional, Union

from pydeye.helper import (
    BOOL_OFF,
    BOOL_ON,
    NumType,
    RegType,
    SSTime,
    ValType,
    hex_str,
    pack_value,
)
from pydeye.sensor import Sensor

if TYPE_CHECKING:
    from pydeye.state import InverterState

_LOG = logging.getLogger(__name__)


class RWSensor(Sensor):
    """Base class for read/write sensors."""

    def reg(self, *regs: int, msg: str = "") -> RegType:
        """Clamp register value to the sensor's bitmask."""
        if self.bitmask and regs[0] != (regs[0] & self.bitmask):
            _LOG.error(
                "Register value outside bitmask for sensor %s: %s %s",
                self.name,
                regs,
                msg,
            )
            return (regs[0] & self.bitmask, *regs[1:])
        return regs

    def value_to_reg(self, value: ValType, state: InverterState) -> RegType:
        """Convert a display value to register format."""
        raise NotImplementedError

    @property
    def dependencies(self) -> list[Sensor]:
        return []


class NumberRWSensor(RWSensor):
    """Numeric read/write sensor with optional min/max bounds.

    min and max can be either numbers or Sensor references; when they are
    Sensors the current state value is resolved at write time.
    """

    def __init__(
        self,
        address: Union[int, tuple[int, ...]],
        name: str,
        unit: str = "",
        factor: float = 1,
        bitmask: int = 0,
        min: Union[NumType, Sensor] = 0,
        max: Union[NumType, Sensor] = 100,
    ) -> None:
        super().__init__(address, name, unit, factor, bitmask)
        self.min = min
        self.max = max

    @property
    def dependencies(self) -> list[Sensor]:
        return [s for s in (self.min, self.max) if isinstance(s, Sensor)]

    def value_to_reg(self, value: ValType, state: InverterState) -> RegType:
        if not self.address:
            raise NotImplementedError("Cannot write to a sensor with no address")
        fval = float(value)
        minv = state.resolve_num(self.min, 0)
        maxv = state.resolve_num(self.max, 100)
        clamped = max(minv, min(maxv, fval))
        val = int(clamped / abs(self.factor))
        bits = len(self.address) * 16
        return self.reg(*pack_value(val, bits=bits, signed=self.factor < 0))


class SelectRWSensor(RWSensor):
    """Read/write sensor with a fixed set of string options."""

    def __init__(
        self,
        address: Union[int, tuple[int, ...]],
        name: str,
        unit: str = "",
        factor: float = 1,
        bitmask: int = 0,
        options: Optional[dict[int, str]] = None,
    ) -> None:
        super().__init__(address, name, unit, factor, bitmask)
        self.options: dict[int, str] = options or {}

    def available_values(self) -> list[str]:
        return list(self.options.values())

    def reg_to_value(self, regs: RegType) -> ValType:
        regs = self.masked(regs)
        res = self.options.get(regs[0])
        if res is None:
            _LOG.warning("%s: unknown register value %s", self.id, regs[0])
        return res

    def value_to_reg(self, value: ValType, state: InverterState) -> RegType:
        value = str(value)
        matches = [r for r, v in self.options.items() if v == value]
        if matches:
            return self.reg(matches[0])
        _LOG.warning("%s: unknown option %r", self.name, value)
        current = state.get(self, "")
        return self.value_to_reg(current, state)


class SwitchRWSensor(RWSensor):
    """Boolean on/off read/write sensor.

    on: register value for ON (None = any non-off value).
    off: register value for OFF (default 0).
    """

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

    def value_to_reg(self, value: ValType, state: InverterState) -> RegType:
        if str(value) == BOOL_ON:
            if self.on_value is not None:
                return self.reg(self.on_value)
            if self.bitmask:
                return self.masked((0xFF,))
            return (1,)
        return self.reg(self.off_value)


class SystemTimeRWSensor(RWSensor):
    """Encodes/decodes inverter date-time across three packed registers.

    Register layout: (year-2000 << 8 | month), (day << 8 | hour), (minute << 8 | second)
    """

    def __init__(
        self,
        address: Union[tuple[int, ...], list[int]],
        name: str,
    ) -> None:
        addr = tuple(address)
        if len(addr) != 3:
            raise ValueError("SystemTimeRWSensor requires exactly 3 register addresses")
        super().__init__(addr, name)

    def value_to_reg(self, value: ValType, state: InverterState) -> RegType:
        pattern = re.compile(r"(2\d{3})-(\d{2})-(\d{2}) ([012]?\d):(\d{2}):(\d{2})")
        m = pattern.fullmatch(str(value).strip())
        if not m:
            raise ValueError(f"Invalid datetime string: {value!r}  (expected YYYY-MM-DD HH:MM:SS)")
        y = int(m.group(1)) - 2000
        mo, d, h, mn, s = int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6))
        return ((y << 8) | mo, (d << 8) | h, (mn << 8) | s)

    def reg_to_value(self, regs: RegType) -> ValType:
        y = ((regs[0] & 0xFF00) >> 8) + 2000
        mo = regs[0] & 0xFF
        d = (regs[1] & 0xFF00) >> 8
        h = regs[1] & 0xFF
        mn = (regs[2] & 0xFF00) >> 8
        s = regs[2] & 0xFF
        return f"{y}-{mo:02d}-{d:02d} {h}:{mn:02d}:{s:02d}"


class TimeRWSensor(RWSensor):
    """Read/write sensor for a time-of-day value stored as HHMM in one register.

    Optional min/max can reference other TimeRWSensors to constrain available slots.
    """

    def __init__(
        self,
        address: Union[int, tuple[int, ...]],
        name: str,
        min: Optional[TimeRWSensor] = None,
        max: Optional[TimeRWSensor] = None,
    ) -> None:
        super().__init__(address, name)
        self.min = min
        self.max = max

    @property
    def dependencies(self) -> list[Sensor]:
        return [s for s in (self.min, self.max) if s is not None]

    def available_values(self, step_minutes: int, state: InverterState) -> list[str]:
        """Return valid time slot strings between min and max."""
        all_times = list(range(0, 24 * 60, step_minutes))
        minv = SSTime(strv=str(state.get(self.min, "0:00"))).minutes if self.min else 0
        maxv = SSTime(strv=str(state.get(self.max, "0:00"))).minutes if self.max else 0
        if minv >= maxv:
            maxv += 24 * 60
        opts = [minv] + [t for t in all_times if minv < t < maxv] + [maxv]
        cur = SSTime(strv=str(state.get(self, "0:00"))).minutes
        if cur not in opts:
            opts.append(cur)
        opts.sort()
        return [SSTime(minutes=m).str_value for m in opts]

    def reg_to_value(self, regs: RegType) -> ValType:
        return SSTime(regv=regs[0]).str_value

    def value_to_reg(self, value: ValType, state: InverterState) -> RegType:
        if not self.address:
            raise NotImplementedError("Cannot write to a sensor with no address")
        return self.reg(SSTime(strv=str(value)).reg_value)
