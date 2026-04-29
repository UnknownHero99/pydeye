from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pydeye.helper import AMPS, VOLT, WATT
from pydeye.rwsensors import NumberRWSensor

from .const import DOMAIN
from .coordinator import DeyeCoordinator
from .entity import DeyeEntity

_HA_UNIT = {
    WATT: UnitOfPower.WATT,
    VOLT: UnitOfElectricPotential.VOLT,
    AMPS: UnitOfElectricCurrent.AMPERE,
    "%": PERCENTAGE,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: DeyeCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        DeyeNumberEntity(coordinator, s)
        for s in coordinator.sensors
        if isinstance(s, NumberRWSensor)
    ]
    async_add_entities(entities)


class DeyeNumberEntity(DeyeEntity, NumberEntity):
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: DeyeCoordinator, sensor: NumberRWSensor) -> None:
        super().__init__(coordinator, sensor)
        unit = sensor.unit or ""
        self._attr_native_unit_of_measurement = _HA_UNIT.get(unit, unit or None)

    @property
    def native_value(self) -> float | None:
        val = self._sensor_value
        return float(val) if val is not None else None

    @property
    def native_min_value(self) -> float:
        return float(self.coordinator.data.resolve_num(self._sensor.min, 0))

    @property
    def native_max_value(self) -> float:
        return float(self.coordinator.data.resolve_num(self._sensor.max, 100))

    @property
    def native_step(self) -> float:
        return abs(self._sensor.factor) if self._sensor.factor else 1.0

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_write_sensor(self._sensor, value)
