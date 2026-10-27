"""
Create the figures used in the report and presentation (results/figures/*.png).
Run after run_c1.py, run_c2.py, run_benchmark.py and run_optimiser_study.py.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path("results/figures")
ORDER = ["FIFO", "Average delays", "C1 only", "C2 only", "Coupled (C1+C2)", "Oracle"]
COLOURS = {"FIFO": "#898781", "Average delays": "#2a78d6", "C1 only": "#1baf7a", "C2 only": "#eda100",
           "Coupled (C1+C2)": "#eb6834", "Oracle": "#4a3aa7",
           "XGBoost": "#eb6834", "Logistic regression": "#2a78d6", "Persistence": "#898781",
           "Weekday climatology": "#eda100", "Linear regression": "#2a78d6", "Group mean (spreadsheet)": "#898781"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": "#e1e0d9", "grid.linewidth": 0.6})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=200)
    plt.close(fig)
    print("saved", name)


def c1_figures():
    cv = pd.read_csv("results/c1/cv_by_year.csv")
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    for m, g in cv.groupby("model"):
        ax.plot(g["year"], g["macro_f1"], marker="o", lw=2, color=COLOURS[m], label=m)
    ax.set(xlabel="Test year (trained on all earlier years)", ylabel="Macro-F1", title="C1: expanding-window cross-validation")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "fig_c1_cv.png")

    cm = pd.read_csv("results/c1/confusion_matrix.csv", index_col=0).to_numpy()
    fig, ax = plt.subplots(figsize=(4.2, 3.8))
    ax.imshow(cm, cmap="Blues")
    labels = ["Low", "Medium", "High"]
    ax.set_xticks(range(3), labels); ax.set_yticks(range(3), labels)
    ax.grid(False)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, int(cm[i, j]), ha="center", va="center", color="white" if cm[i, j] > cm.max() / 2 else "black")
    ax.set(xlabel="Predicted", ylabel="Actual", title="C1 confusion matrix (test)")
    save(fig, "fig_c1_confusion.png")

    shap = pd.read_csv("results/c1/shap_importance.csv", index_col=0).iloc[:10, 0][::-1]
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.barh(shap.index, shap.values, color="#2a78d6", height=0.6)
    ax.set(xlabel="Mean |SHAP value|", title="C1: most influential features")
    save(fig, "fig_c1_shap.png")


def c2_figures():
    m = pd.read_csv("results/c2/test_metrics_gb_only.csv")
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    ax.bar(m["model"], m["MAE_h"], color=[COLOURS[x] for x in m["model"]], width=0.55)
    for x, y in zip(m["model"], m["MAE_h"]):
        ax.text(x, y + 0.01, f"{y:.3f}", ha="center", fontsize=9)
    ax.set(ylabel="MAE (hours)", title="C2: clearance-time error, GB consignments (test)")
    save(fig, "fig_c2_mae.png")
    iv = json.load(open("results/c2/intervals.json"))
    fig, ax = plt.subplots(figsize=(4.5, 3.0))
    cov = [iv["all"]["coverage_q10_q90"], iv["gb_only"]["coverage_q10_q90"]]
    ax.bar(["All", "GB only"], cov, color="#1baf7a", width=0.5)
    ax.axhline(0.8, color="#0b0b0b", ls="--", lw=1)
    ax.text(1.3, 0.81, "target 80%", fontsize=8)
    ax.set(ylim=(0, 1), ylabel="Share inside 10th to 90th percentile", title="C2: prediction range coverage")
    save(fig, "fig_c2_coverage.png")


def benchmark_figures():
    d = pd.read_csv("results/benchmark/daily_results.csv", parse_dates=["date"])
    d80 = d[d["ets2_price"] == 80]
    means = d80.groupby("planner")[["total_cost", "idle_h", "co2_kg", "late_h"]].mean().reindex(ORDER)
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.4))
    for ax, (col, title) in zip(axes, [("total_cost", "Cost per day (EUR, ETS2 EUR 80)"), ("idle_h", "Idle hours per day"),
                                       ("co2_kg", "CO2 per day (kg)"), ("late_h", "Late delivery hours per day")]):
        ax.bar(range(len(ORDER)), means[col], color=[COLOURS[p] for p in ORDER], width=0.65)
        ax.set_xticks(range(len(ORDER)), [p.replace(" (C1+C2)", "") for p in ORDER], rotation=35, ha="right", fontsize=8)
        ax.set_title(title, fontsize=10)
        ax.set_ylim(0, means[col].max() * 1.1)
    save(fig, "fig_benchmark_kpis.png")

    wide = d80.pivot_table(index="date", columns="planner", values="total_cost")
    diffs = {"Coupled vs FIFO": wide["Coupled (C1+C2)"] - wide["FIFO"],
             "Coupled vs Average delays": wide["Coupled (C1+C2)"] - wide["Average delays"],
             "Oracle vs Coupled": wide["Oracle"] - wide["Coupled (C1+C2)"]}
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    ax.boxplot(list(diffs.values()), tick_labels=list(diffs.keys()), widths=0.5, showmeans=True,
               medianprops={"color": "#eb6834"}, meanprops={"marker": "D", "markerfacecolor": "#0b0b0b", "markeredgecolor": "#0b0b0b"})
    ax.axhline(0, color="#0b0b0b", lw=1)
    ax.set(ylabel="Daily cost difference (EUR)", title="Paired daily cost differences (below 0 = cheaper)")
    save(fig, "fig_paired_cost_diff.png")

    ct = pd.read_csv("results/scenarios/carbon_threshold.csv").groupby("ets2_price")[["co2_kg", "eco_share"]].mean()
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    axes[0].plot(ct.index, ct["co2_kg"], marker="o", lw=2, color="#eb6834")
    axes[0].set(xscale="log", xlabel="ETS2 price (EUR per tonne CO2, log scale)", ylabel="CO2 per day (kg)",
                title="Chosen plan's CO2 by carbon price")
    axes[0].set_ylim(0, ct["co2_kg"].max() * 1.1)
    axes[1].plot(ct.index, 100 * ct["eco_share"], marker="o", lw=2, color="#1baf7a")
    axes[1].set(xscale="log", xlabel="ETS2 price (EUR per tonne CO2, log scale)", ylabel="Loads driven at eco speed (%)",
                title="Speed choice by carbon price")
    axes[1].set_ylim(0, 100)
    for ax in axes:
        ax.axvspan(40, 120, color="#e1e0d9", alpha=0.5)
        ax.text(48, ax.get_ylim()[1] * 0.92, "studied ETS2 range", fontsize=8)
    save(fig, "fig_carbon_threshold.png")

    # Value of information: cost difference against the average-delay planner, 4 and 3 trucks.
    rows = []
    t4 = pd.read_csv("results/benchmark/paired_tests.csv")
    t3 = pd.read_csv("results/scenarios/fleet3_paired_tests.csv")
    for fleet, t in (("4 trucks", t4), ("3 trucks", t3)):
        for comp, lab in (("Coupled (C1+C2) vs Average delays", "Coupled (C1+C2)"), ("Oracle vs Average delays", "Oracle")):
            r = t[(t["comparison"] == comp) & (t["kpi"] == "total_cost")]
            if comp == "Oracle vs Average delays" and r.empty:
                a = t[(t["comparison"] == "Oracle vs Coupled (C1+C2)") & (t["kpi"] == "total_cost")]
                b = t[(t["comparison"] == "Coupled (C1+C2) vs Average delays") & (t["kpi"] == "total_cost")]
                rows.append({"fleet": fleet, "planner": lab, "mean": float(a["mean_diff"].iloc[0] + b["mean_diff"].iloc[0]), "lo": np.nan, "hi": np.nan})
                continue
            rows.append({"fleet": fleet, "planner": lab, "mean": float(r["mean_diff"].iloc[0]),
                         "lo": float(r["ci95_low"].iloc[0]), "hi": float(r["ci95_high"].iloc[0])})
    v = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    for j, (fleet, g) in enumerate(v.groupby("fleet", sort=False)):
        for k, (_, r) in enumerate(g.iterrows()):
            x = j * 3 + k
            ax.bar(x, r["mean"], color=COLOURS[r["planner"]], width=0.8, label=r["planner"] if j == 0 else None)
            if not np.isnan(r["lo"]):
                ax.errorbar(x, r["mean"], yerr=[[r["mean"] - r["lo"]], [r["hi"] - r["mean"]]], color="#0b0b0b", capsize=4)
    ax.axhline(0, color="#0b0b0b", lw=1)
    ax.set_xticks([0.5, 3.5], v["fleet"].unique())
    ax.set(ylabel="Daily cost vs average-delay planner (EUR)", title="Value of delay information (below 0 = saving)")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "fig_value_of_information.png")

    s = pd.read_csv("results/benchmark/sensitivity_checks.csv")
    base = d80[d80["planner"].isin(s["planner"].unique())].assign(check_scale=1.0)
    s = pd.concat([s, base[s.columns.intersection(base.columns)]])
    g = s.groupby(["check_scale", "planner"])["idle_h"].mean().unstack()
    fig, ax = plt.subplots(figsize=(6, 3.5))
    for p in ["FIFO", "Average delays", "Coupled (C1+C2)", "Oracle"]:
        ax.plot(g.index, g[p], marker="o", lw=2, color=COLOURS[p], label=p)
    ax.set(xlabel="Customs check rate (x baseline)", ylabel="Idle hours per day", title="Sensitivity to customs check rate")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "fig_sensitivity_checks.png")


def optimiser_figures():
    path = Path("results/optimiser/convergence_summary.csv")
    if not path.exists():
        return
    c = pd.read_csv(path)
    fig, ax = plt.subplots(figsize=(5.5, 3.3))
    ax.bar(c["budget"], c["mean_gap_pct"], color="#2a78d6", width=0.5, label="mean gap")
    ax.plot(c["budget"], c["max_gap_pct"], "D", color="#eb6834", label="worst gap")
    ax.set(xlabel="NSGA-II budget (population x generations)", ylabel="Gap to best plan found (%)", title="Optimiser convergence")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "fig_optimiser_convergence.png")


def pareto_example():
    from irishlogix.evaluation import benchmark as B
    from irishlogix.optim import planners as P
    from irishlogix.world.customs_world import day_instance
    ctx = B.load_context()
    day = B.test_days(ctx, n=100)[0]
    cons = day_instance(ctx.port_days, day, seed=1000)
    front = P.optimise(cons, B.planner_estimates(ctx, cons, day)["Coupled (C1+C2)"], seed=1000)
    front = [f for f in front if f["planned"]["viol_h"] == 0]
    pts = np.array([[f["planned"]["co2_kg"], f["planned"]["cost_ex_carbon"]] for f in front])
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.scatter(pts[:, 0], pts[:, 1], s=28, color="#2a78d6", label="Pareto plans (all legal under EC 561/2006)")
    for price, mk in [(40, "o"), (80, "s"), (120, "^")]:
        ch = P.choose(front, price)["planned"]
        ax.scatter(ch["co2_kg"], ch["cost_ex_carbon"], s=90, marker=mk, facecolor="none", edgecolor="#eb6834", lw=2,
                   label=f"chosen at EUR {price}")
    ax.set(xlabel="CO2 (kg per day)", ylabel="Operating cost excl. carbon (EUR)", title=f"Example Pareto front, {day:%d %b %Y}")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "fig_pareto_example.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    c1_figures()
    c2_figures()
    benchmark_figures()
    optimiser_figures()
    pareto_example()
