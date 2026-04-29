from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pydeye.helper import AMPS, CELSIUS, HZ, KWH, VOLT, WATT
from pydeye.rwsensors import RWSensor
from pydeye.sensor import BinarySensor, Constant, Sensor

from .const import DOMAIN
from .coordinator import DeyeCoordinator
from .entity import DeyeEntity

_HA_UNIT = {
    WATT: UnitOfPower.WATT,
    KWH: UnitOfEnergy.KILO_WATT_HOUR,
    VOLT: UnitOfElectricPotential.VOLT,
    AMPS: UnitOfElectricCurrent.AMPERE,
    HZ: UnitOfFrequency.HERTZ,
    CELSIUS: UnitOfTemperature.CELSIUS,
    "%": PERCENTAGE,
    "AH": "Ah",
}

_DEVICE_CLASS = {
    WATT: SensorDeviceClass.POWER,
    KWH: SensorDeviceClass.ENERGY,
    VOLT: SensorDeviceClass.VOLTAGE,
    AMPS: SensorDeviceClass.CURRENT,
    HZ: SensorDeviceClass.FREQUENCY,
    CELSIUS: SensorDeviceClass.TEMPERATURE,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: DeyeCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for sensor in coordinator.sensors:
        if isinstance(sensor, (BinarySensor, RWSensor, Constant)):
            continue
        if isinstance(sensor, Sensor):
            entities.append(DeyeSensorEntity(coordinator, sensor))
    async_add_entities(entities)


class DeyeSensorEntity(DeyeEntity, SensorEntity):
    def __init__(self, coordinator: DeyeCoordinator, sensor: Sensor) -> None:
        super().__init__(coordinator, sensor)
        unit = sensor.unit or ""
        self._attr_native_unit_of_measurement = _HA_UNIT.get(unit, unit or None)
        self._attr_device_class = _DEVICE_CLASS.get(unit)

        if unit == KWH:
            self._attr_state_class = (
                SensorStateClass.TOTAL
                if "Day" in sensor.name
                else SensorStateClass.TOTAL_INCREASING
            )
        elif unit in _DEVICE_CLASS or unit == "%":
            self._attr_state_class = SensorStateClass.MEASUREMENT
        else:
            self._attr_state_class = None

        # Battery SOC gets battery device class
        if "SOC" in sensor.name and unit == "%":
            self._attr_device_class = SensorDeviceClass.BATTERY

    @property
    def native_value(self):
        return self._sensor_value
