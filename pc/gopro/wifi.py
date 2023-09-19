import os
import re
import subprocess
import tempfile
import time

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


def cmd(command: str) -> str:
    return (
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  # type: ignore
        .stdout.read()
        .decode(errors="ignore")
    )


def connect(ssid: str, password: str) -> str:
    response = cmd("netsh wlan show interfaces")
    interfaces = []

    # Look behind to find field, then match (non-greedy) any chars until CRLF
    match = "(?<={}).+?(?=\\r\\n)"
    for interface in re.findall(match.format("Name"), response):
        # Strip leading whitespace and then the first two chars of remaining (i.e. " :")
        interfaces.append(interface.strip()[2:])

    if len(interfaces) != 1:
        raise RuntimeError(f"Expected 1 wireless interface, found {len(interfaces)}")

    interface = interfaces[0]
    print(f"Connecting to {ssid} on {interface}...")

    profile = WLAN_PROFILE_TEMPLATE.format(ssid=ssid, password=password.replace("&", "&amp;"))

    # Not sure why tempfile.TemporaryFile does not work, but this does :)
    fd, filename = tempfile.mkstemp(suffix=".xml")
    os.write(fd, profile.encode("utf-8"))
    os.close(fd)
    cmd(f'netsh wlan add profile filename="{filename}" interface="{interface}"')

    cmd(f'netsh wlan connect name="{ssid}" ssid="{ssid}" interface="{interface}"')

    return interface


def get_connection_status(interface: str, ssid: str) -> str | None:
    response = cmd("netsh wlan show interfaces")

    # Example output:
    #
    # There is 1 interface on the system:
    #
    # Name                   : Wi-Fi 3
    # Description            : TP-Link Wireless USB Adapter
    # GUID                   : a405e966-5209-46d9-9a04-56a1978429df
    # Physical address       : 40:ed:00:58:c4:07
    # Interface type         : Primary
    # State                  : connected
    # SSID                   : GP26444705
    # BSSID                  : 26:74:f7:3c:76:49
    # Network type           : Infrastructure
    # Radio type             : 802.11n
    # Authentication         : WPA2-Personal
    # Cipher                 : CCMP
    # Connection mode        : Profile
    # Band                   : 2.4 GHz
    # Channel                : 6
    # Receive rate (Mbps)    : 72
    # Transmit rate (Mbps)   : 72
    # Signal                 : 100%
    # Profile                : GP26444705
    #
    # Hosted network status  : Not available

    lines = [line.strip().split(':') for line in response.split("\r\n")]
    lines = [line for line in lines if len(line) == 2]
    lines = {line[0].strip(): line[1].strip() for line in lines}
    if lines.get("SSID") == ssid and lines.get("Name") == interface:
        return lines.get("State")
    else:
        return None


def wait_for_connection(interface: str, ssid: str, timeout: int = 10) -> bool:
    for _ in range(timeout):
        status = get_connection_status(interface, ssid)
        print(f"Connection status: {status}")
        if status == "connected":
            return True

        time.sleep(1)

    return False


def disconnect(interface: str, ssid: str):
    cmd(f'netsh wlan disconnect interface="{interface}"')
    cmd(f'netsh wlan delete profile name="{ssid}"')
