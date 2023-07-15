import pygame

from pi.ui.constants import ACCENT3_COLOR, ACCENT2_COLOR


class Button:
    def __init__(self,
                 location: tuple[int, int, int, int],
                 handle_mouse_click_action: callable = None):
        self.location = pygame.Rect(location)
        self._handle_mouse_click_action = handle_mouse_click_action

    def draw(self, screen: pygame.Surface):
        mouse_pos = pygame.mouse.get_pos()
        mouse_on_button = self.location.collidepoint(mouse_pos)
        color = ACCENT2_COLOR if mouse_on_button else ACCENT3_COLOR
        pygame.draw.rect(screen, color, self.location)

    def handle_mouse_click(self, pos):
        if self.location.collidepoint(pos) and self._handle_mouse_click_action is not None:
            self._handle_mouse_click_action()
