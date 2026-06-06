"""FastAPI app: runs a sniffer in the background, serves the live dashboard.

Run:  uvicorn footfall.server:app --reload
Env:  FOOTFALL_MODE = sim (default) | live | winscan | btscan | combo
      FOOTFALL_IFACE = wlan0mon   (required when MODE=live)
      winscan: real WiFi access-point scan on Windows, no extra hardware.
      btscan:  real Bluetooth-LE scan via the built-in radio (needs `bleak`).
      combo:   winscan + btscan on one radar.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from .counter import FootfallCounter
from .sniffer import make_sniffer

app = FastAPI(title="WiFi Footfall — anonymous crowd sensing")

counter = FootfallCounter()
_mode = os.environ.get("FOOTFALL_MODE", "sim")
_iface = os.environ.get("FOOTFALL_IFACE")
_sniffer = make_sniffer(
    lambda mac, rssi, zone, label="", kind="": counter.observe(mac, rssi, zone, label, kind),
    mode=_mode,
    iface=_iface,
    on_transaction=counter.add_transaction,
    on_meta=counter.set_extra,
)

_WEB = Path(__file__).parent / "web" / "index.html"


@app.on_event("startup")
def _startup() -> None:
    _sniffer.start()


@app.on_event("shutdown")
def _shutdown() -> None:
    _sniffer.stop()


@app.get("/api/stats")
def stats() -> JSONResponse:
    data = counter.snapshot()
    data["mode"] = _mode
    return JSONResponse(data)


@app.post("/api/transaction")
def add_transaction(n: int = 1) -> JSONResponse:
    """Log retail transaction(s) so conversion = transactions / visitors.
    Wire this to a real POS webhook in production; the demo button calls n=1."""
    counter.add_transaction(n)
    return JSONResponse({"transactions": counter.snapshot()["transactions"]})


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _WEB.read_text(encoding="utf-8")
