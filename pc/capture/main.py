import asyncio
import traceback

import gopro
import capture
from gopro.constants import GOPRO_IP


class CaptureState:
    loop = None
    gopro_ble = None
    gopro_wifi = None
    capture_task = None

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop


async def main(state: CaptureState):
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

    try:
        state.gopro_ble = gopro.GoProBLEClient()

        ble_connected = await state.gopro_ble.connect()
        if not ble_connected:
            raise Exception("Failed to connect to GoPro via BLE")

        ssid, password = await state.gopro_ble.enable_wifi()
        print(f"GoPro wifi enabled. SSID: {ssid}, password: {password}")

        state.gopro_wifi = gopro.GoProWifiClient(ssid, password)
        state.gopro_wifi.connect()

        if not await state.gopro_wifi.wait_for_connection(30):
            # Note that this takes quite a long time when the GoPro was just turned on
            print("Failed to connect to GoPro wifi")
            return

        state.gopro_wifi.start_preview()

        print("Capturing video stream (ctrl-c to stop)")
        state.capture_task = capture.CaptureTask(host=f"@{GOPRO_IP}", port=8554, folder='../../training_data')

        task = state.loop.create_task(state.capture_task.start())
        await task
    except Exception as ex:
        traceback.print_exception(ex)


async def close(state: CaptureState):
    print("Stopping capture")
    if state.capture_task:
        await state.capture_task.stop()
    print("Disconnecting from GoPro Wifi")
    if state.gopro_wifi:
        if state.gopro_wifi.is_connected():
            state.gopro_wifi.stop_preview()
        state.gopro_wifi.disconnect()
    print("Disconnecting from GoPro BLE")
    if state.gopro_ble:
        await state.gopro_ble.disconnect()
    print("Quitting")


if __name__ == "__main__":
    main_loop = asyncio.new_event_loop()
    main_state = CaptureState(main_loop)
    try:
        main_loop.run_until_complete(main(main_state))
    except Exception as e:
        traceback.print_exception(e)
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        # Close has to happen here because we also want to catch ctrl-c (= KeyboardInterrupt)
        asyncio.run(close(main_state))
