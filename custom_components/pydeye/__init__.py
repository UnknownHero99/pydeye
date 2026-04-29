from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import DeyeCoordinator

PLATFORMS = ["sensor", "binary_sensor", "switch", "number", "select", "time"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = DeyeCoordinator(
        hass,
        host=entry.data["host"],
        port=entry.data["port"],
        unit=entry.data["unit"],
        inverter_type=entry.data["inverter_type"],
        scan_interval=entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL),
    )
    await coordinator.async_setup()
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        coordinator: DeyeCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    return unloaded
