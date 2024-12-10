import random
from .const import *
from asyncio import Queue
import time
import asyncio
import websockets
import websocket
import logging
import ssl
from .crc import addCRC
import json
_LOGGER = logging.getLogger(__name__)
message_queue = Queue()


class SimpleAlarmWebSocketClient:
    """Class to manage WebSocket connection to the alarm system."""

    def __init__(self, uri, macAddr, pin):
        """Initialize the WebSocket client."""
        self._uri = uri
        self._websocket = None
        self._connected = False
        self._mac = macAddr
        self._pin = pin
        self._id = 0
        self._reciver = ''
        self._stato_allarme = STATE_ALARM_DISARMED
        self._recv_lock = asyncio.Lock()

    async def send(self, message):
        """Send a message to the WebSocket server."""
        if self._connected and self._websocket:
            try:
                await self._websocket.send(message)

                _LOGGER.info(f" \n Sent message: {message}  \n ")
                return message
            except (websockets.ConnectionClosedError, websockets.ConnectionClosedOK, OSError) as e:
                _LOGGER.error(f"Connection lost: {e}")
                self._connected = False
                await self.connect()

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
                    await self.connect()

    async def connect(self):
        """Connect to the WebSocket server."""
        backoff = 5  # Start with 5 seconds
        self._connected = False
        while not self._connected:
            try:

                sslcontext = ssl.create_default_context()
                sslcontext.options |= ssl.OP_LEGACY_SERVER_CONNECT
                sslcontext.check_hostname = False
                sslcontext.verify_mode = ssl.CERT_NONE
                self._websocket = await websockets.connect(
                    self._uri, ssl=sslcontext, subprotocols=["KS_WSOCK"],
                    ping_interval=30, ping_timeout=30
                )

                self._connected = True
                _LOGGER.info(f"Connected to WebSocket server at {self._uri}")
                backoff = 5  # Reset backoff after successful connection
            except asyncio.TimeoutError:
                _LOGGER.error("Connection timed out")
                sleep_time = backoff + random.uniform(0, 1)
                await asyncio.sleep(sleep_time)

                backoff = min(backoff * 2, 300)  # Cap backoff to 5 minutes

            except websockets.InvalidStatusCode as e:
                _LOGGER.error(f"Server rejected connection with status code {
                              e.status_code}")
            except Exception as e:
                _LOGGER.error(f"Failed to connect to WebSocket server: {e}")
                self._connected = False
                sleep_time = backoff + random.uniform(0, 1)
                await asyncio.sleep(sleep_time)
                backoff = min(backoff * 2, 300)  # Cap backoff to 5 minutes

        response = None
        while response is None:
            # Fa il login User
            try:
                await self.send(addCRC('{"SENDER":"012345678901", "RECEIVER":"' + str(self._mac) +
                                       '", "CMD":"LOGIN", "ID": "65535", "PAYLOAD_TYPE":"USER", "PAYLOAD":{ "PIN": "' + str(self._pin) + '"}, "TIMESTAMP":"' + str(int(time.time())) + '", "CRC_16":"0x0000"}'))
                response = await asyncio.wait_for(self.receive(), timeout=60)

                data = json.loads(response)
                self._id = data['PAYLOAD']['ID_LOGIN']
                self._reciver = data['RECEIVER']
            except Exception as e:
                _LOGGER.error(f"Impossibile fare il login: {e}")

            # Lettura zone
            try:
                data_zone = await self.lettura_zone()
                self._zone = data_zone
            except Exception as e:
                _LOGGER.error(f"Impossibile trovare le zone: {e}")

            # Lettura stato zone
            try:
                data_zone = await self.stato_zone()
                self._zonestato = data_zone
            except Exception as e:
                _LOGGER.error(f"Impossibile leggere lo stato delle zone: {e}")

            # Lettura scene
            try:
                data_scenarios = await self.lettura_scenario()
                self._scenarios = data_scenarios
            except Exception as e:
                _LOGGER.error(f"Impossibile leggere lo stato delle scene: {e}")

            # Lettura partizioni
            try:

                data_partizioni = await self.lettura_partizioni()
                self._partizioni = data_partizioni
            except Exception as e:
                _LOGGER.error(f"Impossibile trovare le zone: {e}")

            # Lettura stato partizioni
            try:
                stato_partizione = await self.stato_partizioni()
                self._partizionistato = stato_partizione
            except Exception as e:
                _LOGGER.error(f"Impossibile leggere lo stato delle zone: {e}")

    async def lettura_zone(self):
        try:
            await self.send(addCRC('{"SENDER":"012345678901", "RECEIVER":"' + self._mac +
                                   '", "CMD":"READ", "ID": "65535", "PAYLOAD_TYPE":"ZONES", "PAYLOAD":{ "ID_LOGIN": "' + str(self._id) + '" ,  "TYPES":["ZONES"] }, "TIMESTAMP":"' + str(int(time.time())) + '", "CRC_16":"0x0000"}'))
            response = await self.receive()
            return json.loads(response)

        except Exception as e:
            _LOGGER.error(f"Impossibile leggere le zone: {e}")

    async def lettura_scenario(self):
        try:
            await self.send(addCRC('{"SENDER":"012345678901", "RECEIVER":"' + self._mac +
                                   '", "CMD":"READ", "ID": "65535", "PAYLOAD_TYPE":"SCENARIOS", "PAYLOAD":{ "ID_LOGIN": "' + str(self._id) + '" ,  "TYPES":["SCENARIOS"] }, "TIMESTAMP":"' + str(int(time.time())) + '", "CRC_16":"0x0000"}'))
            response = await self.receive()
            return json.loads(response)

        except Exception as e:
            _LOGGER.error(f"Impossibile leggere gli scenari: {e}")

    async def lettura_partizioni(self):
        try:
            await self.send(addCRC('{"SENDER":"012345678901", "RECEIVER":"' + self._mac +
                                   '", "CMD":"READ", "ID": "65535", "PAYLOAD_TYPE":"PARTITIONS", "PAYLOAD":{ "ID_LOGIN": "' + str(self._id) + '" ,  "TYPES":["PARTITIONS"] }, "TIMESTAMP":"' + str(int(time.time())) + '", "CRC_16":"0x0000"}'))
            response = await self.receive()
            return json.loads(response)

        except Exception as e:
            _LOGGER.error(f"Impossibile leggere le partizioni: {e}")

    async def stato_zone(self):
        try:
            await self.send(addCRC('{"SENDER":"012345678901", "RECEIVER":"' + self._mac +
                                   '", "CMD":"READ", "ID": "65535", "PAYLOAD_TYPE":"STATUS_ZONES", "PAYLOAD":{ "ID_LOGIN": "' + str(self._id) + '" ,  "TYPES":["STATUS_ZONES"] }, "TIMESTAMP":"' + str(int(time.time())) + '", "CRC_16":"0x0000"}'))
            response = await self.receive()
            return json.loads(response)

        except Exception as e:
            _LOGGER.error(f"Impossibile leggere stato zone : {e}")

    async def stato_partizioni(self):
        try:
            await self.send(addCRC('{"SENDER":"012345678901", "RECEIVER":"' + self._mac +
                                   '", "CMD":"READ", "ID": "65535", "PAYLOAD_TYPE":"STATUS_PARTITIONS", "PAYLOAD":{ "ID_LOGIN": "' + str(self._id) + '" ,  "TYPES":["STATUS_PARTITIONS"] }, "TIMESTAMP":"' + str(int(time.time())) + '", "CRC_16":"0x0000"}'))
            response = await self.receive()
            return json.loads(response)

        except Exception as e:
            _LOGGER.error(f"Impossibile leggere stato partizioni: {e}")

    async def bypass_zone(self, bypass: str, zoneId: str):
        try:
            await self.send(addCRC('{"SENDER":"012345678901", "RECEIVER":"' + self._mac + '", "CMD":"CMD_USR","ID":"2","PAYLOAD_TYPE":"CMD_BYP_ZONE","PAYLOAD":{"ID_LOGIN":"' + str(self._id) + '","PIN":"' + self._pin + '","ZONE":{"ID":"' + zoneId + '" , "BYP":"' + bypass + '" }  },"TIMESTAMP" : "' + str(int(time.time())) + '","CRC_16":"0x0000"}'))
            response = await self.receive()
            return json.loads(response)

        except Exception as e:
            _LOGGER.error(f"Impossibile bypass zone : {e}")

    async def arm_partition(self, arm: str, partId: str, code):
        try:
            await self.send(addCRC('{"SENDER":"012345678901", "RECEIVER":"' + self._mac + '", "CMD":"CMD_USR","ID":"2","PAYLOAD_TYPE":"CMD_ARM_PARTITION","PAYLOAD":{"ID_LOGIN":"' + self._id + '","PIN":"' + self._pin + '","PARTITION":{"ID":"' + partId + '" , "MOD":"' + arm + '" }  },"TIMESTAMP" : "' + str(int(time.time())) + '","CRC_16":"0x0000"}'))
            response = await self.receive()
            return json.loads(response)

        except Exception as e:
            _LOGGER.error(f"Impossibile armare partizioni: {e}")

    async def arm_scene(self, scenenId: str):
        try:
            await self.send(addCRC('{"SENDER":"012345678901", "RECEIVER":"' + self._mac + '", "CMD":"CMD_USR","ID":"2","PAYLOAD_TYPE":"CMD_EXE_SCENARIO","PAYLOAD":{"ID_LOGIN":"' + self._id + '","PIN":"' + self._pin + '","SCENARIO":{"ID":"' + scenenId + '"} },"TIMESTAMP" : "' + str(int(time.time())) + '","CRC_16":""}'))
            response = await self.receive()
            return json.loads(response)

        except Exception as e:
            _LOGGER.error(f"Impossibile eseguire scena: {e}")

    async def close(self):
        """Close the WebSocket connection."""
        if self._connected and self._websocket:
            await self._websocket.close()
            _LOGGER.info("Closed WebSocket connection")
            self._connected = False
