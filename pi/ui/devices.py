import pygame
from bleak import BLEDevice

from pi.ui.constants import SCREEN_WIDTH
from pi.ui.device_button import DeviceButton
from pi.ui.reload_button import ReloadButton


class Devices:
    def __init__(self):
        self._reload_button = ReloadButton()
        self._bluetooth_devices: list[BLEDevice] = []
        self._bluetooth_device_buttons: list[DeviceButton] = []

    def draw(self, screen: pygame.Surface):
        self._reload_button.draw(screen)
        for button in self._bluetooth_device_buttons:
            button.draw(screen)

    def set_bluetooth_devices(self, devices):
        self._bluetooth_devices = devices
        print("Bluetooth devices set to: " + str(devices))
        self._bluetooth_device_buttons = []
        for index, device in enumerate(self._bluetooth_devices):
            self._bluetooth_device_buttons.append(
                DeviceButton((SCREEN_WIDTH - 4 * 32 - 10,
                              10 + (32 + 10) * (index + 1),
                              4 * 32,
                              32),
                             device))

    def handle_mouse_click(self, pos):
        self._reload_button.handle_mouse_click(pos)
        for button in self._bluetooth_device_buttons:
            button.handle_mouse_click(pos)
