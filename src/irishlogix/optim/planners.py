"""
Planners compared in the evaluation.

FIFO            spreadsheet practice: loads in vessel order to the first free truck, shortest
                route, trucks sent to arrive when the vessel docks. No delay information.
Average delays  the C3 optimiser fed with historical averages (decoupled planning).
C1 only / C2 only  ablations: one predicted component, the other at its historical average.
Coupled         the C3 optimiser fed with C1 congestion probabilities and C2 clearance predictions.
Oracle          the C3 optimiser fed with the true delays (upper bound, not achievable in practice).

The optimised planners all use the same NSGA-II search over truck assignment, visiting order and
route option, returning a Pareto set of plans trading operating cost against CO2. One plan is
chosen from the set for each ETS2 carbon price by minimising cost plus carbon cost.
"""

from typing import Dict, List

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import Problem
from pymoo.optimize import minimize

from ..world import assumptions as A
from .routes import route_options, shortest
from .schedule import Delays, Plan, simulate, total_cost

CLASSES = ["Low", "Medium", "High"]


def as_dict(cons) -> dict:
    return {k: cons[k].to_numpy() for k in ("vessel_hour", "deadline_hour", "port_node", "destination", "port")}


def mean_unload(port: str) -> float:
    return float(np.exp(np.log(A.UNLOAD_MEDIAN_HOURS[port]) + A.UNLOAD_SPREAD ** 2 / 2))


def expected_queue(port: str, probs: Dict[str, float]) -> float:
    return sum(probs[c] * A.QUEUE_MEAN_HOURS[port][c] for c in CLASSES)


def true_delays(cons) -> Delays:
    sd = A.QUEUE_SPREAD
    noise = np.exp(sd * _norm_ppf(cons["queue_draw"].to_numpy()) - sd ** 2 / 2)
    base = np.array([A.QUEUE_MEAN_HOURS[p][c] for p, c in zip(cons["port"], cons["true_congestion_class"])])
    return Delays((cons["true_unload_hours"] + cons["true_clearance_hours"]).to_numpy(), base, noise)


def _norm_ppf(u: np.ndarray) -> np.ndarray:
    from scipy.stats import norm
    return norm.ppf(np.clip(u, 1e-6, 1 - 1e-6))


def estimate_delays(cons, clearance_est: np.ndarray, class_probs: List[Dict[str, float]]) -> Delays:
    unload = np.array([mean_unload(p) for p in cons["port"]])
    base = np.array([expected_queue(p, pr) for p, pr in zip(cons["port"], class_probs)])
    return Delays(unload + clearance_est, base, np.ones(len(cons)))


def oracle_delays(cons) -> Delays:
    base = np.array([A.QUEUE_MEAN_HOURS[p][c] for p, c in zip(cons["port"], cons["true_congestion_class"])])
    return Delays((cons["true_unload_hours"] + cons["true_clearance_hours"]).to_numpy(), base, np.ones(len(cons)))


# ------------------------------------------------------------------ FIFO (no optimisation)
def fifo_plan(cons) -> Plan:
    c = as_dict(cons)
    order = np.argsort(c["vessel_hour"])
    trucks: List[List[int]] = [[] for _ in range(A.FLEET_SIZE)]
    free_at = np.zeros(A.FLEET_SIZE)
    for i in order:
        k = int(np.argmin(free_at))
        trucks[k].append(int(i))
        free_at[k] = c["vessel_hour"][i] + 1.0 + shortest(c["port_node"][i], c["destination"][i]).hours
    route_idx = {int(i): 0 for i in range(len(cons))}
    target = {int(i): float(c["vessel_hour"][i]) for i in range(len(cons))}
    return Plan(trucks, route_idx, target)


# ------------------------------------------------------------------ NSGA-II optimiser
def decode(x: np.ndarray, n: int, n_opts: List[int]) -> Plan:
    truck = np.minimum((x[:n] * A.FLEET_SIZE).astype(int), A.FLEET_SIZE - 1)
    prio = x[n:2 * n]
    ridx = {i: int(min(x[2 * n + i] * n_opts[i], n_opts[i] - 1)) for i in range(n)}
    trucks = [sorted([i for i in range(n) if truck[i] == k], key=lambda i: prio[i]) for k in range(A.FLEET_SIZE)]
    return Plan(trucks, ridx, {})


class DayProblem(Problem):
    def __init__(self, cons: dict, delays: Delays, n_opts: List[int]):
        self.cons, self.delays, self.n_opts, self.n = cons, delays, n_opts, len(n_opts)
        super().__init__(n_var=3 * self.n, n_obj=2, xl=0.0, xu=1.0)

    def _evaluate(self, X, out, *args, **kwargs):
        F = np.empty((len(X), 2))
        for r, x in enumerate(X):
            tot = simulate(decode(x, self.n, self.n_opts), self.cons, self.delays, set_targets=True)["totals"]
            F[r] = (tot["objective_cost"], tot["co2_kg"])
        out["F"] = F


def optimise(cons, delays: Delays, seed: int, pop: int = 80, gens: int = 100) -> List[dict]:
    """Return the Pareto set as a list of {plan, planned totals}."""
    c = as_dict(cons)
    n_opts = [len(route_options(p, d)) for p, d in zip(c["port_node"], c["destination"])]
    res = minimize(DayProblem(c, delays, n_opts), NSGA2(pop_size=pop), ("n_gen", gens), seed=seed, verbose=False)
    X = np.atleast_2d(res.X)
    front = []
    for x in X:
        plan = decode(x, len(n_opts), n_opts)
        tot = simulate(plan, c, delays, set_targets=True)["totals"]
        front.append({"plan": plan, "planned": tot})
    return front


def choose(front: List[dict], ets2_price: float) -> dict:
    """Pick the plan with the lowest planned cost including carbon at the given ETS2 price."""
    return min(front, key=lambda s: s["planned"]["objective_cost"] + ets2_price * s["planned"]["co2_kg"] / 1000.0)


def execute(plan: Plan, cons) -> dict:
    """Replay a plan against the true delays of the day."""
    return simulate(plan, as_dict(cons), true_delays(cons), set_targets=False)


def realised_cost(result: dict, ets2_price: float) -> float:
    return total_cost(result["totals"], ets2_price)
