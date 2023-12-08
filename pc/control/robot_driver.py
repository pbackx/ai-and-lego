import asyncio
from bleak import BleakScanner, BLEDevice
from .buffered_send import BufferedSend
from .hub_connection import HubConnection
import time
from types import TracebackType
from typing import Optional, Type


class RobotDriver:
    def __init__(self, robot_name: str|None):
        self._robot_name = robot_name
        self._buffered_send = None

    async def __aenter__(self):
        connection = None

        while connection is None or not connection.is_connected():
            devices = await BleakScanner.discover(return_adv=False)
            devices_with_name = [d for d in devices if d.name]

            if self._robot_name is not None:
                device = get_device_by_name(devices_with_name, self._robot_name)
                if device is None:
                    print(f"Could not find device with name {self._robot_name}. Waiting to retry.")
                    await asyncio.sleep(1)
                    continue
            else:
                print("\n".join([f"{count + 1}. {device.name}" for [count, device] in enumerate(devices_with_name)]))
                device_num = input("Enter device number (q to quit, enter to rescan): ")
                if device_num == "q":
                    return None
                elif device_num == "":
                    continue
                device = devices_with_name[int(device_num) - 1]

            print(f"Connecting to {device.name}...")

            try:
                connection = HubConnection(device)
                await connection.connect()
            except AttributeError:
                # Sometimes the bluetooth_address is not set. I am not sure why this happens, but retrying fixes this
                pass

        print("Please push the button on the hub to start the program.")

        start_time = time.time()
        timeout_seconds = 30
        while not connection.is_running():
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout_seconds:
                print("Timeout waiting for hub to start the program.")
                raise TimeoutError()
            await asyncio.sleep(1)

        self._buffered_send = BufferedSend(connection)
        return self._buffered_send

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType]):
        print("Quitting...")
        if self._buffered_send is not None:
            await self._buffered_send.shutdown()


def get_device_by_name(devices: list[BLEDevice], name: str):
    for device in devices:
        if device.name == name:
            return device
    return None
