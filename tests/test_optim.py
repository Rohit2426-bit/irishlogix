"""
Tests for routes, the day schedule (EC 561/2006 breaks) and the planners.
"""

import numpy as np
import pandas as pd

from irishlogix.evaluation.stats import rank_biserial
from irishlogix.optim import planners as P
from irishlogix.optim.routes import fuel_per_km, route_options
from irishlogix.optim.schedule import Delays, Plan, simulate
from irishlogix.world import assumptions as A


def test_fuel_model_shape():
    assert fuel_per_km(85, laden=False) < fuel_per_km(85, laden=True)
    assert fuel_per_km(78, laden=True) < fuel_per_km(88, laden=True)
    assert abs(fuel_per_km(85, laden=True) - 0.315) < 1e-9


def test_route_options_shortest_first():
    opts = route_options("PORT_ROSSLARE", "HUB_LIMERICK")
    standard = [o for o in opts if not o.eco]
    assert standard[0].distance_km == min(o.distance_km for o in standard)
    assert all(o.hours >= 0 for o in opts)


def _cons(dest="HUB_GALWAY"):
    return {"vessel_hour": np.array([8.0]), "deadline_hour": np.array([20.0]),
            "port_node": np.array(["PORT_ROSSLARE"]), "destination": np.array([dest]), "port": np.array(["Rosslare"])}


def test_break_inserted_after_four_and_a_half_hours():
    plan = Plan([[0]], {0: 0}, {0: 8.0})
    delays = Delays(np.array([1.0]), np.array([0.3]), np.array([1.0]))
    tot = simulate(plan, _cons(), delays, set_targets=False)["totals"]
    assert tot["drive_h"] > 4.5
    assert tot["breaks"] >= 1


def test_decode_assigns_each_consignment_once():
    rng = np.random.default_rng(0)
    n, opts = 5, [2, 3, 1, 4, 2]
    plan = P.decode(rng.random(3 * n), n, opts)
    seen = sorted(i for seq in plan.trucks for i in seq)
    assert seen == list(range(n))
    assert len(plan.trucks) == A.FLEET_SIZE
    assert all(0 <= plan.route_idx[i] < opts[i] for i in range(n))


def test_rank_biserial_extremes():
    assert rank_biserial(np.array([1.0, 2.0, 3.0])) == 1.0
    assert rank_biserial(np.array([-1.0, -2.0])) == -1.0
