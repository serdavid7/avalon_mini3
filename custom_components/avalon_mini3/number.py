# custom_components/avalon_mini3/number.py
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
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
            AvalonLimitTempNumber(coordinator, api, entry.entry_id, device_info)
        ]
    )

class AvalonLimitTempNumber(CoordinatorEntity, NumberEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "limit_temp"
    _attr_native_min_value = 20
    _attr_native_max_value = 50
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX
    _attr_native_value = 50  # Default to 50 degrees

    def __init__(
        self,
        coordinator: AvalonMinerCoordinator,
        api: AsyncMini3AvalonAPI,
        entry_id: str,
        device_info: dict,
    ):
        super().__init__(coordinator)
        self.api = api

        self._attr_unique_id = f"{entry_id}_limit_temp"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> float | None:
        """Return the current limit temperature."""
        # Assuming the limit temperature is stored in the coordinator data
        # You might need to adjust this based on how the data is actually stored
        return self.coordinator.data.get("limit_temp")

    async def async_set_native_value(self, value: float) -> None:
        """Set the limit temperature."""
        try:
            await self.api.set_limit_temp(int(value))
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error("Failed to set limit temperature: %s", e)