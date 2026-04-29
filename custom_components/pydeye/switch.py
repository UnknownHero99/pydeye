from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pydeye.helper import BOOL_ON
from pydeye.rwsensors import SwitchRWSensor

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
        DeyeSwitchEntity(coordinator, s)
        for s in coordinator.sensors
        if isinstance(s, SwitchRWSensor)
    ]
    async_add_entities(entities)


class DeyeSwitchEntity(DeyeEntity, SwitchEntity):
    @property
    def is_on(self) -> bool | None:
        val = self._sensor_value
        if val is None:
            return None
        return str(val) == BOOL_ON

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_write_sensor(self._sensor, BOOL_ON)

    async def async_turn_off(self, **kwargs) -> None:
        from pydeye.helper import BOOL_OFF
        await self.coordinator.async_write_sensor(self._sensor, BOOL_OFF)
