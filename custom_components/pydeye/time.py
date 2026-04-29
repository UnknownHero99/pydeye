from __future__ import annotations

import datetime

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pydeye.rwsensors import TimeRWSensor

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
        DeyeTimeEntity(coordinator, s)
        for s in coordinator.sensors
        if isinstance(s, TimeRWSensor)
    ]
    async_add_entities(entities)


class DeyeTimeEntity(DeyeEntity, TimeEntity):
    @property
    def native_value(self) -> datetime.time | None:
        val = self._sensor_value  # e.g. "7:00"
        if val is None:
            return None
        try:
            parts = str(val).split(":")
            return datetime.time(int(parts[0]), int(parts[1]))
        except (ValueError, IndexError):
            return None

    async def async_set_value(self, value: datetime.time) -> None:
        await self.coordinator.async_write_sensor(
            self._sensor, f"{value.hour}:{value.minute:02d}"
        )
