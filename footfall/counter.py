"""Privacy-preserving footfall counter.

Design principles (these ARE the pitch — privacy by design):
  * Raw MAC addresses are never stored. Each observation is immediately
    hashed with SHA-256 + a secret salt that ROTATES on a timer. Once the
    salt rotates, old hashes can no longer be linked to new ones, so an
    individual cannot be followed across rotation windows even in principle.
  * Only aggregate numbers (counts, per-zone totals, trend) leave this object.
  * Modern phones randomize their MAC every few minutes, so this produces an
    ESTIMATE of crowd size, not a per-person tracker. That is by design.
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
    last_seen: float
    zone: str
    rssi: int


@dataclass
class FootfallCounter:
    # A device is "present" if seen within this many seconds.
    presence_window_s: float = 300.0
    # Secret salt rotates this often; after rotation, hashes can't be linked.
    salt_rotation_s: float = 900.0
    # How many minutes of history to keep for the trend line.
    trend_minutes: int = 30

    _salt: bytes = field(default_factory=lambda: os.urandom(16), init=False)
    _salt_set_at: float = field(default_factory=time.time, init=False)
    _devices: dict = field(default_factory=dict, init=False)
    _trend: deque = field(default_factory=lambda: deque(maxlen=240), init=False)
    _total_seen_hashes: set = field(default_factory=set, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def _maybe_rotate_salt(self, now: float) -> None:
        if now - self._salt_set_at >= self.salt_rotation_s:
            self._salt = os.urandom(16)
            self._salt_set_at = now
            # Drop the cross-window unique set so it can't bridge salts.
            self._total_seen_hashes.clear()

    def _hash(self, mac: str) -> str:
        return hashlib.sha256(self._salt + mac.encode("utf-8")).hexdigest()[:16]

    def observe(self, mac: str, rssi: int = -70, zone: str = "main") -> None:
        """Record one probe-request sighting. `mac` is hashed and discarded."""
        now = time.time()
        with self._lock:
            self._maybe_rotate_salt(now)
            h = self._hash(mac)
            self._devices[h] = _Device(last_seen=now, zone=zone, rssi=rssi)
            self._total_seen_hashes.add(h)

    def _prune(self, now: float) -> None:
        cutoff = now - self.presence_window_s
        stale = [h for h, d in self._devices.items() if d.last_seen < cutoff]
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

            # Append a trend sample at most every ~5s.
            if not self._trend or now - self._trend[-1][0] >= 5:
                self._trend.append((now, present))

            cutoff = now - self.trend_minutes * 60
            trend = [
                {"t": int(t), "count": c} for t, c in self._trend if t >= cutoff
            ]

            return {
                "present": present,
                "per_zone": dict(per_zone),
                "unique_since_salt": len(self._total_seen_hashes),
                "trend": trend,
                "presence_window_s": self.presence_window_s,
                "salt_age_s": round(now - self._salt_set_at, 1),
                "ts": int(now),
            }
