# X-Ray — Market & legal validation (for the pitch)

Synthesised from live research. Use the ranges and the honesty caveats — judges reward founders
who name their hardest problem.

## The one-liner
> Every people-counting incumbent needs **installed hardware/cameras/APs** (capex + contracts) or
> **macro mobile-panel data** (no live, per-zone, small-venue sensing). SMBs, pop-ups, events,
> markets and community spaces are **priced and installed out**. X-Ray is **zero-hardware,
> deploy-in-minutes, portable, privacy-by-design** — the empty quadrant.

## Market size (cite the range, not one number)
- **People-counting systems:** $1.45B (2025) → ~$2.65B by 2030, ~13% CAGR — *Mordor, Grand View*.
- **Footfall / heatmap analytics:** $1.7B (2025) → ~$9.4B by 2035, ~18.9% CAGR — *Market.us*.
- **Indoor location:** ~$11–12B (2024) → $31–39B by 2029–30, ~21–23% CAGR — *MarketsandMarkets*.
- Retail ≈ 37.6% of people-counting demand. Industry norm is already anonymised/aggregate — our
  privacy stance matches where the market is.

## Competitors & what they charge (our wedge = £0 hardware)
| Player | Needs | Price signal |
|---|---|---|
| Cisco Spaces / Meraki | their APs installed | per-AP license, multi-year |
| RetailNext | ceiling sensors | ~$500–$2,000/sensor + SaaS |
| Density | radar/LiDAR sensors | Waffle $149/sensor + ~$95/yr; analytics priced per sq ft |
| Placer.ai / Huq / SafeGraph | mobile-panel data | $2k–$10k+/yr; **no live in-venue sensing** |
| Springboard (MRI) | camera networks | subscription; BIDs/malls |
| Qminder / Qudini (queues) | workflow software | Qminder ~$389–$1,149/mo |
| V-Count / FootfallCam | beam/3D/AI cameras | per-device + SaaS |

**Gap:** instant + portable + cheap + privacy-safe for a *single small space, right now*. Nobody owns it.

## UK legal reality (this makes us credible, not reckless)
- A **MAC/BLE address is personal data** when identifiable → UK GDPR applies to raw capture.
- **Anonymised aggregate output is outside GDPR**, but the act of anonymising is itself processing —
  so we hash+salt+**rotate at capture** and never persist raw IDs (we already do).
- **PECR** can apply to reading device signals even when anonymised → post **signage**, run a **DPIA**.
- **Precedent — TfL WiFi pilot (2016):** 509M depersonalised probe requests, salt key destroyed at
  trial end; criticised mainly for weak signage. **We're cleaner than TfL** — a laptop in one venue
  holds no side data (Oyster/contactless) to re-identify anyone.
- **Compliance checklist we satisfy:** salt+hash+rotate at capture · aggregate-only output · on-site
  signage · DPIA · short retention · no raw MAC storage.

## The honesty caveat (say it first, on a slide)
- iOS 14 / Android 10 **randomize MACs by default** → probe counting is a **relative density/trend
  index**, not exact headcount (research: ~95% accuracy at controlled events, ~75% in transit).
- We pitch X-Ray as **busy-vs-quiet, density, dwell and movement** — and we out-credible vendors who
  over-claim absolute counts. BLE adds real *movement* signal from personal devices.

## Martyn's Law (Terrorism (Protection of Premises) Act 2025) — read the fine print
- Royal Assent **3 Apr 2025**, ~24-month implementation, regulator **SIA**. Tiers: <200 exempt;
  Standard 200–799 (**procedures only, no counting required**); Enhanced 800+ (risk assessment +
  monitoring + movement control).
- It does **NOT** mandate crowd-counting. **Sell SafeCount as "audit-ready evidence that strengthens
  your risk assessment and capacity plan," not "mandatory compliance."** Overclaiming gets caught.

## Recommended pitch order
1. **SafeCount** (event/venue overcrowding) — most acute pain (Astroworld, Itaewon), Martyn's-Law
   awareness driving budget. Demo: live density + movement radar + threshold alarm.
2. **FlexFloor** (coworking/office utilization) — strongest *willingness to pay* (rent is the lever).
3. **Shopfront / market-stall footfall** — instant-revenue, no-install SMB story + live conversion.
4. **StandIQ** (trade-show booth dwell) — easy **per-event paid pilot**, exhibitors love ROI proof.

Key slide URLs: Density Waffle pricing (density.io/resources/introducing-waffle), Qminder pricing
(qminder.com/pricing), Martyn's Law factsheet (homeofficemedia.blog.gov.uk/2025/04/03/martyns-law-factsheet),
WiFi-counting accuracy (pmc.ncbi.nlm.nih.gov/articles/PMC9698762), TfL precedent (tfl.gov.uk press 2017).
</content>
