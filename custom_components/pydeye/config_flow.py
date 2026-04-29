from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DEFAULT_UNIT, DOMAIN, INVERTER_TYPES

STEP_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
        vol.Required("port", default=DEFAULT_PORT): int,
        vol.Required("unit", default=DEFAULT_UNIT): int,
        vol.Required("inverter_type", default="three_phase_lv"): vol.In(INVERTER_TYPES),
        vol.Required("scan_interval", default=DEFAULT_SCAN_INTERVAL): int,
    }
)


class DeyeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                from pydeye.interfaces import ModbusTCP

                adapter = ModbusTCP(
                    user_input["host"],
                    port=user_input["port"],
                    unit=user_input["unit"],
                )
                await adapter.connect()
                await adapter.close()
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(
                    f"{user_input['host']}:{user_input['port']}:{user_input['unit']}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Deye {user_input['host']}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_SCHEMA,
            errors=errors,
        )
