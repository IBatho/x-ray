"""Parser test for Windows `netsh wlan show networks mode=bssid` output."""
from footfall.sniffer import parse_netsh

SAMPLE = """
Interface name : Wi-Fi
There are 3 networks currently visible.

SSID 1 : CoffeeShop
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
    BSSID 1                 : 00:11:22:33:44:55
         Signal             : 84%
         Radio type         : 802.11ac
         Band               : 5 GHz
         Channel            : 36
         Bss Load:
             Connected Stations:         3
    BSSID 2                 : 00:11:22:33:44:66
         Signal             : 60%
         Radio type         : 802.11n
         Band               : 2.4 GHz
         Channel            : 6

SSID 2 : Someones iPhone
    Network type            : Infrastructure
    BSSID 1                 : aa:bb:cc:dd:ee:ff
         Signal             : 29%
         Band               : 5 GHz
         Channel            : 11
         Bss Load:
             Connected Stations:         7
"""


def test_parses_bssids_signal_band_and_stations():
    rows = parse_netsh(SAMPLE)
    assert rows == [
        {"bssid": "00:11:22:33:44:55", "ssid": "CoffeeShop",
         "signal": 84, "band": "5 GHz", "stations": 3},
        {"bssid": "00:11:22:33:44:66", "ssid": "CoffeeShop",
         "signal": 60, "band": "2.4 GHz", "stations": 0},
        {"bssid": "aa:bb:cc:dd:ee:ff", "ssid": "Someones iPhone",
         "signal": 29, "band": "5 GHz", "stations": 7},
    ]


def test_total_connected_stations():
    assert sum(r["stations"] for r in parse_netsh(SAMPLE)) == 10


def test_empty_input():
    assert parse_netsh("") == []
