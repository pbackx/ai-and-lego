import asyncio
import csv
import random
import sys
import traceback
from dataclasses import asdict

from pynput import keyboard

from control import BufferedSend, RobotDriver
from control.hub_measurement import HubMeasurement

keyboard_queue = asyncio.Queue()
is_running_backoff = False


def on_press(loop):
    # Both on_press and on_release run in a separate thread created by the keyboard listener code. The way they can
    # access the queue from their thread is through this convoluted method call:
    return lambda key: asyncio.run_coroutine_threadsafe(keyboard_queue.put([key, True]), loop)


def on_release(loop):
    return lambda key: asyncio.run_coroutine_threadsafe(keyboard_queue.put([key, False]), loop)


async def backoff(connection: BufferedSend):
    global is_running_backoff
    direction = random.choice([-50, 50])
    is_running_backoff = True
    for i in range(2):
        await connection.drive(-50,-50)
        await asyncio.sleep(.1)
    for i in range(3):
        await connection.drive(direction, -direction)
        await asyncio.sleep(.1)
    is_running_backoff = False


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


async def drive_and_measure(connection: BufferedSend):
    with open('measurements.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=HubMeasurement.fieldnames())
        writer.writeheader()

        while True:
            try:
                global is_running_backoff
                if not is_running_backoff:
                    await connection.drive(50, 50)
                measurement = connection.last_measurement()
                if measurement is not None:
                    writer.writerow(asdict(measurement))
                await asyncio.sleep(.1)
            except Exception as e:
                traceback.print_exception(e)


async def main():
    robot_name = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else None

    async with RobotDriver(robot_name) as connection:
        print("Collection data. Press <space> every time the robot runs into something, press q to quit.")

        listener = keyboard.Listener(on_press=on_press(asyncio.get_running_loop()),
                                     on_release=on_release(asyncio.get_running_loop()))
        listener.start()

        keyboard_task = asyncio.create_task(read_keyboard(connection))
        measurement_task = asyncio.create_task(drive_and_measure(connection))
        await keyboard_task
        measurement_task.cancel()
        listener.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main(), debug=True)
    except Exception as e:
        traceback.print_exception(e)
        sys.exit(-1)
