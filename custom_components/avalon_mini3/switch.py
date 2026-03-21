# custom_components/avalon_mini3/switch.py
from __future__ import annotations

import logging
import time

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AvalonMinerCoordinator
from .avalon_api import AsyncMini3AvalonAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

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
            AvalonLCDSwitch(coordinator, api, entry.entry_id, device_info),
            AvalonStandbySwitch(coordinator, api, entry.entry_id, device_info)
        ]
    )

class AvalonLCDSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True
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
    def is_on(self) -> bool:
        """Return true if LCD is on."""
        estats = self.coordinator.data.get("estats", {})
        lcd_val = estats.get("lcd", {}).get("Light")
        return lcd_val == 1

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the LCD on."""
        await self.api.set_lcd("0:1")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the LCD off."""
        await self.api.set_lcd("0:0")
        await self.coordinator.async_request_refresh()


class AvalonStandbySwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "standby"
    _attr_icon = "mdi:power"

    def __init__(
        self,
        coordinator: AvalonMinerCoordinator,
        api: AsyncMini3AvalonAPI,
        entry_id: str,
        device_info: dict,
    ):
        super().__init__(coordinator)
        self.api = api

        self._attr_unique_id = f"{entry_id}_standby"
        self._attr_device_info = device_info

    @property
    def is_on(self) -> bool:
        """Return true if standby is on."""
        # Check if system is in idle mode (standby active)
        estats = self.coordinator.data.get("estats", {})
        system_status = estats.get("misc", {}).get("SYSTEMSTATU", "")
        return "In Idle" in system_status

    async def async_turn_on(self, **kwargs) -> None:
        """Turn standby mode on."""
        current_time = int(time.time())
        await self.api.set_soft_off(current_time)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn standby mode off."""
        current_time = int(time.time())
        await self.api.set_soft_on(current_time)
        await self.coordinator.async_request_refresh()