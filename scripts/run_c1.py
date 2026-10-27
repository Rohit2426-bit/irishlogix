"""
Train and evaluate C1, the next-day port congestion classifier.

Outputs (results/c1/): cv_by_year.csv, tuning_grid.csv, test_metrics.csv, confusion_matrix.csv,
shap_importance.csv, test_probabilities.csv (used by the planners), model.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd

from irishlogix.models import c1_congestion as c1


def main():
    out = Path("results/c1")
    out.mkdir(parents=True, exist_ok=True)
    port_days = pd.read_csv("data/world/port_days.csv", parse_dates=["date"])
    feat = c1.build_features(port_days)
    sets = c1.split(feat)
    print({k: len(v) for k, v in sets.items()})

    cv = c1.rolling_cv(feat)
    cv.to_csv(out / "cv_by_year.csv", index=False)
    print("\nExpanding-window CV (mean over 2019 to 2024):")
    print(cv.groupby("model")[["macro_f1", "accuracy", "brier"]].mean().round(3).sort_values("macro_f1", ascending=False))

    best, grid = c1.tune(sets)
    grid.to_csv(out / "tuning_grid.csv", index=False)
    print("\nBest on 2024 validation:", best)

    model = c1.fit_final(sets, best)
    metrics, cm = c1.test_report(model, sets)
    metrics.to_csv(out / "test_metrics.csv", index=False)
    pd.DataFrame(cm, index=[f"true_{c}" for c in c1.CLASSES], columns=[f"pred_{c}" for c in c1.CLASSES]).to_csv(out / "confusion_matrix.csv")
    print("\nTest period 2025 to mid-2026:")
    print(metrics.to_string(index=False))
    print(pd.DataFrame(cm, index=c1.CLASSES, columns=c1.CLASSES))

    imp = c1.shap_importance(model, sets["test"][c1.FEATURES])
    imp.rename("mean_abs_shap").to_csv(out / "shap_importance.csv")
    print("\nTop SHAP features:\n", imp.head(8).round(3).to_string())

    test = sets["test"][["date", "port", "congestion_class"]].copy()
    proba = model.predict_proba(sets["test"][c1.FEATURES])
    for i, c in enumerate(c1.CLASSES):
        test[f"p_{c}"] = proba[:, i].round(4)
    test.to_csv(out / "test_probabilities.csv", index=False)
    model.save_model(out / "model.json")
    json.dump(best, open(out / "best_params.json", "w"))


if __name__ == "__main__":
    main()
