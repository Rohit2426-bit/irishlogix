# IrishLogix: Coupling Port and Customs Delay Prediction with Carbon-Aware Route Optimisation for Post-Brexit Irish Freight

**MSc in Data Analytics, Research Practicum (MSCDAD_A_JAN26I), National College of Ireland**
**Student:** Rohitkumar Amritlal Jaiswal (x25119613)
**Supervisor:** Dr. Athanasios Staikopoulos

## Overview

IrishLogix plans a day of import collections from Dublin Port and Rosslare Europort for a small haulage fleet. It has three components:

1. **C1, port congestion classifier:** XGBoost predicts tomorrow's congestion class (Low, Medium, High) at each port from information known the evening before.
2. **C2, customs clearance regressor:** XGBoost predicts each consignment's clearance time, with a 10th to 90th percentile range.
3. **C3, carbon-aware optimiser:** NSGA-II (pymoo) chooses truck assignment, visiting order, route and speed, with driving-time breaks under Regulation (EC) No 561/2006. It returns a Pareto set of plans (cost against CO2) and picks one plan for a given ETS2 carbon price.

Daily port and customs data are not public, so the components are trained and tested in a **semi-synthetic world**. Quarterly CSO port statistics set the real levels, and the daily variation follows stated assumptions in `src/irishlogix/world/assumptions.py`.

## Research question

To what extent does coupling predictions of port congestion and customs clearance delay with carbon-aware route optimisation reduce waiting time, cost and CO2, compared with spreadsheet (FIFO) planning?

- **SRQ1:** How accurately can the delays be predicted?
- **SRQ2:** How much of the gain comes from the predictions, compared with FIFO and with the same optimiser using average delays?
- **SRQ3:** How do the results change with the ETS2 carbon price and the customs check rate?

## Main results (100 paired test days, 2025 to mid-2026)

| Planner (mean per day, ETS2 EUR 80) | Cost (EUR) | Idle (h) | Rule violations (h) | CO2 (kg) |
|---|---|---|---|---|
| FIFO (spreadsheet) | 2,919 | 9.49 | 4.17 | 1,220 |
| Optimiser with average delays | 2,677 | 5.89 | 0.20 | 1,158 |
| Coupled (C1 + C2) | 2,698 | 5.91 | 0.20 | 1,160 |
| Oracle (perfect information) | 2,675 | 5.36 | 0.21 | 1,158 |

- Compared with FIFO, the coupled planner cuts cost by 7.6%, idle time by 38% and CO2 by 4.8% (Wilcoxon p < 0.001).
- The predictions add no measurable value over average delays with 4 trucks (+0.8%, p = 0.98). Even perfect information is worth under 1%. With 3 trucks, the coupled planner captures about 89% of that value (not significant).
- Between EUR 40 and EUR 500 per tonne, the carbon price barely changes routing. Eco speed only becomes the usual choice at EUR 1,000.
- C1 macro-F1 is 0.63 (persistence 0.51). C2 MAE for GB loads is 0.60 h (group average 0.62 h), and its range covers 79% of actual clearance times.

## Data

| CSO table | Statistic used | Content |
|---|---|---|
| TBQ01 | TBQ01C01 | Vessel arrivals per quarter |
| TBQ03 | TBQ03C05, TBQ03C07 | Ro-Ro freight units, loaded and empty |
| TBQ04 | TBQ04C01 | Lo-Lo container units (reference only, not Ro-Ro) |
| TBQ05, TBQ07 | Goods handled | Tonnage by region of trade (GB, EU) |

Raw files are in `data/raw/cso/`. Each statistic is selected by its code, so counts and tonnages are never added together. Only public secondary data is used, and no personal data is processed.

## Repository structure

```
data/raw/cso/            raw CSO tables
data/processed/          cleaned CSO series and quarterly activity matrix
src/irishlogix/data/     CSO loader
src/irishlogix/network/  11-hub Irish road network
src/irishlogix/world/    simulation world and all assumptions
src/irishlogix/models/   C1 and C2
src/irishlogix/optim/    route options, fuel model, schedule simulator, planners, NSGA-II
src/irishlogix/evaluation/ benchmark and paired statistical tests
scripts/                 one script per pipeline step, plus run_all.py
app/streamlit_app.py     decision-support dashboard
tests/                   unit tests
results/                 tables, saved models and figures
```

## How to run

Use Python 3.14 with the pinned packages:

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests -q        # unit tests
python scripts/run_all.py        # rebuild every result; timings go to results/pipeline_timings.csv
streamlit run app/streamlit_app.py
```

The pipeline runs these steps in order: data ingestion, simulation world, C1, C2, planner benchmark, scenarios, optimiser study, figures and tests. Each script can also be run on its own. All random steps use fixed seeds, so results are repeatable. The configuration manual has the full details.

## Week 1 baseline

`scripts/run_baseline_benchmark.py` and `src/irishlogix/simulation/` hold the first FIFO baseline from Week 1. The final evaluation uses the FIFO planner in `src/irishlogix/optim/planners.py`.
