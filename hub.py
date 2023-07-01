# NOTE: Run this program with the latest
# firmware provided via https://beta.pybricks.com/

from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Color
from pybricks.tools import wait
from pybricks.hubs import InventorHub

# Standard MicroPython modules
from usys import stdin, stdout
from uselect import poll

hub = InventorHub()
left = Motor(Port.A)
right = Motor(Port.B)


def surprise():
    hub.speaker.volume(50)
    hub.light.on(Color.RED)
    hub.speaker.play_notes(["F2/16", "E2/16", "D2/16", "C2/4"])
    hub.light.on(Color.BLUE)

# Optional: Register stdin for polling. This allows
# you to wait for incoming data without blocking.
keyboard = poll()
keyboard.register(stdin)

no_cmd_count = 0

while True:

    # Optional: Check available input.
    while not keyboard.poll(0):
        wait(10)
        no_cmd_count = no_cmd_count + 1
        if no_cmd_count == 50:
            # Stop if we haven't received a command for half a second
            left.stop()
            right.stop()

    no_cmd_count = 0

    # Read three bytes.
    cmd = stdin.buffer.read(3)

    # Decide what to do based on the command.
    response = str(cmd, "utf-8")
    if cmd == b"fwd":
        left.dc(-50)
        right.dc(50)
        response = "OK: " + response
    elif cmd == b"rev":
        left.dc(50)
        right.dc(-50)
        response = "OK: " + response
    elif cmd == b"bye":
        break
    else:
        left.stop()
        right.stop()
        surprise()
        response = "NOK: " + response

    # Send a response.
    stdout.buffer.write(response)

