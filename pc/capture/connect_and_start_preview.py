from .gopro.bluetooth import GoProBLEClient
from .gopro.wifi import GoProWifiClient

async def connect_and_start_preview():
    gopro_ble = GoProBLEClient()

    ble_connected = await gopro_ble.connect()
    if not ble_connected:
        raise Exception("Failed to connect to GoPro via BLE")
    
    ssid, password = await gopro_ble.enable_wifi()
    print(f"GoPro wifi enabled. SSID: {ssid}, password: {password}")
    
    gopro_wifi = GoProWifiClient(ssid, password)
    gopro_wifi.connect()
    
    if not await gopro_wifi.wait_for_connection(30):
        # Note that this takes quite a long time when the GoPro was just turned on
        print("Failed to connect to GoPro wifi")
        return
    
    gopro_wifi.start_preview()
    
    return gopro_ble, gopro_wifi
