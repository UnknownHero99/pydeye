from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pydeye.helper import BOOL_ON
from pydeye.sensor import BinarySensor

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
        DeyeBinarySensorEntity(coordinator, s)
        for s in coordinator.sensors
        if type(s) is BinarySensor
    ]
    async_add_entities(entities)


class DeyeBinarySensorEntity(DeyeEntity, BinarySensorEntity):
    @property
    def is_on(self) -> bool | None:
        val = self._sensor_value
        if val is None:
            return None
        return str(val) == BOOL_ON
