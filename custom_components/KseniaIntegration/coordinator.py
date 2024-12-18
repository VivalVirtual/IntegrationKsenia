from homeassistant.components.alarm_control_panel import AlarmControlPanelState
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from .websocket_client import SimpleAlarmWebSocketClient
from datetime import timedelta
from .const import *
import logging
import json
import async_timeout

SCAN_INTERVAL = timedelta(seconds=10)
_LOGGER = logging.getLogger(__name__)


class AlarmDataCoordinator(DataUpdateCoordinator):
    """Coordinator per gestire l'aggiornamento dei dati dell'allarme e delle zone."""

    def __init__(self, hass: HomeAssistant, client: SimpleAlarmWebSocketClient):
        """Inizializza il coordinatore."""
        super().__init__(hass, _LOGGER, name="Ksenia Lares 4", update_interval=None)
        self.client = client
        zone = client._zone
        stato_zone = client._zonestato
        scenarios = client._scenarios
        partizioni = client._partizioni
        stato_partizioni = client._partizionistato
        self._stato_allarme = AlarmControlPanelState.ARMED_AWAY
        self.TMP_ZONE = self.format_zone(zone, stato_zone, True)
        self.TMP_SCENARIOS = self.format_scenari(scenarios)
        self.TMP_PARTIZIONI = self.format_partizioni(partizioni, stato_partizioni, True)
        self.data = {
            DATA_PARTITIONS: self.TMP_PARTIZIONI,
            DATA_ZONES: self.TMP_ZONE,
            DATA_SCENARIOS: self.TMP_SCENARIOS,
        }

    def format_zone(self, zone: any, stato_zone: any, firsMessage: bool):
        if firsMessage:
            TMP_ZONE = {}
            for value, value_stato in zip(
                zone["PAYLOAD"]["ZONES"], stato_zone["PAYLOAD"]["STATUS_ZONES"]
            ):
                description = value["DES"]
                if value_stato["BYP"] == "NO":
                    status = ZONE_BYPASS_OFF
                else:
                    status = ZONE_BYPASS_ON
                if value_stato["STA"] == "R":
                    allarme = ZONE_STATUS_NORMAL
                elif value_stato["STA"] == "A":
                    allarme = ZONE_STATUS_ALARM
                key = value["ID"]
                TMP_ZONE[key] = {
                    "description": description,
                    "status": status,
                    "allarme": allarme,
                }
            return TMP_ZONE
        else:
            for value, value_stato in zip(
                zone["PAYLOAD"]["ZONES"],
                stato_zone["PAYLOAD"][self.client._reciver]["STATUS_ZONES"],
            ):
                description = value["DES"]
                if value_stato["BYP"] == "NO":
                    status = ZONE_BYPASS_OFF
                else:
                    status = ZONE_BYPASS_ON

                if value_stato["STA"] == "R":
                    allarme = ZONE_STATUS_NORMAL
                elif value_stato["STA"] == "A":
                    allarme = ZONE_STATUS_ALARM
                key = value_stato["ID"]
                self.TMP_ZONE[key] = {
                    "description": description,
                    "status": status,
                    "allarme": allarme,
                }

    def format_scenari(self, scenarios: any):
        TMP_SCENARIOS = {}

        for value in scenarios["PAYLOAD"]["SCENARIOS"]:
            description = value["DES"]
            if value["CAT"] == "ARM":
                status = SCENE_ARM
            elif value["CAT"] == "PARTIAL":
                status = SCENE_PARTIAL
            else:
                status = SCENE_DISARM
            key = value["ID"]
            TMP_SCENARIOS[key] = {"description": description, "status": status}

        return TMP_SCENARIOS

    def format_partizioni(
        self, partizioni: any, stato_partizioni: any, firsMessage: bool
    ):
        zone_bypassate = False
        zone_non_bypassate = False
        """if (update):
            stato_partizioni = stato_partizioni['PAYLOAD'][self.client._reciver]['STATUS_PARTITIONS']
        else: """
        if firsMessage:
            TMP_PARTITIONS = {}
            for value, value_stato in zip(
                partizioni["PAYLOAD"]["PARTITIONS"],
                stato_partizioni["PAYLOAD"]["STATUS_PARTITIONS"],
            ):
                description = value["DES"]
                if value_stato["ARM"] == "D":
                    status = AlarmControlPanelState.DISARMED
                elif value_stato["ARM"] == "IA":
                    status = AlarmControlPanelState.ARMED_HOME
                else:
                    status = AlarmControlPanelState.ARMED_AWAY
                key = value["ID"]
                TMP_PARTITIONS[key] = {"description": description, "status": status}
            return TMP_PARTITIONS
        else:
            for value, value_stato in zip(
                partizioni["PAYLOAD"]["PARTITIONS"],
                stato_partizioni["PAYLOAD"][self.client._reciver]["STATUS_PARTITIONS"],
            ):
                description = value["DES"]
                if value_stato["ARM"] == "D":
                    status = AlarmControlPanelState.DISARMED
                elif value_stato["ARM"] == "IA":
                    status = AlarmControlPanelState.ARMED_HOME
                else:
                    status = AlarmControlPanelState.ARMED_AWAY
                key = value_stato["ID"]
                self.TMP_PARTIZIONI[key] = {
                    "description": description,
                    "status": status,
                }

    async def _async_update_data_realtime(
        self, realTimeDati, firstMessage: bool
    ) -> dict:
        if firstMessage:
            self.TMP_PARTIZIONI = self.format_partizioni(
                self.client._partizioni, json.loads(realTimeDati), True
            )
            self.TMP_ZONE = self.format_zone(
                self.client._zone, json.loads(realTimeDati), True
            )
            self.data = {
                DATA_PARTITIONS: self.TMP_PARTIZIONI,
                DATA_ZONES: self.TMP_ZONE,
                DATA_SCENARIOS: self.TMP_SCENARIOS,
            }

        else:
            if "STATUS_PARTITIONS" in realTimeDati:
                try:
                    value = self.client._partizioni["PAYLOAD"]["PARTITIONS"]
                except KeyError:
                    self.client.lettura_zone
                self.format_partizioni(
                    self.client._partizioni, json.loads(realTimeDati), False
                )
                self.data = {
                    DATA_PARTITIONS: self.TMP_PARTIZIONI,
                    DATA_ZONES: self.TMP_ZONE,
                    DATA_SCENARIOS: self.TMP_SCENARIOS,
                }
            if "STATUS_ZONES" in realTimeDati:
                try:
                    value = self.client._zone["PAYLOAD"]["ZONES"]

                except KeyError:
                    self.client.lettura_zone

                self.format_zone(self.client._zone, json.loads(realTimeDati), False)

                self.data = {
                    DATA_PARTITIONS: self.TMP_PARTIZIONI,
                    DATA_ZONES: self.TMP_ZONE,
                    DATA_SCENARIOS: self.TMP_SCENARIOS,
                }
        self.async_set_updated_data(await self._async_update_data())

    async def _async_update_data(self) -> dict:
        async with async_timeout.timeout(DEFAULT_TIMEOUT):
            return self.data
