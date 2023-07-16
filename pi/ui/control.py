import pygame

from pi.events import BLUETOOTH_SEND_DATA_EVENT
from pi.ui.constants import ACCENT3_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT, TEXT_COLOR, ACCENT2_COLOR


class Control:
    def __init__(self, font: pygame.font.Font):
        self._font = font
        self.location_x = SCREEN_WIDTH / 2
        self.location_y = SCREEN_HEIGHT / 2
        self.width = 3 * (32 + 10) + 10
        self.height = 2 * (32 + 10) + 10 + font.get_height() + 10
        self._manual = True
        self._previousData = None
        self._previousTime = 0
        self._up = pygame.transform.scale(pygame.image.load('./images/2B06_color.png'), (32, 32))

    def draw_key(self, screen: pygame.Surface, icon: pygame.Surface, x: int, y: int):
        pygame.draw.rect(screen, ACCENT2_COLOR, (x, y, 32, 32))

    def draw(self, screen: pygame.Surface):
        if self._manual:
            header = self._font.render("Manual Control", True, TEXT_COLOR)
            screen.blit(header, (self.location_x - header.get_width() / 2, self.location_y - self.height / 2))
            pygame.draw.rect(screen, ACCENT3_COLOR, (self.location_x - self.width / 2,
                                                     self.location_y - self.height / 2 + 10 + header.get_height(),
                                                     self.width,
                                                     self.height - 10 - header.get_height()))

            self.draw_key(screen,
                          self._up,
                          self.location_x - 32 / 2,
                          self.location_y - self.height / 2 + header.get_height() + 2 * 10)
            pygame.draw.rect(screen, ACCENT2_COLOR, (self.location_x - 32 / 2,
                                                     self.location_y - self.height / 2 + header.get_height() + 32 + 3 * 10,
                                                     32, 32))
            pygame.draw.rect(screen, ACCENT2_COLOR, (self.location_x - 32 / 2 - 32 - 10,
                                                     self.location_y - self.height / 2 + header.get_height() + 32 + 3 * 10,
                                                     32, 32))
            pygame.draw.rect(screen, ACCENT2_COLOR, (self.location_x - 32 / 2 + 32 + 10,
                                                     self.location_y - self.height / 2 + header.get_height() + 32 + 3 * 10,
                                                     32, 32))

            key = pygame.key.get_pressed()
            if key[pygame.K_UP]:
                self.send_data(b'D+50+50')
            elif key[pygame.K_DOWN]:
                self.send_data(b'D-50-50')
            elif key[pygame.K_LEFT]:
                self.send_data(b'D-50+50')
            elif key[pygame.K_RIGHT]:
                self.send_data(b'D+50-50')
            else:
                self.send_data(b'D000000')
        else:
            pass

        switch_mode = self._font.render("Switch mode by pressing M", True, TEXT_COLOR)
        screen.blit(switch_mode, (self.location_x - switch_mode.get_width() / 2,
                                  self.location_y + self.height / 2 + 10))

    def send_data(self, data: bytes):
        if data == self._previousData and pygame.time.get_ticks() - self._previousTime < 100:
            return
        self._previousData = data
        self._previousTime = pygame.time.get_ticks()
        pygame.event.post(pygame.event.Event(BLUETOOTH_SEND_DATA_EVENT, {'data': data}))

    def switch_mode(self):
        self._manual = not self._manual
