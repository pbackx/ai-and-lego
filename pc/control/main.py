import asyncio
# msvcrt is Windows only, you could try with the 'getch' package instead: https://stackoverflow.com/a/74583041/227081
import msvcrt
import sys
import time
import traceback

from hub_connection import HubConnection

ESCAPE = 27


async def arrow(key_code, connection):
    # TODO need some way to cancel previous commands if a new one is received
    if key_code == 72:
        print("Up arrow pressed")
        await connection.send(b'D+50+50')
    elif key_code == 80:
        print("Down arrow pressed")
    elif key_code == 75:
        print("Left arrow pressed")
    elif key_code == 77:
        print("Right arrow pressed")
    else:
        print(f"Unknown arrow key {key_code}")


async def read_keyboard(connection):
    while True:
        while msvcrt.kbhit():
            # https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/getch-getwch?view=msvc-170
            # Note that this may not work properly if you run it inside an IDE. For IntelliJ IDEA and PyCharm you need
            # to enable "Emulate terminal in output console" in the Run/Debug configuration.
            key = msvcrt.getch()
            if ord(key) == 0xe0:
                await arrow(ord(msvcrt.getch()), connection)

            if key == b"q" or ord(key) == ESCAPE:
                return
        await asyncio.sleep(0.1)


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

        print("Hub is running, you can now control the robot with the arrow keys (q to quit).")

        keyboard_task = asyncio.create_task(read_keyboard(connection))
        await keyboard_task
    finally:
        print("Quitting...")
        await connection.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        traceback.print_exception(e)
        sys.exit(-1)
