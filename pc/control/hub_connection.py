from bleak import BLEDevice, BleakClient

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

class HubConnection:

    def __init__(self, hub: BLEDevice):
        self._client = BleakClient(hub, disconnected_callback=self.handle_disconnect)
        self._rx_char = None
        self._running = False

    def handle_disconnect(self, _):
        print("Hub was disconnected.")

    def handle_rx(self, _, data: bytearray):
        decode = data.decode('utf-8')
        if decode == "OK: Running":
            self._running = True

    async def send(self, data):
        if self._client is not None and self._running:
            try:
                await self._client.write_gatt_char(self._rx_char, data)
            except Exception as e:
                print(f"Failed to send data to hub: {e}.")
                await self.disconnect()

    async def connect(self) -> bool:
        try:
            await self._client.connect()
            await self._client.start_notify(UART_TX_CHAR_UUID, self.handle_rx)
            nus = self._client.services.get_service(UART_SERVICE_UUID)
            self._rx_char = nus.get_characteristic(UART_RX_CHAR_UUID)
            return True
        except Exception as e:
            print(f"Failed to connect to hub: {e}.")
            await self.disconnect()
            return False

    async def disconnect(self):
        try:
            if self._client is not None and self._client.is_connected:
                await self._client.disconnect()
            self._client = None
        except Exception as e:
            print(f"Failed to disconnect from hub: {e}.")
        finally:
            self._running = False

    async def shutdown(self):
        self.disconnect() # We are wilfully ignoring the result of this call because Windows tends to timeout this operation

    def is_connected(self):
        return self._client and self._client.is_connected

    def is_running(self):
        return self._running
