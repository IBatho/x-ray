"""Privacy-preserving footfall counter.

Design principles (these ARE the pitch — privacy by design):
  * Raw MAC addresses are never stored. Each observation is immediately
    hashed with SHA-256 + a secret salt that ROTATES on a timer. Once the
    salt rotates, old hashes can no longer be linked to new ones, so an
    individual cannot be followed across rotation windows even in principle.
  * Only aggregate numbers (counts, per-zone totals, flows, conversion) leave
    this object — never a per-device record.
  * Modern phones randomize their MAC every few minutes, so this produces an
    ESTIMATE of crowd size, not a per-person tracker. That is by design.

Flow tracking note: we keep a short in-memory zone *sequence* per hashed device
only within the current salt window, purely to aggregate "first zone entered"
and zone-to-zone transitions. The sequences are never exposed and are wiped on
salt rotation. Output is always aggregate.
"""

from __future__ import annotations

import hashlib
import os
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field


@dataclass
class _Device:
    first_seen: float
    last_seen: float
    zone: str
    first_zone: str
    rssi: int
    # Accumulated dwell time per zone for this device, this salt window.
    dwell: dict = field(default_factory=lambda: defaultdict(float))


@dataclass
class FootfallCounter:
    # A device is "present" if seen within this many seconds.
    presence_window_s: float = 300.0
    # Secret salt rotates this often; after rotation, hashes can't be linked.
    salt_rotation_s: float = 900.0
    # How many minutes of history to keep for the trend line.
    trend_minutes: int = 30
    # Fraction of detected "arrivals" estimated to be real distinct people.
    # MAC randomization + multi-device users inflate raw arrivals, so we scale
    # down to estimate visitors. Tunable; calibrate against a manual count.
    visitor_calibration: float = 0.45

    _salt: bytes = field(default_factory=lambda: os.urandom(16), init=False)
    _salt_set_at: float = field(default_factory=time.time, init=False)
    _devices: dict = field(default_factory=dict, init=False)
    _trend: deque = field(default_factory=lambda: deque(maxlen=240), init=False)
    _total_seen_hashes: set = field(default_factory=set, init=False)

    # Aggregate flow accumulators (survive salt rotation — they hold no IDs).
    _arrivals: int = field(default=0, init=False)
    _first_zone: dict = field(default_factory=lambda: defaultdict(int), init=False)
    _transitions: dict = field(default_factory=lambda: defaultdict(int), init=False)
    _zone_dwell_total: dict = field(default_factory=lambda: defaultdict(float), init=False)
    _zone_dwell_n: dict = field(default_factory=lambda: defaultdict(int), init=False)

    # Conversion: externally supplied transaction count for the session.
    _transactions: int = field(default=0, init=False)

    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def _maybe_rotate_salt(self, now: float) -> None:
        if now - self._salt_set_at >= self.salt_rotation_s:
            self._salt = os.urandom(16)
            self._salt_set_at = now
            self._total_seen_hashes.clear()
            self._devices.clear()  # sequences are wiped; aggregates remain

    def _hash(self, mac: str) -> str:
        return hashlib.sha256(self._salt + mac.encode("utf-8")).hexdigest()[:16]

    def observe(self, mac: str, rssi: int = -70, zone: str = "main") -> None:
        """Record one probe-request sighting. `mac` is hashed and discarded."""
        now = time.time()
        with self._lock:
            self._maybe_rotate_salt(now)
            h = self._hash(mac)
            dev = self._devices.get(h)
            if dev is None:
                # New arrival.
                dev = _Device(first_seen=now, last_seen=now, zone=zone,
                              first_zone=zone, rssi=rssi)
                self._devices[h] = dev
                self._arrivals += 1
                self._first_zone[zone] += 1
            else:
                # Accumulate dwell in the zone they were in since last sighting.
                gap = now - dev.last_seen
                if gap <= self.presence_window_s:
                    dev.dwell[dev.zone] += gap
                if zone != dev.zone:
                    self._transitions[(dev.zone, zone)] += 1
                    dev.zone = zone
                dev.last_seen = now
                dev.rssi = rssi
            self._total_seen_hashes.add(h)

    def set_transactions(self, n: int) -> None:
        with self._lock:
            self._transactions = max(0, int(n))

    def add_transaction(self, n: int = 1) -> None:
        with self._lock:
            self._transactions = max(0, self._transactions + int(n))

    def _prune(self, now: float) -> None:
        cutoff = now - self.presence_window_s
        stale = []
        for h, d in self._devices.items():
            if d.last_seen < cutoff:
                # Flush this device's dwell into the aggregate before dropping.
                for z, secs in d.dwell.items():
                    self._zone_dwell_total[z] += secs
                    self._zone_dwell_n[z] += 1
                stale.append(h)
        for h in stale:
            del self._devices[h]

    def snapshot(self) -> dict:
        """Return aggregate stats only. Safe to expose over HTTP."""
        now = time.time()
        with self._lock:
            self._maybe_rotate_salt(now)
            self._prune(now)

            per_zone: dict = defaultdict(int)
            for d in self._devices.values():
                per_zone[d.zone] += 1
            present = len(self._devices)

            if not self._trend or now - self._trend[-1][0] >= 5:
                self._trend.append((now, present))
            cutoff = now - self.trend_minutes * 60
            trend = [{"t": int(t), "count": c} for t, c in self._trend if t >= cutoff]

            # First-zone distribution as percentages.
            fz_total = sum(self._first_zone.values()) or 1
            first_zone = {
                z: round(100 * n / fz_total) for z, n in self._first_zone.items()
            }

            # Top zone-to-zone transitions.
            top_flows = sorted(
                self._transitions.items(), key=lambda kv: kv[1], reverse=True
            )[:6]
            flows = [
                {"from": a, "to": b, "count": n} for (a, b), n in top_flows
            ]

            # Average dwell per zone (seconds), incl. devices still present.
            dwell_total = dict(self._zone_dwell_total)
            dwell_n = dict(self._zone_dwell_n)
            for d in self._devices.values():
                for z, secs in d.dwell.items():
                    dwell_total[z] = dwell_total.get(z, 0.0) + secs
                    dwell_n[z] = dwell_n.get(z, 0) + 1
            avg_dwell = {
                z: round(dwell_total[z] / dwell_n[z], 1)
                for z in dwell_total if dwell_n.get(z)
            }

            estimated_visitors = max(1, round(self._arrivals * self.visitor_calibration))
            conversion = round(100 * self._transactions / estimated_visitors, 1)

            return {
                "present": present,
                "per_zone": dict(per_zone),
                "unique_since_salt": len(self._total_seen_hashes),
                "trend": trend,
                "first_zone": first_zone,
                "flows": flows,
                "avg_dwell_s": avg_dwell,
                "arrivals": self._arrivals,
                "estimated_visitors": estimated_visitors,
                "transactions": self._transactions,
                "conversion_pct": conversion,
                "presence_window_s": self.presence_window_s,
                "salt_age_s": round(now - self._salt_set_at, 1),
                "ts": int(now),
            }
