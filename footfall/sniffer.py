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
    """Parse `netsh wlan show networks mode=bssid` into a list of dicts:
    {bssid, ssid, signal (0-100), band, stations}. English Windows assumed.

    `stations` is netsh's "Connected Stations" count — how many devices are
    associated to that AP right now, a real crowd proxy. Missing on older
    Windows; defaults to 0.
    """
    results = []
    current_ssid = ""
    rec = None
    for raw in text.splitlines():
        line = raw.strip()
        # "SSID 1 : MyNetwork"  (but not the "BSSID" lines)
        if line.startswith("SSID ") and ":" in line:
            current_ssid = line.split(":", 1)[1].strip()
        elif line.startswith("BSSID"):
            # "BSSID 1                 : 00:11:22:33:44:55"
            mac = line.split(":", 1)[1].strip().lower()
            rec = {"bssid": mac, "ssid": current_ssid,
                   "signal": 0, "band": "", "stations": 0}
            results.append(rec)
        elif rec is not None:
            if line.startswith("Signal"):
                pct = line.split(":", 1)[1].strip().rstrip("%")
                try:
                    rec["signal"] = int(pct)
                except ValueError:
                    pass
            elif line.startswith("Band"):
                rec["band"] = line.split(":", 1)[1].strip()
            elif line.startswith("Connected Stations"):
                val = line.split(":", 1)[1].strip()
                try:
                    rec["stations"] = int(val)
                except ValueError:
                    pass
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

    def __init__(self, on_observe: Observer, interval_s: float = 4.0,
                 on_meta=None):
        self.on_observe = on_observe
        self.interval_s = interval_s
        self.on_meta = on_meta
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
                nets = self._scan_once()
                total_stations = 0
                for n in nets:
                    pct = n["signal"]
                    label = n["ssid"] or "(hidden)"
                    if n["band"]:
                        label += " · " + n["band"]
                    self.on_observe(n["bssid"], self._pct_to_rssi(pct),
                                    self._signal_to_zone(pct), label, "wifi")
                    total_stations += n["stations"]
                if self.on_meta:
                    self.on_meta({
                        "connected_stations": total_stations,
                        "networks_visible": len(nets),
                    })
            except Exception:
                pass  # keep the demo alive even if a scan hiccups
            self._stop.wait(self.interval_s)


class BluetoothScanner:
    """Real Bluetooth-LE sensing on Windows/macOS/Linux with NO extra hardware
    beyond the built-in Bluetooth radio.

    Passively listens for BLE advertisements via `bleak` (uses Windows' WinRT
    API under the hood) and reports each advertising device's address + RSSI.
    Unlike WiFi access points, these are mostly *personal, moving* devices —
    earbuds, smartwatches, fitness bands, beacons, some phones — so the radar
    actually tracks movement around you. Addresses are hashed + salt-rotated
    by the counter, and modern phones randomize their BLE address, so this is a
    privacy-preserving crowd/movement ESTIMATE, not a person tracker.
    """

    def __init__(self, on_observe: Observer, on_meta=None):
        self.on_observe = on_observe
        self.on_meta = on_meta
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    @staticmethod
    def _rssi_to_zone(rssi: int) -> str:
        # BLE RSSI runs roughly -30 (touching) to -100 (far room/next room).
        if rssi >= -60:
            return "right-here"
        if rssi >= -78:
            return "nearby"
        return "far-side"

    def _run(self) -> None:
        try:
            import asyncio

            from bleak import BleakScanner
        except Exception:
            return  # bleak not installed; BT mode unavailable, app continues

        recent: dict = {}

        def _cb(device, adv) -> None:
            rssi = int(getattr(adv, "rssi", getattr(device, "rssi", -80)) or -80)
            addr = device.address
            name = (getattr(adv, "local_name", None) or
                    getattr(device, "name", None) or "BLE device")
            recent[addr] = time.time()
            self.on_observe(addr, rssi, self._rssi_to_zone(rssi), name, "bt")

        async def _scan() -> None:
            scanner = BleakScanner(detection_callback=_cb)
            await scanner.start()
            try:
                while not self._stop.is_set():
                    await asyncio.sleep(2.0)
                    # Distinct devices seen in the last 30s = live BT crowd.
                    cutoff = time.time() - 30
                    for a, t in list(recent.items()):
                        if t < cutoff:
                            del recent[a]
                    if self.on_meta:
                        self.on_meta({"ble_devices": len(recent)})
            finally:
                await scanner.stop()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_scan())
        except Exception:
            pass  # keep the rest of the app alive if BT is off / unavailable


class CompositeSniffer:
    """Runs several sources at once into the same counter (e.g. WiFi + BT)."""

    def __init__(self, sniffers):
        self._sniffers = sniffers

    def start(self) -> None:
        for s in self._sniffers:
            s.start()

    def stop(self) -> None:
        for s in self._sniffers:
            s.stop()


def make_sniffer(on_observe: Observer, mode: str, iface: str | None,
                 on_transaction=None, on_meta=None):
    if mode == "winscan":
        return WindowsApScanner(on_observe, on_meta=on_meta)
    if mode == "btscan":
        return BluetoothScanner(on_observe, on_meta=on_meta)
    if mode == "combo":
        # Real WiFi access points + real Bluetooth devices on one radar.
        return CompositeSniffer([
            WindowsApScanner(on_observe, on_meta=on_meta),
            BluetoothScanner(on_observe, on_meta=on_meta),
        ])
    if mode == "live":
        if not iface:
            raise ValueError("live mode requires FOOTFALL_IFACE (a monitor-mode interface)")
        return LiveSniffer(on_observe, iface)
    return SimulatedSniffer(on_observe, on_transaction=on_transaction)
