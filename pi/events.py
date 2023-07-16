import pygame

# Event to indicate that the Bluetooth discovery should start
BLUETOOTH_DISCOVERY_START_EVENT = pygame.USEREVENT + 1
# Event to indicate that the Bluetooth discovery is done and an updated device list can be retrieved
# from the HubConnection class
BLUETOOTH_DISCOVERY_DONE_EVENT = pygame.USEREVENT + 2
# Event to connect to a new device (disconnecting from the current one if there is one)
# The event data should be a dictionary with a "device" key containing the BLEDevice to connect to
BLUETOOTH_CONNECT_EVENT = pygame.USEREVENT + 3
# Event to indicate data was received from the hub
# The event data should be a dictionary with a "data" key containing the received data
BLUETOOTH_DATA_RECEIVED_EVENT = pygame.USEREVENT + 4
# Event to indicate that the connection was made and the program on the hub can be started
BLUETOOTH_CONNECTED_EVENT = pygame.USEREVENT + 5
# Event to indicate some kind of error occurred.
# The event data is a dictionary with a "message" and "exception" key
BLUETOOTH_ERROR_EVENT = pygame.USEREVENT + 6
