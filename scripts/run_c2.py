"""
Train and evaluate C2, the customs clearance time regressor with a prediction range.

Outputs (results/c2/): test_metrics.csv, test_metrics_gb_only.csv, intervals.json, models (json)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd

from irishlogix.models import c2_customs as c2


def main():
    out = Path("results/c2")
    out.mkdir(parents=True, exist_ok=True)
    history = pd.read_csv("data/world/customs_history.csv", parse_dates=["date"])
    sets = c2.split(history)
    print({k: len(v) for k, v in sets.items()})
    trval = pd.concat([sets["train"], sets["valid"]])
    model = c2.C2Model().fit(trval)

    allm = c2.compare(trval, sets["test"], model)
    gb_test = sets["test"][sets["test"]["origin_gb"] == 1]
    gbm = c2.compare(trval, gb_test, model)
    allm.to_csv(out / "test_metrics.csv", index=False)
    gbm.to_csv(out / "test_metrics_gb_only.csv", index=False)
    print("\nAll consignments (test 2025 to mid-2026):\n", allm.to_string(index=False))
    print("\nGB-origin consignments only:\n", gbm.to_string(index=False))

    iv = {"all": c2.interval_report(sets["test"], model), "gb_only": c2.interval_report(gb_test, model)}
    json.dump(iv, open(out / "intervals.json", "w"), indent=1)
    print("\nPrediction range (10th to 90th percentile):", json.dumps(iv, indent=1))
    model.point.save_model(out / "point_model.json")
    model.quant.save_model(out / "quantile_model.json")


if __name__ == "__main__":
    main()
