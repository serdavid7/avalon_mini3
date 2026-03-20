# custom_components/avalon_mini3/select.py
from __future__ import annotations

import logging

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
    "Heater": 0,
    "Mining": 1,
    "Night": 2,
}
REVERSE_WORK_MODES = {v: k for k, v in WORK_MODES.items()}

# =========================
# Worklevels Mapping
# =========================
WORK_LEVELS = {
    "Eco": -1,
    "Super": 0
}
REVERSE_WORK_LEVELS = {v: k for k, v in WORK_LEVELS.items()}

# =========================
# LCD Mapping
# =========================
LCD = {
    "off": "0:0",
    "on": "0:1",
}
REVERSE_LCD = {v: k for k, v in LCD.items()}


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
            AvalonWorkModeSelect(coordinator, api, entry.entry_id, device_info),
            AvalonWorkLevelSelect(coordinator, api, entry.entry_id, device_info),
            AvalonLCDSelect(coordinator, api, entry.entry_id, device_info)
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
        try:
            return REVERSE_WORK_MODES[int(workmode_val)]
        except (TypeError, ValueError, KeyError):
            return "Low"

    async def async_select_option(self, option: str) -> None:
        level = WORK_MODES.get(option)
        if level is None:
            _LOGGER.warning("Unbekannter Workmode: %s", option)
            return

        await self.api.set_workmode(level)
        await self.coordinator.async_request_refresh()

# =========================
# Worklevel Select
# =========================
class AvalonWorkLevelSelect(CoordinatorEntity, SelectEntity):

    _attr_has_entity_name = True
    _attr_options = list(WORK_LEVELS.keys())
    _attr_translation_key = "worklevel"

    def __init__(
        self,
        coordinator: AvalonMinerCoordinator,
        api: AsyncMini3AvalonAPI,
        entry_id: str,
        device_info: dict,
    ):
        super().__init__(coordinator)
        self.api = api

        self._attr_unique_id = f"{entry_id}_worklevel"
        self._attr_device_info = device_info

    @property
    def current_option(self) -> str:
        estats = self.coordinator.data.get("estats", {})
        worklevel_val = estats.get("WORKLEVEL")
        try:
            return REVERSE_WORK_LEVELS[int(worklevel_val)]
        except (TypeError, ValueError, KeyError):
            return "Super"

    async def async_select_option(self, option: str) -> None:
        level = WORK_LEVELS.get(option)
        if level is None:
            _LOGGER.warning("Unbekannter Worklevel: %s", option)
            return

        await self.api.set_worklevel(level)
        await self.coordinator.async_request_refresh()

# =========================
# LCD Select
# =========================
class AvalonLCDSelect(CoordinatorEntity, SelectEntity):

    _attr_has_entity_name = True
    _attr_options = list(LCD.keys())
    _attr_translation_key = "lcd"

    def __init__(
        self,
        coordinator: AvalonMinerCoordinator,
        api: AsyncMini3AvalonAPI,
        entry_id: str,
        device_info: dict,
    ):
        super().__init__(coordinator)
        self.api = api

        self._attr_unique_id = f"{entry_id}_lcd"
        self._attr_device_info = device_info

    @property
    def current_option(self) -> str:
        estats = self.coordinator.data.get("estats", {})
        lcd_val = estats.get("LCD")
        try:
            return REVERSE_LCD[lcd_val]
        except (TypeError, ValueError, KeyError):
            return "off"

    async def async_select_option(self, option: str) -> None:
        level = LCD.get(option)
        if level is None:
            _LOGGER.warning("Unknown LCD option: %s", option)
            return

        await self.api.set_lcd(level)
        await self.coordinator.async_request_refresh()
