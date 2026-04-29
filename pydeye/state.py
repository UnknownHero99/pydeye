from __future__ import annotations

import logging
from collections import defaultdict
from typing import Callable, Generator, Iterable, Iterator, Optional, Sequence, Union

from pydeye.helper import NumType, ValType, as_num
from pydeye.sensor import Sensor

_LOG = logging.getLogger(__name__)


class InverterState:
    """Tracks the current value and history of every registered sensor."""

    def __init__(
        self,
        onchange: Optional[Callable[[Sensor, ValType, ValType], None]] = None,
    ) -> None:
        self.values: dict[Sensor, Optional[ValType]] = {}
        self.registers: dict[int, int] = {}
        self.onchange = onchange
        self.history: dict[Sensor, list[NumType]] = defaultdict(list)
        self.historynn: dict[Sensor, list[ValType]] = defaultdict(list)

    def __getitem__(self, sensor: Sensor) -> Optional[ValType]:
        return self.values.get(sensor)

    def get(self, sensor: Optional[Sensor], default: ValType = None) -> ValType:
        if sensor is None:
            return default
        from pydeye.sensor import Constant
        if isinstance(sensor, Constant):
            return as_num(sensor.value)
        return self.values.get(sensor, default)

    def track(self, *sensors: Sensor) -> None:
        """Register sensors so they are included in future reads and updates."""
        from pydeye.rwsensors import RWSensor
        for sen in sensors:
            self.values.setdefault(sen, None)
            if isinstance(sen, RWSensor):
                for dep in sen.dependencies:
                    self.values.setdefault(dep, None)

    @property
    def sensors(self) -> Iterator[Sensor]:
        return iter(self.values.keys())

    def resolve_num(self, val: Union[NumType, Sensor], default: NumType = 0) -> NumType:
        """Resolve a number or a Sensor reference to a numeric value."""
        if isinstance(val, (int, float)):
            return val
        if isinstance(val, Sensor):
            return as_num(self.get(val, default))
        return as_num(val)

    def update(self, new_regs: dict[int, int]) -> None:
        """Process a batch of newly-read registers and update sensor values."""
        from pydeye.rwsensors import RWSensor
        from pydeye.sensor import BinarySensor

        changed: dict[Sensor, tuple[ValType, ValType]] = {}

        for sen in list(self.sensors):
            if not any(a in new_regs for a in sen.address):
                continue

            regs = tuple(
                new_regs.get(a, self.registers.get(a, 0)) for a in sen.address
            )

            oldv = self.values[sen]
            if sen.bitmask:
                regs = (regs[0] & sen.bitmask,)

            newv = sen.reg_to_value(regs)

            if oldv != newv:
                self.values[sen] = newv
                changed[sen] = (newv, oldv)
                if sen.trace:
                    _LOG.debug(
                        "Sensor %s changed %s → %s [%s]",
                        sen.name,
                        oldv,
                        newv,
                        hex_str(regs, address=sen.address),
                    )

            is_numeric = (
                isinstance(newv, (int, float))
                and not isinstance(sen, (RWSensor, BinarySensor))
                and sen not in self.historynn
            )
            if is_numeric:
                self.history[sen].append(float(newv))
            else:
                self.historynn[sen].append(newv)
                while len(self.historynn[sen]) > 2:
                    self.historynn[sen].pop(0)

        self.registers.update(new_regs)

        for sen, (new, old) in changed.items():
            if self.onchange is not None:
                self.onchange(sen, new, old)

    def history_average(self, sensor: Sensor) -> NumType:
        """Return the mean of collected numeric history, then reset the buffer."""
        hist = self.history[sensor]
        if not hist:
            return 0
        result = sum(hist) / len(hist)
        hist.clear()
        hist.append(result)
        return result


def group_sensors(
    sensors: Iterable[Sensor],
    allow_gap: int = 3,
    max_group_size: int = 60,
) -> Generator[list[int], None, None]:
    """Partition sensor register addresses into contiguous read blocks.

    Registers within allow_gap of each other and within max_group_size of the
    block start are merged into a single group.
    """
    if not sensors:
        return
    regs = sorted({a for s in sensors for a in s.address})
    if not regs:
        return
    group: list[int] = []
    prev = 0
    for adr in regs:
        if group and (adr - prev > allow_gap or adr - group[0] >= max_group_size):
            yield group
            group = []
        prev = adr
        group.append(adr)
    if group:
        yield group


def register_map(start: int, registers: Sequence[int]) -> dict[int, int]:
    """Convert a flat register list into an address-indexed dictionary."""
    return dict(enumerate(registers, start))


def hex_str(regs, address=None):
    from pydeye.helper import hex_str as _hex_str
    return _hex_str(regs, address)
