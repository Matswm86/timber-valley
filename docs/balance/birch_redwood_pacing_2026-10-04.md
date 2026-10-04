# Birch Bend stalls and the Redwood Coast opening: measured, fixed, re-measured (2026-10-04)

Mats' playtest: Birch Bend "fills up, especially birches and veneer, too much waiting and
stalling", and the Redwood Coast opening has "too little action, too much waiting".

## How it was measured

`tests/pacing_probe.gd` (+ `.tscn`), headless, Godot 4.6.2, `--fixed-fps 60`, `Engine.time_scale`
2. All numbers below are my measurements with this probe.

- **Birch Bend (`PROBE_MODE=v2`)**: a save that owns every pad up to the checkpoint (UNLOCKS
  order), piles empty, region upgrades 0, player parked at the Birch Bend handcar stop with no
  input. 360 s run; the summary covers the steady-state window 120-360 s. It tracks every pile
  (share of time at capacity, the longest stretch at capacity, and items in and out, counted on
  each push and pop) and each worker's state each frame: working, `blocked` (standing at a full
  drop with a load), `no_tree`, or `starved` (at an empty source). Idle % = blocked + no_tree +
  starved. Global upgrades: `cap` (backpack 4, the rest 3) and `max` (all at max, the level the
  2026-10-01 model assumes for Valley 2).
- **Redwood Coast (`PROBE_MODE=v4`)**: Valleys 1-3 done, `r4_crossing` just paid, $0, global
  upgrades max. A scripted player follows the Redwood guide (`RedwoodCoast.goal`: chop, feed the
  mill, carry timber, stock the counter, collect cash) and walks to the next opening pad as soon
  as it can pay for it. Carried-in income is the measured ledger from
  `rebalance_2026-10-01.md`: "model" = V1 95.1 + V2 214.5 + V3 741.6 $/s (region upgrades 3/3/3)
  plus 97.5 $/s rent; "low" = V1 95.1 + V2 139.4 + V3 457.6 $/s (no region upgrades) plus
  75 $/s rent. "Waiting" = no useful action on offer (before the mill, only its pad).

## Birch Bend: root cause

1. **One veneer carrier with a count-based load.** The lathe turns 2 logs into 6 veneer, but a
   carrier took 12 veneer per trip (cap levels), one item per 0.09 s. It drained ~1.4 veneer/s
   while one lumberjack supplies about 4 veneer/s. Before the fix at the first checkpoint, the
   lathe output was full 84% of the time, the lathe input 97%, and the lumberjack stood blocked
   73% of the time.
2. **The counter could not sell more**: once the carrier brought more, the veneer counter
   saturated at 3-5 veneer/s (20-shopper cap, long lane).
3. **The flume released one log per 0.5 s** (2 logs/s), and logs in the water hold room in the
   lathe input. At the last checkpoint the lathe input ran down to 0-10 logs while five flume
   crews stood at a full 16-log chute (sampled every 0.5 s).
4. **More lumberjacks than one lathe can use** (structural, not changed): after
   r2_jack2/r2_jack3, 3-6 crews can cut about 6-7 logs/s, while lathe + belt + presses + boat
   workshop + barge take about 3.5-4 logs/s. Birches never limit (`no_tree` 0% in every run), so
   the Forester Camp's faster regrow does nothing. This matches GDD open question 10.

## Birch Bend: changes (all gated by item type or Valley 2 data; Valleys 1, 3, 4, 5 unchanged)

| Where | Change |
|---|---|
| `Balance.CARRY_MULT` (new) | `{"veneer": 3}`: workers, the player and belts move 3 veneer per carried slot |
| `Balance.SHOPPER_QTY_MULT` (new) | `{"veneer": 5}`: a veneer shopper buys 5x the usual amount |
| `Balance.FLUME` | speed 3.5 -> 7.0 m/s, spacing 0.5 -> 0.25 s (2 -> 4 logs/s) |
| `Balance.MACHINES.lathe` | cycle 1.2 -> 0.8 s |
| `Balance.UNLOCKS r2_jack2` | 9,500 -> 13,500, so a cheapest-first player buys the flume crews after belt_lp (11,000) and hauler2 (13,000) |
| `Worker.gd` | carry cap x CARRY_MULT of the carried/source item; load and unload a bundle per tick |
| `Player.gd` | `capacity()` x CARRY_MULT of the carried item |
| `Zone.gd` | DROP/PICK squares move a bundle per tick for those items |
| `Conveyor.gd` | a belt slot carries a stacked bundle of CARRY_MULT items |
| `Shop.gd` | shopper amount x SHOPPER_QTY_MULT |
| `Customer.gd` | takes a bundle per tick (same counter time per shopper as before) |

## Birch Bend: before / after (window 120-360 s)

Idle % = all workers. "Longest full" = the longest stretch any pile sat at capacity.

| Levels | Checkpoint | $/min | Worker idle % | Longest full (pile) | Lathe in full % | Lathe out full % | Flume chute full % |
|---|---|---|---|---|---|---|---|
| cap | hauler1 | 830 -> 2,400 | 36.5 -> 0.2 | 8 s (lathe in) -> 6 s (lathe out) | 97 -> 0 | 84 -> 66 | - |
| cap | jack2 | 772 -> 2,362 | 69.9 -> 55.2 | 88 s -> 28 s (flume) | 88 -> 70 | 85 -> 70 | 100 -> 99 |
| cap | hauler2 | 3,204 -> 5,280 | 54.1 -> 33.8 | 27 s -> 11 s (flume) | 70 -> 26 | 61 -> 48 | 97 -> 91 |
| cap | jack3 | 5,357 -> 11,460 | 77.9 -> 52.5 | 137 s -> 48 s (flume) | 74 -> 7 | 57 -> 20 | 100 -> 97 |
| max | hauler1 | 1,302 -> 3,975 | 36.3 -> 1.8 | 10 s (lathe in) -> 3 s (lathe out) | 72 -> 0 | 82 -> 1 | - |
| max | jack2 | 1,068 -> 3,600 | 74.7 -> 58.3 | 70 s (flume) -> 21 s (lathe out) | 87 -> 68 | 86 -> 70 | 100 -> 99 |
| max | hauler2 | 4,653 -> 7,110 | 60.8 -> 41.2 | 41 s (flume) -> 15 s (veneer counter) | 71 -> 30 | 62 -> 52 | 99 -> 91 |
| max | jack3 | 7,872 -> 15,195 | 80.7 -> 58.2 | 149 s -> 26 s (flume) | 66 -> 11 | 57 -> 27 | 100 -> 98 |

Lumberjack idle (blocked) per crew, cap, jack3: [45, 97, 94, 94, 97, 97]% -> [2, 66, 64, 73, 84, 88]%.
The lumberjack next to the lathe now works all the time. The flume crews still stand 64-92% of
the time because of item 4 above. The "jack2" rows keep the old purchase order (no press line
yet). With the new r2_jack2 cost, a cheapest-first player reaches the flume crews at the
"hauler2" state.

Side effect: Birch Bend income is 1.5-3x higher at every checkpoint, so Valley 2's ledger
(which keeps paying later) rises from ~131 to ~253 $/s at the last checkpoint (max levels, region
upgrades 0). Valley 2 gets shorter than the 35-min target in GDD question 8. Valleys 3-5 get
slightly faster through the carried-in income. Not re-modelled in `rebalance_sim.py`.

## Redwood Coast opening: root cause

With carried-in income of about 1,000-1,150 $/s, the opening pads were paid almost entirely by
the old valleys. Hand work (chop -> mill -> counter) earned 98-108 $/s, 8-11% of income. The
counter takes about 1 timber/s, and trees were never short (4-6 of 6 ready at every sample). So
a bigger grove, faster regrow or fewer hits would not change the pace. The first 72-108 s after
the crossing had nothing to do but wait for the $80K mill.

## Redwood Coast: changes (Balance.UNLOCKS and unlocks_regions.csv)

| Pad | Before | After |
|---|---|---|
| r4_redmill | 80,000 | 20,000 |
| r4_grove2 | 64,000 | 40,000 |
| r4_office | 67,000 | 45,000 |
| r4_jack1 | 93,000 | 55,000 |
| r4_skidder1 | 100,000 | 65,000 |
| r4_harbor | 110,000 | 75,000 |
| r4_cashier | 120,000 | 85,000 |

From r4_decksaw (130,000) on, nothing changes. Redwood total -249,000 of 3.90M.

## Redwood Coast: before / after (scripted player, crossing paid at t = 0)

| Pad | Model before gap | Model after gap | Low before gap | Low after gap |
|---|---|---|---|---|
| r4_redmill | 72.0 s (all waiting) | 19.0 s (all waiting) | 108.0 s (all waiting) | 29.0 s (all waiting) |
| r4_grove2 | 57.7 | 38.7 | 80.4 | 54.0 |
| r4_office | 58.5 | 36.6 | 157.0 | 73.2 |
| r4_jack1 | 74.2 | 44.8 | 34.3 | 47.9 |
| r4_skidder1 | 78.4 | 51.0 | 109.1 | 73.4 |
| r4_harbor | 86.6 | 63.1 | 126.0 | 83.4 |
| r4_cashier | 93.4 | 65.2 | 129.3 | 94.9 |
| **Crossing to cashier** | **521 s (8.7 min)** | **318 s (5.3 min)** | **744 s (12.4 min)** | **456 s (7.6 min)** |
| Waiting share | 14% | 6% | 15% | 6% |
| Hand income | 44.0K in 521 s | 29.2K in 318 s | 69.0K in 744 s | 44.4K in 456 s |

(The low-income office/jack1 pair is lumpy: the bot walks over the next pad on its way and part-pays it.)

The next pad, r4_decksaw at 130K, is unchanged. At the carried-in income above it comes about
1.7-2.5 min after the cashier (my calc, not probed).

## Re-run

```
PROBE_MODE=v2 PROBE_CP=jack3 PROBE_LV=max PROBE_SECONDS=360 PROBE_FROM=120 \
  ~/MWM/data/tools/godot/godot --headless --fixed-fps 60 --audio-driver Dummy --path . res://tests/pacing_probe.tscn
PROBE_MODE=v4 PROBE_LEDGER=low ~/MWM/data/tools/godot/godot --headless --fixed-fps 60 --audio-driver Dummy --path . res://tests/pacing_probe.tscn
```
Parallel runs share `user://save.json` (the game autosaves every 8 s); harmless for the probe.

## Follow-up (same day): other valleys and Birch Bend leftovers

See `valleys_3_5_audit_2026-10-04.md`. Birch Bend: barge 6 -> 12 canoes per trip (canoe dock full
80 -> 14% at the Forester Camp, +37% income there). The flume crews' idle time is a design decision
(the Forester Camp's extra crews add no measurable income).
