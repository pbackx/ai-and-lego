import numpy as np
import vector


class RandomWalk:
    def __init__(self, base_speed: int = 50):
        self._base_speed = base_speed
        self._step_count = 0
        self._steps_per_move = 100
        self._current_move = vector.obj(rho=1, phi=0)
        self._current_speed = 0

    def reset(self) -> None:
        self._step_count = 0

    def convert_vector(self, vec: vector.Vector2D) -> bytes:
        left = self._current_speed
        right = self._current_speed
        if vec.y > 0:
            left = int(self._current_speed * (vec.x - abs(vec.y)))
            right = int(self._current_speed * (vec.x + abs(vec.y)))
        elif vec.y < 0:
            left = int(self._current_speed * (vec.x + abs(vec.y)))
            right = int(self._current_speed * (vec.x - abs(vec.y)))
        left = max(min(left, 99), -99)
        right = max(min(right, 99), -99)
        left_str = f"{left:+03.0f}"
        right_str = f"{right:+03.0f}"
        return b'D' + bytes(left_str, "utf-8") + bytes(right_str, "utf-8")

    def next_move(self) -> None:
        self._step_count = 0
        self._current_speed = 0
        self._current_move = vector.obj(rho=1, phi=np.random.normal(0, np.pi))

    def next_step(self) -> bytes:
        self._step_count += 1
        self._current_speed = (self._base_speed / (self._steps_per_move / 2)) * np.abs(
            np.abs(self._step_count - self._steps_per_move / 2) - self._steps_per_move / 2)
        if self._step_count >= self._steps_per_move:
            self.next_move()
        return self.convert_vector(self._current_move)
