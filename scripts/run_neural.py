"""
Neural network comparison for C1 and C2 (added after the Week 10 supervision meeting).

C1: XGBoost and the simple methods against an LSTM (sequential) and an MLP, on the same 2025 to
mid-2026 test days, with precision, recall and F1 for each congestion class.
C2: XGBoost against an MLP regressor on the same customs test records.

Outputs (results/neural/): c1_comparison.csv, c1_class_report.csv, c1_neural_seeds.csv,
c2_comparison.csv
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import json

import numpy as np
import pandas as pd

from irishlogix.models import c1_congestion as c1
from irishlogix.models import c2_customs as c2
from irishlogix.models import neural as nn_models

FAMILY = {"XGBoost": "Machine learning (trees)", "Logistic regression": "Machine learning (linear)",
          "Persistence": "Simple rule", "Weekday climatology": "Simple rule",
          "LSTM (28-day sequence)": "Neural network (sequential)", "MLP": "Neural network (feed-forward)"}


def main():
    out = Path("results/neural")
    out.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- C1
    port_days = pd.read_csv("data/world/port_days.csv", parse_dates=["date"])
    sets = c1.split(c1.build_features(port_days))
    test, trval = sets["test"], pd.concat([sets["train"], sets["valid"]])
    y = test["y"].to_numpy()
    best = json.load(open("results/c1/best_params.json"))

    # one probability matrix per run; XGBoost and the simple methods are deterministic (one run)
    runs, secs = {}, {}
    t0 = time.time()
    runs["XGBoost"] = [c1.fit_final(sets, best).predict_proba(test[c1.FEATURES])]
    secs["XGBoost"] = time.time() - t0
    runs.update({k: [v] for k, v in c1.baseline_probas(trval, test).items()})
    t0 = time.time()
    lstm_seeds, runs["LSTM (28-day sequence)"] = nn_models.lstm_test(port_days, sets)
    secs["LSTM (28-day sequence)"] = (time.time() - t0) / len(lstm_seeds)
    t0 = time.time()
    mlp_seeds, runs["MLP"] = nn_models.mlp_c1_test(sets)
    secs["MLP"] = (time.time() - t0) / len(mlp_seeds)
    pd.concat([lstm_seeds.assign(model="LSTM (28-day sequence)"), mlp_seeds.assign(model="MLP")]).to_csv(
        out / "c1_neural_seeds.csv", index=False)

    # metrics are the mean over runs (5 seeds for the neural networks)
    rows, reports = [], []
    for name, ps in runs.items():
        m = pd.DataFrame([c1.evaluate(y, p) for p in ps])
        rows.append({"model": name, "family": FAMILY[name], "runs": len(ps), **m.mean().round(4).to_dict(),
                     "macro_f1_sd": round(m["macro_f1"].std(), 4) if len(ps) > 1 else np.nan,
                     "seconds_per_fit": round(secs.get(name, np.nan), 1)})
        rep = pd.concat([nn_models.class_report(name, y, p) for p in ps])
        reports.append(rep.groupby(["model", "class"], sort=False)[["precision", "recall", "f1", "support"]].mean()
                       .round(3).reset_index())
    comp = pd.DataFrame(rows).sort_values("macro_f1", ascending=False)
    comp.to_csv(out / "c1_comparison.csv", index=False)
    report = pd.concat(reports, ignore_index=True)
    report.to_csv(out / "c1_class_report.csv", index=False)
    print("C1 on the test period (mean over runs):")
    print(comp.to_string(index=False))
    print(report.to_string(index=False))

    # bootstrap over test days: macro-F1 difference against XGBoost (mean over the runs of each model)
    from sklearn.metrics import f1_score
    rng = np.random.default_rng(0)
    preds = {k: [p.argmax(1) for p in v] for k, v in runs.items()}
    boot = []
    for name in ["LSTM (28-day sequence)", "Logistic regression", "MLP"]:
        diffs = []
        for _ in range(1000):
            i = rng.integers(0, len(y), len(y))
            f = lambda k: np.mean([f1_score(y[i], p[i], average="macro") for p in preds[k]])
            diffs.append(f(name) - f("XGBoost"))
        boot.append({"comparison": f"{name} minus XGBoost", "macro_f1_diff": round(float(np.mean(diffs)), 4),
                     "ci95_low": round(float(np.percentile(diffs, 2.5)), 4),
                     "ci95_high": round(float(np.percentile(diffs, 97.5)), 4)})
    boot = pd.DataFrame(boot)
    boot.to_csv(out / "c1_bootstrap.csv", index=False)
    print(boot.to_string(index=False))

    # ---------------------------------------------------------------- C2
    history = pd.read_csv("data/world/customs_history.csv", parse_dates=["date"])
    s2 = c2.split(history)
    trval2 = pd.concat([s2["train"], s2["valid"]])
    xgb = c2.C2Model().fit(trval2)
    rows = []
    for subset, te in [("All loads", s2["test"]), ("Loads from Great Britain", s2["test"][s2["test"]["origin_gb"] == 1])]:
        yt = te["clearance_hours"].to_numpy()
        rows.append({"subset": subset, "model": "XGBoost", **c2.metrics(yt, xgb.predict(te)["pred_mean"].to_numpy())})
        mlp_pred = np.mean([nn_models.mlp_regressor(s).fit(trval2[c2.FEATURES], trval2["clearance_hours"])
                            .predict(te[c2.FEATURES]).clip(min=0) for s in range(5)], axis=0)
        rows.append({"subset": subset, "model": "MLP", **c2.metrics(yt, mlp_pred)})
    c2c = pd.DataFrame(rows)
    c2c.to_csv(out / "c2_comparison.csv", index=False)
    print("\nC2 on the test period:\n", c2c.to_string(index=False))


if __name__ == "__main__":
    main()
