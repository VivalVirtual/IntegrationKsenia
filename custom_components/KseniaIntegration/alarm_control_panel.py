from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    CodeFormat,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.const import STATE_ALARM_ARMED_AWAY, STATE_ALARM_DISARMED, STATE_ALARM_TRIGGERED, STATE_ALARM_ARMED_CUSTOM_BYPASS, STATE_ALARM_ARMED_HOME
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, DATA_COORDINATOR, DATA_PARTITIONS, PARTITION_STATUS_ARMED, DATA_SCENARIOS


async def async_setup_entry(hass, config, async_add_entities, discovery_info=None):
    """Configura il pannello di allarme dal config entry."""
    coordinator = hass.data[DOMAIN][config.entry_id][DATA_COORDINATOR]
    await coordinator.async_refresh()
    async_add_entities(
        SimpleAlarmControlPanel(coordinator, 'P' + idx,
                                data['description'])
        for idx, data in coordinator.data[DATA_PARTITIONS].items()
    )

    async_add_entities(
        SimpleAlarmControlPanel(coordinator, 'S' + idx,
                                data['description'])
        for idx, data in coordinator.data[DATA_SCENARIOS].items()
    )


class SimpleAlarmControlPanel(CoordinatorEntity, AlarmControlPanelEntity):
    """Implementazione del pannello di controllo allarme."""

    def __init__(self,
                 coordinator: CoordinatorEntity,
                 idx: str, description: str) -> None:
        """Inizializza il pannello di allarme."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._idx = idx
        self._description = description
        # self._state = coordinator._client.
        self._attr_code_arm_required = True
        self._attr_code_format = CodeFormat.NUMBER

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        name = self._idx
        return f"lares_panel_{name}"

    @property
    def name(self):
        """Nome del pannello di allarme."""
        return self._description

    @property
    def state(self):
        """Restituisce lo stato attuale del pannello di allarme."""
        if ('P' in self._idx):
            self._state = self.coordinator.data[DATA_PARTITIONS][self._idx.split('P')[
                1]]["status"]
            print("state" + self._state)
        else:
            self._state = STATE_ALARM_DISARMED

        return self._state

    @property
    def supported_features(self):
        if ('P' in self._idx):
            return (
                AlarmControlPanelEntityFeature.ARM_HOME
                | AlarmControlPanelEntityFeature.ARM_AWAY
            )
        elif ('S' in self._idx):
            return (
                AlarmControlPanelEntityFeature.ARM_HOME
            )
        """Ritorna le funzionalità supportate."""

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        if (code == self._coordinator.client._pin):
            if ('P' in self._idx):
                await self._coordinator.client.arm_partition('D', self._idx.split('P')[
                    1], code)

    async def async_alarm_arm_away(self, code: str | None = None):
        """Arma il sistema di allarme in modalità 'away'."""
        if (code == self._coordinator.client._pin):
            if ('P' in self._idx):
                await self._coordinator.client.arm_partition('A', self._idx.split('P')[
                    1], code)

    async def async_alarm_arm_home(self, code: str | None = None):
        if (code == self._coordinator.client._pin):
            if ('P' in self._idx):
                await self._coordinator.client.arm_partition('I', self._idx.split('P')[
                    1], code)
            elif ('S' in self._idx):
                await self.coordinator.client.arm_scene(self._idx.split('S')[1])

    async def alarm_trigger(self, code=None):
        """Attiva l'allarme."""
        await self._coordinator.client.arm_partition('A', self._idx)

    def alarm_arm_custom_bypass(self, code=None) -> None:
        """Send arm custom bypass command."""
        pass

    async def async_alarm_arm_custom_bypass(self, code=None) -> None:
        """Send arm custom bypass command."""
        pass
