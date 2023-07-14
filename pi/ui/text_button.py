from typing import Tuple

import pygame

from pi.ui.button import Button
from pi.ui.constants import ACCENT1_COLOR


class TextButton(Button):
    font: pygame.font.Font = None

    def __init__(self, rect: Tuple[int, int, int, int], text: str):
        super().__init__(rect)
        self._text = text
        if self.font is None:
            self.font = pygame.font.SysFont(
                "Helvetica Neue,Helvetica,Ubuntu Sans,Bitstream Vera Sans,DejaVu Sans,Latin Modern Sans,"
                "Liberation Sans,Nimbus Sans L,Noto Sans,Calibri,Futura,Beteckna,Arial", 16)

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        text_surface = self.font.render(self._text, True, ACCENT1_COLOR)

        x = self.location.x + self.location.width/2 - text_surface.get_width()/2
        y = self.location.y + self.location.height/2 - text_surface.get_height()/2

        screen.blit(text_surface, (x, y))

    def handle_mouse_click_action(self):
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"button": self}))
        # TODO: Make this a custom event and connect to the device

