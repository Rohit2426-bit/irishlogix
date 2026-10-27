"""
Run the paired benchmark of all planners on 100 held-out weekdays (500 consignments).

Outputs (results/benchmark/):
  daily_results.csv        one row per day, planner and ETS2 price
  consignment_results.csv  per-consignment idle and lateness (ETS2 EUR 80)
  sensitivity_checks.csv   customs check rate x0.5 and x1.5 (ETS2 EUR 80)
  paired_tests.csv         Wilcoxon tests, bootstrap CIs and effect sizes (ETS2 EUR 80)
  summary_by_planner.csv   mean KPIs by planner and ETS2 price
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd

from irishlogix.evaluation import benchmark as B
from irishlogix.evaluation.stats import paired_tests


def main(n_days: int = 100):
    out = Path("results/benchmark")
    out.mkdir(parents=True, exist_ok=True)
    ctx = B.load_context()
    days = B.test_days(ctx, n=n_days)
    t0 = time.time()
    rows, trips, sens = [], [], []
    for k, day in enumerate(days):
        seed = 1000 + k
        day_rows, day_trips = B.run_day(ctx, day, seed)
        rows += day_rows
        trips += day_trips
        for scale in (0.5, 1.5):
            sens += B.run_day(ctx, day, seed, check_scale=scale,
                              planners=["FIFO", "Average delays", "Coupled (C1+C2)", "Oracle"], prices=[80.0])[0]
        if (k + 1) % 20 == 0:
            print(f"{k + 1}/{len(days)} days, {time.time() - t0:.0f}s")
    daily = pd.DataFrame(rows)
    daily.to_csv(out / "daily_results.csv", index=False)
    pd.DataFrame(trips).to_csv(out / "consignment_results.csv", index=False)
    pd.DataFrame(sens).to_csv(out / "sensitivity_checks.csv", index=False)

    summary = daily.groupby(["ets2_price", "planner"])[B.KPIS + ["total_cost", "eco_share"]].mean().round(2)
    summary.to_csv(out / "summary_by_planner.csv")
    tests = paired_tests(daily, ["total_cost", "idle_h", "late_h", "co2_kg", "g_co2_per_km", "viol_h", "km"])
    tests.to_csv(out / "paired_tests.csv", index=False)
    pd.set_option("display.width", 200)
    print(summary.loc[80.0][["total_cost", "idle_h", "late_h", "viol_h", "co2_kg", "km", "g_co2_per_km"]])


if __name__ == "__main__":
    main()
