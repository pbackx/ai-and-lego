import asyncio
import sys
import traceback

from pynput import keyboard

from buffered_send import BufferedSend
from open_connection import open_connection

keyboard_queue = asyncio.Queue()
action_map = {
    keyboard.Key.up: [50,50],
    keyboard.Key.down: [-50,-50],
    keyboard.Key.left: [-50,50],
    keyboard.Key.right: [50,-50],
}


def arrow(key: [keyboard.Key, bool], connection: BufferedSend):
    if key[0] in action_map:
        if key[1]:
            connection.drive(*action_map[key[0]])
        else:
            connection.stop()


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
    connection = None
    try:
        connection = await open_connection()
        if connection is None:
            return

        print("Hub is running, you can now control the robot with the arrow keys (q to quit).")

        listener = keyboard.Listener(on_press=on_press(loop), on_release=on_release(loop))
        listener.start()

        keyboard_task = loop.create_task(read_keyboard(connection))
        await keyboard_task
        listener.stop()
    finally:
        print("Quitting...")
        if connection is not None:
            await connection.shutdown()


if __name__ == "__main__":
    try:
        main_loop = asyncio.new_event_loop()
        main_loop.run_until_complete(main(main_loop))
    except Exception as e:
        traceback.print_exception(e)
        sys.exit(-1)
