from typing import Any
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from .coordinator import AlarmDataCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import EntityCategory
from .const import DOMAIN, DATA_COORDINATOR, DATA_ZONES, DATA_SCENARIOS, ZONE_BYPASS_ON, ZONE_BYPASS_OFF, DATA_PARTITIONS, PARTITION_STATUS_ARMED, PARTITION_STATUS_DISARMED


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up switch entities for Lares alarm device from a config entry."""

    # Access the coordinator and device info
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]

    # Fetch initial data to ensure entities have data when they subscribe
    await coordinator.async_refresh()

    # Add switch entities for each zone
    async_add_entities(
        ZoneBypassSwitch(coordinator, idx,
                         data['description'], data['status'], 'Z')
        for idx, data in coordinator.data[DATA_ZONES].items()
    )
    # async_add_entities(
    #    ZoneBypassSwitch(coordinator, idx,
    #                     data['description'], data['status'], 'P')
    #    for idx, data in coordinator.data[DATA_PARTITIONS].items()
    # )


class ZoneBypassSwitch(CoordinatorEntity, SwitchEntity):
    """Switch per bypassare una zona dell'allarme."""
    _attr_translation_key = "bypass"
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: AlarmDataCoordinator, idx: int, descrption: str, status, wordIndx):
        """Inizializza l'interruttore di bypass della zona."""
        super().__init__(coordinator)

        self._coordinator = coordinator
        self._idx = wordIndx + str(idx)
        self._attr_name = descrption
        self.___is_on = status
        self._attr_entity_registry_enabled_default = status
        self._attr_entity_registry_visible_default = status

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return f"lares_zone_{self._idx}"

    @property
    def icon(self) -> str:
        if self.___is_on:
            return "mdi:shield"
        else:
            return "mdi:shield-off"

    @property
    def is_on(self) -> bool:
        """Restituisce true se la zona è bypassata."""
        self.___is_on = self.coordinator.data[DATA_ZONES][self._idx.split('Z')[
            1]]["status"] == ZONE_BYPASS_OFF
        return self.___is_on

    async def async_turn_on(self, **kwargs):
        """Abilita il bypass per la zona."""
        await self._coordinator.client.bypass_zone('OFF', self._idx.split('Z')[1])

    async def async_turn_off(self, **kwargs):
        """Disabilita il bypass per la zona."""
        await self._coordinator.client.bypass_zone('ON', self._idx.split('Z')[1])
