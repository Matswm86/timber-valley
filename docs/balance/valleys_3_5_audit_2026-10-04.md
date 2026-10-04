# Valleys 3-5 and the Grand Timber Station: stall audit, fixes, re-measure (2026-10-04)

Mats: "Check the other levels too for flaws in logic and things that might be stalling. Level 1
is fine." Follows `birch_redwood_pacing_2026-10-04.md` (Birch Bend and the Redwood opening). All
numbers are my measurements with `tests/pacing_probe.gd`; nothing here is modelled.

## Method

- **Automation runs** (`PROBE_MODE=auto`): every earlier valley finished, the probed valley owning
  its pads up to a checkpoint in cheapest-first purchase order (each pad bought once its
  requirements are owned), its own build sites empty, player parked at its handcar stop, 360 s,
  summary over 120-360 s. Global upgrades "cap" (backpack 4, rest 3) and "max"; region upgrades 0.
  One run per checkpoint and level: ship launches and orders are lumpy, so single Redwood rows can
  move about +-20% between runs.
- **Scripted player** (`PROBE_MODE=play`): the valley's gateway just paid, $0, global upgrades max,
  carried-in income = measured ledgers with earlier region upgrades 3/3/3 (V1 95.1, V2 214.5,
  V3 741.6, V4 1500.3 $/s; the Birch Bend fix raises V2's share, not included). The player buys the
  cheapest pad it can pay. Otherwise it plays the valley's first machine by hand: carry its goods
  to the counter, collect cash, chop only while the machine has room. It does not buy region
  upgrades and never carries goods to build sites. "Waiting" = nothing useful to do.
- **Station** (`PROBE_MODE=station`): everything owned up to `cap_station`, platforms empty; the
  player stands at each valley's handcar stop in turn until its platform is full.

## Grand Timber Station: no stall

All five platforms fill while the player stands in that valley:

| Platform | Time | Porter idle (starved) |
|---|---|---|
| p1 bookcases 120 | 244 s | 20% |
| p2 canoes 40 | 117 s | 52% |
| p3 cabin kits 40 | 146 s | 32% |
| p4 masts 30 | already full on arrival (it filled while Redwood Coast was awake next door) | - |
| p5 guitars 20 | 168 s | 53% |

No change made.

## Maple Highlands (Valley 3)

**Root cause 1: the village and the Clock Tower starve (logic flaw).** Belts empty the beam saw,
planer and kit-factory outputs the moment anything lands: two yard belts plus, after r3_belt_kit,
the kit-factory feed belts and the kit-to-train belt. The forklift is the only carrier to the build
sites, and it found nothing to load. Measured (max, 360 s): after r3_belt_kit, house1-3 received
0 beams; after r3_rail2, 0 kits. In the scripted run the Clock Tower was bought at 2,623 s and still
stood at beam 0/120, kit 0/12 at 5,400 s (46 min later). **Valley 3 could not finish on its own.**

First attempt (rejected): pausing the belts whenever a site needs the item. With five houses and
the tower open, every belt paused at once, the one forklift carried everything, the planer and
kit-factory outputs sat 100% full, and income fell from 22,843 to 3,442 $/min (clocktower, max).

**Fix 1:** while a village site needs an item, the belts that empty its pile leave a reserve on
it (`Balance.SITE_RESERVE`: beam 12, floorboard 12, cabin kit 4); beyond the reserve they run
normally (`Conveyor.hold`, unset in every other valley). Once a belt feeds the counter or train,
the forklift sends site-bound loads straight to the site instead of alternating with the counter.
The forklift's "emptier site slot first" scoring (Redwood Coast's since 2026-10-03) now also
applies in Maple Highlands (`Worker._pick_source`, `region >= 3`), so a few kits are not left
waiting behind piles of floorboards.

**Root cause 2: the planer.** Its input was 87-98% full at every checkpoint from r3_jack2 on, with
2-3 crews standing at it 60-100% of the time. The kit factory's floorboard side was empty while
26-28 beams waited on the other side. **Fix 2:** planer cycle 1.6 -> 1.1 s. Modest effect: income
+1-4% (max) and +7-15% (cap) at the jack2-rail checkpoints. The input still sits full, because the
crews outnumber it (see "Not fixed").

**Root cause 3: the opening.** The player waits 71 s at the gateway for the $20K beam saw.
**Fix 3:** r3_beamsaw 20,000 -> 8,000.

| Scripted player | Before | After |
|---|---|---|
| Gateway -> beam saw (pure waiting) | 71 s | 34 s |
| Pads in the first 10 min | 8 | 8 |
| Gaps, first 8 pads | 71, 54, 52, 68, 80, 84, 93, 95 s | 34, 52, 69, 54, 82, 85, 95, 96 s |
| Clock Tower bought | 2,623 s | 2,650 s |
| Clock Tower finished | never (0/120 beams, 0/12 kits at 5,400 s) | 2,971 s (321 s after its pad) |

Automation (360 s window):
**Valley 3, max upgrades** (before -> after)

| Checkpoint | $/min | Worker idle % | Longest full (pile) |
|---|---|---|---|
| r3_jack1 | 0 -> 0 | 100.0 -> 100.0 | 339 s (beamsaw_out) -> 339 s (beamsaw_out) |
| r3_forklift1 | 8,482 -> 8,539 | 12.6 -> 12.6 | 1 s (beamsaw_in) -> 1 s (beamsaw_in) |
| r3_planer | 8,494 -> 8,381 | 12.6 -> 12.6 | 1 s (beamsaw_in) -> 1 s (beamsaw_in) |
| r3_house1 | 8,539 -> 8,685 | 13.0 -> 13.6 | 2 s (shelf_beam) -> 1 s (beamsaw_in) |
| r3_belt_bp | 8,539 -> 8,460 | 41.3 -> 41.5 | 1 s (beamsaw_in) -> 3 s (shelf_beam) |
| r3_jack2 | 11,430 -> 11,578 | 41.3 -> 43.2 | 14 s (planer_in) -> 17 s (planer_in) |
| r3_kitfactory | 11,029 -> 11,389 | 41.6 -> 46.3 | 18 s (planer_in) -> 27 s (planer_in) |
| r3_house2 | 11,404 -> 11,772 | 40.6 -> 45.2 | 13 s (planer_in) -> 33 s (planer_in) |
| r3_rail | 11,406 -> 11,893 | 40.2 -> 42.1 | 12 s (planer_in) -> 23 s (planer_in) |
| r3_belt_kit | 19,784 -> 21,501 | 30.9 -> 22.4 | 22 s (dock_cabin_kit) -> 19 s (dock_cabin_kit) |
| r3_house3 | 19,944 -> 21,184 | 30.5 -> 23.9 | 19 s (dock_cabin_kit) -> 22 s (dock_cabin_kit) |
| r3_jack3 | 19,771 -> 21,320 | 51.5 -> 46.8 | 22 s (dock_cabin_kit) -> 19 s (dock_cabin_kit) |
| r3_rail2 | 23,107 -> 25,136 | 51.1 -> 47.2 | 18 s (beamsaw_in) -> 25 s (planer_in) |
| r3_house4 | 23,697 -> 22,927 | 51.8 -> 45.7 | 18 s (beamsaw_in) -> 21 s (planer_in) |
| r3_house5 | 23,952 -> 21,904 | 51.9 -> 44.3 | 18 s (beamsaw_in) -> 13 s (planer_in) |
| r3_clocktower | 22,843 -> 21,427 | 51.3 -> 43.7 | 18 s (beamsaw_in) -> 16 s (planer_in) |

**Valley 3, cap upgrades** (before -> after)

| Checkpoint | $/min | Worker idle % | Longest full (pile) |
|---|---|---|---|
| r3_jack1 | 0 -> 0 | 100.0 -> 100.0 | 335 s (beamsaw_out) -> 335 s (beamsaw_out) |
| r3_forklift1 | 5,860 -> 5,869 | 20.3 -> 20.3 | 3 s (beamsaw_in) -> 3 s (beamsaw_in) |
| r3_planer | 5,869 -> 5,791 | 20.3 -> 20.3 | 3 s (beamsaw_in) -> 3 s (beamsaw_in) |
| r3_house1 | 5,860 -> 5,889 | 20.3 -> 20.3 | 3 s (beamsaw_in) -> 3 s (beamsaw_in) |
| r3_belt_bp | 5,869 -> 5,899 | 40.8 -> 40.7 | 3 s (beamsaw_in) -> 3 s (beamsaw_in) |
| r3_jack2 | 8,957 -> 9,608 | 36.0 -> 33.3 | 14 s (planer_in) -> 13 s (planer_in) |
| r3_kitfactory | 8,949 -> 9,598 | 34.1 -> 33.9 | 13 s (planer_in) -> 14 s (planer_out) |
| r3_house2 | 8,639 -> 9,059 | 29.4 -> 34.5 | 12 s (planer_in) -> 13 s (planer_out) |
| r3_rail | 8,170 -> 9,410 | 35.3 -> 33.9 | 16 s (planer_in) -> 13 s (planer_in) |
| r3_belt_kit | 15,526 -> 17,641 | 30.8 -> 10.2 | 3 s (beamsaw_in) -> 17 s (dock_cabin_kit) |
| r3_house3 | 15,482 -> 17,375 | 30.6 -> 7.6 | 3 s (beamsaw_in) -> 10 s (dock_cabin_kit) |
| r3_jack3 | 15,476 -> 16,030 | 46.2 -> 40.3 | 18 s (beamsaw_in) -> 20 s (beamsaw_in) |
| r3_rail2 | 15,658 -> 19,057 | 46.2 -> 39.2 | 18 s (beamsaw_in) -> 16 s (beamsaw_in) |
| r3_house4 | 15,880 -> 16,873 | 46.2 -> 37.9 | 18 s (beamsaw_in) -> 10 s (beamsaw_in) |
| r3_house5 | 15,738 -> 17,600 | 46.2 -> 36.2 | 18 s (beamsaw_in) -> 18 s (beamsaw_in) |
| r3_clocktower | 15,851 -> 17,750 | 46.2 -> 32.2 | 18 s (beamsaw_in) -> 11 s (beamsaw_in) |


(In these automation runs every site of the checkpoint opens at once with empty piles. From
house4 on, the later houses and the tower still get beams only slowly within 360 s. In normal
play the sites open one at a time, and the scripted run above finishes them all.)

## Redwood Coast (Valley 4), Deck Saw to Lighthouse

**Root cause 1: the Lighthouse waits behind the slipways (logic flaw).** Shipwrights send each
load to the least-full slot. The repeatable slipways empty after every launch, so they kept
winning, and the Lighthouse sat at 145-185/200 timber for about 12 min. In the scripted run it was
bought at 2,546 s and finished at 3,505 s (16 min). **Fix 1:** shipwrights fill the Lighthouse
first while it needs the item (`RedwoodCoast._wright_route`); the slipways continue afterwards.

**Root cause 2: one slow forklift.** From r4_forklift to r4_orders the Deck Saw output sat full
for 300+ s of 360. The single forklift was busy 99-100% of the time, carrying three machines'
output about 45 m to the harbor at 4.5 m/s x 20. **Fix 2:** the Redwood Coast forklift carries 36
at 6.0 m/s (`Balance.FORKLIFT_BY_REGION`; the Maple Highlands forklift is unchanged). Income
+29% at the forklift pad, +66% at skidder2, +14-17% at builders/belt_ds/jack3 (max). The deck saw
output still sits full: deckboards have only the harbor counter to go to until the shipwrights.

Tried and reverted: redwood mill 1.5 -> 1.0 s. Its input stayed 99-100% full and income moved
under 1% (builders 29,122 -> 29,156, belt_ds 34,635 -> 34,447 $/min); the forklift and
shipwrights are the limit, not the mill. Also reverted: r4_jack2 140K -> 155K. r4_belt_rd
*requires* r4_jack2, so a cost cannot put the forklift first (see "Design decisions").

| Scripted player (full valley) | Before | After |
|---|---|---|
| Deck Saw after the cashier | 112 s (my earlier 1.7-2.5 min estimate held) | 110 s |
| Gaps Deck Saw .. forklift | 112, 120, 116, 122 s | 110, 120, 116, 122 s |
| Median gap / longest gap | 122 s / 376 s (Lighthouse) | 122 s / 378 s (Lighthouse) |
| Lighthouse bought -> finished | 2,546 -> 3,505 s (959 s) | 2,540 -> 2,707 s (167 s) |
| Whole valley | 58.4 min | 45.1 min |

The scripted player earns the Redwood pads mostly from carried-in income, so the forklift
change hardly shows in these gaps; it shows in the automation table.

Automation (360 s window; decksaw .. belt_rd have no carrier, identical code before and after):
**Valley 4, max upgrades** (before -> after)

| Checkpoint | $/min | Worker idle % | Longest full (pile) |
|---|---|---|---|
| r4_decksaw | 0 -> 0 | 100.0 -> 100.0 | 336 s (redmill_out) -> 336 s (redmill_out) |
| r4_jack2 | 0 -> 0 | 100.0 -> 100.0 | 349 s (redmill_in) -> 349 s (redmill_in) |
| r4_belt_rd | 0 -> 0 | 100.0 -> 100.0 | 339 s (decksaw_out) -> 339 s (decksaw_out) |
| r4_forklift | 5,486 -> 7,087 | 74.1 -> 73.9 | 306 s (decksaw_out) -> 301 s (decksaw_out) |
| r4_mastlathe | 5,486 -> 6,982 | 74.1 -> 74.0 | 306 s (decksaw_out) -> 307 s (decksaw_out) |
| r4_orders | 5,486 -> 7,035 | 74.1 -> 73.3 | 323 s (decksaw_out) -> 323 s (decksaw_out) |
| r4_skidder2 | 6,967 -> 11,565 | 81.3 -> 80.1 | 161 s (redmill_in) -> 221 s (redmill_in) |
| r4_builders | 29,122 -> 33,341 | 58.5 -> 56.4 | 72 s (mastlathe_out) -> 92 s (mastlathe_out) |
| r4_belt_ds | 34,635 -> 40,279 | 58.7 -> 55.0 | 52 s (redmill_in) -> 40 s (mastlathe_out) |
| r4_jack3 | 34,534 -> 40,324 | 66.6 -> 66.1 | 42 s (mastlathe_in) -> 42 s (mastlathe_in) |
| r4_slipway2 | 34,459 -> 37,129 | 67.4 -> 67.2 | 59 s (mastlathe_in) -> 76 s (mastlathe_in) |
| r4_lighthouse | 29,261 -> 13,372 | 64.6 -> 75.6 | 154 s (mastlathe_in) -> 130 s (mastlathe_in) |

**Valley 4, cap upgrades** (before -> after)

| Checkpoint | $/min | Worker idle % | Longest full (pile) |
|---|---|---|---|
| r4_decksaw | 0 -> 0 | 100.0 -> 100.0 | 330 s (redmill_in) -> 330 s (redmill_in) |
| r4_jack2 | 0 -> 0 | 100.0 -> 100.0 | 330 s (redmill_in) -> 330 s (redmill_in) |
| r4_belt_rd | 0 -> 0 | 100.0 -> 100.0 | 334 s (decksaw_out) -> 334 s (decksaw_out) |
| r4_forklift | 4,345 -> 5,346 | 72.9 -> 70.7 | 299 s (decksaw_out) -> 293 s (decksaw_out) |
| r4_mastlathe | 4,322 -> 5,255 | 72.9 -> 70.7 | 299 s (decksaw_out) -> 293 s (decksaw_out) |
| r4_orders | 4,391 -> 5,252 | 71.8 -> 70.7 | 316 s (decksaw_out) -> 199 s (decksaw_out) |
| r4_skidder2 | 6,952 -> 9,386 | 80.1 -> 78.6 | 182 s (mastlathe_out) -> 136 s (mastlathe_out) |
| r4_builders | 20,459 -> 16,555 | 56.2 -> 57.3 | 112 s (mastlathe_out) -> 122 s (mastlathe_out) |
| r4_belt_ds | 6,773 -> 25,850 | 63.4 -> 51.9 | 190 s (mastlathe_out) -> 59 s (mastlathe_out) |
| r4_jack3 | 6,796 -> 25,763 | 72.9 -> 65.1 | 193 s (mastlathe_in) -> 62 s (mastlathe_in) |
| r4_slipway2 | 22,227 -> 25,720 | 68.5 -> 65.6 | 179 s (mastlathe_in) -> 63 s (mastlathe_in) |
| r4_lighthouse | 12,987 -> 8,564 | 66.5 -> 67.4 | 172 s (mastlathe_in) -> 122 s (mastlathe_in) |


The cargo orders work: orders 1 -> 5 complete in 360 s once masts are fed. One order stall: from
r4_orders until r4_skidder2 nothing feeds the mast lathe, so order 1 waits on 3 masts for the
whole run unless the player hand-feeds red logs to the mast lathe.

## Frost Peaks (Valley 5)

**Root cause 1: the Summit Observatory starves (logic flaw).** The same belt pattern as Maple
Highlands: the kiln belts take most of the dry lumber, and the sled belt and guitar belt empty
those outputs before the snowcat can load for the site. The snowcat also shared its loads with
the counters and the train. Measured: 5/200 dry lumber, 0/20 sleds, 0/10 guitars in 360 s. In a
scripted run from the third kiln, the Observatory was bought at 390 s and stood at 60/200 dry
lumber, 0/20 sleds, 0/10 guitars after 43 min. **Valley 5 could not finish on its own.**
First attempt (rejected): pausing the belts cut income from 82,380 to 28,762 $/min.
**Fix 1:** the kiln-1, sled and guitar belts keep `Balance.SITE_RESERVE` (dry lumber 20, sled 4,
guitar 2) while the Observatory needs the item. The snowcat takes dry lumber, sleds and guitars to
the Observatory first while it needs them (skis keep rotating: the snowcat is the sled shop's only
ski supply).

| Observatory (scripted, starting at the third kiln) | Bought | Finished |
|---|---|---|
| Before | 390 s | never (60/200, 0/20, 0/10 at 3,000 s) |
| Reserve only | 380 s | 1,914 s (25.6 min after) |
| Reserve + snowcat priority (shipped) | 414 s | 927 s (8.5 min after) |

Automation at the Observatory checkpoint (max): 82,380 -> 88,931 $/min, worker idle 42.4 ->
39.2% (reserve only; with the snowcat priority not re-run in auto mode).

**Root cause 2: the opening.** Nothing sells in Frost Peaks before the Ski Lodge (pad 6), and the
automation earns $0 until the snowcat (pad 13). The player waited 97 s for the $230K kiln, then
the next four pads were 61-99% waiting; the lodge came at 500 s. **Fix 2:** cheaper opening
pads: kiln 230K -> 80K, grove2 170K -> 60K, office 180K -> 70K, jack1 250K -> 90K, ski lodge
280K -> 110K.

| Scripted player | Before | After |
|---|---|---|
| Gateway -> kiln (pure waiting) | 97 s | 40 s |
| Ski Lodge (first buyer) at | 500 s | 248 s |
| Gaps kiln .. lodge | 97, 73, 95, 73, 162 s | 40, 27, 30, 84, 67 s |
| Pads in the first 10 min | 5 | 7 |
| Gaps lodge .. snowcat | 135-224 s | 139-218 s |

## Birch Bend leftovers (from the first pass)

- **Canoe dock full 71-80% at jack3 (fixed).** The barge carried 0.32 canoes/s against about
  0.42 built. `Balance.EXPORTS.barge.cap` 6 -> 12 (two layers on its 3x2 bed; screenshot checked).
  Dock full 80 -> 14% (max), 72 -> 0% (cap); jack3 income 15,195 -> 20,850 $/min (max) and
  11,460 -> 15,687 (cap).
- **Flume crews idle 52-58% (not changed, design decision).** With the Forester Camp at 1 crew
  instead of 3 (scratch copy only), income is unchanged (21,015 vs 20,850 $/min max; 15,726 vs
  15,687 cap): the two extra crews add nothing. Even then the remaining flume crews stand 50-66%,
  because one lathe-press-boat line takes about 3.5-4 logs/s. Birches never run out
  (`no_tree` 0%), so the camp's faster regrow does nothing either.

## Not fixed: design decisions for Mats

1. **More lumberjacks than machines, in every valley.** Measured idle crews at the last
   checkpoint (max): Birch Bend flume crews 63-88%, Maple Highlands 42-61%, Redwood Coast 71-100%
   (redwood mill input 97-100% full at every checkpoint), Frost Peaks 37-49%. Options: fewer crews
   per pad, a second first machine (a second lathe / mill), or accept it as the idle-game look.
2. **Redwood Coast earns $0 from automation for pads 9-11** (Deck Saw, 2 Lumberjacks, Mill to
   Deck Saw belt): the forklift (pad 12) is the first carrier, and the two new crews stand at a
   full mill 100% of the time. Fix needs a requirement change: r4_forklift after r4_decksaw, or
   r4_jack2 after r4_forklift.
3. **Frost Peaks earns $0 from automation until the snowcat (pad 13)**, and nothing sells before
   the Ski Lodge (pad 6, requires r5_jack1). Moving the lodge to require only the kiln would
   remove the remaining 84 + 67 s of waiting before it.
4. **Redwood cargo orders wait on masts** from r4_orders until r4_skidder2 (nobody feeds the mast
   lathe). Option: let masts join orders only once a crew feeds the mast lathe.
5. **Forester Camp:** keep 3 crews + faster regrow (measured: neither adds income), cut to 1, or
   give it its own lathe.

## Open / unverified

- In two long scripted Frost Peaks runs the player stopped dead at (53.7, -85.6), the north-west
  corner of the sled shop, for over an hour while walking to the luthier pad. Started from that
  spot, or walking the same line in a short run, it passes in 6.5 s. Not reproduced; worth one
  manual check on the phone (walk from the Ski Lodge straight south to the luthier pad).
- One baseline run also lost time when the bot rode a handcar tile out of the valley; the probe
  now brings it back. Frost Peaks pad gaps after the snowcat therefore come from runs that ended
  early (12-14 pads); the Observatory was measured separately.
- Not tested on a physical phone.

## Changed (this pass)

`scripts/Balance.gd` (SITE_RESERVE, FORKLIFT_BY_REGION, barge cap 12, planer 1.1 s, r3_beamsaw
8K, Frost opening costs), `scripts/Conveyor.gd` (optional `hold`), `scripts/World.gd` (Maple
reserves, forklift site-first), `scripts/FrostPeaks.gd` (Observatory reserves, snowcat priority),
`scripts/RedwoodCoast.gd` (Lighthouse first), `scripts/Worker.gd` (site scoring from Valley 3,
per-valley forklift), `docs/balance/unlocks_regions.csv` (costs and effect text),
`tests/pacing_probe.gd` (generic valleys, scripted player, station), and `tests/capture.gd` (m3
Lighthouse check accepts an already-bought cable-car pad: the Lighthouse now finishes during the
bot's automation phase, and the bot walks over the pad and buys it).
