"""
Scenario analysis on the same 100 benchmark days.

1. Tight fleet: 3 trucks instead of 4 for the same 5 daily loads (does prediction matter more
   when there is less spare capacity?).
2. Carbon price threshold: the coupled planner's chosen plan at ETS2 prices from EUR 40 to
   EUR 1,000 per tonne (at what price do routing decisions start to change?).

Outputs (results/scenarios/): fleet3_daily.csv, fleet3_paired_tests.csv, carbon_threshold.csv
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np
import pandas as pd

from irishlogix.evaluation import benchmark as B
from irishlogix.evaluation.stats import paired_tests
from irishlogix.optim import planners as P
from irishlogix.world import assumptions as A
from irishlogix.world.customs_world import day_instance

PRICES = [40, 80, 120, 200, 300, 500, 1000]


def main():
    out = Path("results/scenarios")
    out.mkdir(parents=True, exist_ok=True)
    ctx = B.load_context()
    days = B.test_days(ctx, n=100)

    # 2. Carbon price threshold with the standard 4-truck fleet.
    rows = []
    for k, day in enumerate(days):
        cons = day_instance(ctx.port_days, day, seed=1000 + k)
        front = P.optimise(cons, B.planner_estimates(ctx, cons, day)["Coupled (C1+C2)"], seed=1000 + k)
        for price in PRICES:
            pick = P.choose(front, price)
            res = P.execute(pick["plan"], cons)
            eco = float(np.mean([r["eco"] for r in res["per_consignment"].values()]))
            rows.append({"date": day, "ets2_price": price, "co2_kg": res["totals"]["co2_kg"], "km": res["totals"]["km"],
                         "cost_ex_carbon": res["totals"]["cost_ex_carbon"], "total_cost": P.realised_cost(res, price),
                         "eco_share": eco, "front_size": len(front)})
    carbon = pd.DataFrame(rows)
    carbon.to_csv(out / "carbon_threshold.csv", index=False)
    print(carbon.groupby("ets2_price")[["co2_kg", "km", "cost_ex_carbon", "eco_share", "front_size"]].mean().round(2))

    # 1. Tight fleet of 3 trucks.
    A.FLEET_SIZE = 3
    rows = []
    for k, day in enumerate(days):
        rows += B.run_day(ctx, day, 1000 + k, planners=["FIFO", "Average delays", "Coupled (C1+C2)", "Oracle"], prices=[80.0])[0]
    fleet3 = pd.DataFrame(rows)
    fleet3.to_csv(out / "fleet3_daily.csv", index=False)
    tests = paired_tests(fleet3, ["total_cost", "idle_h", "late_h", "co2_kg", "viol_h"],
                         pairs=[("Coupled (C1+C2)", "FIFO"), ("Coupled (C1+C2)", "Average delays"), ("Oracle", "Average delays"),
                                ("Oracle", "Coupled (C1+C2)")])
    tests.to_csv(out / "fleet3_paired_tests.csv", index=False)
    print(fleet3.groupby("planner")[["total_cost", "idle_h", "late_h", "viol_h", "co2_kg"]].mean().round(2))
    print(tests[tests.kpi == "total_cost"][["comparison", "mean_diff", "ci95_low", "ci95_high", "pct_change", "wilcoxon_p"]].round(3))


if __name__ == "__main__":
    main()
