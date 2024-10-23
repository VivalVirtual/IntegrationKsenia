from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .websocket_client import SimpleAlarmWebSocketClient
from .websocket_super_user import WebsocketSuperUser

from homeassistant.const import Platform
from .coordinator import AlarmDataCoordinator  # Importa il coordinatore
from .const import DOMAIN, DATA_COORDINATOR


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Simple Alarm from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    websocket_uri = 'wss://' + \
        entry.data.get("ip") + ':' + entry.data.get("port") + '/KseniaWsock'

    # Inizializza WebSocket e gestisci il login
    websocket_client = SimpleAlarmWebSocketClient(
        websocket_uri, entry.data.get("macAddr"), entry.data.get('code'))

    await websocket_client.connect()

    coordinator = AlarmDataCoordinator(hass, websocket_client)
    websocket_super_user = WebsocketSuperUser(
        websocket_uri, entry.data.get("macAddr"), entry.data.get('pinSuper'), coordinator, websocket_client)

    await websocket_super_user.connectSuperUser()

    # Crea entità, servizi, ecc.
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(
            entry, "alarm_control_panel")
    )
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator
    }

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(
            entry, [Platform.ALARM_CONTROL_PANEL, Platform.SWITCH,  Platform.BUTTON, Platform.BINARY_SENSOR])
    )

    return True
