"""
Optimiser study: search budget and alternative optimisation methods (Oracle delays, 12 test days).

1. NSGA-II convergence for three budgets and three seeds (justifies the 80 x 100 budget).
2. Alternatives at the same budget: a weighted-sum genetic algorithm (one combined cost at
   EUR 80 per tonne, as in single-objective low-carbon routing) and random search.

Outputs (results/optimiser/): convergence.csv, convergence_summary.csv, alternatives.csv
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np
import pandas as pd
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.core.problem import Problem
from pymoo.optimize import minimize

from irishlogix.evaluation import benchmark as B
from irishlogix.optim import planners as P
from irishlogix.optim.routes import route_options
from irishlogix.optim.schedule import simulate
from irishlogix.world.customs_world import day_instance

PRICE = 80.0


def scalar(tot):
    return tot["objective_cost"] + PRICE * tot["co2_kg"] / 1000.0


class WeightedSum(Problem):
    def __init__(self, cons, delays, n_opts):
        self.cons, self.delays, self.n_opts, self.n = cons, delays, n_opts, len(n_opts)
        super().__init__(n_var=3 * self.n, n_obj=1, xl=0.0, xu=1.0)

    def _evaluate(self, X, out, *args, **kwargs):
        out["F"] = np.array([[scalar(simulate(P.decode(x, self.n, self.n_opts), self.cons, self.delays, True)["totals"])] for x in X])


def main(n_days: int = 12):
    out = Path("results/optimiser")
    out.mkdir(parents=True, exist_ok=True)
    ctx = B.load_context()
    days = B.test_days(ctx, n=100)[:n_days]
    conv, alt = [], []
    for k, day in enumerate(days):
        cons = day_instance(ctx.port_days, day, seed=1000 + k)
        d = P.oracle_delays(cons)
        c = P.as_dict(cons)
        n_opts = [len(route_options(p, q)) for p, q in zip(c["port_node"], c["destination"])]
        for pop, gens in [(40, 50), (80, 100), (120, 200)]:
            for s in range(3):
                t0 = time.time()
                best = P.choose(P.optimise(cons, d, seed=s, pop=pop, gens=gens), PRICE)["planned"]
                conv.append({"day": k, "budget": f"{pop}x{gens}", "evaluations": pop * gens, "seed": s,
                             "objective": scalar(best), "seconds": time.time() - t0})
        for s in range(3):
            t0 = time.time()
            res = minimize(WeightedSum(c, d, n_opts), GA(pop_size=80), ("n_gen", 100), seed=s, verbose=False)
            alt.append({"day": k, "method": "Weighted-sum GA (EUR 80 only)", "seed": s,
                        "objective": float(res.F[0]), "seconds": time.time() - t0})
            t0 = time.time()
            rng = np.random.default_rng(s)
            X = rng.random((8000, 3 * len(n_opts)))
            val = min(scalar(simulate(P.decode(x, len(n_opts), n_opts), c, d, True)["totals"]) for x in X)
            alt.append({"day": k, "method": "Random search (8,000 plans)", "seed": s, "objective": val,
                        "seconds": time.time() - t0})
    conv = pd.DataFrame(conv)
    best_known = pd.concat([conv[["day", "objective"]], pd.DataFrame(alt)[["day", "objective"]]]).groupby("day").objective.min()
    conv["gap_pct"] = 100 * (conv.objective - conv.day.map(best_known)) / conv.day.map(best_known)
    conv.to_csv(out / "convergence.csv", index=False)
    summary = conv.groupby("budget").agg(evaluations=("evaluations", "first"), mean_gap_pct=("gap_pct", "mean"),
                                         max_gap_pct=("gap_pct", "max"), seconds=("seconds", "mean")).round(3)
    summary["sd_across_seeds_eur"] = conv.groupby(["budget", "day"]).objective.std().groupby("budget").mean().round(2)
    summary.to_csv(out / "convergence_summary.csv")
    alt = pd.DataFrame(alt)
    nsga = conv[conv.budget == "80x100"].assign(method="NSGA-II (whole Pareto front)")[["day", "method", "seed", "objective", "seconds"]]
    alt = pd.concat([alt, nsga], ignore_index=True)
    alt["gap_pct"] = 100 * (alt.objective - alt.day.map(best_known)) / alt.day.map(best_known)
    alt.to_csv(out / "alternatives.csv", index=False)
    print(summary.to_string())
    print(alt.groupby("method").agg(mean_gap_pct=("gap_pct", "mean"), max_gap_pct=("gap_pct", "max"),
                                    seconds=("seconds", "mean")).round(3).to_string())


if __name__ == "__main__":
    main()
