# X-Ray — Strategy: 100 → 25 → 10 use cases

**The asset:** a laptop-only, zero-extra-hardware sensor that produces *anonymous, real-time*
crowd density + movement from ambient **WiFi** (access points + "connected stations" device
counts) and **Bluetooth-LE** (nearby personal devices + signal-distance). Outputs: live count,
dwell time, zone heatmap, movement radar, trend. Privacy-first (salted+rotating hashes, aggregate
only). Deployable in minutes on any Windows laptop.

**Why this wins:** every incumbent (Purple, Cisco DNA Spaces, Density, Placer.ai, RetailNext)
needs **installed hardware, cameras, contracts, or telco data**. We need a **laptop**. That
collapses time-to-value from weeks to minutes and price from £000s to ~£0 capex — which unlocks
the long tail of small operators nobody serves.

---

## Stage 1 — 100 candidate use cases

### Retail & high street
1. Independent shop footfall counter
2. Market-stall dwell & engagement
3. Window-display "stop power" (do people pause?)
4. Shop conversion (footfall → till sales)
5. Promo-table effectiveness (zone dwell)
6. Staff-rota matching to footfall peaks
7. High-street/BID pedestrian counting
8. Vacant-unit footfall (leasing evidence for landlords)
9. Pop-up shop ROI reporting
10. Queue length at tills
11. Changing-room demand
12. Cross-shop visit patterns in a parade
13. Late-night shop safety occupancy
14. Charity-shop footfall benchmarking
15. Garden centre / large-format flow

### Hospitality & nightlife
16. Café live "how busy now" widget
17. Restaurant table dwell & turnover
18. Bar occupancy vs licence capacity
19. Queue/wait-time at street food
20. Beer-garden capacity in good weather
21. Nightclub crowd-density safety
22. Smoking-area overcrowding
23. Pub quiz / event-night attendance lift
24. Coffee-shop morning-rush staffing
25. Hotel lobby / breakfast-room flow

### Events, venues, culture
26. Trade-show booth engagement (dwell at stand)
27. Exhibition/museum exhibit popularity heatmap
28. Festival zone crowd-flow
29. Conference session attendance
30. Gallery private-view headcount
31. Theatre foyer/interval bar flow
32. Sports-venue concourse congestion
33. Cinema lobby & screen occupancy
34. Wedding/private-event guest flow
35. Comic-con / fan-event stage crowd-density

### Fitness & wellness
36. Gym live occupancy ("is it busy?")
37. Boutique studio class-fill
38. Pool/leisure-centre capacity
39. Climbing-wall busy-zones
40. Spa quiet-zone monitoring

### Workplace & property
41. Coworking desk utilization
42. Meeting-room occupancy / ghost bookings
43. Office return-to-office attendance
44. Canteen peak-time flow
45. Building-lobby footfall for landlords
46. Estate-agent open-house engagement
47. Show-home viewer dwell per room
48. Commercial-space "prove the footfall" for rent reviews
49. Warehouse break-room density
50. Reception visitor counting

### Public sector, transport, safety
51. Council high-street vitality monitoring
52. Bus-stop / station crowding
53. Pedestrianisation impact studies
54. Library / study-space occupancy
55. Town-square event crowd estimates
56. Polling-station queue monitoring
57. A&E / GP waiting-room occupancy
58. Vaccination/clinic queue flow
59. Park / green-space usage counts
60. Public-toilet demand timing
61. Martyn's Law crowd-density evidence for venues
62. Protest/gathering size estimation (ethics-gated)
63. Flood-shelter / emergency-centre headcount
64. School-gate congestion
65. University lecture-hall attendance

### Advertising & media
66. OOH/billboard audience measurement
67. Shop-window ad dwell
68. In-store digital-signage attention
69. Sampling/brand-activation reach
70. Sponsorship footfall proof for brands

### Tourism & destinations
71. Visitor-attraction queue & dwell
72. Tourist hotspot congestion alerts
73. Heritage-site flow management
74. Christmas-market footfall
75. Beach/promenade crowd levels

### Logistics & operations
76. Loading-bay congestion
77. Click-and-collect counter queue
78. Self-checkout vs staffed flow
79. Returns-desk wait
80. Showroom test-drive desk demand

### Health, care, education
81. Care-home communal-room activity
82. Hospital corridor congestion
83. Dentist/optician waiting flow
84. Nursery pickup congestion
85. Exam-hall occupancy

### Faith, community, civic
86. Place-of-worship attendance counting
87. Community-centre room usage
88. Food-bank queue dignity (volume without IDs)
89. Town-hall meeting turnout
90. Youth-centre footfall for grant reporting

### Niche / experimental
91. Empty-shop "is anyone here" security
92. Home-viewing privacy audit (count unknown devices)
93. Anti-skimming: rogue-device near ATM
94. Lost-device proximity finder
95. Desk-presence for hot-desk cleaning triggers
96. Retail theft-hotspot dwell anomalies
97. Restaurant ghost-kitchen pickup flow
98. Drive-thru queue (BT in cars)
99. Stadium turnstile load-balancing
100. Smart-bin / amenity siting via footfall

---

## Stage 2 — cull to 25 (filters: needs only a laptop · legal/ethical · a buyer who can say "yes" fast · demoable today in London)

**Kept (with why):**
1. Independent shop footfall + conversion (#1,4) — huge long tail, owner decides
2. Market-stall dwell (#2) — Borough/Camden/Spitalfields traders on site today
3. High-street/BID pedestrian counting (#7) — BIDs already buy this data
4. Pop-up / brand-activation ROI (#9,69) — agencies need proof, pay fast
5. Café/bar live "how busy now" widget (#16) — embeddable, viral, recurring
6. Restaurant table dwell & turnover (#17)
7. Bar/venue capacity vs licence (#18)
8. Street-food queue/wait-time (#19)
9. Nightclub/venue crowd-density safety (#21)
10. Trade-show booth engagement (#26) — exhibitors pay £000s for stands
11. Museum/gallery exhibit dwell heatmap (#27,30)
12. Conference session attendance (#29)
13. Gym/studio live occupancy (#36,37)
14. Coworking desk utilization (#41)
15. Meeting-room ghost-booking detection (#42)
16. Office return-to-office attendance (#43)
17. Estate-agent open-house / show-home engagement (#46,47)
18. Landlord "prove the footfall" leasing evidence (#8,48)
19. Library/study-space occupancy (#54)
20. Martyn's Law crowd-density evidence (#61) — new legal duty = new demand
21. OOH/window-display audience measurement (#66,67)
22. Visitor-attraction queue & dwell (#71)
23. Place-of-worship / community-centre attendance (#86,87,90)
24. Clinic/waiting-room occupancy (#57,58)
25. Christmas/seasonal-market footfall (#74)

**Dropped:** anything needing fixed install over time, multi-site triangulation, identifying
individuals, or raising ethics flags (protest sizing #62, theft #96, ATM skimming #93), or where a
laptop in one spot can't deliver (transport networks #52, drive-thru #98, stadium turnstiles #99).

---

## Stage 3 — research lens → final 10 (deployable in London in <6h, someone pays)

Selection criteria, scored:
- **Pain acuteness** · **Speed to "yes" / pay** · **Laptop-only feasibility** · **Reachable in London today** · **Demo wow**

### THE FINAL 10 (each = a lens in the app)

| # | Product lens | Hero metric | Who pays (London) | Why it pays today |
|---|---|---|---|---|
| 1 | **Shopfront** — retail footfall + conversion | shoppers now · conversion % | Indie retailers, market traders | Owner sees footfall→sales gap instantly; staffing + promo ROI |
| 2 | **QueuePulse** — live queue & wait-time | est. wait mins | Cafés, street food, clinics | Walk-aways cost money; live wait board reduces them |
| 3 | **SafeCount** — crowd-density & capacity (Martyn's Law) | % of capacity · alert | Bars, clubs, venues, events | New UK Protect Duty pushes venues to evidence crowd numbers |
| 4 | **BusyNow** — public "how busy" live widget | busyness % | Gyms, cafés, bars | Embeddable on web/Google; reduces queues, recurring SaaS |
| 5 | **StandIQ** — exhibition/booth engagement | visitors · dwell at stand | Exhibitors, event organisers | Stands cost £000s; exhibitors crave proof of engagement |
| 6 | **FlexFloor** — coworking/office utilization | desks in use · room ghost-bookings | Coworking ops, facilities | Justify space cost, kill ghost bookings, plan cleaning |
| 7 | **OpenHouse** — estate-agent viewing engagement | viewers · dwell per room | Estate agents | Proves marketing pull; "12 viewers, kitchen held them longest" |
| 8 | **DistrictPulse** — BID/high-street pedestrian counts | footfall index · zone flow | BIDs, councils, landlords | BIDs already buy footfall reports for levy-payers |
| 9 | **DwellMap** — museum/gallery exhibit popularity | dwell heatmap by zone | Museums, galleries, attractions | Curation + sponsorship value; no camera privacy worries |
| 10 | **CongregationCount** — community/venue attendance | attendance · trend | Faith/community centres, libraries | Grant + capacity reporting without surveilling people |

(Final ordering & emphasis updated from live research — see RESEARCH.md.)
