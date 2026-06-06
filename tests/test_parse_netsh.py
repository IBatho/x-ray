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
         Channel            : 36
    BSSID 2                 : 00:11:22:33:44:66
         Signal             : 60%
         Radio type         : 802.11n
         Channel            : 6

SSID 2 : Someones iPhone
    Network type            : Infrastructure
    BSSID 1                 : aa:bb:cc:dd:ee:ff
         Signal             : 29%
         Channel            : 11
"""


def test_parses_all_bssids_and_signals():
    rows = parse_netsh(SAMPLE)
    assert rows == [
        ("00:11:22:33:44:55", 84),
        ("00:11:22:33:44:66", 60),
        ("aa:bb:cc:dd:ee:ff", 29),
    ]


def test_empty_input():
    assert parse_netsh("") == []
