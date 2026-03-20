# custom_components/avalon_mini3/select.py
from __future__ import annotations

import logging
import asyncio

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AvalonMinerCoordinator
from .avalon_api import AsyncMini3AvalonAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# =========================
# Workmode Mapping
# =========================
WORK_MODES = {
    "Mining": 1,
    "Night": 2,
    "Heater - Eco": "heater_eco",
    "Heater - Super": "heater_super",
}

# =========================
# Setup Entry
# =========================
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]

    coordinator: AvalonMinerCoordinator = data["coordinator"]
    api: AsyncMini3AvalonAPI = data["api"]
    device_info = data["device_info"]

    async_add_entities(
        [
            AvalonWorkModeSelect(coordinator, api, entry.entry_id, device_info)
        ]
    )


# =========================
# Workmode Select
# =========================
class AvalonWorkModeSelect(CoordinatorEntity, SelectEntity):

    _attr_has_entity_name = True
    _attr_options = list(WORK_MODES.keys())
    _attr_translation_key = "workmode"

    def __init__(
        self,
        coordinator: AvalonMinerCoordinator,
        api: AsyncMini3AvalonAPI,
        entry_id: str,
        device_info: dict,
    ):
        super().__init__(coordinator)
        self.api = api

        self._attr_unique_id = f"{entry_id}_workmode"
        self._attr_device_info = device_info

    @property
    def current_option(self) -> str:
        estats = self.coordinator.data.get("estats", {})
        workmode_val = estats.get("WORKMODE")
        worklevel_val = estats.get("WORKLEVEL")

        # Determine the current mode and level
        if workmode_val == 0 and worklevel_val == -1:
            return "Heater - Eco"
        elif workmode_val == 0 and worklevel_val == 0:
            return "Heater - Super"
        elif workmode_val == 1:
            return "Mining"
        elif workmode_val == 2:
            return "Night"
        
        return "Mining"  # Default fallback

    async def async_select_option(self, option: str) -> None:
        try:
            if option == "Heater - Eco":
                await self.api.set_workmode(0)  # Heater mode
                await asyncio.sleep(0.5)  # Small delay to prevent race condition
                await self.api.set_worklevel(-1)  # Eco level
            elif option == "Heater - Super":
                await self.api.set_workmode(0)  # Heater mode
                await asyncio.sleep(0.5)  # Small delay to prevent race condition
                await self.api.set_worklevel(0)  # Super level
            elif option == "Mining":
                await self.api.set_workmode(1)  # Mining mode
            elif option == "Night":
                await self.api.set_workmode(2)  # Night mode
            else:
                _LOGGER.warning("Unknown work mode: %s", option)
                return

            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error("Error setting work mode: %s", e)
