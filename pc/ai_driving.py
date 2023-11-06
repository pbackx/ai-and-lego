import asyncio
import sys
import traceback

from control.buffered_send import BufferedSend
from control.open_connection import open_connection

from capture import connect_and_start_preview, GOPRO_IP, GoProBLEClient, GoProWifiClient


class Connections:
    hub_connection: BufferedSend = None
    gopro_ble: GoProBLEClient = None
    gopro_wifi: GoProWifiClient = None


async def main(c: Connections):
    # Connect to Mindstorms Hub
    c.hub_connection = await open_connection()

    if c.hub_connection is None:
        print("Failed to connect to hub.")
        return

    # Connect to GoPro
    c.gopro_ble, c.gopro_wifi = await connect_and_start_preview()

    if c.gopro_ble is None or c.gopro_wifi is None:
        print("Failed to connect to GoPro.")
        return

    # Start loop
    action = [50, 50]
    while True:
        # Drive for 1 second
        await c.hub_connection.drive(*action)
        await asyncio.sleep(0.05)

        # Take a picture
        # Classify the picture
        # If the result is safe, go to 1 driving 1 second straight
        # If the result is danger, go to 1 turning 1 second left


if __name__ == "__main__":
    connections = Connections()
    try:
        main_loop = asyncio.new_event_loop()
        main_loop.run_until_complete(main(connections))
    except Exception as e:
        traceback.print_exception(e)
        sys.exit(-1)
    finally:
        print("Closing connections")
        if connections.hub_connection is not None:
            asyncio.run(connections.hub_connection.shutdown())
        if connections.gopro_wifi is not None:
            connections.gopro_wifi.disconnect()
        if connections.gopro_ble is not None:
            asyncio.run(connections.gopro_ble.disconnect())
        print("Done")
