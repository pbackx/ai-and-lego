import asyncio

import pygame

from events import BLUETOOTH_DISCOVERY_START_EVENT, BLUETOOTH_DISCOVERY_DONE_EVENT, BLUETOOTH_CONNECT_EVENT, \
    BLUETOOTH_DATA_RECEIVED_EVENT, BLUETOOTH_CONNECTED_EVENT, BLUETOOTH_ERROR_EVENT
from hub_connection import HubConnection
from pi.ui.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, TEXT_COLOR
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

run = True
loop = asyncio.new_event_loop()


def run_once(event_loop: asyncio.AbstractEventLoop):
    # See https://docs.python.org/3.11/library/asyncio-eventloop.html#asyncio.loop.run_forever
    event_loop.call_soon(event_loop.stop)
    event_loop.run_forever()


loop.create_task(HubConnection.scan())

while run:
    screen.fill(BACKGROUND_COLOR)

    header = font.render("Robot Control", True, TEXT_COLOR)
    screen.blit(header, (10, 10))

    devices_display.draw(screen)
    log.draw(screen)

    key = pygame.key.get_pressed()
    if key[pygame.K_a]:
        pass
    elif key[pygame.K_d]:
        pass
    elif key[pygame.K_w]:
        pass
    elif key[pygame.K_s]:
        pass
    elif key[pygame.K_ESCAPE]:
        run = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONUP:
            devices_display.handle_mouse_click(event.pos)
        elif event.type == BLUETOOTH_DISCOVERY_START_EVENT:
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
