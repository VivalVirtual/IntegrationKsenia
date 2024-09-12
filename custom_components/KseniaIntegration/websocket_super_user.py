from .coordinator import AlarmDataCoordinator
from .const import *
from asyncio import Queue
import time
import asyncio
import websockets
import logging
import ssl
from .crc import addCRC
import json
from .websocket_client import SimpleAlarmWebSocketClient
_LOGGER = logging.getLogger(__name__)
message_queue = Queue()


class WebsocketSuperUser:
    """Class to manage WebSocket connection to the alarm system."""

    def __init__(self, uri, macAddr, pinSuper, coordinator: AlarmDataCoordinator, websocket: SimpleAlarmWebSocketClient):
        """Initialize the WebSocket client."""
        self._uri = uri
        self._websocket = None
        self.userWebsocket = websocket
        self._connected = False
        self._mac = macAddr
        self._pinSuper = pinSuper
        self._id = 0
        self._reciver = ''
        self._stato_allarme = STATE_ALARM_DISARMED
        self._recv_lock = asyncio.Lock()
        self.coordinator = coordinator

    async def send(self, message):
        """Send a message to the WebSocket server."""
        if self._connected and self._websocket:
            try:
                await self._websocket.send(message)

                _LOGGER.info(f" \n Sent message: {message}  \n ")
                return message
            except (websockets.ConnectionClosedError, websockets.ConnectionClosedOK, OSError) as e:
                _LOGGER.error(f"Connection lost: {e}")
                self._running = False
                self._connected = False

                await self.connectSuperUser()
                await self.userWebsocket.connect()

    async def receive(self):
        """Receive a message from the WebSocket server."""
        if self._connected and self._websocket:
            async with self._recv_lock:  # Assicura che solo una coroutine alla volta possa chiamare recv()
                try:
                    message = await self._websocket.recv()
                    _LOGGER.info(f" \n  Received message: {message} \n ")
                    return message
                except (websockets.ConnectionClosedError, websockets.ConnectionClosedOK, OSError) as e:
                    _LOGGER.error(f"Connection lost: {e}")
                    self._connected = False
                    self._running = False
                    return None

    async def connectSuperUser(self):
        """Connect to the WebSocket server."""
        response = None
        while not self._connected:
            try:
                sslcontext = ssl.create_default_context()
                sslcontext.options |= ssl.OP_LEGACY_SERVER_CONNECT
                sslcontext.check_hostname = False
                sslcontext.verify_mode = ssl.CERT_NONE
                self._websocket = await websockets.connect(
                    self._uri, ssl=sslcontext, subprotocols=["KS_WSOCK"],  ping_interval=20, ping_timeout=10)
                self._connected = True
                _LOGGER.info(
                    f"Connected super user to WebSocket server at {self._uri}")
                print("-------- connessione super user ripresa ")
            except Exception as e:
                _LOGGER.error(f"Failed to connect to WebSocket server: {e}")
                print("-------- connessione persa ")
                self._connected = False
                time.sleep(30)
        response = None
        while response == None:
            # Fa il login User
            try:
                await self.send(addCRC('{"SENDER":"012345678901", "RECEIVER":"' + self._mac +
                                       '", "CMD":"LOGIN", "ID": "65535", "PAYLOAD_TYPE":"IP_SUPERV", "PAYLOAD":{ "PIN": "' + self._pinSuper + '"}, "TIMESTAMP":"' + str(int(time.time())) + '", "CRC_16":"0x0000"}'))
                response = await asyncio.wait_for(self.receive(), timeout=60)
                if response:
                    data = json.loads(response)
                    self._id = data['PAYLOAD']['ID_LOGIN']
                    self._reciver = data['RECEIVER']

            except Exception as e:
                _LOGGER.error(f"Impossibile fare il login: {e}")

        await self.send(addCRC('{"SENDER":"012345678901", "RECEIVER":"' + self._mac + '", "CMD":"REALTIME","ID":"2","PAYLOAD_TYPE":"REGISTER","PAYLOAD":{ "ID_LOGIN": "' + str(self._id) + '" ,  "TYPES":["STATUS_PARTITIONS", "STATUS_ZONES", "ZONES"] },"TIMESTAMP" : "' + str(int(time.time())) + '","CRC_16":""}'))
        response = await self.receive()
        await self.coordinator._async_update_data_realtime(response, True)
        self._running = True
        asyncio.create_task(self.listen_for_messages())

    async def listen_for_messages(self):
        message = ""
        """Listen for incoming messages in a loop."""
        while self._running and message is not None:
            print("running -- " + str(self._running))
            message = await self.receive()
            print("stop" + str(self._running))
            if message:
                await self.coordinator._async_update_data_realtime(message, False)

        print("reconecting")
        await self.connectSuperUser()
        await self.userWebsocket.connect()

    def process_message(self, message):
        """Process the received WebSocket message."""
        # Logica per elaborare il messaggio
        _LOGGER.info(f"Processing message: {message}")
