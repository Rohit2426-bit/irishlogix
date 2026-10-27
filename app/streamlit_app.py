"""
IrishLogix decision-support dashboard (demo artefact).

Run from the project root:  streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import os

os.chdir(ROOT)

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

from irishlogix.evaluation import benchmark as B
from irishlogix.network.corridor_network import NODES
from irishlogix.optim import planners as P
from irishlogix.optim.routes import route_options
from irishlogix.world.customs_world import day_instance

st.set_page_config(page_title="IrishLogix", layout="wide")


@st.cache_resource
def context():
    return B.load_context()


@st.cache_data
def plan_day(day: str, seed: int):
    ctx = context()
    d = pd.Timestamp(day)
    cons = day_instance(ctx.port_days, d, seed=seed)
    est = B.planner_estimates(ctx, cons, d)
    fronts = {name: P.optimise(cons, est[name], seed=seed) for name in ["Average delays", "Coupled (C1+C2)"]}
    return cons, est, fronts


ctx = context()
test_days = [d for d in pd.to_datetime(ctx.c1_probs.index.get_level_values("date").unique()) if d.dayofweek < 5]

st.title("IrishLogix: delay-aware, carbon-aware freight planning")
st.caption("Research prototype (MSc Data Analytics, NCI). Delays come from a semi-synthetic world calibrated to CSO port statistics.")

with st.sidebar:
    st.header("Scenario")
    day = st.selectbox("Planning day (test period)", test_days, index=10, format_func=lambda d: d.strftime("%a %d %b %Y"))
    seed = st.number_input("Consignment set (seed)", 1, 9999, 1000)
    price = st.select_slider("ETS2 carbon price (EUR per tonne CO2)", [40, 80, 120, 200, 300, 500, 1000], 80)

tab_plan, tab_bench = st.tabs(["Plan a day", "Benchmark results"])

with tab_plan:
    cons, est, fronts = plan_day(str(day.date()), int(seed))
    c2p = ctx.c2_model.predict(cons)

    st.subheader("1. Predictions for the day")
    col1, col2 = st.columns([1, 2])
    with col1:
        rows = []
        for port in ["Dublin", "Rosslare"]:
            p = ctx.c1_probs.loc[(day, port)]
            rows.append({"Port": port, "Low": p["p_Low"], "Medium": p["p_Medium"], "High": p["p_High"],
                         "Actual": p["congestion_class"]})
        st.markdown("**C1: port congestion tomorrow**")
        st.dataframe(pd.DataFrame(rows).style.format({"Low": "{:.0%}", "Medium": "{:.0%}", "High": "{:.0%}"}), hide_index=True)
    with col2:
        view = cons[["consignment_id", "port", "origin_gb", "commodity", "prelodged", "vessel_hour", "destination", "deadline_hour"]].copy()
        view["C2 clearance (h)"] = c2p["pred_mean"].round(2)
        view["C2 range (h)"] = c2p["pred_q10"].round(2).astype(str) + " to " + c2p["pred_q90"].round(2).astype(str)
        view["Actual clearance (h)"] = cons["true_clearance_hours"].round(2)
        st.markdown("**C2: customs clearance per consignment**")
        st.dataframe(view, hide_index=True)

    st.subheader("2. Cost versus CO2 trade-off (C3)")
    front = fronts["Coupled (C1+C2)"]
    chosen = P.choose(front, price)
    legal = [s for s in front if s["planned"]["viol_h"] == 0] or front
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[s["planned"]["co2_kg"] for s in legal], y=[s["planned"]["cost_ex_carbon"] for s in legal],
                             mode="markers", name="Pareto plans (legal)", marker=dict(size=8, color="#2a78d6")))
    fig.add_trace(go.Scatter(x=[chosen["planned"]["co2_kg"]], y=[chosen["planned"]["cost_ex_carbon"]], mode="markers",
                             name=f"Chosen at EUR {price}", marker=dict(size=16, symbol="star", color="#eb6834")))
    fig.update_layout(xaxis_title="CO2 (kg per day)", yaxis_title="Operating cost excl. carbon (EUR)", height=360,
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, width="stretch")

    st.subheader("3. Outcome when the plan meets the real day")
    plans = {"FIFO (spreadsheet)": P.fifo_plan(cons), "Average delays": P.choose(fronts["Average delays"], price)["plan"],
             "IrishLogix (C1+C2)": chosen["plan"]}
    results = {k: P.execute(v, cons) for k, v in plans.items()}
    kpi = pd.DataFrame({k: {"Total cost (EUR)": P.realised_cost(r, price), "Idle hours": r["totals"]["idle_h"],
                            "Late hours": r["totals"]["late_h"], "Driving-rule violation (h)": r["totals"]["viol_h"],
                            "CO2 (kg)": r["totals"]["co2_kg"], "km": r["totals"]["km"]} for k, r in results.items()}).T
    st.dataframe(kpi.style.format("{:,.1f}"))

    st.subheader("4. IrishLogix truck plan")
    plan = chosen["plan"]
    per = results["IrishLogix (C1+C2)"]["per_consignment"]
    sched = []
    for t, seq in enumerate(plan.trucks, start=1):
        for i in seq:
            r = per[i]
            sched.append({"Truck": t, "Consignment": cons.loc[i, "consignment_id"], "Port": cons.loc[i, "port"],
                          "Arrive port": f"{r['arrive']:.2f}", "Idle (h)": round(r["idle"], 2), "Deliver": f"{r['deliver']:.2f}",
                          "Late (h)": round(r["late"], 2), "Route": r["route"]})
    st.dataframe(pd.DataFrame(sched), hide_index=True)
    m = folium.Map(location=[53.1, -7.6], zoom_start=7, tiles="cartodbpositron")
    colours = ["#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"]
    for t, seq in enumerate(plan.trucks):
        for i in seq:
            opt = route_options(cons.loc[i, "port_node"], cons.loc[i, "destination"])[plan.route_idx[i]]
            folium.PolyLine([(NODES[n]["lat"], NODES[n]["lon"]) for n in opt.nodes], color=colours[t % 4], weight=4,
                            tooltip=f"Truck {t + 1}: {cons.loc[i, 'consignment_id']}").add_to(m)
    for n, a in NODES.items():
        folium.CircleMarker((a["lat"], a["lon"]), radius=5, tooltip=a["name"], color="#0b0b0b", fill=True).add_to(m)
    st_folium(m, height=430, width=None)

with tab_bench:
    path = Path("results/benchmark/summary_by_planner.csv")
    if path.exists():
        s = pd.read_csv(path)
        st.markdown(f"**Mean per day over the benchmark days (ETS2 EUR {price if price in (40, 80, 120) else 80})**")
        sel = s[s["ets2_price"] == (price if price in (40, 80, 120) else 80)]
        st.dataframe(sel.drop(columns=["ets2_price"]).set_index("planner").style.format("{:,.2f}"))
        t = pd.read_csv("results/benchmark/paired_tests.csv")
        st.markdown("**Paired tests (ETS2 EUR 80): Wilcoxon signed-rank and bootstrap 95% CI**")
        st.dataframe(t.style.format({c: "{:.3f}" for c in t.columns if t[c].dtype != object}), hide_index=True)
    for f in ["fig_benchmark_kpis.png", "fig_paired_cost_diff.png", "fig_value_of_information.png", "fig_carbon_threshold.png"]:
        if (Path("results/figures") / f).exists():
            st.image(str(Path("results/figures") / f))
