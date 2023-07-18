from pybricks.pupdevices import Motor, UltrasonicSensor
from pybricks.parameters import Port, Color
from pybricks.tools import wait
from pybricks.hubs import InventorHub

from usys import stdin, stdout
from uselect import poll

from drive_protocol import DriveProtocol

hub = InventorHub()
left = Motor(Port.A)
right = Motor(Port.B)
protocol = DriveProtocol()

head_lights = UltrasonicSensor(Port.D)
head_lights.lights.on((75, 75, 25, 25))


def surprise():
    left.stop()
    right.stop()
    hub.speaker.volume(50)
    hub.light.on(Color.RED)
    hub.speaker.play_notes(["F2/16", "E2/16", "D2/16", "C2/4"])
    hub.light.on(Color.BLUE)


def drive(command: str):
    left_command = -1 * int(command[0:3])
    right_command = int(command[3:6])
    left.dc(left_command)
    right.dc(right_command)


keyboard = poll()
keyboard.register(stdin)

no_cmd_count = 0

stdout.buffer.write("OK: Running")

while True:
    while not keyboard.poll(0):
        wait(10)
        no_cmd_count = no_cmd_count + 1
        if no_cmd_count > 50:
            # Stop if we haven't received a command for half a second
            left.stop()
            right.stop()

    rec = stdin.buffer.read(1)
    if rec == b"D":
        protocol.clear()
    elif rec == b"B":
        head_lights.lights.off()
        left.stop()
        right.stop()
        break
    else:
        if not protocol.add_byte(rec):
            surprise()
            stdout.buffer.write("NOK: " + "".join([str(x, 'utf-8') for x in protocol.get_bytes()]) + str(rec, 'utf-8'))
            protocol.clear()
            continue
    no_cmd_count = 0

    if len(protocol.get_bytes()) == 6:
        full_cmd = "".join([str(x, 'utf-8') for x in protocol.get_bytes()])
        drive(full_cmd)
        protocol.clear()
        stdout.buffer.write("OK: " + full_cmd)
