# Timber Valley pacing sim (my calc)

> **Superseded for Valleys 2-6 on 2026-10-01** by `rebalance_2026-10-01.md` and `rebalance_sim.py` (costs derived from measured income). Valley 1 numbers here still stand, except the modeled V1 end income: measured is 95 $/s at max upgrades, not 149.

Model, not measurement. Simplification: the model lets the extended global upgrades (capacity_x, speed_x, axe_x) be bought from the start instead of from the Riverside Office; effect on Valley 1 time is under 1 minute. Income per unlock is estimated from the code rates (cycle times, worker speed/capacity, prices) with about 0.6-0.7 utilisation. Replace the estimates with bot-measured rates after each milestone (GDD section 11). Run: save both blocks as `sim.py` and `regions.py` in one folder, then `python3 regions.py`.

## Output
```
--- efficiency 1.0
R1:   16.8 min  cum  0.28 h  auto income at end        149 $/s (8,940/min)
R2:   49.8 min  cum  1.11 h  auto income at end        495 $/s (29,730/min)
R3:   70.0 min  cum  2.28 h  auto income at end       1327 $/s (79,626/min)
R4:   90.0 min  cum  3.78 h  auto income at end       3249 $/s (194,916/min)
R5:  109.9 min  cum  5.61 h  auto income at end       6493 $/s (389,586/min)
R6:   19.8 min  cum  5.94 h  auto income at end       6493 $/s (389,586/min)
--- efficiency 0.7
R1:   24.0 min  cum  0.40 h  auto income at end        149 $/s (8,940/min)
R2:   71.1 min  cum  1.58 h  auto income at end        495 $/s (29,730/min)
R3:  100.0 min  cum  3.25 h  auto income at end       1327 $/s (79,626/min)
R4:  128.6 min  cum  5.40 h  auto income at end       3249 $/s (194,916/min)
R5:  157.1 min  cum  8.01 h  auto income at end       6493 $/s (389,586/min)
R6:   28.3 min  cum  8.48 h  auto income at end       6493 $/s (389,586/min)
scale k per region: {2: 1337, 3: 8217, 4: 26672, 5: 85463, 6: 32299646}
R2 pads total $1,164,700  upgrades bases [8019, 10693, 13366]
    [('r2_bridge', 11000), ('r2_lathe', 13000), ('r2_grove2', 6700), ('r2_office', 8000), ('r2_jack1', 13000), ('r2_hauler1', 16000), ('r2_flume', 21000), ('r2_cashier', 19000), ('r2_press', 33000), ('r2_jack2', 40000), ('r2_belt_lp', 45000), ('r2_hauler2', 51000), ('r2_press2', 74000), ('r2_boatshop', 94000), ('r2_barge', 110000), ('r2_belt_pb', 120000), ('r2_belt_bb', 130000), ('r2_jack3', 150000), ('r2_boathouse', 210000)]
R3 pads total $9,095,000  upgrades bases [49301, 65735, 82169]
    [('r3_gate', 82000), ('r3_beamsaw', 99000), ('r3_grove2', 49000), ('r3_office', 66000), ('r3_jack1', 99000), ('r3_forklift1', 130000), ('r3_cashier', 130000), ('r3_planer', 230000), ('r3_jack2', 260000), ('r3_house1', 250000), ('r3_belt_bp', 330000), ('r3_kitfactory', 490000), ('r3_house2', 370000), ('r3_rail', 660000), ('r3_belt_kit', 700000), ('r3_house3', 490000), ('r3_jack3', 780000), ('r3_rail2', 900000), ('r3_house4', 660000), ('r3_house5', 820000), ('r3_clocktower', 1500000)]
R4 pads total $32,500,000  upgrades bases [160032, 213376, 266720]
    [('r4_crossing', 270000), ('r4_redmill', 370000), ('r4_grove2', 160000), ('r4_office', 210000), ('r4_jack1', 320000), ('r4_skidder1', 480000), ('r4_harbor', 530000), ('r4_cashier', 430000), ('r4_decksaw', 800000), ('r4_jack2', 930000), ('r4_belt_rd', 1100000), ('r4_forklift', 1200000), ('r4_mastlathe', 1500000), ('r4_slipway', 2100000), ('r4_orders', 1600000), ('r4_skidder2', 2400000), ('r4_builders', 2700000), ('r4_belt_ds', 2900000), ('r4_jack3', 3200000), ('r4_slipway2', 4000000), ('r4_lighthouse', 5300000)]
R5 pads total $90,740,000  upgrades bases [512780, 683706, 854633]
    [('r5_cablecar', 850000), ('r5_kiln', 1200000), ('r5_grove2', 510000), ('r5_office', 680000), ('r5_jack1', 1000000), ('r5_skilodge', 1400000), ('r5_skiworks', 1900000), ('r5_cashier', 1400000), ('r5_jack2', 2600000), ('r5_kiln2', 3400000), ('r5_belt_ks', 3800000), ('r5_sledshop', 5100000), ('r5_snowcat', 6000000), ('r5_luthier', 7300000), ('r5_express_r5', 7700000), ('r5_belt_sl', 8500000), ('r5_jack3', 9400000), ('r5_kiln3', 11000000), ('r5_observatory', 17000000)]
R6 pads total $32,000,000  upgrades bases [193797878, 258397171, 322996464]
    [('cap_station', 32000000)]
--- income curve (attentive player)
t=   5 min  rate       7.4 $/s  purchases so far 16
t=  15 min  rate      92.3 $/s  purchases so far 51
t=  30 min  rate     232.7 $/s  purchases so far 73
t=  60 min  rate    1045.0 $/s  purchases so far 92
t= 120 min  rate    3545.3 $/s  purchases so far 125
t= 180 min  rate    7084.6 $/s  purchases so far 155
t= 240 min  rate   13734.0 $/s  purchases so far 176
t= 300 min  rate   21155.5 $/s  purchases so far 193
t= 360 min  rate   26916.4 $/s  purchases so far 200
--- purchases per region and gap
R1: 58 buys, median gap 13 s, max gap 0.6 min
R2: 39 buys, median gap 66 s, max gap 2.6 min
R3: 34 buys, median gap 110 s, max gap 5.1 min
R4: 35 buys, median gap 137 s, max gap 6.7 min
R5: 33 buys, median gap 167 s, max gap 10.4 min
```

## sim.py
```python
"""Timber Valley pacing sim (my calc). Greedy player: buys the next pad in list order,
buys an upgrade when it costs <= UPG_RATIO of the next pad. Income = automated $/s per owned
unlock (base, estimated from code rates) x upgrade multipliers + hand income in the current region."""
import math

UPG_RATIO = 0.45
EVENTS = []
# ---- R1 as shipped: (id, cost, auto $/s added, hand $/s added)
R1 = [("trees2",10,0,0.2),("office",25,0,0),("jack1",50,1.0,0),("hauler1",70,1.3,0),
 ("carpentry",120,0.3,0.4),("hauler3",160,0.8,0),("pine",180,0,0.2),("roadsign",200,0.5,0),
 ("cashier",220,0.6,0),("sawmill2",260,0.3,0),("jack2",300,1.2,0),("hauler2",320,2.0,0),
 ("belt_planks",350,1.0,0),("belt_saw2",500,1.5,0),("cnc",600,1.0,0),("belt_chairs",650,1.0,0),
 ("conveyor1",700,2.0,0),("hauler4",750,2.5,0),("factory",1200,0.8,0.5),("jack3",900,0.5,0),
 ("dock",1500,6.0,0),("conveyor2",1300,8.0,0),("megasaw",2500,3.0,0),("belt_mega",1000,12.0,0),
 ("lodge",6000,0,0)]
HAND = {1:1.5}
# global upgrades (Game.UPGRADES): base, max, growth 1.75
GUP = {"capacity":(30,6),"speed":(40,5),"axe":(35,5),"machines":(90,5),"workers":(120,5),"prices":(150,5)}

def gmult(lv):
    auto = (1+0.10*lv["prices"])*(1+0.08*lv["machines"])*(1+0.10*lv["workers"])
    hand = (1+0.10*lv["prices"])*(1+0.08*lv["capacity"])*(1+0.05*lv["speed"])*(1+0.04*lv["axe"])
    return auto, hand

def run(regions, hand, gup, rup=None, verbose=False, eff=1.0):
    lv = {k:0 for k in gup}
    rlv = {}  # (region, key) -> level
    t = 0.0; money = 0.0; auto = {}; handr = {}
    log = []
    global EVENTS
    EVENTS = []
    for r, pads in regions:
        auto.setdefault(r,0.0); handr[r] = hand[r]
        start = t
        for pid, cost, da, dh in pads:
            while True:
                # candidate upgrades
                cands = [(gup[k][0]*1.75**lv[k], ("g",k)) for k in gup if lv[k] < gup[k][1]]
                if rup and r in rup:
                    for k,(b,mx,g) in rup[r].items():
                        l = rlv.get((r,k),0)
                        if l < mx: cands.append((b*g**l, ("r",k)))
                cands = [c for c in cands if c[0] <= UPG_RATIO*cost]
                target = min(cands)[0] if cands else cost
                am, hm = gmult(lv)
                rate = hm*handr[r]
                for rr in auto:
                    rm = 1.0
                    if rup and rr in rup:
                        rm = (1+0.25*0.6*rlv.get((rr,"saws"),0))*(1+0.15*rlv.get((rr,"crew"),0))*(1+0.10*rlv.get((rr,"fame"),0))
                    rate += auto[rr]*am*rm
                rate *= eff
                if money < target:
                    t += (target-money)/rate; money = target
                money -= target
                EVENTS.append((t, r, (min(cands)[1][1] if cands else pid), target, rate))
                if cands:
                    kind,k = min(cands)[1]
                    if kind=="g": lv[k]+=1
                    else: rlv[(r,k)] = rlv.get((r,k),0)+1
                    continue
                break
            auto[r] += da; handr[r] += dh
        am,_ = gmult(lv)
        tot = sum(auto[rr] for rr in auto)*am
        log.append((r, (t-start)/60, t/60, tot, dict(lv)))
    return log

if __name__ == "__main__":
    for eff in (1.0, 0.7):
        lg = run([(1,R1)], HAND, GUP, eff=eff)
        for r,dt,tt,inc,lv in lg:
            print(f"eff={eff} R{r}: {dt:.1f} min, total {tt:.1f} min, auto income {inc:.1f} $/s = {inc*60:.0f}/min, upg {lv}")
    print("R1 pad total", sum(p[1] for p in R1))
    print("R1 upgrade total", round(sum(b*(1.75**m-1)/0.75 for b,m in GUP.values())))
```

## regions.py
```python
import sys, math
sys.path.insert(0, "/tmp/claude-1000/-home-mm-MWM/4fde2fae-024e-4ae4-9a94-c0721d819a7d/scratchpad")
from sim import run, R1, GUP

# (id, relative cost weight, auto base $/s, hand base $/s)
R2 = [("r2_bridge",8,0,0),("r2_lathe",10,0,8),("r2_grove2",5,0,1),("r2_office",6,0,0),
 ("r2_jack1",10,4,0),("r2_hauler1",12,6,0),("r2_flume",16,3,2),("r2_cashier",14,3,0),
 ("r2_press",25,4,4),("r2_jack2",30,8,0),("r2_belt_lp",34,8,0),("r2_hauler2",38,8,0),
 ("r2_press2",55,6,0),("r2_boatshop",70,6,3),("r2_barge",85,20,0),("r2_belt_pb",90,12,0),
 ("r2_belt_bb",100,12,0),("r2_jack3",110,10,0),("r2_boathouse",160,0,0)]
R3 = [("r3_gate",10,0,0),("r3_beamsaw",12,0,16),("r3_grove2",6,0,2),("r3_office",8,0,0),
 ("r3_jack1",12,8,0),("r3_forklift1",16,12,0),("r3_cashier",16,6,0),("r3_planer",28,6,8),
 ("r3_jack2",32,16,0),("r3_house1",30,15,0),("r3_belt_bp",40,16,0),("r3_kitfactory",60,10,4),
 ("r3_house2",45,15,0),("r3_rail",80,40,0),("r3_belt_kit",85,25,0),("r3_house3",60,15,0),
 ("r3_jack3",95,20,0),("r3_rail2",110,30,0),("r3_house4",80,15,0),("r3_house5",100,15,0),
 ("r3_clocktower",180,0,0)]
R4 = [("r4_crossing",10,0,0),("r4_redmill",14,0,35),("r4_grove2",6,0,4),("r4_office",8,0,0),
 ("r4_jack1",12,20,0),("r4_skidder1",18,30,0),("r4_harbor",20,20,0),("r4_cashier",16,10,0),
 ("r4_decksaw",30,20,15),("r4_jack2",35,35,0),("r4_belt_rd",40,35,0),("r4_forklift",45,30,0),
 ("r4_mastlathe",55,25,0),("r4_slipway",80,60,0),("r4_orders",60,40,0),("r4_skidder2",90,50,0),
 ("r4_builders",100,60,0),("r4_belt_ds",110,50,0),("r4_jack3",120,45,0),("r4_slipway2",150,80,0),
 ("r4_lighthouse",200,0,0)]
R5 = [("r5_cablecar",10,0,0),("r5_kiln",14,0,80),("r5_grove2",6,0,8),("r5_office",8,0,0),
 ("r5_jack1",12,45,0),("r5_skilodge",16,50,0),("r5_skiworks",22,40,20),("r5_cashier",16,25,0),
 ("r5_jack2",30,80,0),("r5_kiln2",40,70,0),("r5_belt_ks",45,70,0),("r5_sledshop",60,60,0),
 ("r5_snowcat",70,90,0),("r5_luthier",85,80,0),("r5_express_r5",90,120,0),("r5_belt_sl",100,90,0),
 ("r5_jack3",110,90,0),("r5_kiln3",130,120,0),("r5_observatory",200,0,0)]
CAP = [("cap_station",1,0,0)]

TARGET = {2:50, 3:70, 4:90, 5:110, 6:20}
REG = {2:R2, 3:R3, 4:R4, 5:R5, 6:CAP}
HAND = {1:1.5, 2:0, 3:0, 4:0, 5:0, 6:0}

def scaled(pads, k, nice=True):
    out = []
    for pid, w, a, h in pads:
        c = w*k
        if nice:
            e = 10**max(0, int(math.log10(c))-1)
            c = int(round(c/e)*e)
        out.append((pid, c, a, h))
    return out

def rup_for(k):
    # region upgrade boards: saws / crew / fame, base as multiple of the region scale
    return {"saws": (6*k, 5, 1.8), "crew": (8*k, 5, 1.8), "fame": (10*k, 5, 1.8)}

GUP2 = dict(GUP)
GUP2.update({"capacity_x": (2500, 4), "speed_x": (3000, 2), "axe_x": (2000, 3)})  # extended caps, unlocked in R2 office

ks = {}
regions = [(1, R1)]
rup = {}
for r in (2,3,4,5,6):
    lo, hi = 1.0, 1e9
    for _ in range(80):
        mid = math.sqrt(lo*hi)
        rup_try = dict(rup); rup_try[r] = rup_for(mid)
        lg = run(regions + [(r, scaled(REG[r], mid, False))], HAND, GUP2, rup_try)
        if lg[-1][1] > TARGET[r]: hi = mid
        else: lo = mid
    ks[r] = lo
    rup[r] = rup_for(lo)
    regions.append((r, scaled(REG[r], lo)))

for eff in (1.0, 0.7):
    lg = run(regions, HAND, GUP2, rup, eff=eff)
    print(f"--- efficiency {eff}")
    for r, dt, tt, inc, lv in lg:
        print(f"R{r}: {dt:6.1f} min  cum {tt/60:5.2f} h  auto income at end {inc:10.0f} $/s ({inc*60:,.0f}/min)")
print("scale k per region:", {r: round(k) for r, k in ks.items()})
for r, pads in regions[1:]:
    print(f"R{r} pads total ${sum(p[1] for p in pads):,}  upgrades bases {[round(v[0]) for v in rup[r].values()]}")
    print("   ", [(p[0], p[1]) for p in pads])

import sim
lg = run(regions, HAND, GUP2, rup, eff=1.0)
ev = sim.EVENTS
print("--- income curve (attentive player)")
for m in (5, 15, 30, 60, 120, 180, 240, 300, 360):
    last = [e for e in ev if e[0] <= m*60]
    rate = last[-1][4] if last else ev[0][4]
    print(f"t={m:4d} min  rate {rate:9.1f} $/s  purchases so far {len(last)}")
print("--- purchases per region and gap")
for r in (1,2,3,4,5,6):
    es = [e for e in ev if e[1]==r]
    if len(es) > 1:
        span = (es[-1][0]-es[0][0])/60
        gaps = sorted((es[i+1][0]-es[i][0]) for i in range(len(es)-1))
        print(f"R{r}: {len(es)} buys, median gap {gaps[len(gaps)//2]:.0f} s, max gap {gaps[-1]/60:.1f} min")
```
