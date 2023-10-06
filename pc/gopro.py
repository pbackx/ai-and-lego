# Note that this code is currently mostly copied from https://github.com/gopro/OpenGoPro
# It will be removed and rewritten to match our needs once I confirm everything is working.

import argparse
import asyncio
import sys
import traceback
from binascii import hexlify
from typing import Optional

import requests
from bleak import BleakGATTCharacteristic

from gopro import connect_ble
from gopro.response import Response
from gopro import wifi
from capture import capture

GOPRO_BASE_UUID = "b5f9{}-aa8d-11e3-9046-0002a5d5c51b"
GOPRO_BASE_URL = "http://10.5.5.9:8080"
WIFI_AP_SSID_UUID = GOPRO_BASE_UUID.format("0002")
WIFI_AP_PASSWORD_UUID = GOPRO_BASE_UUID.format("0003")

# BLE command request and response UUID
COMMAND_REQ_UUID = GOPRO_BASE_UUID.format("0072")
COMMAND_RSP_UUID = GOPRO_BASE_UUID.format("0073")


class NotificationHandler:
    def __init__(self, response_uuid: str):
        self.event = asyncio.Event()
        self.response = Response()
        self.response_uuid = response_uuid

    def reset(self, response_uuid: str):
        self.event.clear()
        self.response = Response()
        self.response_uuid = response_uuid

    def handle(self, handle: BleakGATTCharacteristic, data: bytes) -> None:
        print(f'Received response at {handle.uuid=}: {hexlify(data, ":")!r}')
        self.response.accumulate(data)
        if self.response.is_received:
            self.response.parse()
            if handle.uuid == self.response_uuid and self.response.status == 0:
                print("Received response: ", self.response)
            else:
                print("Unexpected response: ", self.response)
            self.event.set()

    def wait(self):
        return self.event.wait()


async def enable_wifi(client, handler) -> (str, str):
    if not client:
        return None, None

    ssid = await client.read_gatt_char(WIFI_AP_SSID_UUID)
    ssid = ssid.decode()
    print(f"SSID: {ssid}")

    password = await client.read_gatt_char(WIFI_AP_PASSWORD_UUID)
    password = password.decode()
    print(f"Password: {password}")

    handler.reset(COMMAND_RSP_UUID)
    await client.write_gatt_char(COMMAND_REQ_UUID, bytearray([0x03, 0x17, 0x01, 0x01]))
    await handler.wait()  # Wait to receive the notification response
    print("Wifi enabled")

    return ssid, password


async def main(identifier: Optional[str]) -> None:

    response_uuid = COMMAND_RSP_UUID

    handler = NotificationHandler(response_uuid)

    client = await connect_ble(handler.handle, identifier)

    ssid, password = await enable_wifi(client, handler)

    # Note that in Europe you may not to be able to use 5GHz, so you may need to change the band to 2.4GHz
    # This can be done in the Connection settings of the GoPro (swipe down > swipe left > connections)
    interface = wifi.connect(ssid, password)

    try:
        if not wifi.wait_for_connection(interface, ssid, 10):
            print("Failed to connect to GoPro wifi")
            return

        print("Connected to GoPro wifi")

        # response = requests.get(f"{GOPRO_BASE_URL}/gopro/media/list")
        # response_json = response.json()
        # file_list = response_json['media'][0]['fs']
        # print(f'Found {len(file_list)} files')
        # last_cre = 0
        # last_cre_index = 0
        # for index, file in enumerate(file_list):
        #     if int(file['cre']) > last_cre:
        #         last_cre = int(file['cre'])
        #         last_cre_index = index
        # last_file = file_list[last_cre_index]
        # print(f'Most recent file at {last_cre_index}: {json.dumps(last_file, indent=2)}')
        # print(datetime.datetime.utcfromtimestamp(int(last_file['cre'])))

        print("Starting video stream")
        response = requests.get(f"{GOPRO_BASE_URL}/gopro/camera/stream/start")
        # TODO if the video stream was not stopped, this returns a 409 Conflict error, which can be ignored
        response.raise_for_status()

        print("Capturing video stream")
        capture(host="@10.5.5.9", port=8554)

    finally:
        print("Stopping video stream")
        requests.get(f"{GOPRO_BASE_URL}/gopro/camera/stream/stop", timeout=1)
        print("Disconnecting from GoPro wifi")
        wifi.disconnect(interface, ssid)
        await client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Connect to a GoPro camera, pair, then enable notifications.")
    parser.add_argument(
        "-i",
        "--identifier",
        type=str,
        help="Last 4 digits of GoPro serial number, which is the last 4 digits of the default camera SSID. \
            If not used, first discovered GoPro will be connected to",
        default=None,
    )
    args = parser.parse_args()

    try:
        asyncio.run(main(args.identifier))
    except Exception as e:  # pylint: disable=broad-exception-caught
        traceback.print_exception(e)
        sys.exit(-1)
    else:
        sys.exit(0)
