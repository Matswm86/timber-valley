"""Timber Valley: Valley 4-5 and Station costs from MEASURED income (2026-10-03, my calc).

Same model as rebalance_sim.py (2026-10-01): a casual player walks the pad list; each pad costs
income-when-reached x a target wait; one scale factor per valley is solved by bisection so the
casual player hits TARGET_MIN. Only the V4/V5 income lists change: they were modeled, now they
are the headless probe's numbers (docs/balance/m345_2026-10-03.md, econ_probe.gd extended to
valleys 4-5, --fixed-fps 60, global upgrades at max, region upgrades 0, player parked).

Probe = cumulative automated $/s of the valley after the first n pads; the deltas below are those
steps. Unprobed pads (n = 16, 19) get no step; the gap between n = 20 and 21 on the slipway line is
ship-timing noise over a 300 s window and is split over jack3 and slipway2.

Run: python3 docs/balance/rebalance_m345.py
"""
import rebalance_sim as rs

# (id, auto $/s added (measured), attentive hand $/s added (2026-10-01 estimate), wait weight)
R4_M = [("r4_crossing", 0, 0, 0.75), ("r4_redmill", 0, 95, 0.85), ("r4_grove2", 0, 6, 0.6),
        ("r4_office", 0, 0, 0.6), ("r4_jack1", 0, 0, 0.8), ("r4_skidder1", 0, 0, 0.85),
        ("r4_harbor", 0, 0, 0.9), ("r4_cashier", 0, -20, 0.9), ("r4_decksaw", 0, 20, 1.0),
        ("r4_jack2", 0, 0, 1.0), ("r4_belt_rd", 0, 0, 1.0), ("r4_forklift", 93.3, -60, 1.0),
        ("r4_mastlathe", 0, 10, 1.05), ("r4_slipway", 0.9, 0, 1.1), ("r4_orders", 0.6, 0, 1.1),
        ("r4_skidder2", 0, 0, 1.15), ("r4_builders", 328.1, -10, 1.15), ("r4_belt_ds", 140.0, 0, 1.2),
        ("r4_jack3", 72.0, 0, 1.2), ("r4_slipway2", 72.0, 0, 1.25), ("r4_lighthouse", 0, 0, 1.9)]
R5_M = [("r5_cablecar", 0, 0, 0.75), ("r5_kiln", 0, 0, 0.85), ("r5_grove2", 0, 0, 0.6),
        ("r5_office", 0, 0, 0.6), ("r5_jack1", 0, 0, 0.8), ("r5_skilodge", 0, 115, 0.85),
        ("r5_skiworks", 0, 20, 0.9), ("r5_cashier", 0, -25, 0.9), ("r5_jack2", 0, 0, 1.0),
        ("r5_kiln2", 0, 0, 1.0), ("r5_belt_ks", 0, 0, 1.0), ("r5_sledshop", 0, 10, 1.05),
        ("r5_snowcat", 613.7, -100, 1.05), ("r5_luthier", 0, 10, 1.1), ("r5_express_r5", 75.5, 0, 1.1),
        ("r5_belt_sl", 0, -10, 1.15), ("r5_jack3", 291.5, 0, 1.15), ("r5_kiln3", 572.2, 0, 1.2),
        ("r5_observatory", 0, 0, 1.9)]


def build_regions():
    return [(2, rs.R2), (3, rs.R3), (4, R4_M), (5, R5_M), (6, rs.R6)]


if __name__ == "__main__":
    rs.build_regions = build_regions
    rs.main()
