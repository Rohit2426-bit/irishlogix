"""
Paired statistical comparison of planners across benchmark days.

For each pair (A versus B) and KPI: mean and median daily difference (A minus B), a 95%
bootstrap confidence interval for the mean difference, the Wilcoxon signed-rank test and the
matched-pairs rank-biserial correlation as effect size.
"""

import numpy as np
import pandas as pd
from scipy.stats import rankdata, wilcoxon

PAIRS = [
    ("Coupled (C1+C2)", "FIFO"),
    ("Average delays", "FIFO"),
    ("Coupled (C1+C2)", "Average delays"),
    ("C1 only", "Average delays"),
    ("C2 only", "Average delays"),
    ("Oracle", "Coupled (C1+C2)"),
]


def rank_biserial(diff: np.ndarray) -> float:
    d = diff[diff != 0]
    if len(d) == 0:
        return 0.0
    ranks = rankdata(np.abs(d))
    return float((ranks[d > 0].sum() - ranks[d < 0].sum()) / ranks.sum())


def bootstrap_ci(diff: np.ndarray, n_boot: int = 5000, seed: int = 0):
    rng = np.random.default_rng(seed)
    means = rng.choice(diff, (n_boot, len(diff)), replace=True).mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def paired_tests(df: pd.DataFrame, kpis, pairs=PAIRS, price: float = 80.0) -> pd.DataFrame:
    d = df[df["ets2_price"] == price]
    wide = {k: d.pivot_table(index="date", columns="planner", values=k) for k in kpis}
    rows = []
    for a, b in pairs:
        for k in kpis:
            if a not in wide[k] or b not in wide[k]:
                continue
            diff = (wide[k][a] - wide[k][b]).dropna().to_numpy()
            lo, hi = bootstrap_ci(diff)
            p = wilcoxon(diff).pvalue if np.any(diff != 0) else 1.0
            base = wide[k][b].mean()
            rows.append({"comparison": f"{a} vs {b}", "kpi": k, "n_days": len(diff),
                         "mean_a": wide[k][a].mean(), "mean_b": base,
                         "mean_diff": diff.mean(), "ci95_low": lo, "ci95_high": hi,
                         "pct_change": 100 * diff.mean() / base if base else np.nan,
                         "median_diff": float(np.median(diff)), "wilcoxon_p": p,
                         "effect_rank_biserial": rank_biserial(diff)})
    return pd.DataFrame(rows)
