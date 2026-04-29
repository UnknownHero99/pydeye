from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DeyeCoordinator


class DeyeEntity(CoordinatorEntity[DeyeCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: DeyeCoordinator, sensor) -> None:
        super().__init__(coordinator)
        self._sensor = sensor
        self._attr_unique_id = f"{coordinator.serial}_{sensor.id}"
        self._attr_name = sensor.name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.serial)},
            name=f"Deye Inverter ({coordinator.serial})",
            manufacturer="Deye",
            model=DOMAIN,
        )

    @property
    def _sensor_value(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._sensor)
