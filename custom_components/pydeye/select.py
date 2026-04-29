from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pydeye.rwsensors import SelectRWSensor

from .const import DOMAIN
from .coordinator import DeyeCoordinator
from .entity import DeyeEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: DeyeCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        DeyeSelectEntity(coordinator, s)
        for s in coordinator.sensors
        if isinstance(s, SelectRWSensor)
    ]
    async_add_entities(entities)


class DeyeSelectEntity(DeyeEntity, SelectEntity):
    def __init__(self, coordinator: DeyeCoordinator, sensor: SelectRWSensor) -> None:
        super().__init__(coordinator, sensor)
        self._attr_options = sensor.available_values()

    @property
    def current_option(self) -> str | None:
        val = self._sensor_value
        return str(val) if val is not None else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_write_sensor(self._sensor, option)
