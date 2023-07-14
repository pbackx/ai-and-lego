import pygame

from pi.ui.constants import HEAD3_COLOR, SCREEN_WIDTH, HEAD1_COLOR


class ReloadButton:
    def __init__(self):
        self._image = pygame.transform.scale(pygame.image.load('./images/1F504_color.png'), (32, 32))
        self.location = pygame.Rect((SCREEN_WIDTH - 32 - 10, 10, 32, 32))

    def draw(self, screen: pygame.Surface):
        mouse_pos = pygame.mouse.get_pos()
        color = HEAD1_COLOR if self.location.collidepoint(mouse_pos) else HEAD3_COLOR
        pygame.draw.rect(screen, color, self.location)
        screen.blit(self._image, (SCREEN_WIDTH - 32 - 10, 10))
