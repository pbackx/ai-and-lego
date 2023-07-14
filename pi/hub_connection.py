import threading
from events import BLUETOOTH_DISCOVERY_EVENT
import pygame

from bleak import BleakScanner, BLEDevice

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"


class HubConnection:
    _detected_hubs_lock: threading.Lock = threading.Lock()
    _detected_hubs: list[BLEDevice] = []

    def __init__(self):
        pass

    @classmethod
    async def scan(cls):
        devices = await BleakScanner.discover(return_adv=False, service_uuids=[UART_SERVICE_UUID])
        devices_with_name = [d for d in devices if d.name]
        with cls._detected_hubs_lock:
            cls._detected_hubs = devices_with_name
        pygame.event.post(pygame.event.Event(BLUETOOTH_DISCOVERY_EVENT))

    @classmethod
    def get_detected_hubs(cls) -> list[BLEDevice]:
        with cls._detected_hubs_lock:
            return cls._detected_hubs