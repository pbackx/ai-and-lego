import asyncio
# msvcrt is Windows only, you could try with the 'getch' package instead: https://stackoverflow.com/a/74583041/227081
import sys
import time
import traceback

from pynput import keyboard

from buffered_send import BufferedSend
from hub_connection import HubConnection

ESCAPE = 27

action_map = {
    72: b'D+50+50',
    80: b'D-50-50',
    75: b'D-50+50',
    77: b'D+50-50',
}


def arrow(key_code: int, connection: BufferedSend) -> bool:
    if key_code in action_map:
        connection.send(action_map[key_code])
        return True

    return False


def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(key.char))
    except AttributeError:
        print('special key {0} pressed'.format(key))
    # Both on_press and on_release run in a separate thread. The way they can access the queue from is through this
    # convoluted method call:
    asyncio.run_coroutine_threadsafe(keyboard_queue.put(key), loop)


def on_release(key):
    print('{0} released'.format(key))
    # if key == keyboard.Key.esc:
    #     return False


keyboard_queue = asyncio.Queue()


async def read_keyboard(connection: BufferedSend):
    while True:
        key = await keyboard_queue.get()
        print(key)
        # data_send = False
        # while msvcrt.kbhit():
        #     # https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/getch-getwch?view=msvc-170
        #     # Note that this may not work properly if you run it inside an IDE. For IntelliJ IDEA and PyCharm you need
        #     # to enable "Emulate terminal in output console" in the Run/Debug configuration.
        #     key = msvcrt.getch()
        #     if ord(key) == 0xe0:
        #         data_send = arrow(ord(msvcrt.getch()), connection)
        #
        try:
            # This section for normal key presses
            key_char = key.char
            if key_char == "q" or key_char == "Q":
                return
        except AttributeError:
            # This section is for special keys, like arrow keys
            if key == keyboard.Key.esc:
                return
        # if not data_send:
        #     connection.send(b"D000000")
        # await asyncio.sleep(0.5)


async def main():
    connection = HubConnection()
    try:
        while not connection.is_connected():
            devices = await HubConnection.scan()
            print("\n".join([f"{count + 1}. {device.name}" for [count, device] in enumerate(devices)]))
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

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()

        keyboard_task = loop.create_task(read_keyboard(BufferedSend(connection)))
        await keyboard_task
        listener.stop()
    finally:
        print("Quitting...")
        await connection.shutdown()

loop = asyncio.new_event_loop()

if __name__ == "__main__":
    try:
        loop.run_until_complete(main())
    except Exception as e:
        traceback.print_exception(e)
        sys.exit(-1)
