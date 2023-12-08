import asyncio
from bleak import BleakScanner, BLEDevice
from .buffered_send import BufferedSend
from .hub_connection import HubConnection
import time


async def open_connection(robot_name: str|None) -> BufferedSend|None:
    connection = None

    while connection is None or not connection.is_connected():
        devices = await BleakScanner.discover(return_adv=False)
        devices_with_name = [d for d in devices if d.name]

        if robot_name is not None:
            device = get_device_by_name(devices_with_name, robot_name)
            if device is None:
                print(f"Could not find device with name {robot_name}. Waiting to retry.")
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
            return None
        await asyncio.sleep(1)

    return BufferedSend(connection)

def get_device_by_name(devices: list[BLEDevice], name: str):
    for device in devices:
        if device.name == name:
            return device
    return None
