# Note that this code is currently mostly copied from https://github.com/gopro/OpenGoPro
# It will be removed and rewritten to match our needs once I confirm everything is working.

import re
import asyncio
from typing import Dict, Any, List, Callable, Optional

from bleak import BleakScanner, BleakClient, BleakGATTCharacteristic
from bleak.backends.device import BLEDevice as BleakDevice


def exception_handler(loop: asyncio.AbstractEventLoop, context: Dict[str, Any]) -> None:
    """Catch exceptions from non-main thread

    Args:
        loop (asyncio.AbstractEventLoop): loop to catch exceptions in
        context (Dict[str, Any]): exception context
    """
    msg = context.get("exception", context["message"])
    print(f"Caught exception {str(loop)}: {msg}")
    print("This is unexpected and unrecoverable.")


async def connect_ble(
        notification_handler: Callable[[BleakGATTCharacteristic, bytes], None],
        identifier: Optional[str] = None,
) -> BleakClient:
    """Connect to a GoPro, then pair, and enable notifications

    If identifier is None, the first discovered GoPro will be connected to.

    Retry 10 times

    Args:
        notification_handler (Callable[[int, bytes], None]): callback when notification is received
        identifier (str, optional): Last 4 digits of GoPro serial number. Defaults to None.

    Raises:
        Exception: couldn't establish connection after retrying 10 times

    Returns:
        BleakClient: connected client
    """

    asyncio.get_event_loop().set_exception_handler(exception_handler)

    RETRIES = 10
    for retry in range(RETRIES):
        try:
            # Map of discovered devices indexed by name
            devices: Dict[str, BleakDevice] = {}

            # Scan for devices
            print("Scanning for bluetooth devices...")

            # Scan callback to also catch nonconnectable scan responses
            # pylint: disable=cell-var-from-loop
            def _scan_callback(device: BleakDevice, _: Any) -> None:
                # Add to the dict if not unknown
                if device.name and device.name != "Unknown":
                    devices[device.name] = device

            # Scan until we find devices
            matched_devices: List[BleakDevice] = []
            while len(matched_devices) == 0:
                # Now get list of connectable advertisements
                for device in await BleakScanner.discover(timeout=5, detection_callback=_scan_callback):
                    if device.name != "Unknown" and device.name is not None:
                        devices[device.name] = device
                # Log every device we discovered
                for d in devices:
                    print(f"\tDiscovered: {d}")
                # Now look for our matching device(s)
                token = re.compile(r"GoPro [A-Z0-9]{4}" if identifier is None else f"GoPro {identifier}")
                matched_devices = [device for name, device in devices.items() if token.match(name)]
                print(f"Found {len(matched_devices)} matching devices.")

            # Connect to first matching Bluetooth device
            device = matched_devices[0]

            print(f"Establishing BLE connection to {device}...")
            client = BleakClient(device, winrt={"use_cached_services": False})
            await client.connect(timeout=15)
            print("BLE Connected!")

            # Try to pair (on some OS's this will expectedly fail)
            print("Attempting to pair...")
            try:
                await client.pair()
            except NotImplementedError:
                # This is expected on Mac
                pass
            print("Pairing complete!")

            # Enable notifications on all notifiable characteristics
            print("Enabling notifications...")
            for service in client.services:
                for char in service.characteristics:
                    if "notify" in char.properties:
                        print(f"Enabling notification on char {char.uuid}")
                        await client.start_notify(char, notification_handler)  # type: ignore
            print("Done enabling notifications")

            return client
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"Connection establishment failed: {exc}")
            print(f"Retrying #{retry}")

    raise RuntimeError(f"Couldn't establish BLE connection after {RETRIES} retries")
