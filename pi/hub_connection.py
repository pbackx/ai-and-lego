import threading

import pygame
from bleak import BleakScanner, BLEDevice, BleakClient

from events import BLUETOOTH_DISCOVERY_DONE_EVENT, BLUETOOTH_DATA_RECEIVED_EVENT, BLUETOOTH_CONNECTED_EVENT, \
    BLUETOOTH_ERROR_EVENT

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"


class HubConnection:
    _detecting_hubs = False
    _detected_hubs_lock: threading.Lock = threading.Lock()
    _detected_hubs: list[BLEDevice] = []

    def __init__(self):
        self._client = None
        self._rx_char = None
        self._running = False

    @classmethod
    async def scan(cls):
        if cls._detecting_hubs:
            return

        cls._detecting_hubs = True
        devices = await BleakScanner.discover(return_adv=False, service_uuids=[UART_SERVICE_UUID])
        devices_with_name = [d for d in devices if d.name]
        with cls._detected_hubs_lock:
            cls._detected_hubs = devices_with_name
        pygame.event.post(pygame.event.Event(BLUETOOTH_DISCOVERY_DONE_EVENT))
        cls._detecting_hubs = False

    @classmethod
    def get_detected_hubs(cls) -> list[BLEDevice]:
        with cls._detected_hubs_lock:
            return cls._detected_hubs

    def handle_disconnect(self, _):
        print("Hub was disconnected.")

    def handle_rx(self, _, data: bytearray):
        pygame.event.post(pygame.event.Event(BLUETOOTH_DATA_RECEIVED_EVENT, {"data": data}))
        decode = data.decode('utf-8')
        if decode == "OK: Running":
            self._running = True

    async def send(self, data):
        if self._client is not None and self._running:
            try:
                await self._client.write_gatt_char(self._rx_char, data)
            except Exception as e:
                pygame.event.post(pygame.event.Event(BLUETOOTH_ERROR_EVENT, {
                    "exception": e,
                    "message": "Failed to send data to hub."
                }))
                await self.disconnect()

    async def connect(self, hub: BLEDevice):
        try:
            await self.disconnect()

            self._client = BleakClient(hub, disconnected_callback=self.handle_disconnect)
            await self._client.connect()
            await self._client.start_notify(UART_TX_CHAR_UUID, self.handle_rx)
            nus = self._client.services.get_service(UART_SERVICE_UUID)
            self._rx_char = nus.get_characteristic(UART_RX_CHAR_UUID)
            pygame.event.post(pygame.event.Event(BLUETOOTH_CONNECTED_EVENT))
        except Exception as e:
            pygame.event.post(pygame.event.Event(BLUETOOTH_ERROR_EVENT, {
                "exception": e,
                "message": "Failed to connect to hub."
            }))
            await self.disconnect()

    async def disconnect(self):
        try:
            if self._client is not None:
                await self._client.disconnect()
                self._client = None
        except Exception as e:
            pygame.event.post(pygame.event.Event(BLUETOOTH_ERROR_EVENT, {
                "exception": e,
                "message": "Failed to disconnect from hub."
            }))
        finally:
            self._running = False

    async def shutdown(self):
        await self.send(b"B")
        await self.disconnect()
