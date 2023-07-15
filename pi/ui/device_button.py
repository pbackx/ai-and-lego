import pygame
from bleak import BLEDevice

from pi.events import BLUETOOTH_CONNECT_EVENT
from pi.ui.text_button import TextButton


class DeviceButton(TextButton):
    def __init__(self, rect: tuple[int, int, int, int], device: BLEDevice):
        super().__init__(rect,
                         device.name,
                         self.handle_mouse_click_action)
        self._device = device

    def handle_mouse_click_action(self):
        pygame.event.post(pygame.event.Event(BLUETOOTH_CONNECT_EVENT, {"device": self._device}))
