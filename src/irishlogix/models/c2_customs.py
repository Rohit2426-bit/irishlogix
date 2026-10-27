"""
Component C2: customs clearance time regressor with a prediction range.

Point predictions use XGBoost with squared error; the range uses multi-quantile XGBoost
(10th, 50th and 90th percentiles). Alternatives: the historical mean for each group of
origin, commodity and pre-lodgement (a spreadsheet-style estimate) and linear regression.
Only features known before the vessel arrives are used; random customs checks are not known.
"""

from typing import Dict

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from ..world import assumptions as A

COMMODITY_COLS = ["is_agrifood", "is_machinery"]
FEATURES = ["origin_gb", "prelodged", "aeo", "night", "vessel_hour", "is_dublin", "dow", "month"] + COMMODITY_COLS
QUANTILES = [0.1, 0.5, 0.9]
GROUP_KEYS = ["origin_gb", "commodity", "prelodged"]


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["is_agrifood"] = (d["commodity"] == "Agrifood (SPS)").astype(int)
    d["is_machinery"] = (d["commodity"] == "Machinery and parts").astype(int)
    d["is_dublin"] = (d["port"] == "Dublin").astype(int)
    for c in ["origin_gb", "prelodged", "aeo", "night"]:
        d[c] = d[c].astype(int)
    return d


def split(history: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    h = prepare(history)
    return {"train": h[h["date"] <= A.TRAIN_END],
            "valid": h[(h["date"] > A.TRAIN_END) & (h["date"] <= A.VALID_END)],
            "test": h[h["date"] > A.VALID_END]}


def point_model() -> XGBRegressor:
    return XGBRegressor(n_estimators=400, max_depth=4, learning_rate=0.05, subsample=0.9,
                        colsample_bytree=0.9, random_state=42)


def quantile_model() -> XGBRegressor:
    return XGBRegressor(objective="reg:quantileerror", quantile_alpha=np.array(QUANTILES),
                        n_estimators=400, max_depth=4, learning_rate=0.05, random_state=42)


class C2Model:
    """Point and quantile clearance-time predictors fitted together."""

    def fit(self, train: pd.DataFrame) -> "C2Model":
        self.point = point_model().fit(train[FEATURES], train["clearance_hours"])
        self.quant = quantile_model().fit(train[FEATURES], train["clearance_hours"])
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        X = prepare(df)[FEATURES] if "is_agrifood" not in df.columns else df[FEATURES]
        q = np.sort(self.quant.predict(X), axis=1)          # enforce non-crossing quantiles
        return pd.DataFrame({"pred_mean": self.point.predict(X).clip(min=0),
                             "pred_q10": q[:, 0].clip(min=0), "pred_q50": q[:, 1].clip(min=0),
                             "pred_q90": q[:, 2].clip(min=0)}, index=df.index)


def pinball(y, q, a):
    diff = y - q
    return float(np.mean(np.maximum(a * diff, (a - 1) * diff)))


def metrics(y: np.ndarray, pred: np.ndarray) -> Dict[str, float]:
    return {"MAE_h": round(mean_absolute_error(y, pred), 4),
            "RMSE_h": round(float(np.sqrt(mean_squared_error(y, pred))), 4),
            "R2": round(r2_score(y, pred), 4)}


def compare(train: pd.DataFrame, test: pd.DataFrame, model: C2Model) -> pd.DataFrame:
    y = test["clearance_hours"].to_numpy()
    rows = []
    group_mean = train.groupby(GROUP_KEYS)["clearance_hours"].mean()
    gm = test.set_index(GROUP_KEYS).index.map(group_mean).to_numpy(dtype=float)
    gm = np.where(np.isnan(gm), train["clearance_hours"].mean(), gm)
    rows.append({"model": "Group mean (spreadsheet)", **metrics(y, gm)})
    lin = LinearRegression().fit(train[FEATURES], train["clearance_hours"])
    rows.append({"model": "Linear regression", **metrics(y, lin.predict(test[FEATURES]))})
    p = model.predict(test)
    rows.append({"model": "XGBoost", **metrics(y, p["pred_mean"].to_numpy())})
    return pd.DataFrame(rows)


def interval_report(test: pd.DataFrame, model: C2Model) -> Dict[str, float]:
    p = model.predict(test)
    y = test["clearance_hours"].to_numpy()
    inside = (y >= p["pred_q10"]) & (y <= p["pred_q90"])
    return {"coverage_q10_q90": round(float(inside.mean()), 4),
            "mean_width_h": round(float((p["pred_q90"] - p["pred_q10"]).mean()), 4),
            "pinball_q10": round(pinball(y, p["pred_q10"].to_numpy(), 0.1), 4),
            "pinball_q50": round(pinball(y, p["pred_q50"].to_numpy(), 0.5), 4),
            "pinball_q90": round(pinball(y, p["pred_q90"].to_numpy(), 0.9), 4)}
