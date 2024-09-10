"""Support for the Scene ."""
from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from .coordinator import AlarmDataCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import EntityCategory
from .const import DOMAIN, DATA_COORDINATOR, DATA_ZONES, DATA_SCENARIOS

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    CodeFormat,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:

    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]
    await coordinator.async_refresh()
    """async_add_entities(
        NAMButton(coordinator, idx,
                  data['description'], data['status'], 'S')
        for idx, data in coordinator.data[DATA_SCENARIOS].items()
    )"""


class NAMButton(CoordinatorEntity, ButtonEntity):

    _attr_has_entity_name = True
    _attr_translation_key = "scenario"
    _attr_device_class = ButtonDeviceClass.IDENTIFY
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        idx: int, description: str, status, wordIndx,

    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._idx = wordIndx + str(idx)
        self._attr_name = description
        self._attr_code_arm_required = True,
        self._attr_code_format = CodeFormat.NUMBER,

    async def async_press(self, **kwargs) -> None:
        """Triggers the scene."""
        await self.coordinator.client.arm_scene(self._idx.split('S')[1])

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return f"lares_zone_{self._idx}"
