import asyncio
import sys
import traceback

import gopro
import capture
from gopro.constants import GOPRO_IP


async def main():
    print("===========================")
    print("Image capture using a GoPro")
    print("===========================")
    print()
    print("If this is the first time running the program, you need to enable pairing:")
    print("  1. Swipe down on the GoPro screen")
    print("  2. Swipe left")
    print("  3. Select Connections")
    print("  4. Select Connect Device")
    print("  5. Select Quik App")
    print("This program assumes that your GoPro's name starts with GoPro, which is the default.")
    print("If you have changed it, or you have multiple GoPros, check and modify the source code.")
    print()
    print("This program will set up a wifi connection to the GoPro, then start a video stream.")
    print("This means you will not be able to access the internet over Wifi while the program is running.")
    print()

    gopro_ble = gopro.GoProBLEClient()
    gopro_wifi = None

    ble_connected = await gopro_ble.connect()
    if not ble_connected:
        raise Exception("Failed to connect to GoPro via BLE")

    try:
        ssid, password = await gopro_ble.enable_wifi()
        print(f"GoPro wifi enabled. SSID: {ssid}, password: {password}")

        gopro_wifi = gopro.GoProWifiClient(ssid, password)
        gopro_wifi.connect()

        if not gopro_wifi.wait_for_connection(10):
            print("Failed to connect to GoPro wifi")
            return

        gopro_wifi.start_preview()

        print("Capturing video stream")
        capture.capture(host=f"@{GOPRO_IP}", port=8554)
    finally:
        if gopro_wifi:
            gopro_wifi.stop_preview()
            gopro_wifi.disconnect()
        await gopro_ble.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        traceback.print_exception(e)
        sys.exit(-1)
