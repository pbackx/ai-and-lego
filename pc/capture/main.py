import asyncio
import sys
import traceback
from signal import SIGTERM, SIGINT

import gopro
import capture
from gopro.constants import GOPRO_IP


async def main(loop: asyncio.AbstractEventLoop):
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
            # Note that this seems to often fail if I first turned on the GoPro.
            # A second run of the program usually works.
            print("Failed to connect to GoPro wifi")
            return

        gopro_wifi.start_preview()

        print("Capturing video stream (ctrl-c to stop)")
        capture_task = loop.create_task(capture.start_capture(host=f"@{GOPRO_IP}", port=8554, folder='../../training_data'))
        for signal in [SIGINT, SIGTERM]:
            # Cancel the capture task when the program is terminated
            loop.add_signal_handler(signal, capture_task.cancel)
        await capture_task # TODO for some reason the task is not awaited and the finally close is immediately executed
    finally:
        print("Stopping capture")
        if gopro_wifi:
            if gopro_wifi.is_connected():
                gopro_wifi.stop_preview()
            gopro_wifi.disconnect()
        await gopro_ble.disconnect()


if __name__ == "__main__":
    try:
        main_loop = asyncio.new_event_loop()
        main_loop.run_until_complete(main(main_loop))
    except Exception as e:
        traceback.print_exception(e)
        sys.exit(-1)
