from datetime import timedelta
import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, DATA_COORDINATOR, DATA_ZONES, DATA_SCENARIOS, ZONE_BYPASS_ON, ZONE_BYPASS_OFF, DATA_PARTITIONS, PARTITION_STATUS_ARMED, PARTITION_STATUS_DISARMED
from .const import (
    DOMAIN,
    DATA_ZONES,
    ZONE_BYPASS_ON,
    ZONE_STATUS_ALARM,
    ZONE_STATUS_NOT_USED,
    DATA_COORDINATOR,
)
SCAN_INTERVAL = timedelta(seconds=10)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors attached to a Lares alarm device from a config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]
    await coordinator.async_refresh()

    async_add_entities(
        LaresBinarySensor(coordinator, idx,
                          data['description'])
        for idx, data in coordinator.data[DATA_ZONES].items()
    )


class LaresBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """An implementation of a Lares door/window/motion sensor."""

    def __init__(self,
                 coordinator: CoordinatorEntity,
                 idx: int, description: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._description = description
        self._idx = idx

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"lares_zones_{self._idx}"

    @property
    def name(self):
        """Return the name of this camera."""
        return self._description

    @property
    def is_on(self):
        """Return the state of the sensor."""
        self._ison = self._coordinator.data[DATA_ZONES][self._idx]["allarme"] == ZONE_STATUS_ALARM
        return self._ison

    @property
    def available(self):
        """Return True if entity is available."""
        return True
