from time import time

import pygame

from pi.ui.constants import TEXT_COLOR, SCREEN_HEIGHT


class Log:
    def __init__(self, font: pygame.font.Font):
        self._log: list[tuple[time, str]] = []
        self._font = font

    def draw(self, screen: pygame.Surface):
        for index, line in enumerate(self._log):
            if line[0] + 10 < time():
                self._log.pop(index)
            else:
                text = self._font.render(line[1], True, TEXT_COLOR)
                screen.blit(text, (10, SCREEN_HEIGHT - 10 - (len(self._log) - index) * (text.get_height() + 10)))

    def add(self, line: str):
        self._log.append((time(), line))