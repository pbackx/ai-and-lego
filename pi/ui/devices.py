import pygame
from bleak import BLEDevice

from pi.ui.reload_button import ReloadButton


class Devices:
    def __init__(self):
        self._reload_button = ReloadButton()
        self._bluetooth_devices: list[BLEDevice] = []

    def draw(self, screen: pygame.Surface):
        self._reload_button.draw(screen)
        for device in self._bluetooth_devices:
            pass

    def set_bluetooth_devices(self, devices):
        self._bluetooth_devices = devices
        print("Bluetooth devices set to: " + str(devices))
