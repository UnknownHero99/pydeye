from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _get_sensor_defs(inverter_type: str):
    if inverter_type == "three_phase_lv":
        from pydeye.definitions.three_phase_lv import THREE_PHASE_LV
        return THREE_PHASE_LV
    if inverter_type == "three_phase":
        from pydeye.definitions.three_phase_common import THREE_PHASE
        return THREE_PHASE
    if inverter_type == "single_phase":
        from pydeye.definitions.single_phase import SINGLE_PHASE
        return SINGLE_PHASE
    from pydeye.definitions.three_phase_lv import THREE_PHASE_LV
    return THREE_PHASE_LV


class DeyeCoordinator(DataUpdateCoordinator):
    serial: str
    inverter_type: str

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        unit: int,
        inverter_type: str,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.host = host
        self.port = port
        self.unit = unit
        self.inverter_type = inverter_type
        self._adapter = None
        self._inverter = None
        self.sensors: list = []
        self.serial = f"{host}:{port}"

    async def async_setup(self) -> None:
        from pydeye.interfaces import ModbusTCP
        from pydeye.inverters.base_inverter import BaseInverter

        self._adapter = ModbusTCP(self.host, port=self.port, unit=self.unit)
        await self._adapter.connect()

        self._inverter = BaseInverter(self._adapter)
        defs = _get_sensor_defs(self.inverter_type)
        self.sensors = list(defs)
        for s in self.sensors:
            self._inverter.state.track(s)

        try:
            basic_info = await self._adapter.get_basic_info()
            self.serial = str(basic_info.serial_number)
        except Exception:
            pass

    async def _async_update_data(self):
        try:
            if not self._adapter.connected():
                await self._adapter.connect()
            await self._inverter.read_sensors(self.sensors)
        except Exception as err:
            raise UpdateFailed(f"Error reading inverter at {self.host}: {err}") from err
        return self._inverter.state

    async def async_shutdown(self) -> None:
        if self._adapter:
            await self._adapter.close()

    async def async_write_sensor(self, sensor, value) -> None:
        await self._inverter.write_sensor(sensor, value)
        await self.async_request_refresh()
