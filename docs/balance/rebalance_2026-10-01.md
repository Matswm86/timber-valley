# Timber Valley cost rebalance, Valleys 2-6 (2026-10-01)

**Verdict: every pad after Valley 1 now costs 6-49% of its old price. Birch Bend pads total
$288K instead of $1.16M, and a casual player clears the valley in about 35 minutes instead of
about 2 hours (my calc).** Valley 1 is unchanged.

- Measured income backs up Mats' report. Valley 1 with every pad and global upgrades at max
  earns **95 $/s** (headless probe). The old model assumed 150 $/s, and it overrated every
  later valley by more. Re-run with the measured income, the old prices give V2 2.0 h, V3
  4.2 h, V4 5.7 h and V5 6.9 h, about 20 h in all, with landmark waits of 9-40 min (my calc).
- New prices come from income: each pad costs "income when the player reaches it x a target
  wait". The wait ramps from about 1 min at the gate to about 2 min late in the valley, with
  3-4.5 min for landmarks. One scale factor per valley is solved so the casual player hits
  the valley time.
- Result for a casual player (my calc): V2 35 min, V3 44 min, V4 53 min, V5 63 min, Station
  4 min. That is 3.3 h after the Lodge, about 3.7 h in all. Median wait between two purchases
  is 0.5 / 1.2 / 1.4 / 2.0 min by valley, and the longest single wait is 4.5 min (Lighthouse,
  Observatory).

Apply: paste section 3 into `scripts/Balance.gd`. Valleys 4-5 and the Station live only in
`unlocks_regions.csv` (already updated), because they are not built yet.

| Casual player (my calc) | V2 | V3 | V4 | V5 | Station | After the Lodge |
|---|---:|---:|---:|---:|---:|---:|
| Old prices, measured income | 120 min | 254 min | 339 min | 416 min | 60 min | 19.8 h |
| New prices | 35 min | 44 min | 53 min | 63 min | 4 min | 3.3 h |
| Old longest wait | 9.0 min | 20.3 min | 27.6 min | 40.2 min | 60 min | |
| New longest wait | 2.7 min | 3.9 min | 4.5 min | 4.5 min | 4.3 min | |

---

## 1. Measured income (headless probe, 2026-10-01)

How it was measured: `econ_probe.gd` (section 7) loads a save that owns a prefix of the pad
list, parks the player at the valley's handcar stop, and runs Godot 4.6.2 headless at
`--fixed-fps 60`: a 120 s warm-up, then a 180 s window. Income = coins collected plus coins
waiting at each till, per valley. Global upgrades are at max and region upgrades at 0 unless
noted. Houses owned in the prefix were pre-filled, so their rent is on. The probe ran against
a copy of `scripts/` taken at 13:00 today, including the M2 work in progress. It measures only
automation, no hand work.

| Setup | Valley 1 $/s | Valley 2 $/s | Valley 3 $/s |
|---|---:|---:|---:|
| V1 complete, global upgrades 0 | 28.9 | | |
| V1 complete, capture-bot levels (backpack 4, rest 3) | 66.9 | | |
| V1 complete, max (mean of the 29 runs below, 92.6-97.2) | 95.1 | | |
| V2 up to lathe (2 pads) | 95.9 | 0 | |
| V2 up to hauler1 (6) | 96.0 | 22.4 (waits at till) | |
| V2 up to cashier (8) | 93.6 | 22.3 | |
| V2 up to press (9) | 96.2 | 22.1 | |
| V2 up to hauler2 (12) | 93.4 | 72.7 | |
| V2 up to press2 (13) | 94.5 | 78.6 | |
| V2 up to barge (15) | 94.4 | 83.0 | |
| V2 up to belt_bb (17) | 93.5 | 141.0 | |
| V2 up to jack3 (18) | 93.6 | 140.4 | |
| V2 complete (19) | 96.4 | 139.4 | |
| V2 complete, Sharp Saws 5 | 96.1 | 186.2 | |
| V2 complete, Crew Coffee 5 | 95.6 | 152.6 | |
| V2 complete, Local Fame 5 | 96.9 | 208.1 | |
| V2 complete, all three at 3 | 92.6 | 214.5 | |
| V2 complete, all three at 5 | 96.5 | 280.8 | |
| V3 up to beamsaw (2) | 94.1 | asleep | 0 |
| V3 up to forklift1 (6) | 95.6 | asleep | 142.3 (waits at till) |
| V3 up to cashier (7) | 95.9 | asleep | 142.5 |
| V3 up to planer (8) | 93.3 | asleep | 143.3 |
| V3 up to jack2 (9) | 97.2 | asleep | **90.0** |
| V3 up to house1 (10) | 96.1 | asleep | 104.7 |
| V3 up to belt_bp (11) | 95.3 | asleep | 208.2 |
| V3 up to kitfactory (12) | 92.7 | asleep | 214.0 |
| V3 up to rail (14) | 94.6 | asleep | 224.7 |
| V3 up to belt_kit (15) | 96.1 | asleep | 361.2 |
| V3 up to jack3 (17) | 95.3 | asleep | 363.3 |
| V3 up to rail2 (18) | 94.9 | asleep | 421.9 |
| V3 up to house5 (20) | 96.3 | asleep | 457.6 |
| V3 complete, all three region upgrades at 3 | 94.9 | asleep | 741.6 |

Region upgrade effect per level, fitted on Valley 2 (my calc): Sharp Saws +6%, Crew Coffee
+1.5%, Local Fame +9%, multiplied together. The fit gives 219 at 3/3/3 (215 measured) and 284
at 5/5/5 (281 measured). The Valley 3 run at 3/3/3 agrees: 742 = 458 x 1.62.

Why the old prices broke: the old model gave each pad an estimated income, and those
estimates ran about 1.6x high in Valley 1 (150 vs 95 $/s) and grew 2.5-3x per valley.
Measured, Valley 2 adds 140 $/s and Valley 3 adds 460 $/s. The old prices grew about 8x per
valley.

## 2. Method and assumptions (all my calc)

- Start: the moment the Lodge is paid, with $0. Valley 1 earns 66.9 $/s (capture-bot
  levels). The player buys the rest of the Valley 1 office (about $7.2K) early in Valley 2,
  which lifts Valley 1 to 95 $/s. They buy the ext. levels (Riverside Office, `GLOBAL_EXT`,
  unchanged) once that office is owned.
- **Casual player**: does half the hand work and needs 10 s to walk to each pad. The
  attentive player does full hand work and needs 4 s. Hand income is my estimate, about 30% of
  the first machine's $/s at max upgrades: V2 30, V3 44, V4 95, V5 115 $/s for an attentive
  player. It fades as carriers and belts take over (see the comments in
  `rebalance_sim.py`).
- **Upgrades**: the player buys the cheapest region upgrade or leftover global level as soon
  as it costs at most 45% of the next pad. A region board opens with that valley's office.
- **Sleeping valleys** pay their measured awake rate (the ledger), so the income of every
  finished valley adds up.
- **Valleys 4-5 are modeled**: the old CSV income weights, scaled so V4 adds 2.2x what V3
  added and V5 adds 2.0x what V4 added. When they are built, re-measure them with the probe
  and re-run the sim. Only the V4/V5 numbers will move.
- Pad cost = income when the player reaches the pad x target wait, rounded to 2 significant
  figures. Target wait = (a 1.0 to 2.0 min ramp across the valley) x pad weight (gate 0.75,
  first machine 0.85, grove/office 0.6, landmark 1.9) x valley scale, capped at 4.5 min.
  Bisection finds the valley scale that gives a casual player V2 35, V3 44, V4 53 and V5 63
  min, and 4.5 min for the Station.
- Region upgrade base = gateway cost x 0.8 for saws, 0.5 for crew and 1.2 for fame. Growth
  1.8 and max 5 are unchanged. Crew Coffee is now the cheapest, because it does the least
  (+1.5% per level).

## 3. Paste-ready for `scripts/Balance.gd`

Only `cost` changes in these rows. Positions, reqs and titles are copied from the live file
as of today. If a position has moved since, change only the cost numbers.

```gdscript
# region upgrades: base cost per valley, growth 1.8, max 5 (rebalance 2026-10-01)
const REGION_UPGRADES := {
	2: {"saws": 2200, "crew": 1400, "fame": 3400},
	3: {"saws": 13000, "crew": 8000, "fame": 19000},
	4: {"saws": 51000, "crew": 32000, "fame": 77000},
	5: {"saws": 180000, "crew": 120000, "fame": 280000},
}
const REGION_UPGRADE_GROWTH := 1.8   # unchanged
const REGION_UPGRADE_MAX := 5        # unchanged
```

UNLOCKS rows for Valleys 2 and 3 (they replace the existing r2_ and r3_ rows):

```gdscript
	# ---- Valley 2: Birch Bend (unlocks_regions.csv). Bridge pad moved from the river (-27) to the V1 bank.
	{"id": "r2_bridge", "cost": 2800, "req": ["lodge"], "title": "River Bridge to Birch Bend", "pad": Vector3(-20.5, 0, -6)},
	{"id": "r2_lathe", "cost": 3600, "req": ["r2_bridge"], "title": "Veneer Lathe", "pad": Vector3(-45, 0, -6)},
	{"id": "r2_grove2", "cost": 3200, "req": ["r2_lathe"], "title": "More Birches", "pad": Vector3(-55, 0, 6)},
	{"id": "r2_office", "cost": 3400, "req": ["r2_lathe"], "title": "Riverside Office", "pad": Vector3(-34, 0, 11)},
	{"id": "r2_jack1", "cost": 4700, "req": ["r2_grove2"], "title": "Hire a Birch Lumberjack", "pad": Vector3(-50, 0, 2)},
	{"id": "r2_hauler1", "cost": 5400, "req": ["r2_jack1"], "title": "Hire a Veneer Carrier", "pad": Vector3(-40, 0, -2)},
	{"id": "r2_flume", "cost": 6000, "req": ["r2_jack1"], "title": "Log Flume", "pad": Vector3(-60, 0, -22)},
	{"id": "r2_cashier", "cost": 6400, "req": ["r2_hauler1"], "title": "Riverside Cashier", "pad": Vector3(-35, 0, 0)},
	{"id": "r2_press", "cost": 8700, "req": ["r2_hauler1"], "title": "Plywood Press", "pad": Vector3(-45, 0, -18)},
	{"id": "r2_jack2", "cost": 9500, "req": ["r2_flume"], "title": "Hire 2 Flume Lumberjacks", "pad": Vector3(-56, 0, -26)},
	{"id": "r2_belt_lp", "cost": 11000, "req": ["r2_press"], "title": "Conveyor: Lathe to Press", "pad": Vector3(-42, 0, -12)},
	{"id": "r2_hauler2", "cost": 13000, "req": ["r2_press"], "title": "Hire a Plywood Carrier", "pad": Vector3(-38.5, 0, -14.5)},
	{"id": "r2_press2", "cost": 17000, "req": ["r2_belt_lp"], "title": "Second Plywood Press", "pad": Vector3(-45, 0, -28)},
	{"id": "r2_boatshop", "cost": 19000, "req": ["r2_press2"], "title": "Boat Workshop: Canoes", "pad": Vector3(-40, 0, -38)},
	{"id": "r2_barge", "cost": 21000, "req": ["r2_boatshop"], "title": "Barge Landing", "pad": Vector3(-33, 0, -36)},
	{"id": "r2_belt_pb", "cost": 23000, "req": ["r2_barge"], "title": "Conveyor: Presses to Boat Workshop", "pad": Vector3(-43, 0, -33)},
	{"id": "r2_belt_bb", "cost": 30000, "req": ["r2_barge"], "title": "Conveyor: Boat Workshop to Barge", "pad": Vector3(-35, 0, -41.5)},
	{"id": "r2_jack3", "cost": 37000, "req": ["r2_belt_pb"], "title": "Forester Camp: West Grove + 2 Lumberjacks", "pad": Vector3(-68, 0, -14)},
	{"id": "r2_boathouse", "cost": 63000, "req": ["r2_belt_bb", "r2_jack3"], "title": "Build the Boathouse", "pad": Vector3(-68, 0, 8)},
	# ---- Valley 3: Maple Highlands (unlocks_regions.csv). Gate pad on the Home Valley side, like the bridge.
	{"id": "r3_gate", "cost": 16000, "req": ["r2_boathouse"], "title": "Highland Gate", "pad": Vector3(0, 0, -42.4)},
	{"id": "r3_beamsaw", "cost": 20000, "req": ["r3_gate"], "title": "Beam Saw", "pad": Vector3(2.5, 0, -64.5)},
	{"id": "r3_grove2", "cost": 16000, "req": ["r3_beamsaw"], "title": "More Maples", "pad": Vector3(-8, 0, -72)},
	{"id": "r3_office", "cost": 17000, "req": ["r3_beamsaw"], "title": "Highland Office", "pad": Vector3(6.5, 0, -59.5)},
	{"id": "r3_jack1", "cost": 23000, "req": ["r3_grove2"], "title": "Hire a Maple Lumberjack", "pad": Vector3(-2.0, 0, -61.2)},
	{"id": "r3_forklift1", "cost": 28000, "req": ["r3_jack1"], "title": "Hire a Forklift: Beams", "pad": Vector3(6, 0, -69)},
	{"id": "r3_cashier", "cost": 37000, "req": ["r3_forklift1"], "title": "Builders' Yard Cashier", "pad": Vector3(12, 0, -58)},
	{"id": "r3_planer", "cost": 42000, "req": ["r3_forklift1"], "title": "Planer Mill: Floorboards", "pad": Vector3(2.5, 0, -78)},
	{"id": "r3_jack2", "cost": 46000, "req": ["r3_planer"], "title": "Hire 2 Lumberjacks + North Maples", "pad": Vector3(-8, 0, -96)},
	{"id": "r3_house1", "cost": 42000, "req": ["r3_planer"], "title": "Village Plot 1: Cottage", "pad": Vector3(-17, 0, -62)},
	{"id": "r3_belt_bp", "cost": 45000, "req": ["r3_house1"], "title": "Conveyor: Beam Saw + Planer to Yard", "pad": Vector3(8, 0, -72)},
	{"id": "r3_kitfactory", "cost": 63000, "req": ["r3_belt_bp"], "title": "Cabin Kit Factory", "pad": Vector3(6, 0, -90)},
	{"id": "r3_house2", "cost": 63000, "req": ["r3_kitfactory"], "title": "Village Plot 2: Farmhouse", "pad": Vector3(-17, 0, -70)},
	{"id": "r3_rail", "cost": 72000, "req": ["r3_kitfactory"], "title": "Highland Railway", "pad": Vector3(13, 0, -100)},
	{"id": "r3_belt_kit", "cost": 75000, "req": ["r3_rail"], "title": "Conveyors: Kit Factory Feed + Rail", "pad": Vector3(9, 0, -94)},
	{"id": "r3_house3", "cost": 100000, "req": ["r3_belt_kit"], "title": "Village Plot 3: Barn", "pad": Vector3(-17, 0, -78)},
	{"id": "r3_jack3", "cost": 110000, "req": ["r3_belt_kit"], "title": "Hire 3 Lumberjacks + Ridge Maples", "pad": Vector3(-4, 0, -110)},
	{"id": "r3_rail2", "cost": 120000, "req": ["r3_jack3"], "title": "Longer Train", "pad": Vector3(15, 0, -102)},
	{"id": "r3_house4", "cost": 140000, "req": ["r3_rail2"], "title": "Village Plot 4: School", "pad": Vector3(-17, 0, -86)},
	{"id": "r3_house5", "cost": 150000, "req": ["r3_house4"], "title": "Village Plot 5: Inn", "pad": Vector3(-17, 0, -94)},
	{"id": "r3_clocktower", "cost": 280000, "req": ["r3_house5"], "title": "Build the Clock Tower", "pad": Vector3(-10, 0, -112)},
```

Gateway prices (the pads named in `GATEWAYS`; the price lives in the UNLOCKS row):

| Gateway | Old | New | Time to afford after the landmark, casual (my calc) |
|---|---:|---:|---|
| r2_bridge | 11,000 | 2,800 | 2.1 min, because the player first buys about $7.2K of leftover Valley 1 office upgrades. The bridge alone takes 30 s at 95 $/s, 42 s at 67 $/s and 97 s with no upgrades. |
| r3_gate | 82,000 | 16,000 | 0.7 min |
| r4_crossing | 270,000 | 64,000 | 0.9 min |
| r5_cablecar | 850,000 | 230,000 | 1.3 min |

First machine after the gateway: lathe 0.9 min, beam saw 0.9 min, redwood mill 1.1 min,
kiln 1.6 min (casual, my calc).

Not built yet (CSV only, provisional until measured):

```
V4: r4_crossing 64,000, r4_redmill 76,000, r4_grove2 60,000, r4_office 63,000, r4_jack1 88,000, r4_skidder1 100,000, r4_harbor 110,000, r4_cashier 120,000, r4_decksaw 140,000, r4_jack2 150,000, r4_belt_rd 160,000, r4_forklift 180,000, r4_mastlathe 200,000, r4_slipway 230,000, r4_orders 250,000, r4_skidder2 280,000, r4_builders 300,000, r4_belt_ds 360,000, r4_jack3 390,000, r4_slipway2 440,000, r4_lighthouse 800,000
V5: r5_cablecar 230,000, r5_kiln 280,000, r5_grove2 210,000, r5_office 220,000, r5_jack1 310,000, r5_skilodge 360,000, r5_skiworks 410,000, r5_cashier 440,000, r5_jack2 520,000, r5_kiln2 560,000, r5_belt_ks 610,000, r5_sledshop 700,000, r5_snowcat 760,000, r5_luthier 870,000, r5_express_r5 950,000, r5_belt_sl 1,100,000, r5_jack3 1,200,000, r5_kiln3 1,400,000, r5_observatory 1,600,000
V6: cap_station 1,500,000
```

**Unchanged:** every Valley 1 row, `UPGRADES`, `UPGRADE_GROWTH`, `GLOBAL_EXT`, `PRICES`,
`MACHINES`, `RENT_PER_HOUSE`, `SHIP_REWARD`, `ORDER`, `EXPORTS`. This pass changes costs only.
Section 5 lists rate problems the probe found; this pass does not fix them.

## 4. Before / after (all pads after Valley 1)

| Valley | id | Old | New | New/old |
|---|---|---:|---:|---:|
| 2 | r2_bridge | 11,000 | 2,800 | 0.25 |
| 2 | r2_lathe | 13,000 | 3,600 | 0.28 |
| 2 | r2_grove2 | 6,700 | 3,200 | 0.48 |
| 2 | r2_office | 8,000 | 3,400 | 0.42 |
| 2 | r2_jack1 | 13,000 | 4,700 | 0.36 |
| 2 | r2_hauler1 | 16,000 | 5,400 | 0.34 |
| 2 | r2_flume | 21,000 | 6,000 | 0.29 |
| 2 | r2_cashier | 19,000 | 6,400 | 0.34 |
| 2 | r2_press | 33,000 | 8,700 | 0.26 |
| 2 | r2_jack2 | 40,000 | 9,500 | 0.24 |
| 2 | r2_belt_lp | 45,000 | 11,000 | 0.24 |
| 2 | r2_hauler2 | 51,000 | 13,000 | 0.25 |
| 2 | r2_press2 | 74,000 | 17,000 | 0.23 |
| 2 | r2_boatshop | 94,000 | 19,000 | 0.20 |
| 2 | r2_barge | 110,000 | 21,000 | 0.19 |
| 2 | r2_belt_pb | 120,000 | 23,000 | 0.19 |
| 2 | r2_belt_bb | 130,000 | 30,000 | 0.23 |
| 2 | r2_jack3 | 150,000 | 37,000 | 0.25 |
| 2 | r2_boathouse | 210,000 | 63,000 | 0.30 |
| **2** | **total** | **1,164,700** | **287,700** | **0.25** |
| 3 | r3_gate | 82,000 | 16,000 | 0.20 |
| 3 | r3_beamsaw | 99,000 | 20,000 | 0.20 |
| 3 | r3_grove2 | 49,000 | 16,000 | 0.33 |
| 3 | r3_office | 66,000 | 17,000 | 0.26 |
| 3 | r3_jack1 | 99,000 | 23,000 | 0.23 |
| 3 | r3_forklift1 | 130,000 | 28,000 | 0.22 |
| 3 | r3_cashier | 130,000 | 37,000 | 0.28 |
| 3 | r3_planer | 230,000 | 42,000 | 0.18 |
| 3 | r3_jack2 | 260,000 | 46,000 | 0.18 |
| 3 | r3_house1 | 250,000 | 42,000 | 0.17 |
| 3 | r3_belt_bp | 330,000 | 45,000 | 0.14 |
| 3 | r3_kitfactory | 490,000 | 63,000 | 0.13 |
| 3 | r3_house2 | 370,000 | 63,000 | 0.17 |
| 3 | r3_rail | 660,000 | 72,000 | 0.11 |
| 3 | r3_belt_kit | 700,000 | 75,000 | 0.11 |
| 3 | r3_house3 | 490,000 | 100,000 | 0.20 |
| 3 | r3_jack3 | 780,000 | 110,000 | 0.14 |
| 3 | r3_rail2 | 900,000 | 120,000 | 0.13 |
| 3 | r3_house4 | 660,000 | 140,000 | 0.21 |
| 3 | r3_house5 | 820,000 | 150,000 | 0.18 |
| 3 | r3_clocktower | 1,500,000 | 280,000 | 0.19 |
| **3** | **total** | **9,095,000** | **1,505,000** | **0.17** |
| 4 | r4_crossing | 270,000 | 64,000 | 0.24 |
| 4 | r4_redmill | 370,000 | 76,000 | 0.21 |
| 4 | r4_grove2 | 160,000 | 60,000 | 0.38 |
| 4 | r4_office | 210,000 | 63,000 | 0.30 |
| 4 | r4_jack1 | 320,000 | 88,000 | 0.28 |
| 4 | r4_skidder1 | 480,000 | 100,000 | 0.21 |
| 4 | r4_harbor | 530,000 | 110,000 | 0.21 |
| 4 | r4_cashier | 430,000 | 120,000 | 0.28 |
| 4 | r4_decksaw | 800,000 | 140,000 | 0.17 |
| 4 | r4_jack2 | 930,000 | 150,000 | 0.16 |
| 4 | r4_belt_rd | 1,100,000 | 160,000 | 0.15 |
| 4 | r4_forklift | 1,200,000 | 180,000 | 0.15 |
| 4 | r4_mastlathe | 1,500,000 | 200,000 | 0.13 |
| 4 | r4_slipway | 2,100,000 | 230,000 | 0.11 |
| 4 | r4_orders | 1,600,000 | 250,000 | 0.16 |
| 4 | r4_skidder2 | 2,400,000 | 280,000 | 0.12 |
| 4 | r4_builders | 2,700,000 | 300,000 | 0.11 |
| 4 | r4_belt_ds | 2,900,000 | 360,000 | 0.12 |
| 4 | r4_jack3 | 3,200,000 | 390,000 | 0.12 |
| 4 | r4_slipway2 | 4,000,000 | 440,000 | 0.11 |
| 4 | r4_lighthouse | 5,300,000 | 800,000 | 0.15 |
| **4** | **total** | **32,500,000** | **4,561,000** | **0.14** |
| 5 | r5_cablecar | 850,000 | 230,000 | 0.27 |
| 5 | r5_kiln | 1,200,000 | 280,000 | 0.23 |
| 5 | r5_grove2 | 510,000 | 210,000 | 0.41 |
| 5 | r5_office | 680,000 | 220,000 | 0.32 |
| 5 | r5_jack1 | 1,000,000 | 310,000 | 0.31 |
| 5 | r5_skilodge | 1,400,000 | 360,000 | 0.26 |
| 5 | r5_skiworks | 1,900,000 | 410,000 | 0.22 |
| 5 | r5_cashier | 1,400,000 | 440,000 | 0.31 |
| 5 | r5_jack2 | 2,600,000 | 520,000 | 0.20 |
| 5 | r5_kiln2 | 3,400,000 | 560,000 | 0.16 |
| 5 | r5_belt_ks | 3,800,000 | 610,000 | 0.16 |
| 5 | r5_sledshop | 5,100,000 | 700,000 | 0.14 |
| 5 | r5_snowcat | 6,000,000 | 760,000 | 0.13 |
| 5 | r5_luthier | 7,300,000 | 870,000 | 0.12 |
| 5 | r5_express_r5 | 7,700,000 | 950,000 | 0.12 |
| 5 | r5_belt_sl | 8,500,000 | 1,100,000 | 0.13 |
| 5 | r5_jack3 | 9,400,000 | 1,200,000 | 0.13 |
| 5 | r5_kiln3 | 11,000,000 | 1,400,000 | 0.13 |
| 5 | r5_observatory | 17,000,000 | 1,600,000 | 0.09 |
| **5** | **total** | **90,740,000** | **12,730,000** | **0.14** |
| 6 | cap_station | 25,000,000 | 1,500,000 | 0.06 |
| **6** | **total** | **25,000,000** | **1,500,000** | **0.06** |

Smoothness at the seams:

| Seam | Last prices before it | First pads after it |
|---|---|---|
| Valley 1 to 2 | $1.3K-6K | $2.8K-4.7K |
| Valley 2 to 3 | Boathouse $63K | $16K-23K |
| Valley 3 to 4 | Clock Tower $280K | $60K-88K |
| Valley 4 to 5 | Lighthouse $800K | $210K-310K |

From Valley 3 on, each gateway costs 23-29% of the landmark before it (the bridge is 47% of the Lodge). Arriving in a new
valley feels like a step down in price, not a wall.

## 5. Found by the probe (for the builder; not changed here)

1. **Buying r3_jack2 (Hire 2 Lumberjacks + North Maples) drops income from 143 to 90 $/s**
   until the next belt pad (r3_belt_bp) is bought. The sim includes the dip. The likely cause:
   the single forklift now splits its trips between beams and floorboards. Options: make
   r3_jack2 require r3_belt_bp, or have the forklift favour the beam pile. **Ask Mats.**
2. **The Forester Camp (r2_jack3) adds nothing**: 140.4 vs 141.0 $/s. Birch Bend is
   machine-bound by then (Sharp Saws 5 lifts it to 186). The pad still costs $37K, about 1.7
   min of waiting. Options: keep it as a "more logs for after Sharp Saws" pad, or move it
   later in the order.
3. **Crew Coffee is weak**: +9% income at level 5 in Valley 2, against +33% for Sharp Saws
   and +49% for Local Fame. This pass makes it the cheapest of the three. A stronger effect
   (for example +3 carry per level) would need a code change.
4. **Valley 3 houses 3-5 and the Longer Train add little** while the forklift is the
   bottleneck: house3 and jack3 together add 2 $/s. Rent is paid, but the forklift spends
   trips on site goods.
5. The GDD claim "Valley 1 ends at about $150/s" was wrong. Measured: 29 $/s with no
   upgrades, 67 at the capture-bot levels, 95 at max. The GDD now says so.

## 6. Sim output (`python3 docs/balance/rebalance_sim.py`, all my calc)

"median wait" counts every purchase, pads and upgrades. "pad to pad" counts only pads. Its
maximum is always the stretch before a landmark, where the player buys 2-4 region upgrades on
the way. The longest single wait anywhere is 4.5 min.

```
--- casual player (hand x0.5, 10 s walk per buy)
V2:  35.0 min  cum 0.58 h  auto at end     363 $/s  buys 54  median wait 0.5 min (pad to pad 1.6, max 4.6)  max 2.7 min (r2_boathouse)  first: r2_bridge 2.1 + r2_lathe 0.9 min
V3:  43.9 min  cum 1.32 h  auto at end    1192 $/s  buys 34  median wait 1.2 min (pad to pad 1.8, max 7.8)  max 3.9 min (r3_clocktower)  first: r3_gate 0.7 + r3_beamsaw 0.9 min
V4:  53.0 min  cum 2.20 h  auto at end    2895 $/s  buys 33  median wait 1.4 min (pad to pad 2.0, max 9.7)  max 4.5 min (r4_lighthouse)  first: r4_crossing 0.9 + r4_redmill 1.1 min
V5:  63.0 min  cum 3.25 h  auto at end    5865 $/s  buys 28  median wait 2.0 min (pad to pad 3.1, max 6.5)  max 4.5 min (r5_observatory)  first: r5_cablecar 1.3 + r5_kiln 1.6 min
V6:   4.3 min  cum 3.32 h  auto at end    5865 $/s  buys  1  median wait 4.3 min (pad to pad 4.3, max 4.3)  max 4.3 min (cap_station)  first: cap_station 4.3 min
--- attentive player (hand x1.0, 4 s walk per buy)
V2:  30.9 min  cum 0.52 h  auto at end     363 $/s  buys 54  median wait 0.4 min (pad to pad 1.3, max 4.3)  max 2.5 min (r2_boathouse)  first: r2_bridge 1.9 + r2_lathe 0.9 min
V3:  42.8 min  cum 1.23 h  auto at end    1192 $/s  buys 34  median wait 1.2 min (pad to pad 1.8, max 7.7)  max 3.8 min (r3_clocktower)  first: r3_gate 0.7 + r3_beamsaw 0.9 min
V4:  50.9 min  cum 2.08 h  auto at end    2895 $/s  buys 33  median wait 1.3 min (pad to pad 1.9, max 9.5)  max 4.4 min (r4_lighthouse)  first: r4_crossing 0.9 + r4_redmill 1.1 min
V5:  61.5 min  cum 3.10 h  auto at end    5865 $/s  buys 28  median wait 1.9 min (pad to pad 3.0, max 6.4)  max 4.4 min (r5_observatory)  first: r5_cablecar 1.3 + r5_kiln 1.6 min
V6:   4.3 min  cum 3.17 h  auto at end    5865 $/s  buys  1  median wait 4.3 min (pad to pad 4.3, max 4.3)  max 4.3 min (cap_station)  first: cap_station 4.3 min
--- costs (id, old, new, new/old)
V2 total pads: old $1,164,700 -> new $287,700 (x0.25)  region upgrades base {'saws': 2200, 'crew': 1400, 'fame': 3400}
  r2_bridge            11,000      2,800  x0.25
  r2_lathe             13,000      3,600  x0.28
  r2_grove2             6,700      3,200  x0.48
  r2_office             8,000      3,400  x0.42
  r2_jack1             13,000      4,700  x0.36
  r2_hauler1           16,000      5,400  x0.34
  r2_flume             21,000      6,000  x0.29
  r2_cashier           19,000      6,400  x0.34
  r2_press             33,000      8,700  x0.26
  r2_jack2             40,000      9,500  x0.24
  r2_belt_lp           45,000     11,000  x0.24
  r2_hauler2           51,000     13,000  x0.25
  r2_press2            74,000     17,000  x0.23
  r2_boatshop          94,000     19,000  x0.20
  r2_barge            110,000     21,000  x0.19
  r2_belt_pb          120,000     23,000  x0.19
  r2_belt_bb          130,000     30,000  x0.23
  r2_jack3            150,000     37,000  x0.25
  r2_boathouse        210,000     63,000  x0.30
V3 total pads: old $9,095,000 -> new $1,505,000 (x0.17)  region upgrades base {'saws': 13000, 'crew': 8000, 'fame': 19000}
  r3_gate              82,000     16,000  x0.20
  r3_beamsaw           99,000     20,000  x0.20
  r3_grove2            49,000     16,000  x0.33
  r3_office            66,000     17,000  x0.26
  r3_jack1             99,000     23,000  x0.23
  r3_forklift1        130,000     28,000  x0.22
  r3_cashier          130,000     37,000  x0.28
  r3_planer           230,000     42,000  x0.18
  r3_jack2            260,000     46,000  x0.18
  r3_house1           250,000     42,000  x0.17
  r3_belt_bp          330,000     45,000  x0.14
  r3_kitfactory       490,000     63,000  x0.13
  r3_house2           370,000     63,000  x0.17
  r3_rail             660,000     72,000  x0.11
  r3_belt_kit         700,000     75,000  x0.11
  r3_house3           490,000    100,000  x0.20
  r3_jack3            780,000    110,000  x0.14
  r3_rail2            900,000    120,000  x0.13
  r3_house4           660,000    140,000  x0.21
  r3_house5           820,000    150,000  x0.18
  r3_clocktower     1,500,000    280,000  x0.19
V4 total pads: old $32,500,000 -> new $4,561,000 (x0.14)  region upgrades base {'saws': 51000, 'crew': 32000, 'fame': 77000}
  r4_crossing         270,000     64,000  x0.24
  r4_redmill          370,000     76,000  x0.21
  r4_grove2           160,000     60,000  x0.38
  r4_office           210,000     63,000  x0.30
  r4_jack1            320,000     88,000  x0.28
  r4_skidder1         480,000    100,000  x0.21
  r4_harbor           530,000    110,000  x0.21
  r4_cashier          430,000    120,000  x0.28
  r4_decksaw          800,000    140,000  x0.17
  r4_jack2            930,000    150,000  x0.16
  r4_belt_rd        1,100,000    160,000  x0.15
  r4_forklift       1,200,000    180,000  x0.15
  r4_mastlathe      1,500,000    200,000  x0.13
  r4_slipway        2,100,000    230,000  x0.11
  r4_orders         1,600,000    250,000  x0.16
  r4_skidder2       2,400,000    280,000  x0.12
  r4_builders       2,700,000    300,000  x0.11
  r4_belt_ds        2,900,000    360,000  x0.12
  r4_jack3          3,200,000    390,000  x0.12
  r4_slipway2       4,000,000    440,000  x0.11
  r4_lighthouse     5,300,000    800,000  x0.15
V5 total pads: old $90,740,000 -> new $12,730,000 (x0.14)  region upgrades base {'saws': 180000, 'crew': 120000, 'fame': 280000}
  r5_cablecar         850,000    230,000  x0.27
  r5_kiln           1,200,000    280,000  x0.23
  r5_grove2           510,000    210,000  x0.41
  r5_office           680,000    220,000  x0.32
  r5_jack1          1,000,000    310,000  x0.31
  r5_skilodge       1,400,000    360,000  x0.26
  r5_skiworks       1,900,000    410,000  x0.22
  r5_cashier        1,400,000    440,000  x0.31
  r5_jack2          2,600,000    520,000  x0.20
  r5_kiln2          3,400,000    560,000  x0.16
  r5_belt_ks        3,800,000    610,000  x0.16
  r5_sledshop       5,100,000    700,000  x0.14
  r5_snowcat        6,000,000    760,000  x0.13
  r5_luthier        7,300,000    870,000  x0.12
  r5_express_r5     7,700,000    950,000  x0.12
  r5_belt_sl        8,500,000  1,100,000  x0.13
  r5_jack3          9,400,000  1,200,000  x0.13
  r5_kiln3         11,000,000  1,400,000  x0.13
  r5_observatory   17,000,000  1,600,000  x0.09
V6 total pads: old $25,000,000 -> new $1,500,000 (x0.06)
  cap_station      25,000,000  1,500,000  x0.06
--- casual purchase log (min, valley, what, cost, wait min, $/s)
     0.2  V2  g_axe4                  188   0.2       67
     0.4  V2  g_shoes4                214   0.2       67
     0.5  V2  g_backpack5             276   0.2       67
     0.7  V2  g_axe5                  328   0.2       67
     0.9  V2  g_shoes5                375   0.2       67
     1.0  V2  g_machines4             482   0.2       67
     1.2  V2  g_backpack6             492   0.2       71
     1.4  V2  g_workers4              643   0.2       71
     1.5  V2  g_prices4               804   0.2       75
     1.7  V2  g_machines5             844   0.2       81
     1.9  V2  g_workers5            1,125   0.2       85
     2.1  V2  r2_bridge             2,800   0.3       89
     2.4  V2  g_prices5             1,407   0.3       89
     3.1  V2  r2_lathe              3,600   0.6       95
     3.6  V2  r2_grove2             3,200   0.5      113
     4.0  V2  r2_office             3,400   0.5      115
     4.3  V2  r2_crew1              1,400   0.2      115
     4.5  V2  x_axe6                2,000   0.3      115
     5.2  V2  r2_jack1              4,700   0.7      115
     5.5  V2  r2_saws1              2,200   0.3      118
     6.3  V2  r2_hauler1            5,400   0.8      118
     6.7  V2  r2_crew2              2,500   0.4      118
     7.0  V2  x_backpack7           2,500   0.4      118
     7.9  V2  r2_flume              6,000   0.8      119
     8.7  V2  r2_cashier            6,400   0.9      121
     9.1  V2  x_shoes6              3,000   0.4      140
     9.5  V2  r2_fame1              3,400   0.4      141
     9.9  V2  x_axe7                3,500   0.4      143
    10.9  V2  r2_press              8,700   1.0      144
    11.4  V2  r2_saws2              4,000   0.5      149
    12.4  V2  r2_jack2              9,500   1.1      151
    12.9  V2  x_backpack8           4,375   0.5      163
    13.4  V2  r2_crew3              4,500   0.5      165
    14.5  V2  r2_belt_lp           11,000   1.1      165
    15.0  V2  x_shoes7              5,250   0.5      184
    16.1  V2  r2_hauler2           13,000   1.2      185
    16.6  V2  r2_fame2              6,100   0.5      213
    17.1  V2  x_axe8                6,125   0.5      221
    17.6  V2  r2_saws3              7,100   0.5      222
    18.9  V2  r2_press2            17,000   1.2      227
    19.4  V2  x_backpack9           7,656   0.5      236
    20.0  V2  r2_crew4              8,200   0.6      237
    21.3  V2  r2_boatshop          19,000   1.3      239
    22.8  V2  r2_barge             21,000   1.4      247
    24.3  V2  r2_belt_pb           23,000   1.5      253
    24.9  V2  r2_fame3             11,000   0.6      292
    25.6  V2  r2_saws4             13,000   0.7      305
    26.4  V2  x_backpack10         13,398   0.7      314
    27.9  V2  r2_belt_bb           30,000   1.6      315
    28.7  V2  r2_crew5             15,000   0.7      359
    30.4  V2  r2_jack3             37,000   1.7      362
    31.3  V2  r2_fame4             20,000   0.9      362
    32.3  V2  r2_saws5             23,000   1.0      379
    35.0  V2  r2_boathouse         63,000   2.7      392
    35.7  V3  r3_gate              16,000   0.7      363
    36.6  V3  r3_beamsaw           20,000   0.9      363
    37.3  V3  r3_grove2            16,000   0.7      400
    38.0  V3  r3_office            17,000   0.7      404
    38.3  V3  r3_crew1              8,000   0.3      404
    39.3  V3  r3_jack1             23,000   0.9      404
    40.4  V3  r3_forklift1         28,000   1.1      438
    40.8  V3  r3_saws1             13,000   0.4      511
    41.3  V3  r3_crew2             14,000   0.5      519
    42.5  V3  r3_cashier           37,000   1.2      522
    43.8  V3  r3_planer            42,000   1.3      522
    44.4  V3  r3_fame1             19,000   0.6      531
    45.8  V3  r3_jack2             46,000   1.4      545
    47.2  V3  r3_house1            42,000   1.4      482
    48.7  V3  r3_belt_bp           45,000   1.5      499
    49.4  V3  r3_saws2             23,000   0.6      622
    50.1  V3  r3_crew3             26,000   0.7      636
    51.7  V3  r3_kitfactory        63,000   1.6      640
    53.3  V3  r3_house2            63,000   1.6      652
    55.2  V3  r3_rail              72,000   1.8      659
    57.0  V3  r3_belt_kit          75,000   1.9      665
    57.8  V3  r3_fame2             34,000   0.7      839
    58.6  V3  r3_saws3             42,000   0.8      877
    60.4  V3  r3_house3           100,000   1.8      904
    61.3  V3  r3_crew4             47,000   0.9      906
    63.3  V3  r3_jack3            110,000   2.0      913
    65.5  V3  r3_rail2            120,000   2.2      915
    66.5  V3  r3_fame3             62,000   1.0     1001
    68.7  V3  r3_house4           140,000   2.2     1049
    71.1  V3  r3_house5           150,000   2.3     1077
    72.2  V3  r3_saws4             76,000   1.2     1105
    73.4  V3  r3_crew5             84,000   1.2     1142
    75.0  V3  r3_fame4            110,000   1.6     1153
    78.9  V3  r3_clocktower       280,000   3.9     1208
    79.8  V4  r4_crossing          64,000   0.9     1192
    80.9  V4  r4_redmill           76,000   1.1     1192
    81.7  V4  r4_grove2            60,000   0.8     1273
    82.5  V4  r4_office            63,000   0.8     1278
    82.9  V4  r4_crew1             32,000   0.4     1278
    84.1  V4  r4_jack1             88,000   1.1     1278
    85.3  V4  r4_skidder1         100,000   1.3     1311
    86.7  V4  r4_harbor           110,000   1.4     1361
    87.3  V4  r4_saws1             51,000   0.6     1395
    88.7  V4  r4_cashier          120,000   1.4     1402
    89.4  V4  r4_crew2             58,000   0.7     1403
    91.1  V4  r4_decksaw          140,000   1.7     1405
    92.8  V4  r4_jack2            150,000   1.7     1458
    94.6  V4  r4_belt_rd          160,000   1.8     1521
    95.4  V4  r4_fame1             77,000   0.8     1584
    97.2  V4  r4_forklift         180,000   1.9     1611
    99.3  V4  r4_mastlathe        200,000   2.0     1653
   100.2  V4  r4_saws2             92,000   0.9     1711
   101.1  V4  r4_crew3            100,000   1.0     1736
   103.3  V4  r4_slipway          230,000   2.2     1743
   105.6  V4  r4_orders           250,000   2.2     1869
   108.0  V4  r4_skidder2         280,000   2.4     1953
   110.4  V4  r4_builders         300,000   2.4     2058
   111.5  V4  r4_fame2            140,000   1.1     2176
   114.1  V4  r4_belt_ds          360,000   2.7     2252
   115.4  V4  r4_saws3            170,000   1.2     2365
   118.0  V4  r4_jack3            390,000   2.7     2425
   119.3  V4  r4_crew4            190,000   1.3     2533
   122.2  V4  r4_slipway2         440,000   2.9     2551
   123.7  V4  r4_fame3            250,000   1.5     2746
   125.5  V4  r4_saws4            300,000   1.8     2859
   127.4  V4  r4_crew5            340,000   1.9     2940
   131.9  V4  r4_lighthouse       800,000   4.5     2964
   133.2  V5  r5_cablecar         230,000   1.3     2895
   134.8  V5  r5_kiln             280,000   1.6     2895
   136.0  V5  r5_grove2           210,000   1.2     2993
   137.2  V5  r5_office           220,000   1.2     3000
   137.9  V5  r5_crew1            120,000   0.7     3000
   139.6  V5  r5_jack1            310,000   1.7     3000
   141.6  V5  r5_skilodge         360,000   1.9     3089
   142.5  V5  r5_saws1            180,000   0.9     3188
   144.6  V5  r5_skiworks         410,000   2.1     3199
   146.9  V5  r5_cashier          440,000   2.2     3300
   148.0  V5  r5_crew2            220,000   1.1     3332
   150.6  V5  r5_jack2            520,000   2.6     3337
   153.2  V5  r5_kiln2            560,000   2.7     3507
   156.0  V5  r5_belt_ks          610,000   2.8     3657
   157.3  V5  r5_fame1            280,000   1.2     3806
   160.3  V5  r5_sledshop         700,000   3.0     3879
   161.6  V5  r5_saws2            320,000   1.3     4027
   164.7  V5  r5_snowcat          760,000   3.1     4085
   166.2  V5  r5_crew3            390,000   1.5     4289
   169.6  V5  r5_luthier          870,000   3.4     4308
   173.1  V5  r5_express_r5       950,000   3.5     4516
   176.9  V5  r5_belt_sl        1,100,000   3.8     4815
   178.6  V5  r5_fame2            500,000   1.7     5030
   182.4  V5  r5_jack3          1,200,000   3.9     5199
   184.2  V5  r5_saws3            580,000   1.8     5442
   188.4  V5  r5_kiln3          1,400,000   4.2     5574
   190.4  V5  r5_crew4            700,000   2.0     5915
   194.9  V5  r5_observatory    1,600,000   4.5     5957
   199.1  V6  cap_station       1,500,000   4.3     5865
```

## 7. How to re-measure

Copy the project to a scratch folder. The probe writes `user://save.json`, so give the copy
its own `config/custom_user_dir_name`. Add the two files below to the copy as
`tests/econ_probe.gd` and `tests/econ_probe.tscn`, then run, for example:

```
PROBE_REGION=2 PROBE_N=19 PROBE_LV=max PROBE_RUP=0,0,5 PROBE_WARM=120 PROBE_WIN=180 \
  ~/MWM/data/tools/godot/godot --headless --fixed-fps 60 --audio-driver Dummy --path . res://tests/econ_probe.tscn
```

One run covers 300 s of game time and takes about 15 min of wall time on this box. Six can
run in parallel. Put the new $/s values in `R2`/`R3` (or `R4_W`/`R5_W`) in
`rebalance_sim.py` and re-run it.

```gdscript
extends Node
## Scratch-only economy probe: loads a save with a prefix of pads owned, parks the player,
## and measures automated income per valley ($/s) over a window. Env:
## PROBE_REGION (1/2/3) PROBE_N (number of that region's pads owned, in UNLOCKS order)
## PROBE_LV ("cap" or "max") PROBE_WARM, PROBE_WIN (s)
var world: World

func _ready() -> void:
	var region := int(OS.get_environment("PROBE_REGION"))
	var n := int(OS.get_environment("PROBE_N"))
	var lvmode := OS.get_environment("PROBE_LV")
	var warm := float(OS.get_environment("PROBE_WARM")) if OS.get_environment("PROBE_WARM") != "" else 90.0
	var win := float(OS.get_environment("PROBE_WIN")) if OS.get_environment("PROBE_WIN") != "" else 180.0
	var ids := []
	var reg_ids := []
	for u in World.UNLOCKS:
		var id: String = u.id
		var r := 1
		if id.begins_with("r2_"): r = 2
		elif id.begins_with("r3_"): r = 3
		if r < region: ids.append(id)
		elif r == region: reg_ids.append(id)
	for i in mini(n, reg_ids.size()):
		ids.append(reg_ids[i])
	var ups := {"capacity": 4, "speed": 3, "axe": 3, "machines": 3, "workers": 3, "prices": 3}
	if lvmode == "max":
		ups = {"capacity": 6, "speed": 5, "axe": 5, "machines": 5, "workers": 5, "prices": 5}
	if lvmode == "zero":
		ups = {"capacity": 0, "speed": 0, "axe": 0, "machines": 0, "workers": 0, "prices": 0}
	var sites := {}
	for sid in Balance.BUILD_SITES:
		if sid in ids and sid != "r3_clocktower":
			sites[sid] = Balance.BUILD_SITES[sid].goods.duplicate()
	Game.apply_save({"version": 3, "money": 0, "total_earned": 0, "unlocked": ids,
		"upgrades": ups, "region_upgrades": _rup(region), "ledger": {}, "region_stats": {}, "sites": sites,
		"piles": {}, "finished": true, "sound_on": false})
	Game.sound_on = false
	var main: Node = load("res://scenes/Main.tscn").instantiate()
	add_child(main)
	world = main.get_node("World")
	await _frames(5)
	var stop: Dictionary = Balance.HANDCAR_STOPS[maxi(region, 1)]
	world.player.global_position = stop.land
	var t := 0.0
	while t < warm:
		await get_tree().process_frame
		t += get_process_delta_time()
	var e0 := _snap()
	var g0 := Game.total_earned
	t = 0.0
	while t < win:
		await get_tree().process_frame
		t += get_process_delta_time()
	var e1 := _snap()
	var out := []
	for r in [1, 2, 3]:
		out.append("r%d=%.2f" % [r, (e1[r] - e0[r]) / win])
	print("PROBE rup=%s region=%d n=%d lv=%s last=%s %s total=%.2f awake=%s" % [OS.get_environment("PROBE_RUP"), region, n, lvmode,
		(reg_ids[mini(n, reg_ids.size()) - 1] if n > 0 else "-"), " ".join(out), float(Game.total_earned - g0) / win,
		str([world.r1.awake, world.r2.awake, world.r3.awake])])
	get_tree().quit()

func _snap() -> Dictionary:
	var d := {}
	for r in [1, 2, 3]:
		d[r] = float(Game.stats(r).get("earned", 0))
	if world.shop: d[1] += world.shop.coin_value
	if world.shop2: d[2] += world.shop2.coin_value
	if world.shop3: d[3] += world.shop3.coin_value
	return d

func _frames(k: int) -> void:
	for i in k:
		await get_tree().process_frame

func _rup(region: int) -> Dictionary:
	var e := OS.get_environment("PROBE_RUP")  # "saws,crew,fame" levels for the probed region
	if e == "":
		return {}
	var p := e.split(",")
	return {str(region): {"saws": int(p[0]), "crew": int(p[1]), "fame": int(p[2])}}
```

`econ_probe.tscn`:

```
[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://tests/econ_probe.gd" id="1"]

[node name="EconProbe" type="Node"]
script = ExtResource("1")
```

Raw probe lines:

```
PROBE region=2 n=2 lv=max last=r2_lathe r1=96.03 r2=0.00 r3=0.00 total=95.94 awake=[true, true, false]
PROBE region=2 n=6 lv=max last=r2_hauler1 r1=96.03 r2=22.40 r3=0.00 total=96.03 awake=[true, true, false]
PROBE region=2 n=8 lv=max last=r2_cashier r1=93.56 r2=22.27 r3=0.00 total=115.42 awake=[true, true, false]
PROBE region=2 n=9 lv=max last=r2_press r1=96.15 r2=22.13 r3=0.00 total=118.25 awake=[true, true, false]
PROBE region=2 n=12 lv=max last=r2_hauler2 r1=93.40 r2=72.67 r3=0.00 total=169.84 awake=[true, true, false]
PROBE region=2 n=13 lv=max last=r2_press2 r1=94.49 r2=78.60 r3=0.00 total=173.33 awake=[true, true, false]
PROBE region=2 n=17 lv=max last=r2_belt_bb r1=93.51 r2=141.03 r3=0.00 total=234.43 awake=[true, true, false]
PROBE region=2 n=18 lv=max last=r2_jack3 r1=93.61 r2=140.37 r3=0.00 total=233.89 awake=[true, true, false]
PROBE region=2 n=15 lv=max last=r2_barge r1=94.37 r2=83.00 r3=0.00 total=176.73 awake=[true, true, false]
PROBE region=2 n=19 lv=max last=r2_boathouse r1=96.41 r2=139.37 r3=0.00 total=235.81 awake=[true, true, false]
PROBE rup= region=1 n=25 lv=zero last=lodge r1=28.88 r2=0.00 r3=0.00 total=28.88 awake=[true, false, false]
PROBE rup= region=1 n=25 lv=cap last=lodge r1=66.70 r2=0.00 r3=0.00 total=66.93 awake=[true, false, false]
PROBE rup=3,3,3 region=2 n=19 lv=max last=r2_boathouse r1=92.62 r2=214.50 r3=0.00 total=307.23 awake=[true, true, false]
PROBE rup=5,0,0 region=2 n=19 lv=max last=r2_boathouse r1=96.06 r2=186.20 r3=0.00 total=282.96 awake=[true, true, false]
PROBE rup=0,0,5 region=2 n=19 lv=max last=r2_boathouse r1=96.85 r2=208.05 r3=0.00 total=304.68 awake=[true, true, false]
PROBE rup=0,5,0 region=2 n=19 lv=max last=r2_boathouse r1=95.61 r2=152.57 r3=0.00 total=248.71 awake=[true, true, false]
PROBE rup= region=3 n=2 lv=max last=r3_beamsaw r1=94.08 r2=0.00 r3=0.00 total=94.24 awake=[true, false, true]
PROBE rup=5,5,5 region=2 n=19 lv=max last=r2_boathouse r1=96.49 r2=280.80 r3=0.00 total=377.09 awake=[true, true, false]
PROBE rup= region=3 n=6 lv=max last=r3_forklift1 r1=95.56 r2=0.00 r3=142.25 total=95.73 awake=[true, false, true]
PROBE rup= region=3 n=7 lv=max last=r3_cashier r1=95.94 r2=0.00 r3=142.50 total=238.47 awake=[true, false, true]
PROBE rup= region=3 n=8 lv=max last=r3_planer r1=93.28 r2=0.00 r3=143.25 total=235.87 awake=[true, false, true]
PROBE rup= region=3 n=9 lv=max last=r3_jack2 r1=97.21 r2=0.00 r3=89.95 total=187.19 awake=[true, false, true]
PROBE rup= region=3 n=10 lv=max last=r3_house1 r1=96.06 r2=0.00 r3=104.70 total=200.76 awake=[true, false, true]
PROBE rup= region=3 n=11 lv=max last=r3_belt_bp r1=95.33 r2=0.00 r3=208.15 total=304.44 awake=[true, false, true]
PROBE rup= region=3 n=12 lv=max last=r3_kitfactory r1=92.67 r2=0.00 r3=213.95 total=305.07 awake=[true, false, true]
PROBE rup= region=3 n=14 lv=max last=r3_rail r1=94.56 r2=0.00 r3=224.65 total=318.54 awake=[true, false, true]
PROBE rup= region=3 n=15 lv=max last=r3_belt_kit r1=96.11 r2=0.00 r3=361.20 total=457.46 awake=[true, false, true]
PROBE rup= region=3 n=17 lv=max last=r3_jack3 r1=95.32 r2=0.00 r3=363.30 total=458.12 awake=[true, false, true]
PROBE rup= region=3 n=18 lv=max last=r3_rail2 r1=94.94 r2=0.00 r3=421.87 total=516.18 awake=[true, false, true]
PROBE rup= region=3 n=20 lv=max last=r3_house5 r1=96.33 r2=0.00 r3=457.57 total=553.78 awake=[true, false, true]
PROBE rup=3,3,3 region=3 n=21 lv=max last=r3_clocktower r1=94.93 r2=0.00 r3=741.55 total=835.31 awake=[true, false, true]
```

## 8. Open questions for Mats

1. **Total length.** These valley times make the whole game about 3.7 h for a casual player.
   The old GDD target was 6-10 h. Is the shorter game right, or should V4/V5 sit at the top of
   the 60-75 min band?
2. **The r3_jack2 income dip** (section 5.1): reorder the pads, or fix the forklift?
3. **r2_jack3 does nothing until Sharp Saws** (section 5.2): keep it, move it, or give it a
   real effect?
