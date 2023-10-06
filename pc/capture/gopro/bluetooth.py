import asyncio

from bleak import BleakScanner, BleakClient, BleakGATTCharacteristic

from .constants import GOPRO_COMMAND_RSP_UUID, GOPRO_WIFI_AP_SSID_UUID, GOPRO_WIFI_AP_PASSWORD_UUID, \
    GOPRO_COMMAND_REQ_UUID


class GoProBLEClient:
    class BLENotificationHandler:
        def __init__(self):
            self.event = asyncio.Event()
            self.response_uuid = None

        def reset(self, response_uuid: str):
            self.event.clear()
            self.response_uuid = response_uuid

        def handle(self, handle: BleakGATTCharacteristic, data: bytes):
            if self.response_uuid == handle.uuid and data[2] == 0x00:
                pass
            else:
                print('Received unexpected response at {handle.uuid=}: {hexlify(data, ":")!r}')
            self.event.set()

        def wait(self):
            return self.event.wait()

    def __init__(self):
        self.handler = self.BLENotificationHandler()
        self.client = None

    async def connect(self) -> bool:
        print("Connecting to GoPro via BLE. This could take a few retries.")

        for retry in range(10):
            try:
                devices = await BleakScanner.discover()
                gopro_devices = [device for device in devices if device.name is not None and device.name.startswith("GoPro")]
                if len(gopro_devices) != 1:
                    print("No GoPro found. Make sure it is on.")
                    print(f"Retrying... {retry}")
                    continue
                gopro = gopro_devices[0]
                print(f"Connecting to: {gopro.name} ({gopro.address})")
                client = BleakClient(gopro, winrt={"use_cached_services": False})
                await client.connect(timeout=15)
                await client.pair()

                await client.start_notify(GOPRO_COMMAND_RSP_UUID, self.handler.handle)
                print("Connected via BLE.")

                self.client = client
                return True
            except Exception as e:
                print(f"Failed to connect: {e}")
                print(f"Retrying... {retry}")
        return False

    async def enable_wifi(self) -> (str, str):
        if not self.client:
            return None, None

        ssid = await self.client.read_gatt_char(GOPRO_WIFI_AP_SSID_UUID)
        ssid = ssid.decode()

        password = await self.client.read_gatt_char(GOPRO_WIFI_AP_PASSWORD_UUID)
        password = password.decode()

        self.handler.reset(GOPRO_COMMAND_RSP_UUID)
        await self.client.write_gatt_char(GOPRO_COMMAND_REQ_UUID, bytearray([0x03, 0x17, 0x01, 0x01]))
        await self.handler.wait()  # Wait to receive the notification response

        return ssid, password

    async def disconnect(self):
        return await self.client.disconnect()
