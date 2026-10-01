# Timber Valley - Game Design Doc (expansion: five valleys)

Status: design for the "last longer" expansion, written 2026-09-30 on branch `lookdev-test`.
Owner: game-designer. Builder: godot-android-dev. Data: `docs/balance/unlocks_regions.csv`
(every new pad) and `docs/balance/pacing_sim.md` (the pacing model and its output).

Numbers tagged **(my calc)** come from the pacing model in `docs/balance/pacing_sim.md`, not
from play. The model estimates income per purchase from the code rates (cycle times, worker
speed and carry, prices) at 60-70% use. Section 11 says how to replace the estimates with
measured numbers.

---

## 1. Pitch

Walk up to trees, carry logs and feed machines. The first valley's lumber yard grows into five
connected valleys, and each valley has its own wood, product chain and big landmark to build.

## 2. Core loop

**Chop, carry, craft, sell, build.** Each valley adds one new twist to the same loop (a log
flume, two-input machines and construction sites, cargo orders and ships, batch kilns). Older
valleys keep earning on their own, so money builds up across the whole map.

## 3. Controls (unchanged, one thumb, portrait)

| Input | Effect |
|---|---|
| Drag anywhere | Walk (virtual joystick). Only input in the world. |
| Stand on a tree | Chop; logs stack on your back |
| Stand on a white DROP square | Unload matching items into it |
| Stand on a PICK square | Load the machine's output |
| Stand on a counter | Stock it |
| Stand on CASH | Collect |
| Stand on a dark pad with a price | Pay into it (drains in about 0.75 s, any cost) |
| Stand on a build-site slot (new) | Deliver the slot's item; counter shows `24/60` |
| Stand on a handcar stop tile (new) | 0.8 s hold, then ride to that valley's hub |
| Stand on UPGRADES / an office | Upgrade sheet opens (tap buttons, 130 px min) |

No new gestures. Every new mechanic below is "stand on a square".

---

## 4. Current state audit (what ships today)

### 4.1 Map
One valley. Playable interior **x -23.5 to 19, z 15.5 to -47**, about **43 x 62 m**
(`World._bounds`). West edge: river at x = -27 (half-width 3.2, one decorative bridge at
z = -6). East edge: road at x = 17. North (z = -47) and south (z = 15.5) are invisible walls
behind border forest. Ground plane 160 x 170 m. The camera sits at offset (0, 8.4, 6.6) with
FOV 45 in portrait, so the player sees about 18 x 22 m around themselves. Shadows reach 30 m.

### 4.2 Purchases (25 pads, `World.UNLOCKS`)

| id | Cost | Requires | What it does |
|---|---:|---|---|
| trees2 | 10 | - | +6 broadleaf trees |
| office | 25 | - | Upgrade shop |
| jack1 | 50 | trees2 | Lumberjack, forest A to sawmill 1 |
| hauler1 | 70 | jack1 | Plank carrier, sawmill 1 to counter |
| carpentry | 120 | hauler1 | Planks x2 to chair, 1.4 s; chair counter |
| hauler3 | 160 | carpentry | Chair carrier |
| pine | 180 | carpentry | Pine forest (4x3, 4 logs per tree) |
| roadsign | 200 | carpentry | Shopper spawn rate x1.7 |
| cashier | 220 | carpentry | Collects cash every 1.2 s |
| sawmill2 | 260 | pine | Log to 2 planks, 0.8 s |
| jack2 | 300 | sawmill2 | Lumberjack, pine to sawmill 2 |
| hauler2 | 320 | sawmill2 | Sawmill 2 to carpentry |
| belt_planks | 350 | cashier | Belt, sawmill 1 to plank counter |
| belt_saw2 | 500 | hauler2 | Belt, sawmill 2 to carpentry |
| cnc | 600 | hauler2 | Planks x3 to table, 1.6 s; table counter |
| belt_chairs | 650 | hauler3, belt_planks | Belt, chairs to counter |
| conveyor1 | 700 | cnc | Belt, sawmill 2 to CNC |
| hauler4 | 750 | cnc | Table carrier |
| jack3 | 900 | factory | North forest + 2 lumberjacks to factory |
| factory | 1,200 | conveyor1 | Logs x3 to bookcase, 1.8 s |
| conveyor2 | 1,300 | dock | Belt, factory to dock |
| dock | 1,500 | factory | Truck: 8 bookcases per trip, only sale point for bookcases |
| belt_mega | 1,000 | megasaw | Belt, mega saw to CNC |
| megasaw | 2,500 | factory | Endless crane log, 2 planks per 0.7 s |
| lodge | 6,000 | conveyor2, jack3, belt_mega | Ends the game (`Game.finished`) |
| **Total** | **19,865** | | |

### 4.3 Items, machines, upgrades

| Item | Price | Made by | Value per log |
|---|---:|---|---:|
| plank | $3 | sawmill 1 (1 s), sawmill 2 (0.8 s), mega saw | $6 |
| chair | $8 | carpentry, 2 planks | $8 |
| table | $20 | CNC, 3 planks | $13 |
| bookcase | $45 | factory, 3 logs | $15 |

Trees: broadleaf 3 logs / 3 hits, pine 4 logs / 4 hits, both regrow in 7 s. Player chop time
0.32 s x 0.8^axe per hit; workers chop 1.6x slower. Player carries 8 + 4 per level; workers
6 + 2 per level at 3.2 m/s x (1 + 0.15 per level).

Upgrades (global, cost = base x 1.75^level): Backpack 30 (max 6), Shoes 40 (5), Axe 35 (5),
Oiled Machines 90 (5), Coffee Break 120 (5), Reputation 150 (5). All levels together cost
**$10,049**.

**Everything in the valley costs about $29,900** (pads plus upgrades).

### 4.4 How long it lasts today (my calc)
- The screenshot bot does not measure this. It plays 90 s of the tutorial, then `_showcase()`
  adds $20,000 and unlocks every pad, which is where the "about $24k" end balance comes from.
- Pacing model: an **attentive player clears the valley in about 17 minutes** and a casual one
  (70% efficiency) in **about 24 minutes** (my calc). A purchase comes every 13 s on median
  and the longest wait is 0.6 min. By the end, income is about $150/s (about $9k/min), so the
  $6,000 Lodge takes under a minute.
- Verdict: **20-25 minutes of content.** The pace is good, but it stops just when the
  automation becomes satisfying to watch.

---

## 5. Target

| Metric | Target | Model result (my calc) |
|---|---|---|
| Total to finish | 6-10 h | **5.9 h attentive, 8.5 h casual** |
| Session | 10-20 min | One or two pads per session late game, one valley stage early |
| Wait between purchases (median) | under 3 min | 13 s (V1), 66 s (V2), 110 s (V3), 137 s (V4), 167 s (V5) |
| Longest wait | under 12 min, only for landmarks | 10.4 min (V5 Observatory) |

Pacing curve (attentive player, my calc):

| Valley | Minutes | Hours total | Income at end | Purchases incl. upgrades |
|---|---:|---:|---:|---:|
| 1 Home Valley (today) | 17 | 0.3 | $150/s | 58 |
| 2 Birch Bend | 50 | 1.1 | $500/s | 39 |
| 3 Maple Highlands | 70 | 2.3 | $1,300/s | 34 |
| 4 Redwood Coast | 90 | 3.8 | $3,250/s | 35 |
| 5 Frost Peaks | 110 | 5.6 | $6,500/s | 33 |
| Grand Timber Station | 20 | 5.9 | - | 1 |

Income by play time (my calc): 5 min $7/s, 15 min $92/s, 30 min $233/s, 1 h $1.0k/s,
2 h $3.5k/s, 4 h $13.7k/s, 6 h $27k/s. Growth is about x3 per valley and each valley takes
about 20 minutes longer than the one before. The first purchases in a new valley add about
8-15% to total income, enough to feel.

---

## 6. Structure: sequential valleys on one map (recommended)

**Decision: five valleys on one continuous map, unlocked in a fixed order.** Each valley is a
"level": its own tree type, its own product chain, its own market and export, its own upgrade
board, and a landmark at the end. The landmark reveals the gate pad to the next valley. All
valleys share one wallet, and every built valley keeps earning while you work elsewhere.

Why this and not the alternatives:
- **Prestige resets** rebuild the same 25 pads with a multiplier. Mats asked for more builds
  and a bigger map, and a reset gives neither: it repeats content. It also throws away the
  automation, and watching the automation is the reward in this genre.
- **Separate level scenes** are the cheapest for the phone, but the map stays small, the player
  never walks back to a busy earlier valley, and the save needs one state per scene.
- **Connected valleys** is the genre standard (every lumber idle store page we checked lists
  "unlock new regions, each with new tree types"). It uses what already exists (pads, walking,
  the road and the river as borders) and fits in one scene if far valleys go to sleep
  (section 10).

Shared wallet: yes. The tradeoff is that old income dominates, so the first new-valley pads can
feel small. The price ladder counters this: each valley's goods are worth 3-10x more per log
(section 8.1). If the model's 8-15% per early pad feels weak in play, raise the new valley's
prices and do not split the wallet.

Rules:
1. A valley's pads appear only after its gate pad is bought. The gate pad appears when the
   previous landmark is finished.
2. **The Lodge no longer ends the game.** It shows a "Valley complete" card and reveals the
   River Bridge pad. The finish panel moves to the Grand Timber Station.
3. Each valley has a self-contained economy: nothing needs goods from another valley, except
   the final Station (section 7.7), which fills from each valley's own platform.
4. The HUD shows a valley chip under the money pill: `Birch Bend 7/19`.

---

## 7. New content

### 7.1 Overview

| # | Valley | Size (interior) | Wood | Chain | New idea | Export | Landmark |
|---|---|---|---|---|---|---|---|
| 1 | Home Valley (exists) | 43 x 62 m | oak, pine | plank, chair, table, bookcase | - | truck | Grand Lodge |
| 2 | Birch Bend (west, over the river) | 48 x 62 m | birch | veneer, plywood, canoe | **Log flume** | river barge | Boathouse |
| 3 | Maple Highlands (north) | 43 x 64 m | maple | beam, floorboard, cabin kit | **Two-input machine + build sites (village houses)** | railway | Clock Tower |
| 4 | Redwood Coast (east, over the road) | 54 x 62 m | redwood | timber, deckboard, mast, ships | **Cargo orders + repeatable ship builds** | harbour | Lighthouse |
| 5 | Frost Peaks (north-east) | 54 x 64 m | frost fir | dry lumber, skis, sled, guitar | **Batch kiln** | mountain train | Summit Observatory |
| 6 | Grand Timber Station | hub at (0,-52) | - | - | victory lap through all valleys | - | ends the game |

Map area grows from about 2,700 m² to about 16,400 m² playable (x6).

Each valley brings one new idea. Valley 2's landmark is paid with money only, like the Lodge,
so build sites are new in Valley 3 and nowhere earlier.

### 7.2 Trees

| Tree | Valley | Logs | Hits | Regrow | Scale vs today | Look |
|---|---|---:|---:|---:|---:|---|
| broadleaf | 1 | 3 | 3 | 7 s | 1.0 | exists |
| pine | 1 | 4 | 4 | 7 s | 1.0 | exists |
| birch | 2 | 4 | 4 | 8 s | 1.0 | white trunk, light green blob |
| maple | 3 | 5 | 5 | 9 s | 1.1 | red/orange canopy (`tree_*_fall` models work as stand-ins) |
| redwood | 4 | 8 | 7 | 14 s | 1.6, collision radius 0.45 | red-brown trunk, tall dark canopy |
| frost fir | 5 | 6 | 6 | 12 s | 1.15 | snow-capped cone |

Each wood is its own item (`birch_log`, `maple_log`, `red_log`, `frost_log`) so each valley's
machines take only their own logs. `ChopTree.setup` gets a kind table (logs, hits, regrow,
models, log item). Hits no longer follow the `logs <= 3` rule.

### 7.3 Items (new)

| Item | Valley | Price (base) | Stack cell (m) | Layer (m) | Look |
|---|---|---:|---|---:|---|
| birch_log | 2 | - | 1.05 x 0.36 | 0.31 | log, pale bark |
| veneer | 2 | 8 | 1.0 x 0.5 | 0.05 | thin pale sheet |
| plywood | 2 | 40 | 1.0 x 0.6 | 0.12 | layered edge board |
| canoe | 2 | 300 | 0.7 x 2.0 | 0.35 | small canoe (export only) |
| maple_log | 3 | - | 1.05 x 0.36 | 0.31 | log, grey bark |
| beam | 3 | 30 | 1.2 x 0.3 | 0.28 | square beam |
| floorboard | 3 | 12 | 1.0 x 0.25 | 0.07 | tongue-and-groove board |
| cabin_kit | 3 | 260 | 1.0 x 1.0 | 0.6 | strapped bundle with red tag (export only) |
| red_log | 4 | - | 1.3 x 0.5 | 0.42 | thick log |
| timber | 4 | 70 | 1.3 x 0.45 | 0.4 | big square timber |
| deckboard | 4 | 30 | 1.1 x 0.35 | 0.09 | dark board |
| mast | 4 | 500 | 0.4 x 2.4 | 0.4 | long pole (never sold at a counter) |
| frost_log | 5 | - | 1.05 x 0.4 | 0.33 | log with snow |
| dry_lumber | 5 | 90 | 1.0 x 0.4 | 0.11 | warm orange plank |
| skis | 5 | 400 | 0.4 x 1.6 | 0.12 | pair of skis |
| sled | 5 | 1,500 | 0.8 x 1.3 | 0.5 | wooden sled |
| guitar | 5 | 2,000 | 0.5 x 1.2 | 0.2 | acoustic guitar (export only) |

### 7.4 Machines (new)

All run at `Game.machine_speed()` x the valley's Sharp Saws multiplier. Input pile 36 and
output pile 48 unless noted.

| Machine | In | Out | Cycle | Notes |
|---|---|---|---:|---|
| Veneer Lathe | birch_log x2 | veneer x6 | 1.2 s | spinning log, peel sheet |
| Plywood Press | veneer x3 | plywood x1 | 1.5 s | press plate stamps down |
| Boat Workshop | plywood x4 | canoe x1 | 3.0 s | output pile 12 |
| Beam Saw | maple_log x1 | beam x2 | 1.4 s | reuse `_dress_sawmill` with a red frame |
| Planer Mill | maple_log x1 | floorboard x4 | 1.6 s | |
| Cabin Kit Factory (**Assembler**) | beam x2 **and** floorboard x4 | cabin_kit x1 | 2.0 s | two DROP squares, one per input |
| Redwood Mill | red_log x1 | timber x2 | 1.5 s | big version of the sawmill |
| Deck Saw | timber x1 | deckboard x3 | 1.2 s | |
| Mast Lathe | red_log x3 | mast x1 | 4.0 s | output pile 12 |
| Drying Kiln (**Batch**) | frost_log up to 20 | same count of dry_lumber | 16 s bake | see 7.6 |
| Ski Workshop | dry_lumber x2 | skis x1 | 2.0 s | |
| Sled Workshop (**Assembler**) | dry_lumber x3 **and** skis x1 | sled x1 | 3.0 s | |
| Luthier Workshop | dry_lumber x4 | guitar x1 | 5.0 s | output pile 12 |

Assembler: `Machine` gets an optional second input (`in_type_b`, `in_per_cycle_b`, its own pile
and DROP zone). A cycle starts when both piles hold enough. Carriers and belts pick the input by
item type.

### 7.5 Workers and vehicles

All read `Game.worker_speed()` and `Game.worker_capacity()` times the valley's Crew Coffee
multiplier.

| Worker | Valleys | Base | Carry | Job |
|---|---|---|---|---|
| Lumberjack | all | 3.2 m/s | 6 (+2/lvl) | exists |
| Carrier | all | 3.2 m/s | 6 (+2/lvl) | exists (hauler) |
| Cashier | all | - | - | exists; one per valley market |
| Forklift | 3, 4 | 4.5 m/s | 20 (+2/lvl) | hauler with a forklift model; may serve 2 sources, taking the fuller pile |
| Log Skidder | 4 | 4.8 m/s | 16 (+2/lvl) | lumberjack with a tractor model, chops at 1.6x like workers |
| Shipwright | 4 | 3.2 m/s | 10 (+2/lvl) | builder: fills slipway slots from named piles, picking the least-full slot first |
| Snowcat | 5 | 4.5 m/s | 24 (+2/lvl) | hauler, 2 sources (ski + sled workshops) to the Ski Lodge |

### 7.6 New mechanics (all one-thumb)

**A. Log flume (Valley 2).** A raised wooden trough with the water shader. It is a `Conveyor`
with a water look: speed 3.5 m/s, spacing 0.5 s, logs bob up and down (sin, 0.06 m, 3 Hz).
Its chute (a DROP square for `birch_log`) sits by the North Grove, and it runs 20 m to the
lathe's input pile. Lumberjacks assigned to the flume deliver to the chute, so their walk
drops from about 20 m to about 4 m. The player can use the chute too.

**B. Build sites (Valley 3 on).** New `BuildSite` node: 1-4 item slots plus an optional money
slot.
- Each slot is a DROP zone that takes only its item and shows `delivered/need` on a label and
  a fill bar.
- The money slot works like an `UnlockPad`.
- The building has N stages (N = 4 for houses, 6 for landmarks). Stage k shows when the
  delivered fraction reaches k/N. Each stage rises from the ground in 0.6 s (TRANS_BACK).
- When complete: confetti, the camera pulls out 20% for 1.2 s, then the reward applies.
- Village houses pay **rent: +$15/s base each** (x Local Fame), paid straight to the wallet,
  and add +10% to the Builders' Yard shopper spawn rate.
- **Repeatable sites** (ship slipways): after completion the ship launches (4 s slide into the
  sea), pays its reward, and the slots reset. A new ship cannot finish less than 45 s after the
  last launch. Slots can still fill during that time, and the hull shows "Next ship in 0:12".

Build recipes (money slot = the CSV cost):

| Site | Goods |
|---|---|
| Cottage (r3_house1) | 30 beam, 40 floorboard |
| Farmhouse (r3_house2) | 40 beam, 50 floorboard, 2 cabin_kit |
| Barn (r3_house3) | 50 beam, 60 floorboard, 4 cabin_kit |
| School (r3_house4) | 60 beam, 70 floorboard, 6 cabin_kit |
| Inn (r3_house5) | 70 beam, 80 floorboard, 8 cabin_kit |
| Clock Tower (r3_clocktower) | 120 beam, 100 floorboard, 12 cabin_kit |
| Ship (r4_slipway, r4_slipway2), repeatable | 60 timber, 80 deckboard, 3 mast; launch pays **$14,000** base |
| Lighthouse (r4_lighthouse) | 200 timber, 150 deckboard, 10 mast |
| Summit Observatory (r5_observatory) | 200 dry_lumber, 60 skis, 20 sled, 10 guitar |
| Grand Timber Station (cap_station) | $25,000,000 plus five platform slots (7.7) |

**C. Cargo orders (Valley 4 on).** An Order Board by the harbour pier.
- A cargo ship docks with a manifest of 2-3 lines drawn from the valley's sellable items.
  Example: `20 timber, 30 deckboard`. Size scales with the order number n: each line needs
  `10 + 4n` items, capped at 60.
- The dock DROP square takes any manifest item until that line is full, and refuses the rest.
- When the manifest is full, the ship pays **1.6x the base sale value** (x Local Fame), sounds
  its horn and leaves. The next ship docks 15 s later.
- No deadline, no failure, no timer on screen. One order at a time.
- The Frost Peaks Ski Lodge gets a second board in M4 (open question 5).

**D. Batch kiln (Valley 5).**
- Its DROP square takes up to 20 frost_log.
- Baking starts when the kiln is full, or 6 s after the last log arrived if it holds at least
  one. It never waits forever.
- Bake time is 16 s divided by machine speed. The door closes and the chimney glows orange
  (emission ramps up over the bake).
- The door opens with a "ding" and the batch pops out as dry_lumber into the output pile
  (cap 48). The kiln loads nothing while baking.

**E. Handcar stops (fast travel, free with r3_gate).** Every valley hub has a stop with one
1.6 m tile per other unlocked valley, labelled with its name. Stand on a tile for 0.8 s: fade
out 0.3 s, move player and camera, fade in 0.3 s. That is 1.4 s total with a rail clack sound
and no menu. Stops: V1 (-7, 12), V2 (-34, 8), V3 (4, -56), V4 (26, 10), V5 (46, -60).

### 7.7 Capstone: Grand Timber Station
- The pad appears when the Observatory is done, at (0, -52) on the rail line between Valley 1
  and Valley 3.
- It is a build site with a $25M money slot and five **platform slots**, one in each valley
  next to its handcar stop:

  | Platform | Needs |
  |---|---|
  | V1 | 120 bookcase |
  | V2 | 40 canoe |
  | V3 | 40 cabin_kit |
  | V4 | 30 mast |
  | V5 | 20 guitar |

- A platform fills only while its valley is awake, from the player or that valley's workers
  (the valley's export carrier also serves its platform once the platform exists). This sends
  the player on a victory lap through every valley.
- On completion the Timber Express runs one loop past every valley (cutscene, 12 s). Then the
  existing finish panel appears ("Keep playing": orders and ships keep running).

### 7.8 Upgrades

Global (existing, office in V1, unchanged). Extended levels unlock at the Riverside Office:

| Upgrade | New levels | Cost of level L | Effect per level |
|---|---|---|---|
| Bigger Backpack | 7-10 | 2,500 x 1.75^(L-7) | +4 carry |
| Running Shoes | 6-7 | 3,000 x 1.75^(L-6) | +12% walk |
| Sharper Axe | 6-8 | 2,000 x 1.75^(L-6) | chop time x0.8 |

Per valley (new; one board in each valley office, affects only that valley). Cost =
base x 1.8^level, max 5 levels each.

| Valley | Sharp Saws (+25% machine speed) | Crew Coffee (+15% worker speed, +2 carry) | Local Fame (+10% prices and shoppers) |
|---|---:|---:|---:|
| 2 | 8,000 | 11,000 | 13,000 |
| 3 | 50,000 | 65,000 | 80,000 |
| 4 | 160,000 | 210,000 | 270,000 |
| 5 | 510,000 | 680,000 | 850,000 |

### 7.9 Markets, shoppers and exports

- Each valley market is a `Shop` with its own counters, till and spawn point:

  | Market | Shoppers arrive from |
  |---|---|
  | V2 Riverside Market (-40, 6) | a lane from the west edge, z = 12 |
  | V3 Builders' Yard (10, -62) | the existing road x = 17, which already runs to z = -100 |
  | V4 Harbor Market (66, -2) | boats that tie up at the pier end (72, 8) |
  | V5 Ski Lodge (60, -62) | the cable car top station |

- Spawn formula as in `Shop._process`, with the valley's Local Fame and pier/sign bonus.
  Customer cap drops from 34 to **20 per valley**.
- Exports generalise `TruckDock` (vehicle, capacity, path, away time):

  | Export | Carries | Away |
  |---|---|---:|
  | V1 truck (exists) | 8 bookcases | 5 s |
  | V2 barge on the river (south to north) | 6 canoes | 8 s |
  | V3 train | 12 kits, 20 after Longer Train | 10 s |
  | V5 mountain train | 10 guitars | 12 s |

---

## 8. Economy (for `scripts/Balance.gd`)

Every pad for Valleys 2-6 (id, title, cost, requirements, pad position, kind, modelled
income, effect) is in **`docs/balance/unlocks_regions.csv`** (81 rows). Costs come from the
pacing model, scaled per valley to hit the section 5 targets and rounded to 2 significant
figures. Valley totals: V2 $1.16M, V3 $9.1M, V4 $32.5M, V5 $90.7M, Station $25M plus goods.
Pad positions are world coordinates. Nudge any of them up to 3 m to clear paths; keep the
order and the costs.

### 8.1 Value ladder (base prices, value per log)

| Valley | Starter product | Mid | Top | Best $/log |
|---|---|---|---|---:|
| 1 | plank $6/log | table $13 | bookcase $15 | 15 |
| 2 | veneer $24/log | plywood $40 | canoe $75 | 75 |
| 3 | floorboard $48/log | beam $60 | cabin kit $130 | 130 |
| 4 | timber $140/log | deckboard $180, mast $167 | ship $270 (orders 1.6x) | 270 |
| 5 | dry lumber $90/log | skis $200, sled $300 | guitar $500 | 500 |

The top product must stay the best per log, or players will skip the chain. Check this
whenever a price changes.

### 8.2 Const block to paste

```gdscript
# scripts/Balance.gd  (class_name Balance). Pads live in UNLOCKS, generated from docs/balance/unlocks_regions.csv
const PRICES := {
	"plank": 3, "chair": 8, "table": 20, "bookcase": 45,
	"veneer": 8, "plywood": 40, "canoe": 300,
	"beam": 30, "floorboard": 12, "cabin_kit": 260,
	"timber": 70, "deckboard": 30, "mast": 500,
	"dry_lumber": 90, "skis": 400, "sled": 1500, "guitar": 2000,
}
const TREES := {
	"broad": {"log": "log", "logs": 3, "hits": 3, "regrow": 7.0, "scale": 1.0},
	"pine": {"log": "log", "logs": 4, "hits": 4, "regrow": 7.0, "scale": 1.0},
	"birch": {"log": "birch_log", "logs": 4, "hits": 4, "regrow": 8.0, "scale": 1.0},
	"maple": {"log": "maple_log", "logs": 5, "hits": 5, "regrow": 9.0, "scale": 1.1},
	"redwood": {"log": "red_log", "logs": 8, "hits": 7, "regrow": 14.0, "scale": 1.6},
	"frost": {"log": "frost_log", "logs": 6, "hits": 6, "regrow": 12.0, "scale": 1.15},
}
# id: [in_a, n_a, in_b, n_b, out, n_out, cycle_s]  ("" = no second input)
const MACHINES := {
	"lathe": ["birch_log", 2, "", 0, "veneer", 6, 1.2],
	"press": ["veneer", 3, "", 0, "plywood", 1, 1.5],
	"boatshop": ["plywood", 4, "", 0, "canoe", 1, 3.0],
	"beamsaw": ["maple_log", 1, "", 0, "beam", 2, 1.4],
	"planer": ["maple_log", 1, "", 0, "floorboard", 4, 1.6],
	"kitfactory": ["beam", 2, "floorboard", 4, "cabin_kit", 1, 2.0],
	"redmill": ["red_log", 1, "", 0, "timber", 2, 1.5],
	"decksaw": ["timber", 1, "", 0, "deckboard", 3, 1.2],
	"mastlathe": ["red_log", 3, "", 0, "mast", 1, 4.0],
	"skiworks": ["dry_lumber", 2, "", 0, "skis", 1, 2.0],
	"sledshop": ["dry_lumber", 3, "skis", 1, "sled", 1, 3.0],
	"luthier": ["dry_lumber", 4, "", 0, "guitar", 1, 5.0],
}
const KILN := {"batch": 20, "bake_s": 16.0, "idle_start_s": 6.0}
const RENT_PER_HOUSE := 15            # $/s base, x Local Fame
const SHIP_REWARD := 14000
const SHIP_MIN_INTERVAL := 45.0
const ORDER := {"lines_min": 2, "lines_max": 3, "base_qty": 10, "qty_per_order": 4, "qty_cap": 60, "pay_mult": 1.6, "gap_s": 15.0}
# region upgrades: base cost per valley, growth 1.8, max 5
const REGION_UPGRADES := {
	2: {"saws": 8000, "crew": 11000, "fame": 13000},
	3: {"saws": 50000, "crew": 65000, "fame": 80000},
	4: {"saws": 160000, "crew": 210000, "fame": 270000},
	5: {"saws": 510000, "crew": 680000, "fame": 850000},
}
const REGION_UPGRADE_GROWTH := 1.8
const GLOBAL_EXT := {"capacity": [2500, 4], "speed": [3000, 2], "axe": [2000, 3]}  # [base, extra levels], growth 1.75
const CUSTOMERS_PER_REGION := 20
```

### 8.3 Money display
Money passes $1M in Valley 3. Show `$999`, `$12.5K`, `$3.40M`, `$1.20B` (3 significant
figures) in the money pill, pad prices, float texts and toasts. `Game.money` stays an int
(64-bit in GDScript, no overflow).

---

## 9. Map

### 9.1 Layout (north is up, as on screen)

```
 x:  -101     -79          -31 -27 -23.5         19 21 23               77      110
      .........................................................................
 z-119 : border  :   (future  :    :  V3 MAPLE        | R |  V5 FROST PEAKS   : sea/
      :  forest  :    valley) :    :  HIGHLANDS       | o |  kiln, ski works, : cliffs
      :          :            :    :  village plots W | a |  luthier, lodge   :
      :          :            :    :  groves N, rail E| d |  Observatory NE   :
 z-55 :..........:............:....:=====[gate]======|===|==[cable car top]=:.....
 z-51  ~~~~~~~~~~ TIMBER EXPRESS RAIL (x -75..75), Grand Station at (0,-52) ~~~~~~~
 z-47 :..........:............:....:=================|===|===[cable car]====:.....
      :          :  V2 BIRCH  : R :  V1 HOME VALLEY  | R |  V4 REDWOOD       :
      :  border  :  BEND      : i :  (exists)        | o |  COAST            : SEA
      :  forest  :  flume NW  : v :  sawmills, shop  | a |  mill, slipways,  : harbour
      :          :  lathe,    : e :  factory, lodge  | d |  lighthouse SE    : pier
      :          :  presses   : r :                  |[X]|  crossing z=-20   :
 z 15 :..........:....[bridge z=-6]......................................:......
                        border forest (south, z 15..37)
```

Every valley is 43-54 m wide and 62-64 m deep, about what the camera and one shadow cascade
handle comfortably. Between valleys there is a 4-8 m belt of border forest with one gate
opening each:

| Crossing | Where | What |
|---|---|---|
| River bridge | z = -6 | the existing bridge, widened to 2.4 m and walkable |
| North gate | x = 0, z = -47..-55 | the V1 path already runs to z = -44 |
| Road crossing | z = -20 | barrier arms; trucks stop 1 s when the player is on it |
| Cable car | x = 50, z = -45 to -58 | 4 s ride, same as a handcar stop |

The existing river wall at x = -23.5 gets an opening only at the bridge. The road wall at
x = 19.2 gets an opening only at the crossing.

### 9.2 Per-valley anchor positions (world coords)

| Valley | Hub / stop | Market | First machine | First grove (cols x rows, spacing) | Landmark |
|---|---|---|---|---|---|
| 2 | (-34, 8) | (-40, 6) | lathe (-45, -6) | (-55, -2), 3x3, 2.6 m | Boathouse (-68, 8) |
| 3 | (4, -56) | (10, -62) | beam saw (2, -64) | (-6, -64), 3x3, 2.6 m | Clock Tower (-10, -112) |
| 4 | (26, 10) | (66, -2) | redwood mill (32, -20) | (45, -8), 3x2, 4.0 m | Lighthouse (72, -44) |
| 5 | (46, -60) | (60, -62) | kiln (40, -66) | (30, -64), 3x3, 2.8 m | Observatory (66, -114) |

The later groves are listed per pad in the CSV (`effect` column).

### 9.3 World-building changes in `World.gd`
- Split the build into `Region` nodes: `Region.gd`, a new `Node3D` with `id`, `rect: Rect2`,
  `awake: bool`. Everything a valley owns becomes a child of its Region: forests, machines,
  walkers, pads, market, belts, props.
- **One ground plane and ground material per valley.** The ground shader holds only 32 paths
  and 24 plazas (`ground.gdshader`), and one plane cannot carry five valleys' paths. Each
  valley gets its own plane (rect plus 8 m) with its own `grass_a/b` colours:

  | Valley | Grass |
  |---|---|
  | V2 | lighter spring green |
  | V3 | autumn olive |
  | V4 | sand blend toward the east shore |
  | V5 | snow white-blue, dirt becomes packed snow |

- The border forest moves out to the new outer edges (x -101..-79, x 77..110, z -119..-141,
  z 15..37) plus the 4-8 m belts between valleys. It keeps the density formula `area / 3.2`.
- The river mesh and bounds stay at x = -27. The road stays at x = 17 and ends at z = -100 as
  today.
- The deco scatter (`_scatter_deco`) runs once per region rect with the counts scaled by area
  (V1 counts are for 2,700 m²).

---

## 10. Camera and phone budget

**Camera:** unchanged (offset (0, 8.4, 6.6), FOV 45 portrait, follow lerp 6/s). Additions:
- Build sites and landmarks pull out 20% for 1.2 s on completion only.
- `camera.far` drops from 160 to **110** and fog density rises from 0.0025 to **0.006**, so
  far edges and a waking valley fade in instead of popping. Check the sky look with the
  graphic-designer.

**Studio budget** (templates/DESIGN.md): under 100 draw calls, under 100k visible triangles,
one shadow light. Today's single valley already sits near that. Five valleys fit only if the
far ones are asleep.

**Valley sleep (streaming) rules:**
1. A valley is **awake** when the camera focus is inside its rect grown by 24 m. It **sleeps**
   only once the focus is more than 30 m outside (hysteresis). At most 2 valleys are awake; if
   3 qualify, the one whose centre is farthest from the focus sleeps.
2. Sleeping means the Region node gets `visible = false` and
   `process_mode = PROCESS_MODE_DISABLED`. Trees, machines, walkers, customers, belts, pads and
   particles all stop costing CPU and GPU. Piles keep their counts (already saved per pile id).
3. Scenery MultiMeshes (border forest, deco) stay outside Region nodes. They are already
   chunked at 16 m with `visibility_range_end = 60`, so they cull themselves.
4. **Ledger income while asleep:**
   - Each Region measures what its automated sinks paid while awake: tills collected by a
     cashier, exports, launches, orders filled by workers, rent. It keeps a rolling window of
     the last 120 awake seconds.
   - Asleep, it pays that average rate once per second straight into the wallet. No coins,
     no float text.
   - A valley without a cashier earns nothing from its till while asleep.
   - Rent always pays.
   - The rate is saved (`"ledger": {"r2": 312.5}`), so it survives a restart.
   - Build sites and platforms never progress while asleep.
5. Per awake valley, aim for **45 draw calls, 45k triangles, 12 workers and 20 customers at
   most**. Two awake valleys then fit inside the budget together with the HUD.
6. Verify on the phone with the PerfOverlay (three-finger tap) at each valley border. Laptop
   Xvfb numbers do not count.

**Save:** unlock ids stay in `unlocked` (new ids are prefixed `r2_` ... `cap_`). New keys:
`ledger`, `region_upgrades` (per valley), `sites` (delivered counts per slot), `orders`
(order number, current manifest). Old saves load unchanged. A save with `lodge` owned shows
the River Bridge pad. Old `finished = true` is read as "Lodge done", and the finish panel does
not reopen.

---

## 11. Feel

| Event | Sound | Visual | Duration |
|---|---|---|---|
| Log drops into flume | splash (new, or `drop_002` pitched down) | 8 white splash particles, log bobs | 0.4 s |
| Lathe peel | machine sfx, pitch 1.2 | log spins, sheets slide out | per cycle |
| Assembler cycle | two thunks | both input piles pulse 5% | 0.2 s |
| Build-site stage | `creak1` + thunk | stage rises (TRANS_BACK), dust puff 12 particles | 0.6 s |
| Build complete | `confirmation_002` + confetti | camera pull-out 20% | 1.2 s |
| House rent | none (avoid noise) | small "+$15/s" float over the house on completion only | 1.3 s |
| Ship launch | horn + big splash | hull slides 8 m into the sea, bow wave | 4 s |
| Order filled | bell + coins | ship horn, coin burst on the dock, "+$X" float | 1.5 s |
| Kiln bake | low hum loop | chimney glow ramps 0 to 1, door closed | 16 s |
| Kiln done | "ding" | door swings open, lumber pops out one by one 0.05 s apart | 1.0 s |
| Handcar ride | rail clack | fade 0.3 / move / fade 0.3 | 1.4 s |
| Gate opened | `unlock` + confetti | belt of trees at the gate shrinks away (scale to 0.01) | 0.8 s |
| Valley complete card | fanfare (`confirmation_001` x2) | centre card: valley name, time played there, earned | stays until tapped |

Haptics: none. Android vibration needs the VIBRATE permission and the studio rule says no
permissions unless needed (open question 4).

---

## 12. Onboarding and session shape

- **First 60 s of a new game:** unchanged (the arrow tutorial runs until `jack1`).
- **First 60 s of each new valley:** a 2 s banner ("Valley 2: Birch Bend") and nothing more.
  The guide arrow runs a mini-tutorial until that valley's first lumberjack is bought: chop
  the new tree, then feed the new machine, then stock the new counter. Hints stay at 5 words
  or fewer ("Chop the birch trees", "Feed the veneer lathe"). This reuses `World._goal()`
  keyed by the current valley.
- **First contact with each new mechanic** gets one hint line only, for example "Drop logs in
  the flume" or "Fill every square to build".
- **Where players stop:** after a landmark (natural chapter end, the card says so), or after a
  big pad in late valleys. Sessions run 10-20 min. Late valleys have 2-3 min between purchases,
  filled by house and ship progress.
- **Why they come back:** the next valley's gate is visible, a building stands half-built, the
  last order is half-filled. Nothing expires. Offline earnings are not part of the design yet
  (open question 1).
- No ads, no IAP, no energy, no deadlines, no daily streaks.

---

## 13. Build order (each milestone is playable and shippable alone)

**M1: Birch Bend (first new valley).**
- Groundwork:
  - `Balance.gd` data file with `UNLOCKS` moved in, plus the section 8.2 consts.
  - `Region.gd` with the sleep/wake and ledger rules.
  - Per-region ground plane and money formatting.
  - Tree kinds table, and new items (birch_log, veneer, plywood, canoe).
  - `Shop` parameterised (spawn point, customer cap).
  - `TruckDock` generalised (barge).
  - Lodge changed to the "Valley complete" card.
- Content: all 19 `r2_*` pads, the flume, the Riverside Office with the V2 upgrade board and
  the global extension levels, and the money-only Boathouse.
- Save migration and the V2 mini-tutorial.
- Done when:
  - the bot can buy the bridge from a save with the Lodge;
  - PerfOverlay holds 60 fps at the bridge on Mats's phone and tablet;
  - an old save loads with nothing lost.

**M2: Maple Highlands.**
- Assembler machine, `BuildSite`, forklift, the train export and handcar stops.
- All `r3_*` pads, 5 village houses with rent, and the Clock Tower.
- Done when houses fill from carriers and the player, rent keeps paying while the valley
  sleeps, and the handcar tiles work.

**M3: Redwood Coast.**
- Redwood trees, skidder, road crossing, and the harbour pier with boat shoppers.
- Repeatable slipway (45 s minimum), shipwrights, the Order Board, and the Lighthouse.
- Done when two slipways run with shipwrights only and orders need no player.

**M4: Frost Peaks.**
- Batch kiln, snowcat, cable car, Ski Lodge, luthier, mountain train and the Observatory.
- Snow ground palette.

**M5: Grand Timber Station.**
- The rail line along z = -51, the five platforms, the capstone site and the Express loop
  cutscene.
- The finish panel moves here.

**M6: Balance pass.**
- Extend `tests/capture.gd` with a bot mode that plays from a given save without the $20,000
  grant. It should log `t, pad id, money, income/s` at `Engine.time_scale = 3`.
- Replace the model's income estimates in `pacing_sim.md` with the measured rates and re-solve
  the costs.
- Any valley that runs over 1.3x its target minutes gets its costs scaled down.

Art needed per milestone goes to the graphic-designer (models_v3 pipeline):

| Milestone | Models |
|---|---|
| M1 | birch tree, lathe, press, canoe, barge, boathouse |
| M2 | maple tree, beam saw, planer, kit factory, forklift, train, 5 houses, clock tower |
| M3 | redwood tree, skidder, ship hull stages, cargo ship, pier, lighthouse |
| M4 | frost fir, kiln, skis, sled, guitar, cable car, lodge, observatory |

---

## 14. Open questions for Mats

1. **Offline earnings?** Today nothing is earned while the app is closed. Proposal: pay up to
   2 h of 50% ledger income as a coin pile at the Valley 1 office that you walk over to
   collect (no popup). Yes or no?
2. **Length:** the target is about 6 h attentive and 8.5 h casual (my calc). Is that the right
   size, or do you want a shorter first release that ships M1-M3 only (about 4 h)?
3. **Shared wallet** across valleys (recommended), or each valley starts from $0 with its own
   money? The shared wallet makes old valleys matter. Separate wallets make each valley feel
   like a fresh level but hide the stacking.
4. **Haptics** on purchases need the Android VIBRATE permission. Leave them out (current
   design) or add the permission?
5. **Orders in Frost Peaks too**, or keep orders a Redwood Coast feature?
6. **Valley names and themes** (Birch Bend, Maple Highlands, Redwood Coast, Frost Peaks,
   Grand Timber Station): keep, or do you have names or a theme in mind (for example Norwegian
   place names)?
7. **After the ending:** is "keep playing with orders and ships" enough, or do you want a
   post-game loop (for example a golden-axe replay of Valley 1 at 10x prices)? Not designed
   here, on purpose.

## Decisions (Mats, 2026-09-30)
- First release: all 5 valleys plus the Grand Timber Station (M1-M6), not a 3-valley cut.
- Offline earnings: yes, up to 2 hours at 50% income, collected as a coin pile at the office.
- Wallet: one shared wallet across all valleys.
- Valley names: keep the English names.
