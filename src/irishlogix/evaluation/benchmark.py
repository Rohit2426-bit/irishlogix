"""
Paired benchmark of the planners on held-out days (2025 to mid-2026).

Every planner plans the same consignments and is executed against the same realised delays
(common random numbers), so differences between planners are paired by day.
"""

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd

from ..models import c2_customs as c2
from ..optim import planners as P
from ..world import assumptions as A
from ..world.customs_world import day_instance

ETS2_PRICES = [40.0, 80.0, 120.0]
PLANNERS = ["FIFO", "Average delays", "C1 only", "C2 only", "Coupled (C1+C2)", "Oracle"]
KPIS = ["cost_ex_carbon", "co2_kg", "km", "idle_h", "late_h", "viol_h", "duty_h", "fuel_l", "g_co2_per_km"]


@dataclass
class Context:
    port_days: pd.DataFrame
    c1_probs: pd.DataFrame
    c2_model: c2.C2Model
    clearance_group_mean: pd.Series
    clearance_overall_mean: float
    class_freq: pd.DataFrame


def load_context(world_dir="data/world", c1_dir="results/c1") -> Context:
    port_days = pd.read_csv(f"{world_dir}/port_days.csv", parse_dates=["date"])
    probs = pd.read_csv(f"{c1_dir}/test_probabilities.csv", parse_dates=["date"]).set_index(["date", "port"])
    hist = pd.read_csv(f"{world_dir}/customs_history.csv", parse_dates=["date"])
    sets = c2.split(hist)
    trval = pd.concat([sets["train"], sets["valid"]])
    model = c2.C2Model().fit(trval)
    known = port_days[port_days["date"] <= A.VALID_END]
    freq = known.groupby("port")["congestion_class"].value_counts(normalize=True).unstack().fillna(0)
    return Context(port_days, probs, model, trval.groupby(c2.GROUP_KEYS)["clearance_hours"].mean(),
                   float(trval["clearance_hours"].mean()), freq)


def test_days(ctx: Context, n: int = 100, seed: int = 11) -> List[pd.Timestamp]:
    days = ctx.port_days.loc[(ctx.port_days["date"] > A.VALID_END) & (ctx.port_days["dow"] < 5), "date"].unique()
    rng = np.random.default_rng(seed)
    return sorted(pd.Timestamp(d) for d in rng.choice(days, n, replace=False))


def planner_estimates(ctx: Context, cons: pd.DataFrame, day: pd.Timestamp) -> Dict[str, P.Delays]:
    avg_clear = np.array([ctx.clearance_group_mean.get((int(g), c, int(p)), ctx.clearance_overall_mean)
                          for g, c, p in zip(cons["origin_gb"], cons["commodity"], cons["prelodged"])])
    ml_clear = ctx.c2_model.predict(cons)["pred_mean"].to_numpy()
    avg_p = [ctx.class_freq.loc[p].to_dict() for p in cons["port"]]
    c1_p = [{c: float(ctx.c1_probs.loc[(day, p), f"p_{c}"]) for c in P.CLASSES} for p in cons["port"]]
    return {
        "Average delays": P.estimate_delays(cons, avg_clear, avg_p),
        "C1 only": P.estimate_delays(cons, avg_clear, c1_p),
        "C2 only": P.estimate_delays(cons, ml_clear, avg_p),
        "Coupled (C1+C2)": P.estimate_delays(cons, ml_clear, c1_p),
        "Oracle": P.oracle_delays(cons),
    }


def run_day(ctx: Context, day: pd.Timestamp, seed: int, check_scale: float = 1.0,
            planners=PLANNERS, prices=ETS2_PRICES, trip_price: float = 80.0):
    """Plan and execute one day for every planner. Returns (daily rows, per-consignment rows)."""
    cons = day_instance(ctx.port_days, day, seed=seed, check_scale=check_scale)
    rows, trips = [], []
    fifo = P.execute(P.fifo_plan(cons), cons)
    estimates = planner_estimates(ctx, cons, day)
    for name in planners:
        if name == "FIFO":
            results = {price: fifo for price in prices}
            front_size = 1
        else:
            front = P.optimise(cons, estimates[name], seed=seed)
            front_size = len(front)
            results = {price: P.execute(P.choose(front, price)["plan"], cons) for price in prices}
        for price in prices:
            tot = results[price]["totals"]
            eco = float(np.mean([r["eco"] for r in results[price]["per_consignment"].values()]))
            rows.append({"date": day, "planner": name, "ets2_price": price, "check_scale": check_scale,
                         "front_size": front_size, "eco_share": eco,
                         "total_cost": P.realised_cost(results[price], price),
                         **{k: tot[k] for k in KPIS}})
        if trip_price in results:
            for i, r in results[trip_price]["per_consignment"].items():
                trips.append({"date": day, "planner": name, "consignment_id": cons.loc[i, "consignment_id"],
                              "port": cons.loc[i, "port"], "origin_gb": bool(cons.loc[i, "origin_gb"]),
                              "commodity": cons.loc[i, "commodity"], "idle_h": r["idle"], "queue_h": r["queue"],
                              "wait_release_h": r["wait_release"], "late_h": r["late"], "route": r["route"]})
    return rows, trips
