import pygame

from pi.events import BLUETOOTH_DISCOVERY_START_EVENT
from pi.ui.button import Button
from pi.ui.constants import SCREEN_WIDTH


class ReloadButton(Button):
    def __init__(self):
        super().__init__((SCREEN_WIDTH - 32 - 10, 10, 32, 32))
        self._image = pygame.transform.scale(pygame.image.load('./images/1F504_color.png'), (32, 32))

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        screen.blit(self._image, (SCREEN_WIDTH - 32 - 10, 10))

    def handle_mouse_click_action(self):
        pygame.event.post(pygame.event.Event(BLUETOOTH_DISCOVERY_START_EVENT))
