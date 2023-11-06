import asyncio
from bleak import BleakScanner
from .buffered_send import BufferedSend
from .hub_connection import HubConnection, UART_SERVICE_UUID
import time


async def open_connection() -> BufferedSend|None:
    connection = None

    while connection is None or not connection.is_connected():
        devices = await BleakScanner.discover(return_adv=False, service_uuids=[UART_SERVICE_UUID])
        devices_with_name = [d for d in devices if d.name]

        print("\n".join([f"{count + 1}. {device.name}" for [count, device] in enumerate(devices_with_name)]))
        device_num = input("Enter device number (q to quit, enter to rescan): ")
        if device_num == "q":
            return None
        elif device_num == "":
            continue
        device = devices_with_name[int(device_num) - 1]
        print(f"Connecting to {device.name}...")

        connection = HubConnection(device)
        await connection.connect()

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
