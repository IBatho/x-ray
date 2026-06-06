"""Probe-request sources that feed the FootfallCounter.

Two interchangeable sources:
  * SimulatedSniffer  - realistic synthetic crowd; runs anywhere, no hardware.
  * LiveSniffer       - real 802.11 probe requests via Scapy + a monitor-mode
                        adapter. Captures ONLY the sender MAC and signal
                        strength of probe-request management frames. It does
                        not associate, decrypt, or read any payload.

Both call `on_observe(mac, rssi, zone)` for every sighting. The counter hashes
and discards the MAC immediately, so nothing identifying is persisted.
"""

from __future__ import annotations

import random
import threading
import time
from typing import Callable

Observer = Callable[[str, int, str], None]


class SimulatedSniffer:
    """Generates a plausible high-street crowd so the whole stack is demo-able
    with zero hardware. Devices arrive, linger across zones, and leave."""

    def __init__(self, on_observe: Observer, zones=None, base_crowd=18,
                 on_transaction=None):
        self.on_observe = on_observe
        # Ordered like a store: entrance first, till last.
        self.zones = zones or ["entrance", "promo-display", "aisles", "checkout"]
        self.base_crowd = base_crowd
        self.on_transaction = on_transaction
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _run(self) -> None:
        # Each "device" is a randomized MAC (mimicking real phones) that hangs
        # around for a while, then is replaced — just like real foot traffic.
        active: list[list] = []  # [mac, zone, expires_at]
        while not self._stop.is_set():
            now = time.time()
            # Gentle sinusoidal busyness so the trend line looks alive.
            target = self.base_crowd + int(8 * (1 + random.random()) *
                                            (0.6 + 0.4 * random.random()))
            active = [d for d in active if d[2] > now]
            while len(active) < target:
                mac = ":".join("%02x" % random.randint(0, 255) for _ in range(6))
                zone = random.choice(self.zones)
                active.append([mac, zone, now + random.uniform(20, 180)])
            for dev in active:
                if random.random() < 0.3:  # occasional zone hop
                    dev[1] = random.choice(self.zones)
                rssi = random.randint(-85, -45)
                self.on_observe(dev[0], rssi, dev[1])
            # Roughly a few sales per minute, so conversion is non-trivial.
            if self.on_transaction and random.random() < 0.15:
                self.on_transaction(1)
            self._stop.wait(1.0)


class LiveSniffer:
    """Real probe-request capture. Requires Scapy and an interface already in
    monitor mode (e.g. `sudo airmon-ng start wlan0`)."""

    def __init__(self, on_observe: Observer, iface: str):
        self.on_observe = on_observe
        self.iface = iface
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    @staticmethod
    def _rssi_to_zone(rssi: int) -> str:
        # Coarse distance bucketing from signal strength — good enough for a
        # "near / mid / far" heatmap without any per-person tracking.
        if rssi >= -55:
            return "right-here"
        if rssi >= -70:
            return "nearby"
        return "passing-by"

    def _handle(self, pkt) -> None:
        from scapy.layers.dot11 import Dot11, Dot11ProbeReq

        if not pkt.haslayer(Dot11ProbeReq):
            return
        dot11 = pkt.getlayer(Dot11)
        mac = getattr(dot11, "addr2", None)
        if not mac:
            return
        rssi = int(getattr(pkt, "dBm_AntSignal", -70))
        self.on_observe(mac, rssi, self._rssi_to_zone(rssi))

    def _run(self) -> None:
        from scapy.all import sniff

        sniff(
            iface=self.iface,
            prn=self._handle,
            store=False,
            stop_filter=lambda _: self._stop.is_set(),
        )


def parse_netsh(text: str):
    """Parse `netsh wlan show networks mode=bssid` output into
    [(bssid, signal_percent), ...]. English Windows output assumed."""
    results = []
    current_bssid = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("BSSID"):
            # "BSSID 1                 : 00:11:22:33:44:55"
            parts = line.split(":", 1)
            if len(parts) == 2:
                current_bssid = parts[1].strip().lower()
        elif line.startswith("Signal") and current_bssid:
            # "Signal             : 84%"
            pct = line.split(":", 1)[1].strip().rstrip("%")
            try:
                results.append((current_bssid, int(pct)))
            except ValueError:
                pass
            current_bssid = None
    return results


class WindowsApScanner:
    """Real WiFi sensing on Windows with NO extra hardware.

    Uses the built-in `netsh wlan show networks mode=bssid` to read every
    access point / hotspot radio in range and its signal strength, live. This
    senses the RF environment around you (routers, phone hotspots, repeaters) —
    it is NOT a silent pedestrian counter (that needs monitor mode), so label
    it honestly. Walk around and the signal-strength heatmap shifts in real
    time, which makes a strong, real demo on any Windows laptop.
    """

    def __init__(self, on_observe: Observer, interval_s: float = 4.0):
        self.on_observe = on_observe
        self.interval_s = interval_s
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    @staticmethod
    def _pct_to_rssi(pct: int) -> int:
        # Windows reports signal as 0-100%; map to a dBm-like scale.
        return (pct // 2) - 100

    @staticmethod
    def _signal_to_zone(pct: int) -> str:
        if pct >= 75:
            return "right-here"
        if pct >= 45:
            return "nearby"
        return "far-side"

    def _scan_once(self):
        import subprocess

        out = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True, text=True, timeout=15,
        )
        return parse_netsh(out.stdout)

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                for bssid, pct in self._scan_once():
                    self.on_observe(bssid, self._pct_to_rssi(pct),
                                    self._signal_to_zone(pct))
            except Exception:
                pass  # keep the demo alive even if a scan hiccups
            self._stop.wait(self.interval_s)


def make_sniffer(on_observe: Observer, mode: str, iface: str | None,
                 on_transaction=None):
    if mode == "winscan":
        return WindowsApScanner(on_observe)
    if mode == "live":
        if not iface:
            raise ValueError("live mode requires FOOTFALL_IFACE (a monitor-mode interface)")
        return LiveSniffer(on_observe, iface)
    return SimulatedSniffer(on_observe, on_transaction=on_transaction)
