import asyncio
import math

import vector
from bleak import BleakScanner, BleakClient

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

# Replace this with the name of your hub if you changed
# it when installing the Pybricks firmware.
HUB_NAME = "Robot Inventor"


def hub_filter(device, ad):
    return device.name and device.name.lower() == HUB_NAME.lower()


def handle_disconnect(_):
    print("Hub was disconnected.")


def handle_rx(_, data: bytearray):
    print("Received:", data.decode('utf-8'))


async def send(client, rx_char, data):
    await client.write_gatt_char(rx_char, data)


async def send_vector(client, rx_char, vec: vector.Vector2D):
    if abs(vec.phi) > math.radians(45):
        print("Phi is too large! Only 45 or below accepted.")
        return

    print("Sending:", vec.x, vec.y)
    left = 50
    right = 50
    if vec.y > 0:
        left = int(50 * (vec.x - abs(vec.y)))
        right = int(50 * (vec.x + abs(vec.y)))
    elif vec.y < 0:
        left = int(50 * (vec.x + abs(vec.y)))
        right = int(50 * (vec.x - abs(vec.y)))
    left_str = f"{left:02.0f}"
    right_str = f"{right:02.0f}"
    print("Sending:", left_str, right_str)
    await send(client, rx_char, b"D+" + bytes(left_str, "utf-8") + b"+" + bytes(right_str, "utf-8"))


async def main():
    # Find the device and initialize client.
    device = await BleakScanner.find_device_by_filter(hub_filter)
    client = BleakClient(device, disconnected_callback=handle_disconnect)

    try:
        # Connect and get services.
        await client.connect()
        await client.start_notify(UART_TX_CHAR_UUID, handle_rx)
        nus = client.services.get_service(UART_SERVICE_UUID)
        rx_char = nus.get_characteristic(UART_RX_CHAR_UUID)

        print("Start the program on the hub now with the button.")

        # TODO some kind of delay needed here to wait for the program to start

        await send_vector(client, rx_char, vector.obj(rho=1, phi=0))
        await asyncio.sleep(5)

        await send_vector(client, rx_char, vector.obj(rho=1, phi=math.radians(20)))
        await asyncio.sleep(5)

        await send_vector(client, rx_char, vector.obj(rho=1, phi=math.radians(-20)))
        await asyncio.sleep(5)

        # Send a message to indicate stop.
        await send(client, rx_char, b"B")

    except Exception as e:
        # Handle exceptions.
        print(e)
    finally:
        # Disconnect when we are done.
        await client.disconnect()


# Run the main async program.
asyncio.run(main())
