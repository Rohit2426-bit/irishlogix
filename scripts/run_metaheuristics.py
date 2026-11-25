"""
More metaheuristics for C3 (added after the Week 10 supervision meeting).

Differential evolution, particle swarm optimisation and simulated annealing are run on the same
12 days, 3 seeds, Oracle delays and budget (8,000 plan evaluations) as the optimiser study, and
compared with NSGA-II, the weighted-sum genetic algorithm and random search from that study.
The single-objective methods minimise cost plus carbon cost at EUR 80 per tonne.

Needs results/optimiser/alternatives.csv (run_optimiser_study.py) first.
Outputs (results/optimiser/): metaheuristics.csv, metaheuristics_summary.csv
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np
import pandas as pd
from pymoo.algorithms.soo.nonconvex.de import DE
from pymoo.algorithms.soo.nonconvex.pso import PSO
from pymoo.core.problem import Problem
from pymoo.optimize import minimize

from irishlogix.evaluation import benchmark as B
from irishlogix.optim import planners as P
from irishlogix.optim.routes import route_options
from irishlogix.optim.schedule import simulate
from irishlogix.world.customs_world import day_instance

PRICE = 80.0
BUDGET = 8000


def objective(x, c, d, n_opts):
    tot = simulate(P.decode(x, len(n_opts), n_opts), c, d, True)["totals"]
    return tot["objective_cost"] + PRICE * tot["co2_kg"] / 1000.0


class WeightedSum(Problem):
    def __init__(self, c, d, n_opts):
        self.c, self.d, self.n_opts = c, d, n_opts
        super().__init__(n_var=3 * len(n_opts), n_obj=1, xl=0.0, xu=1.0)

    def _evaluate(self, X, out, *args, **kwargs):
        out["F"] = np.array([[objective(x, self.c, self.d, self.n_opts)] for x in X])


def simulated_annealing(c, d, n_opts, seed, evals=BUDGET):
    """Change one to three genes at a time; accept worse plans with a probability that falls as it cools."""
    rng = np.random.default_rng(seed)
    m = 3 * len(n_opts)
    x = rng.random(m)
    fx = objective(x, c, d, n_opts)
    best = fx
    t0, t1 = 50.0, 0.5            # temperature in EUR, from start to end
    for k in range(1, evals):
        frac = k / evals
        temp = t0 * (t1 / t0) ** frac
        step = 0.3 * (1 - frac) + 0.02
        y = x.copy()
        genes = rng.choice(m, size=rng.integers(1, 4), replace=False)
        y[genes] = np.clip(y[genes] + rng.normal(0, step, len(genes)), 0, 1)
        fy = objective(y, c, d, n_opts)
        if fy < fx or rng.random() < np.exp(-(fy - fx) / temp):
            x, fx = y, fy
            best = min(best, fx)
    return best


def main(n_days: int = 12):
    out = Path("results/optimiser")
    prev = pd.read_csv(out / "alternatives.csv")
    ctx = B.load_context()
    days = B.test_days(ctx, n=100)[:n_days]
    rows = []
    for k, day in enumerate(days):
        cons = day_instance(ctx.port_days, day, seed=1000 + k)
        d = P.oracle_delays(cons)
        c = P.as_dict(cons)
        n_opts = [len(route_options(p, q)) for p, q in zip(c["port_node"], c["destination"])]
        for s in range(3):
            for name, algo in [("Differential evolution", DE(pop_size=80)), ("Particle swarm", PSO(pop_size=80))]:
                t0 = time.time()
                res = minimize(WeightedSum(c, d, n_opts), algo, ("n_gen", BUDGET // 80), seed=s, verbose=False)
                rows.append({"day": k, "method": name, "seed": s, "objective": float(res.F[0]), "seconds": time.time() - t0})
            t0 = time.time()
            rows.append({"day": k, "method": "Simulated annealing", "seed": s,
                         "objective": simulated_annealing(c, d, n_opts, s), "seconds": time.time() - t0})
        print("day", k, "done", flush=True)

    allm = pd.concat([prev[["day", "method", "seed", "objective", "seconds"]], pd.DataFrame(rows)], ignore_index=True)
    best_known = allm.groupby("day").objective.min()
    allm["gap_pct"] = 100 * (allm.objective - allm.day.map(best_known)) / allm.day.map(best_known)
    allm.to_csv(out / "metaheuristics.csv", index=False)
    summary = (allm.groupby("method").agg(mean_gap_pct=("gap_pct", "mean"), max_gap_pct=("gap_pct", "max"),
                                          seconds=("seconds", "mean")).round(3).sort_values("mean_gap_pct"))
    summary.to_csv(out / "metaheuristics_summary.csv")
    print(summary.to_string())


if __name__ == "__main__":
    main()
