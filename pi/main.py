import asyncio

import pygame

from events import BLUETOOTH_DISCOVERY_START_EVENT, BLUETOOTH_DISCOVERY_DONE_EVENT, BLUETOOTH_CONNECT_EVENT, \
    BLUETOOTH_DATA_RECEIVED_EVENT, BLUETOOTH_CONNECTED_EVENT, BLUETOOTH_ERROR_EVENT, BLUETOOTH_SEND_DATA_EVENT
from hub_connection import HubConnection
from pi.ui.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR
from pi.ui.control import Control
from pi.ui.devices import Devices
from pi.ui.log import Log

pygame.init()

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

devices_display = Devices()
font = pygame.font.SysFont("Helvetica Neue,Helvetica,Ubuntu Sans,Bitstream Vera Sans,DejaVu Sans,Latin Modern Sans,"
                           "Liberation Sans,Nimbus Sans L,Noto Sans,Calibri,Futura,Beteckna,Arial", 16)

connection = HubConnection()
log = Log(font)
control = Control(font)

run = True
loop = asyncio.new_event_loop()
clock = pygame.time.Clock()


def run_once(event_loop: asyncio.AbstractEventLoop):
    # See https://docs.python.org/3.11/library/asyncio-eventloop.html#asyncio.loop.run_forever
    event_loop.call_soon(event_loop.stop)
    event_loop.run_forever()


loop.create_task(HubConnection.scan())
log.add("Scanning for Bluetooth devices...")

while run:
    clock.tick(60)

    screen.fill(BACKGROUND_COLOR)

    devices_display.draw(screen)
    log.draw(screen)
    control.draw(screen)

    key = pygame.key.get_pressed()
    if key[pygame.K_ESCAPE]:
        run = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONUP:
            devices_display.handle_mouse_click(event.pos)
        elif event.type == pygame.KEYUP:
            if key[pygame.K_m]:
                control.switch_mode()
        elif event.type == BLUETOOTH_DISCOVERY_START_EVENT:
            log.add("Scanning for Bluetooth devices...")
            loop.create_task(HubConnection.scan())
        elif event.type == BLUETOOTH_DISCOVERY_DONE_EVENT:
            devices_display.set_bluetooth_devices(HubConnection.get_detected_hubs())
        elif event.type == BLUETOOTH_CONNECT_EVENT:
            loop.create_task(connection.connect(event.device))
        elif event.type == BLUETOOTH_DATA_RECEIVED_EVENT:
            decode = event.data.decode('utf-8')
            log.add(f"Received: {decode}")
        elif event.type == BLUETOOTH_CONNECTED_EVENT:
            log.add("Connected to hub, start the program!")
        elif event.type == BLUETOOTH_ERROR_EVENT:
            log.add(f"Error: {event.message}, check console for more details.")
            print("Error:", event.message, event.exception)
        elif event.type == BLUETOOTH_SEND_DATA_EVENT:
            loop.create_task(connection.send(event.data))

    pygame.display.update()
    run_once(loop)

print("Quitting...")

loop.create_task(connection.shutdown())
# Make sure all async tasks are done before quitting.
while len(asyncio.all_tasks(loop)):
    run_once(loop)
loop.run_until_complete(loop.shutdown_asyncgens())
loop.close()
pygame.quit()
