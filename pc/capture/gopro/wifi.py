import os
import re
import subprocess
import tempfile
import time

import requests

from .constants import GOPRO_URL

# `netsh wlan` tutorial can be found here: https://lazyadmin.nl/it/netsh-wlan-commands/
# None of this code will work properly if there are two wireless interfaces on the PC!
WLAN_PROFILE_TEMPLATE = r"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
    <MacRandomization xmlns="http://www.microsoft.com/networking/WLAN/profile/v3">
        <enableRandomization>false</enableRandomization>
    </MacRandomization>
</WLANProfile>"""


def run_cmd(command: str) -> str:
    return (
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  # type: ignore
        .stdout.read()
        .decode(errors="ignore")
    )


class GoProWifiClient:
    def __init__(self, ssid: str, password: str) -> None:
        self.ssid = ssid
        self.password = password
        self.interface = None

    def connect(self):
        response = run_cmd("netsh wlan show interfaces")
        interfaces = []

        # Look behind to find field, then match (non-greedy) any chars until CRLF
        match = "(?<={}).+?(?=\\r\\n)"
        for interface in re.findall(match.format("Name"), response):
            # Strip leading whitespace and then the first two chars of remaining (i.e. " :")
            interfaces.append(interface.strip()[2:])

        if len(interfaces) != 1:
            raise RuntimeError(f"Expected 1 wireless interface, found {len(interfaces)}")

        self.interface = interfaces[0]
        print(f"Connecting to {self.ssid} on {self.interface}...")

        profile = WLAN_PROFILE_TEMPLATE.format(ssid=self.ssid, password=self.password.replace("&", "&amp;"))

        # Not sure why tempfile.TemporaryFile does not work, but this does :)
        fd, filename = tempfile.mkstemp(suffix=".xml")
        os.write(fd, profile.encode("utf-8"))
        os.close(fd)
        run_cmd(f'netsh wlan add profile filename="{filename}" interface="{self.interface}"')
        run_cmd(f'netsh wlan connect name="{self.ssid}" ssid="{self.ssid}" interface="{self.interface}"')

    def get_connection_status(self) -> str | None:
        response = run_cmd("netsh wlan show interfaces")

        lines = [line.strip().split(':') for line in response.split("\r\n")]
        lines = [line for line in lines if len(line) == 2]
        lines = {line[0].strip(): line[1].strip() for line in lines}
        if lines.get("SSID") == self.ssid and lines.get("Name") == self.interface:
            return lines.get("State")
        else:
            return None

    def wait_for_connection(self, timeout: int = 10) -> bool:
        for _ in range(timeout):
            status = self.get_connection_status()
            print(f"Wifi connection status: {status}")
            if status == "connected":
                return True
            time.sleep(1)
        return False

    def disconnect(self):
        if self.interface:
            run_cmd(f'netsh wlan disconnect interface="{self.interface}"')
            run_cmd(f'netsh wlan delete profile name="{self.ssid}"')

    @staticmethod
    def start_preview():
        response = requests.get(f"{GOPRO_URL}/gopro/camera/stream/start")
        # TODO if the video stream was not stopped, this returns a 409 Conflict error, which can be ignored
        response.raise_for_status()

    @staticmethod
    def stop_preview():
        requests.get(f"{GOPRO_URL}/gopro/camera/stream/stop", timeout=1)
        # ignore result
