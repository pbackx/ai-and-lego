import asyncio
import sys
import time
import traceback

from pynput import keyboard

from buffered_send import BufferedSend
from hub_connection import HubConnection

keyboard_queue = asyncio.Queue()
action_map = {
    keyboard.Key.up: b'D+50+50',
    keyboard.Key.down: b'D-50-50',
    keyboard.Key.left: b'D-50+50',
    keyboard.Key.right: b'D+50-50',
}


def arrow(key: [keyboard.Key, bool], connection: BufferedSend):
    if key[0] in action_map:
        if key[1]:
            connection.send(action_map[key[0]])
        else:
            connection.send(b'D000000')


def on_press(loop):
    # Both on_press and on_release run in a separate thread created by the keyboard listener code. The way they can
    # access the queue from their thread is through this convoluted method call:
    return lambda key: asyncio.run_coroutine_threadsafe(keyboard_queue.put([key, True]), loop)


def on_release(loop):
    return lambda key: asyncio.run_coroutine_threadsafe(keyboard_queue.put([key, False]), loop)


async def read_keyboard(connection: BufferedSend):
    while True:
        key = await keyboard_queue.get()
        try:
            # This section for normal key presses
            key_char = key[0].char
            if key_char == "q" or key_char == "Q":
                return
        except AttributeError:
            # This section is for special keys, like arrow keys
            if key[0] == keyboard.Key.esc:
                return
            else:
                arrow(key, connection)


async def main(loop: asyncio.AbstractEventLoop):
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

        listener = keyboard.Listener(on_press=on_press(loop), on_release=on_release(loop))
        listener.start()

        keyboard_task = loop.create_task(read_keyboard(BufferedSend(connection)))
        await keyboard_task
        listener.stop()
    finally:
        print("Quitting...")
        await connection.shutdown()


if __name__ == "__main__":
    try:
        main_loop = asyncio.new_event_loop()
        main_loop.run_until_complete(main(main_loop))
    except Exception as e:
        traceback.print_exception(e)
        sys.exit(-1)
