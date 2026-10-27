"""
Component C1: next-day port congestion classifier (Low, Medium, High).

The prediction for day d is made on the evening of day d-1, so every feature must be known by
then: the vessel schedule for day d, the calendar, any disruption warning, and congestion and
traffic observed up to day d-1. XGBoost is compared with three alternatives: persistence
(tomorrow equals today), a weekday climatology and multinomial logistic regression.
"""

from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from ..world import assumptions as A

CLASSES = ["Low", "Medium", "High"]
CLASS_ID = {c: i for i, c in enumerate(CLASSES)}

FEATURES = [
    "is_dublin", "dow", "month", "is_holiday", "disruption_warning",
    "scheduled_arrivals", "arrivals_vs_28d", "index_lag1", "index_lag2", "index_lag7",
    "index_mean7", "class_lag1", "units_lag1", "units_mean7", "units_prev_quarter",
]


def build_features(port_days: pd.DataFrame) -> pd.DataFrame:
    """One row per port and day with features known the evening before and the day's class."""
    frames = []
    for port, d in port_days.sort_values("date").groupby("port"):
        d = d.copy()
        d["is_dublin"] = int(port == "Dublin")
        d["arrivals_vs_28d"] = d["scheduled_arrivals"] / d["scheduled_arrivals"].shift(1).rolling(28).mean()
        idx = d["congestion_index"]
        d["index_lag1"], d["index_lag2"], d["index_lag7"] = idx.shift(1), idx.shift(2), idx.shift(7)
        d["index_mean7"] = idx.shift(1).rolling(7).mean()
        d["class_lag1"] = d["congestion_class"].map(CLASS_ID).shift(1)
        d["units_lag1"] = d["roro_units"].shift(1)
        d["units_mean7"] = d["roro_units"].shift(1).rolling(7).mean()
        q_units = d.groupby("quarter")["roro_units"].sum()
        d["units_prev_quarter"] = d["quarter"].map(q_units.shift(1))
        d["is_holiday"] = d["is_holiday"].astype(int)
        d["disruption_warning"] = d["disruption_warning"].astype(int)
        d["y"] = d["congestion_class"].map(CLASS_ID)
        frames.append(d)
    out = pd.concat(frames, ignore_index=True).dropna(subset=FEATURES)
    return out


def split(feat: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    return {
        "train": feat[feat["date"] <= A.TRAIN_END],
        "valid": feat[(feat["date"] > A.TRAIN_END) & (feat["date"] <= A.VALID_END)],
        "test": feat[feat["date"] > A.VALID_END],
    }


def make_xgb(**kw) -> XGBClassifier:
    params = dict(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.9,
                  colsample_bytree=0.9, objective="multi:softprob", eval_metric="mlogloss", random_state=42)
    params.update(kw)
    return XGBClassifier(**params)


def multiclass_brier(y: np.ndarray, proba: np.ndarray) -> float:
    onehot = np.eye(len(CLASSES))[y]
    return float(np.mean(np.sum((proba - onehot) ** 2, axis=1)))


def evaluate(y: np.ndarray, proba: np.ndarray) -> Dict[str, float]:
    pred = proba.argmax(axis=1)
    return {"macro_f1": round(f1_score(y, pred, average="macro"), 4),
            "accuracy": round(accuracy_score(y, pred), 4),
            "brier": round(multiclass_brier(y, proba), 4)}


def baseline_probas(train: pd.DataFrame, test: pd.DataFrame) -> Dict[str, np.ndarray]:
    """Probabilities from the three alternative methods."""
    persist = np.eye(3)[test["class_lag1"].astype(int)] * 0.9 + 0.1 / 3
    clim = (train.groupby(["is_dublin", "dow"])["y"].value_counts(normalize=True).unstack(fill_value=0)
            .reindex(columns=range(3), fill_value=0))
    clim_p = clim.loc[list(zip(test["is_dublin"], test["dow"]))].to_numpy()
    logit = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    logit.fit(train[FEATURES], train["y"])
    return {"Persistence": persist, "Weekday climatology": clim_p,
            "Logistic regression": logit.predict_proba(test[FEATURES])}


def rolling_cv(feat: pd.DataFrame, years=range(2019, 2025)) -> pd.DataFrame:
    """Expanding-window time-series cross-validation: train on all years before Y, test on Y."""
    rows = []
    for y in years:
        tr = feat[feat["date"].dt.year < y]
        te = feat[feat["date"].dt.year == y]
        model = make_xgb().fit(tr[FEATURES], tr["y"])
        res = {"year": y, "model": "XGBoost", **evaluate(te["y"].to_numpy(), model.predict_proba(te[FEATURES]))}
        rows.append(res)
        for name, p in baseline_probas(tr, te).items():
            rows.append({"year": y, "model": name, **evaluate(te["y"].to_numpy(), p)})
    return pd.DataFrame(rows)


def tune(sets: Dict[str, pd.DataFrame]) -> Tuple[dict, pd.DataFrame]:
    """Small grid search on the 2024 validation year."""
    rows = []
    for depth in (2, 3, 4, 6):
        for lr in (0.03, 0.05, 0.1):
            m = make_xgb(max_depth=depth, learning_rate=lr).fit(sets["train"][FEATURES], sets["train"]["y"])
            rows.append({"max_depth": depth, "learning_rate": lr,
                         **evaluate(sets["valid"]["y"].to_numpy(), m.predict_proba(sets["valid"][FEATURES]))})
    grid = pd.DataFrame(rows).sort_values(["macro_f1", "brier"], ascending=[False, True])
    best = grid.iloc[0][["max_depth", "learning_rate"]].to_dict()
    best["max_depth"] = int(best["max_depth"])
    return best, grid


def fit_final(sets: Dict[str, pd.DataFrame], best: dict) -> XGBClassifier:
    """Refit on train plus validation (2017 to 2024) for use on the 2025 to 2026 test period."""
    trval = pd.concat([sets["train"], sets["valid"]])
    return make_xgb(**best).fit(trval[FEATURES], trval["y"])


def test_report(model: XGBClassifier, sets: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, np.ndarray]:
    test = sets["test"]
    trval = pd.concat([sets["train"], sets["valid"]])
    proba = model.predict_proba(test[FEATURES])
    rows = [{"model": "XGBoost", **evaluate(test["y"].to_numpy(), proba)}]
    for name, p in baseline_probas(trval, test).items():
        rows.append({"model": name, **evaluate(test["y"].to_numpy(), p)})
    cm = confusion_matrix(test["y"], proba.argmax(axis=1), labels=range(3))
    return pd.DataFrame(rows), cm


def shap_importance(model: XGBClassifier, X: pd.DataFrame) -> pd.Series:
    import shap
    values = shap.TreeExplainer(model).shap_values(X)
    arr = np.abs(np.asarray(values))
    # shap returns (n, features, classes) for multiclass XGBoost; average over rows and classes.
    if arr.ndim == 3 and arr.shape[1] == X.shape[1]:
        imp = arr.mean(axis=(0, 2))
    else:
        imp = arr.mean(axis=tuple(i for i in range(arr.ndim) if arr.shape[i] != X.shape[1]))
    return pd.Series(imp, index=X.columns).sort_values(ascending=False)
