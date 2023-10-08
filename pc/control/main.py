import asyncio
import sys
import time
import traceback

from hub_connection import HubConnection


async def main():
    connection = HubConnection()
    try:
        while not connection.is_connected():
            devices = await HubConnection.scan()
            print("\n".join([f"{count+1}. {device.name}" for [count, device] in enumerate(devices)]))
            device_num = input("Enter device number (q to quit, enter to rescan): ")
            if device_num == "q":
                return
            elif device_num == "":
                continue
            device = devices[int(device_num) - 1]
            print(f"Connecting to {device.name}...")

            await connection.connect(device)

        print("Pleas push the button on the hub to start the program.")

        start_time = time.time()
        timeout_seconds = 30
        while not connection.is_running():
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout_seconds:
                print("Timeout waiting for hub to start the program.")
                return
            await asyncio.sleep(1)

        print("Hub is running, you can now control the robot.")

        await connection.send(b'D+50+50')

    finally:
        await connection.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        traceback.print_exception(e)
        sys.exit(-1)
