"""
Control for the C2 range planner: is the gain from C2's 90th percentile, or from any conservative buffer?
Compares 'Historical 90th percentile' (group 90th percentile from past data, no machine learning) with
'Coupled, C2 90th percentile' on the same 100 test days (4 trucks).
Output: results/extensions/c2_range_control_daily.csv, c2_range_control_tests.csv
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd

from irishlogix.evaluation import benchmark as B
from irishlogix.evaluation.stats import paired_tests

KPIS = ["total_cost", "idle_h", "late_h", "viol_h", "co2_kg"]


def main():
    out = Path("results/extensions"); out.mkdir(parents=True, exist_ok=True)
    ctx = B.load_context()
    rows = []
    for k, day in enumerate(B.test_days(ctx, n=100)):
        rows += B.run_day(ctx, day, 1000 + k, planners=["Historical 90th percentile"], prices=[80.0])[0]
    ctrl = pd.DataFrame(rows)
    prev = pd.read_csv(out / "c2_range_daily.csv", parse_dates=["date"])
    df = pd.concat([prev, ctrl], ignore_index=True)
    df.to_csv(out / "c2_range_control_daily.csv", index=False)
    tests = paired_tests(df, KPIS, pairs=[("Coupled, C2 90th percentile", "Historical 90th percentile"),
                                          ("Historical 90th percentile", "Average delays"),
                                          ("Coupled, C2 90th percentile", "Average delays")])
    tests.to_csv(out / "c2_range_control_tests.csv", index=False)
    print(df.groupby("planner")[KPIS].mean().round(2))
    print(tests[tests.kpi == "total_cost"][["comparison", "mean_diff", "ci95_low", "ci95_high", "pct_change", "wilcoxon_p"]].round(3).to_string())


if __name__ == "__main__":
    main()
