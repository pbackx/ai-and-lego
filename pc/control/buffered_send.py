import asyncio
import time

from hub_connection import HubConnection


def current_time():
    return int(time.time_ns() / 1000000)


# This class will only send out commands every 100 ms to not overload the connection
class BufferedSend:
    def __init__(self, connection: HubConnection):
        self.connection = connection
        self.previous_data = None
        self.previous_time = current_time()

    def send(self, data: bytes):
        if data == self.previous_data:
            if current_time() - self.previous_time < 100:
                return
            elif data == b'D000000':
                return

        self.previous_data = data
        self.previous_time = current_time()
        asyncio.create_task(self.connection.send(data))
