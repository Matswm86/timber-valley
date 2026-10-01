"""Timber Valley cost rebalance for Valleys 2-6 (my calc), 2026-10-01.

Derives every pad and region-upgrade cost after Valley 1 from income, instead of the old
fixed per-valley scale. Valley 1 is not touched: the run starts the moment the Lodge is paid,
with Valley 1 earning what the headless probe measured.

How costs are derived: a casual player walks the pad list in order. When they reach pad i the
model sets cost_i = income_now x wait_i, where wait_i is a target wait (minutes) from the
per-valley schedule below, times one scale factor per valley. The scale factor is found by
bisection so the casual player's valley time hits TARGET_MIN. Region upgrades are bought
greedily when one costs <= UPG_RATIO x the next pad, and they cost time too, so the derived
waits come out a little longer than the schedule; the bisection accounts for that.

Income sources:
  * MEASURED (Valleys 1-3): automated $/s per valley from tests/econ_probe.gd (headless Godot,
    --fixed-fps 60, 120 s warm-up, 180 s window, player parked at the handcar stop, global
    upgrades at max). The probe counts collected coins + coins waiting at the till.
  * MODELED (Valleys 4-5, not built yet): the old CSV income weights, scaled so each valley
    adds V4 = 2.2x and V5 = 2.0x what Valley 3 / Valley 4 added. Re-measure when built.
  * HAND income (all valleys): my estimate, about 30% of the first machine's $/s at max
    upgrades for an attentive player; a casual player gets HAND_EFF of that.
Sleeping valleys pay their ledger (= their measured awake rate), so all valleys sum.

Run: python3 docs/balance/rebalance_sim.py
"""
import math
import statistics

UPG_RATIO = 0.45          # buy a region upgrade when it costs <= this x the next pad
CASUAL = {"hand": 0.5, "overhead_s": 10.0}    # half the hand work, 10 s to walk to each pad
ATTENTIVE = {"hand": 1.0, "overhead_s": 4.0}
TARGET_MIN = {2: 35.0, 3: 44.0, 4: 53.0, 5: 63.0, 6: 4.5}
MAX_WAIT_MIN = 4.5        # no single target wait above this, landmarks included

# Valley 1 after the Lodge (measured): global upgrades at 0 = 28.9 $/s, at the capture-bot
# levels (backpack 4, others 3) = 66.9 $/s, at max = 93.4-96.4 $/s (11 runs, mean 95).
# The casual player arrives with the capture-bot levels; the rest of the Valley 1 office is
# bought in Valley 2 (below), which lifts Valley 1 to 95 $/s.
V1_AUTO = 66.9
# One-off buys available from the start of Valley 2: (name, cost, valley-1 auto $/s, hand x).
# Costs = base x 1.75^level for the levels from the capture-bot save to max (Balance.UPGRADES).
# Hand x = multiplier on hand income (ext. backpack/shoes/axe from the Riverside Office:
# Balance.GLOBAL_EXT, my guess of +4% hand each).
V2_EXTRAS = [("g_backpack5", 276, 0, 1.03), ("g_backpack6", 492, 0, 1.03),
             ("g_shoes4", 214, 0, 1.03), ("g_shoes5", 375, 0, 1.03),
             ("g_axe4", 188, 0, 1.03), ("g_axe5", 328, 0, 1.03),
             ("g_machines4", 482, 4, 1.0), ("g_machines5", 844, 4, 1.0),
             ("g_workers4", 643, 4.5, 1.0), ("g_workers5", 1125, 4.5, 1.0),
             ("g_prices4", 804, 5.5, 1.0), ("g_prices5", 1407, 5.5, 1.0)]
V2_EXTRAS += [(f"x_backpack{i + 7}", round(2500 * 1.75 ** i), 0, 1.04) for i in range(4)]
V2_EXTRAS += [(f"x_shoes{i + 6}", round(3000 * 1.75 ** i), 0, 1.04) for i in range(2)]
V2_EXTRAS += [(f"x_axe{i + 6}", round(2000 * 1.75 ** i), 0, 1.04) for i in range(3)]

# Region upgrade effect per level on that valley's automated income (measured on Valley 2
# complete, base 140 $/s): saws 5 = 186 (+6.6%/lvl), crew 5 = 153 (+1.8%/lvl), fame 5 = 208
# (+9.7%/lvl). Fitted multiplicative: 3,3,3 model 219 vs measured 215; 5,5,5 model 284 vs 281.
RUP_PER_LEVEL = {"saws": 0.06, "crew": 0.015, "fame": 0.09}
# Region upgrade base cost as a multiple of the valley gateway cost; growth 1.8, max 5.
RUP_BASE_X = {"saws": 0.8, "crew": 0.5, "fame": 1.2}   # crew is the weakest (+1.8%/lvl), so cheapest
RUP_GROWTH = 1.8
RUP_MAX = 5

# (id, auto $/s added (measured/modeled), attentive hand $/s added, wait weight)
# Wait weight 1.0 = a normal pad; small things (grove, office) lighter, landmarks heavier.
R2 = [
    ("r2_bridge", 0.0, 0.0, 0.75),
    ("r2_lathe", 0.0, 30.0, 0.85),
    ("r2_grove2", 0.0, 3.0, 0.6),
    ("r2_office", 0.0, 0.0, 0.6),
    ("r2_jack1", 0.0, 4.0, 0.8),
    ("r2_hauler1", 0.0, 0.0, 0.85),     # veneer to counter: coins wait at the till
    ("r2_flume", 0.0, 3.0, 0.9),
    ("r2_cashier", 22.3, -8.0, 0.9),    # till now automated (probe n=6..9: 22.1-22.4)
    ("r2_press", 0.0, 8.0, 1.0),
    ("r2_jack2", 10.0, 0.0, 1.0),
    ("r2_belt_lp", 15.0, 0.0, 1.0),
    ("r2_hauler2", 25.4, -6.0, 1.0),    # probe n=12: 72.7
    ("r2_press2", 5.9, 0.0, 1.05),      # n=13: 78.6
    ("r2_boatshop", 0.0, 10.0, 1.1),
    ("r2_barge", 4.4, 0.0, 1.15),       # n=15: 83.0
    ("r2_belt_pb", 29.0, -5.0, 1.2),
    ("r2_belt_bb", 29.0, -5.0, 1.2),    # n=17: 141.0
    ("r2_jack3", 0.0, 0.0, 1.25),       # n=18: 140.4 (adds nothing: barge-bound)
    ("r2_boathouse", 0.0, 0.0, 1.9),    # landmark
]
R3 = [
    ("r3_gate", 0.0, 0.0, 0.75),
    ("r3_beamsaw", 0.0, 44.0, 0.85),
    ("r3_grove2", 0.0, 4.0, 0.6),
    ("r3_office", 0.0, 0.0, 0.6),
    ("r3_jack1", 0.0, 40.0, 0.8),       # player carries the lumberjack's beams
    ("r3_forklift1", 142.3, -84.0, 0.85),  # probe n=6: 142.3 (beam saw runs flat out)
    ("r3_cashier", 0.0, 0.0, 0.9),      # n=7: 142.5
    ("r3_planer", 0.8, 10.0, 1.0),      # n=8: 143.3
    ("r3_jack2", -53.3, 0.0, 1.0),      # n=9: 90.0 (income DROPS, see the doc)
    ("r3_house1", 14.7, 0.0, 1.0),      # n=10: 104.7 (site pre-filled in the probe)
    ("r3_belt_bp", 103.5, 0.0, 1.0),    # n=11: 208.2
    ("r3_kitfactory", 5.8, 5.0, 1.05),  # n=12: 214.0
    ("r3_house2", 5.3, 0.0, 1.0),
    ("r3_rail", 5.3, 0.0, 1.1),         # n=14: 224.7
    ("r3_belt_kit", 136.5, 0.0, 1.1),   # n=15: 361.2
    ("r3_house3", 1.0, 0.0, 1.1),
    ("r3_jack3", 1.1, 0.0, 1.15),       # n=17: 363.3
    ("r3_rail2", 58.6, 0.0, 1.15),      # n=18: 421.9
    ("r3_house4", 17.9, 0.0, 1.2),
    ("r3_house5", 17.8, 0.0, 1.2),      # n=20: 457.6
    ("r3_clocktower", 0.0, 0.0, 1.9),   # n=21 with region upgrades 3,3,3: 741.6
]
R4_W = [("r4_crossing", 0, 0, 0.75), ("r4_redmill", 0, 95, 0.85), ("r4_grove2", 0, 6, 0.6),
        ("r4_office", 0, 0, 0.6), ("r4_jack1", 20, 0, 0.8), ("r4_skidder1", 30, 0, 0.85),
        ("r4_harbor", 20, 0, 0.9), ("r4_cashier", 10, -20, 0.9), ("r4_decksaw", 20, 20, 1.0),
        ("r4_jack2", 35, 0, 1.0), ("r4_belt_rd", 35, 0, 1.0), ("r4_forklift", 30, -20, 1.0),
        ("r4_mastlathe", 25, 10, 1.05), ("r4_slipway", 60, 0, 1.1), ("r4_orders", 40, 0, 1.1),
        ("r4_skidder2", 50, 0, 1.15), ("r4_builders", 60, -10, 1.15), ("r4_belt_ds", 50, 0, 1.2),
        ("r4_jack3", 45, 0, 1.2), ("r4_slipway2", 80, 0, 1.25), ("r4_lighthouse", 0, 0, 1.9)]
R5_W = [("r5_cablecar", 0, 0, 0.75), ("r5_kiln", 0, 115, 0.85), ("r5_grove2", 0, 8, 0.6),
        ("r5_office", 0, 0, 0.6), ("r5_jack1", 45, 0, 0.8), ("r5_skilodge", 50, 0, 0.85),
        ("r5_skiworks", 40, 20, 0.9), ("r5_cashier", 25, -25, 0.9), ("r5_jack2", 80, 0, 1.0),
        ("r5_kiln2", 70, 0, 1.0), ("r5_belt_ks", 70, 0, 1.0), ("r5_sledshop", 60, 10, 1.05),
        ("r5_snowcat", 90, -20, 1.05), ("r5_luthier", 80, 10, 1.1), ("r5_express_r5", 120, 0, 1.1),
        ("r5_belt_sl", 90, -10, 1.15), ("r5_jack3", 90, 0, 1.15), ("r5_kiln3", 120, 0, 1.2),
        ("r5_observatory", 0, 0, 1.9)]
R6 = [("cap_station", 0, 0, 1.0)]

# Costs before this rebalance (Balance.gd / unlocks_regions.csv as of 2026-10-01 morning).
OLD = {
    "r2_bridge": 11000, "r2_lathe": 13000, "r2_grove2": 6700, "r2_office": 8000, "r2_jack1": 13000,
    "r2_hauler1": 16000, "r2_flume": 21000, "r2_cashier": 19000, "r2_press": 33000, "r2_jack2": 40000,
    "r2_belt_lp": 45000, "r2_hauler2": 51000, "r2_press2": 74000, "r2_boatshop": 94000, "r2_barge": 110000,
    "r2_belt_pb": 120000, "r2_belt_bb": 130000, "r2_jack3": 150000, "r2_boathouse": 210000, "r3_gate": 82000,
    "r3_beamsaw": 99000, "r3_grove2": 49000, "r3_office": 66000, "r3_jack1": 99000, "r3_forklift1": 130000,
    "r3_cashier": 130000, "r3_planer": 230000, "r3_jack2": 260000, "r3_house1": 250000, "r3_belt_bp": 330000,
    "r3_kitfactory": 490000, "r3_house2": 370000, "r3_rail": 660000, "r3_belt_kit": 700000, "r3_house3": 490000,
    "r3_jack3": 780000, "r3_rail2": 900000, "r3_house4": 660000, "r3_house5": 820000, "r3_clocktower": 1500000,
    "r4_crossing": 270000, "r4_redmill": 370000, "r4_grove2": 160000, "r4_office": 210000, "r4_jack1": 320000,
    "r4_skidder1": 480000, "r4_harbor": 530000, "r4_cashier": 430000, "r4_decksaw": 800000, "r4_jack2": 930000,
    "r4_belt_rd": 1100000, "r4_forklift": 1200000, "r4_mastlathe": 1500000, "r4_slipway": 2100000, "r4_orders": 1600000,
    "r4_skidder2": 2400000, "r4_builders": 2700000, "r4_belt_ds": 2900000, "r4_jack3": 3200000, "r4_slipway2": 4000000,
    "r4_lighthouse": 5300000, "r5_cablecar": 850000, "r5_kiln": 1200000, "r5_grove2": 510000, "r5_office": 680000,
    "r5_jack1": 1000000, "r5_skilodge": 1400000, "r5_skiworks": 1900000, "r5_cashier": 1400000, "r5_jack2": 2600000,
    "r5_kiln2": 3400000, "r5_belt_ks": 3800000, "r5_sledshop": 5100000, "r5_snowcat": 6000000, "r5_luthier": 7300000,
    "r5_express_r5": 7700000, "r5_belt_sl": 8500000, "r5_jack3": 9400000, "r5_kiln3": 11000000, "r5_observatory": 17000000,
    "cap_station": 25000000,
}


def scale_modeled(pads, add_total):
    """Old CSV income weights rescaled so the valley adds add_total $/s in all."""
    s = sum(p[1] for p in pads)
    return [(i, a * add_total / s, h, w) for i, a, h, w in pads]


def nice(c):
    """Two significant figures."""
    if c < 100:
        return int(round(c))
    e = 10 ** (int(math.log10(c)) - 1)
    return int(round(c / e) * e)


def wait_schedule(n, weights):
    """Target wait in minutes before scaling: ramps 1.0 -> 2.0 across the valley, x weight."""
    out = []
    for k, w in enumerate(weights):
        ramp = 1.0 + 1.0 * k / max(n - 1, 1)
        out.append(ramp * w)
    return out


def rup_mult(levels):
    m = 1.0
    for k, lv in levels.items():
        m *= 1.0 + RUP_PER_LEVEL[k] * lv
    return m


def run(regions, costs, rup_base, player, derive=None, scale=None):
    """Simulate (or derive costs, when derive=region id). Returns per-region stats and events.
    costs: dict id -> cost (used for regions not being derived; written for the derived one)."""
    t = 0.0
    money = 0.0
    auto = {1: V1_AUTO}
    hand = {}
    rlv = {}
    events = []
    stats = {}
    bought = set()
    owned = set()
    hmult = [1.0]
    for r, pads in regions:
        auto.setdefault(r, 0.0)
        hand[r] = 0.0
        rlv[r] = {"saws": 0, "crew": 0, "fame": 0}
        start = t
        weights = [p[3] for p in pads]
        sched = wait_schedule(len(pads), weights)
        for k, (pid, da, dh, _w) in enumerate(pads):
            while True:
                rate = sum(auto[x] * rup_mult(rlv.get(x, {})) for x in auto) + player["hand"] * hmult[0] * max(hand[r], 0.0)
                if derive == r:
                    cost = nice(rate * min(sched[k] * scale, MAX_WAIT_MIN) * 60.0)
                    costs[pid] = cost
                cost = costs[pid]
                cands = []
                office = f"r{r}_office" in owned
                if r in rup_base and office:
                    for key, base in rup_base[r].items():
                        lv = rlv[r][key]
                        if lv < RUP_MAX:
                            c = nice(base * RUP_GROWTH ** lv)
                            if c <= UPG_RATIO * cost:
                                cands.append((c, key))
                if r == 2:
                    for name, c, dv1, hx in V2_EXTRAS:
                        if name.startswith("x_") and not office:
                            continue   # extended levels are sold at the Riverside Office
                        if name not in bought and c <= UPG_RATIO * cost:
                            cands.append((c, name))
                target = min(cands)[0] if cands else cost
                t_before = t
                if money < target:
                    t += (target - money) / rate
                    money = target
                t += player["overhead_s"]
                money -= target
                money += rate * player["overhead_s"]
                if cands:
                    c, key = min(cands)
                    if key in rlv[r]:
                        rlv[r][key] += 1
                        events.append((t, r, f"r{r}_{key}{rlv[r][key]}", c, t - t_before, rate))
                    else:
                        bought.add(key)
                        ex = next(x for x in V2_EXTRAS if x[0] == key)
                        auto[1] += ex[2]
                        hmult[0] *= ex[3]
                        events.append((t, r, key, c, t - t_before, rate))
                    continue
                events.append((t, r, pid, cost, t - t_before, rate))
                break
            auto[r] += da
            hand[r] += dh
            owned.add(pid)
        rate_end = sum(auto[x] * rup_mult(rlv.get(x, {})) for x in auto)
        stats[r] = {"min": (t - start) / 60.0, "cum_h": t / 3600.0, "auto_end": rate_end,
                    "levels": dict(rlv[r])}
    return stats, events


def derive_all(regions):
    costs = {}
    rup_base = {}
    done = []
    for r, pads in regions:
        lo, hi = 0.05, 20.0
        for _ in range(60):
            mid = math.sqrt(lo * hi)
            trial = dict(costs)
            # gateway cost decides the region-upgrade bases, so derive it first at this scale
            run(done + [(r, pads[:1])], trial, rup_base, CASUAL, derive=r, scale=mid)
            rb = dict(rup_base)
            if r <= 5:
                rb[r] = {k: nice(trial[pads[0][0]] * x) for k, x in RUP_BASE_X.items()}
            st, _ = run(done + [(r, pads)], trial, rb, CASUAL, derive=r, scale=mid)
            if st[r]["min"] > TARGET_MIN[r]:
                hi = mid
            else:
                lo = mid
        run(done + [(r, pads[:1])], costs, rup_base, CASUAL, derive=r, scale=lo)
        if r <= 5:
            rup_base[r] = {k: nice(costs[pads[0][0]] * x) for k, x in RUP_BASE_X.items()}
        run(done + [(r, pads)], costs, rup_base, CASUAL, derive=r, scale=lo)
        done.append((r, pads))
    return costs, rup_base


def report(regions, costs, rup_base):
    for name, pl in (("casual", CASUAL), ("attentive", ATTENTIVE)):
        st, ev = run(regions, costs, rup_base, pl)
        print(f"--- {name} player (hand x{pl['hand']}, {pl['overhead_s']:.0f} s walk per buy)")
        for r, pads in regions:
            s = st[r]
            padids = {p[0] for p in pads}
            es = [e for e in ev if e[1] == r]
            waits = [e[4] / 60.0 for e in es]
            first = [e for e in es if e[2] in padids][:2]
            t0 = es[0][0] - es[0][4]
            fw = f"{first[0][2]} {(first[0][0] - t0) / 60:.1f}"
            if len(first) > 1:
                fw += f" + {first[1][2]} {(first[1][0] - first[0][0]) / 60:.1f}"
            pt = [t0] + [e[0] for e in first[:0]] + [e[0] for e in es if e[2] in padids]
            pw = [(pt[i + 1] - pt[i]) / 60.0 for i in range(len(pt) - 1)]
            print(f"V{r}: {s['min']:5.1f} min  cum {s['cum_h']:4.2f} h  auto at end {s['auto_end']:7.0f} $/s"
                  f"  buys {len(es):2d}  median wait {statistics.median(waits):.1f} min"
                  f" (pad to pad {statistics.median(pw):.1f}, max {max(pw):.1f})"
                  f"  max {max(waits):.1f} min ({max(es, key=lambda e: e[4])[2]})  first: {fw} min")
    return run(regions, costs, rup_base, CASUAL)


def main():
    regions = build_regions()
    costs, rup_base = derive_all(regions)
    st, ev = report(regions, costs, rup_base)
    print("--- costs (id, old, new, new/old)")
    for r, pads in regions:
        tot_old = sum(OLD.get(p[0], 0) for p in pads)
        tot_new = sum(costs[p[0]] for p in pads)
        print(f"V{r} total pads: old ${tot_old:,} -> new ${tot_new:,} (x{tot_new / tot_old:.2f})"
              + (f"  region upgrades base {rup_base[r]}" if r in rup_base else ""))
        for p in pads:
            o = OLD.get(p[0], 0)
            print(f"  {p[0]:16s} {o:>10,} {costs[p[0]]:>10,}  x{costs[p[0]] / o:.2f}")
    print("--- casual purchase log (min, valley, what, cost, wait min, $/s)")
    for e in ev:
        print(f"  {e[0] / 60:6.1f}  V{e[1]}  {e[2]:16s} {e[3]:>10,}  {e[4] / 60:4.1f}  {e[5]:7.0f}")
    return costs, rup_base


def build_regions():
    v3_add = sum(p[1] for p in R3)
    r4 = scale_modeled(R4_W, 2.2 * v3_add)
    r5 = scale_modeled(R5_W, 2.0 * 2.2 * v3_add)
    return [(2, R2), (3, R3), (4, r4), (5, r5), (6, R6)]


if __name__ == "__main__":
    main()
