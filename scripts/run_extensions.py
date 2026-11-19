"""
Extension experiments (Week 10), run on the same test set as the main benchmark.

1. C2 range planner: plan with the 90th percentile of C2 instead of its expected value (100 days, 4 trucks).
2. Tight fleet on more days: 3 trucks on 200 test days, to check whether the gain from prediction is significant.
3. Gate queue sensitivity: all queue times multiplied by 0.5 and 1.5 (100 days, 4 trucks).

Outputs (results/extensions/): c2_range_daily.csv, c2_range_tests.csv, fleet3_200_daily.csv, fleet3_200_tests.csv,
queue_sensitivity_daily.csv, queue_sensitivity_summary.csv
"""

import copy
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd

from irishlogix.evaluation import benchmark as B
from irishlogix.evaluation.stats import paired_tests
from irishlogix.world import assumptions as A

KPIS = ["total_cost", "idle_h", "late_h", "viol_h", "co2_kg"]
OUT = Path("results/extensions")


def run(ctx, days, planners, seed_base=1000):
    rows = []
    for k, day in enumerate(days):
        rows += B.run_day(ctx, day, seed_base + k, planners=planners, prices=[80.0])[0]
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ctx = B.load_context()
    days100 = B.test_days(ctx, n=100)

    # 1. C2 range planner on the main test days
    t0 = time.time()
    df = run(ctx, days100, ["Average delays", "Coupled (C1+C2)", "Coupled, C2 90th percentile", "Oracle"])
    df.to_csv(OUT / "c2_range_daily.csv", index=False)
    tests = paired_tests(df, KPIS, pairs=[("Coupled, C2 90th percentile", "Coupled (C1+C2)"),
                                          ("Coupled, C2 90th percentile", "Average delays")])
    tests.to_csv(OUT / "c2_range_tests.csv", index=False)
    print(f"[1] C2 range planner done in {time.time() - t0:.0f}s")
    print(df.groupby("planner")[KPIS].mean().round(2))

    # 2. Tight fleet on 200 days
    t0 = time.time()
    fleet = A.FLEET_SIZE
    A.FLEET_SIZE = 3
    days200 = B.test_days(ctx, n=200)
    df = run(ctx, days200, ["FIFO", "Average delays", "Coupled (C1+C2)", "Coupled, C2 90th percentile", "Oracle"])
    A.FLEET_SIZE = fleet
    df.to_csv(OUT / "fleet3_200_daily.csv", index=False)
    tests = paired_tests(df, KPIS, pairs=[("Coupled (C1+C2)", "Average delays"), ("Coupled, C2 90th percentile", "Average delays"),
                                          ("Oracle", "Average delays"), ("Coupled (C1+C2)", "FIFO")])
    tests.to_csv(OUT / "fleet3_200_tests.csv", index=False)
    print(f"[2] 3 trucks on 200 days done in {time.time() - t0:.0f}s")
    print(df.groupby("planner")[KPIS].mean().round(2))

    # 3. Gate queue sensitivity
    t0 = time.time()
    base = copy.deepcopy(A.QUEUE_MEAN_HOURS)
    frames = []
    for scale in (0.5, 1.5):
        A.QUEUE_MEAN_HOURS = {p: {c: v * scale for c, v in cls.items()} for p, cls in base.items()}
        d = run(ctx, days100, ["FIFO", "Average delays", "Coupled (C1+C2)", "Oracle"])
        d["queue_scale"] = scale
        frames.append(d)
    A.QUEUE_MEAN_HOURS = base
    df = pd.concat(frames, ignore_index=True)
    df.to_csv(OUT / "queue_sensitivity_daily.csv", index=False)
    summary = df.groupby(["queue_scale", "planner"])[KPIS].mean().round(2)
    summary.to_csv(OUT / "queue_sensitivity_summary.csv")
    rows = []
    for scale, d in df.groupby("queue_scale"):
        t = paired_tests(d, ["total_cost"], pairs=[("Coupled (C1+C2)", "Average delays"), ("Oracle", "Average delays"),
                                                   ("Average delays", "FIFO")])
        t["queue_scale"] = scale
        rows.append(t)
    pd.concat(rows).to_csv(OUT / "queue_sensitivity_tests.csv", index=False)
    print(f"[3] queue sensitivity done in {time.time() - t0:.0f}s")
    print(summary)


if __name__ == "__main__":
    main()
