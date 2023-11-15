import asyncio
import random
import sys
import traceback

from pynput import keyboard

from control import BufferedSend, open_connection

keyboard_queue = asyncio.Queue()
drive_lock = asyncio.Lock()


def on_press(loop):
    # Both on_press and on_release run in a separate thread created by the keyboard listener code. The way they can
    # access the queue from their thread is through this convoluted method call:
    return lambda key: asyncio.run_coroutine_threadsafe(keyboard_queue.put([key, True]), loop)


def on_release(loop):
    return lambda key: asyncio.run_coroutine_threadsafe(keyboard_queue.put([key, False]), loop)


async def backoff(connection: BufferedSend):
    direction = random.choice([-20, 20])
    async with drive_lock:
        for i in range(3):
            await connection.drive(-50 + direction, -50 - direction)
            await asyncio.sleep(.1)


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
            elif key[1] and key[0] == keyboard.Key.space:
                asyncio.create_task(backoff(connection))


async def show_measurement(connection: BufferedSend):
    while True:
        async with drive_lock:
            await connection.drive(50, 50)
        # print(connection.last_measurement)
        await asyncio.sleep(.1)


async def main(loop: asyncio.AbstractEventLoop):
    connection = None
    try:
        connection = await open_connection()
        if connection is None:
            return

        print("Collection data. Press <space> every time the robot runs into something, press q to quit.")

        listener = keyboard.Listener(on_press=on_press(loop), on_release=on_release(loop))
        listener.start()

        keyboard_task = loop.create_task(read_keyboard(connection))
        measurement_task = loop.create_task(show_measurement(connection))
        await keyboard_task
        measurement_task.cancel()
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
