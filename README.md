# 📡 WiFi X-Ray — Anonymous Footfall Sensing

Count how busy a high street, shopfront, or venue is **using ambient WiFi
signals instead of cameras** — and do it *privacy-first*. Phones constantly
broadcast "probe requests" looking for networks; we count those to estimate
crowd size and movement between zones. No camera, no login, no individual
tracking.

> **The pitch:** "We see the crowd without watching anyone." Device IDs are
> salted-hashed and thrown away, the salt rotates so nobody can be followed
> over time, and only aggregate numbers ever leave the box. Privacy *is* the
> feature.

## ⚠️ Read this before you run it live

This project deliberately does **only** the legal, ethical version:

- ✅ Captures **probe-request management frames** (sender MAC + signal strength), hashes the MAC instantly with a rotating salt, and keeps only aggregate counts.
- ❌ Does **not** connect to, associate with, or read traffic from anyone's network.
- ❌ Does **not** track or re-identify individuals (modern MAC randomization makes this an *estimate* — by design).
- ❌ Does **not** touch CCTV/security cameras. Accessing systems you don't own is a crime (UK Computer Misuse Act 1990).

If you capture **live** data in a public place: show an **on-site notice**,
keep it **aggregate-only**, and don't store raw identifiers. That keeps you on
the right side of UK GDPR / the ICO. The defaults here already do this.

## 🪟 Windows laptop, no extra hardware (real WiFi, runs on the laptop itself)

Counting silent pedestrians needs monitor mode, which Windows + a built-in Intel
card can't do. But Windows *can* read every WiFi access point / hotspot in range
and its live signal strength via the built-in `netsh` — real RF sensing of the
room with zero hardware. Walk around and the heatmap shifts.

```cmd
run_windows.bat
```

Then open **http://127.0.0.1:8000** on the same laptop. (Manual equivalent:
`set FOOTFALL_MODE=winscan` then `python -m uvicorn footfall.server:app`.)

> Honest framing for the demo: this senses **WiFi sources** (routers, phone
> hotspots, repeaters) — not every silent phone in someone's pocket. The
> dashboard labels it "WiFi sources in range" in this mode. For true pedestrian
> counting you need monitor mode (Linux or a USB adapter — see "Going live").

## Quick start (works with zero hardware)

```bash
pip install -r requirements.txt
uvicorn footfall.server:app --reload
# open http://127.0.0.1:8000
```

Runs in **simulated mode** by default — a synthetic high-street crowd so you
can build and demo the whole stack on any laptop.

## Going live (real WiFi capture)

You need a WiFi adapter that supports **monitor mode** (built-in Intel on
Linux often works; a reliable external is the Alfa AWUS036ACH/NHA).

```bash
sudo airmon-ng start wlan0          # creates e.g. wlan0mon
export FOOTFALL_MODE=live
export FOOTFALL_IFACE=wlan0mon
sudo -E uvicorn footfall.server:app   # raw capture needs root
```

> **Test capture works in your first hour.** Driver/monitor-mode issues are the
> #1 hackathon time-sink — if your adapter won't sniff probe requests, swap it
> immediately and keep demoing in sim mode meanwhile.

## How it works

```
 phones ──probe requests──▶  sniffer.py  ──(mac,rssi,zone)──▶  counter.py  ──aggregate──▶  /api/stats ──▶ dashboard
                            (sim | live)                     (hash+rotate salt)
```

- `footfall/sniffer.py` — `SimulatedSniffer` (no hardware) and `LiveSniffer` (Scapy + monitor mode). Same callback interface.
- `footfall/counter.py` — salted-hash + rotating-salt presence counter; emits only aggregates.
- `footfall/server.py` — FastAPI: runs a sniffer in the background, serves `/api/stats` + the dashboard.
- `footfall/web/index.html` — live dashboard: big count, trend, zone heatmap.

## Background: the "see through walls" research

This repo is the *buildable-in-a-day* cousin of the famous through-wall WiFi
sensing work. Those need special hardware and trained models and are **not**
reproducible in a hackathon, but they're the inspiration:

- **MIT RF-Pose / RF-Pose3D** — stick-figure poses through walls from RF reflections (custom radar-like hardware). https://rfpose.csail.mit.edu/ · https://news.mit.edu/2018/artificial-intelligence-senses-people-through-walls-0612
- **CMU DensePose From WiFi (2023)** — full body surfaces from Channel State Information using 3 TX + 3 RX antennas + a graph-transformer. https://arxiv.org/pdf/2301.00250
- Want to go deeper later (CSI motion/presence on cheap **ESP32** boards): https://github.com/espressif/esp-csi · curated list: https://github.com/NTUMARS/Awesome-WiFi-CSI-Sensing

## Retail analytics it computes (all aggregate, all anonymous)

- **Footfall** — live crowd estimate in the presence window.
- **Zone heatmap** — how the crowd is distributed right now.
- **Where they go first** — first-zone-entered distribution (is your promo display pulling people in?).
- **Crowd flow** — top zone-to-zone movements (do people reach the back of the store?).
- **Attention by dwell** — avg seconds per zone. This is the honest proxy for "what catches their eye" — WiFi gives *location*, not *gaze*, so longest-dwell zone ≈ what's holding attention. (True eye-tracking needs cameras.)
- **Conversion** — `transactions ÷ estimated visitors`. POST to `/api/transaction` (or hit the **+ Sale** button) to feed sales; wire it to a real POS webhook in production. `visitor_calibration` scales raw device arrivals down to real people (MAC randomization + multi-device users inflate the raw count) — calibrate it against a manual head-count.

## Why not the "see-through-walls X-ray" model?

Public WiFi-pose datasets exist ([MM-Fi](https://arxiv.org/pdf/2305.10345) ~320k frames, [WiPose](https://github.com/NjtechCVLab/Wi-PoseDataset), [Person-in-WiFi-3D](https://github.com/cseeyangchen/DT-Pose)) but CSI is specific to the exact antenna geometry and room it was recorded in — a model trained on those data **won't work on your hardware/venue**. Cross-environment generalisation is an [open research problem](https://arxiv.org/pdf/2501.09411). You'd have to collect tens of thousands of labelled frames in *your* setup with a synchronised camera and train for days. Out of scope for a hackathon; the footfall/flow/conversion stack above delivers the same business value and actually runs today.

## Roadmap if you have extra time

- **CSI presence panel:** flash 2× ESP32 with esp-csi, stream CSI amplitude into a "motion" widget next to the footfall count — the visual "X-ray" moment, scoped to your own booth.
- **Dwell time & flow:** estimate how long the crowd lingers and which zone they move to next (still aggregate).
- **Map overlay:** drop the zone counts onto a floor plan / street map.
