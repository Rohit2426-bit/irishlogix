# IrishLogix: Coupled Predictive Delay Analytics & Carbon-Aware Route Optimisation

**MSc in Data Analytics: Research Practicum (MSCDAD_A_JAN26I)**  
**National College of Ireland (NCI)**  
**Student:** Rohitkumar Amritlal Jaiswal (Student ID: 25119613)  
**Academic Supervisor:** Dr. Thanos Staikopoulos  
**Date:** September 2026  

---

## 1. Project Overview & Research Context

**IrishLogix** is a closed-loop decision support system designed to bridge the void between **predictive delay forecasting** and **prescriptive vehicle route optimisation** across post-Brexit Irish freight corridors.

Over 80% of Ireland's external freight moves through maritime ports (Dublin Port, Port of Cork, Rosslare Europort). Following the UK's departure from the EU single market and customs union, Irish freight hauliers face volatile port berth congestion and unpredictable customs inspection hold-ups. Combined with strict driver rest mandates under **Regulation (EC) No 561/2006** and impending carbon costs under **EU ETS2 (Directive 2023/959)** and **CSRD (Directive 2022/2464)**, traditional spreadsheet-based (FIFO) haulage planning causes severe vehicle gate idling, excess diesel consumption, and inflated operational costs.

### Research Questions
- **Primary Research Question (PRQ):** To what extent does an integrated decision-support system coupling machine learning delay predictions with carbon-aware multi-objective route optimisation outperform traditional spreadsheet-based planning in reducing vehicle waiting hours, operational costs, and carbon intensity across post-Brexit Irish freight corridors?
- **SRQ 1 (Predictive Modeling):** How accurately can gradient-boosted models (XGBoost) predict next-day port congestion risk and customs clearance delays using open maritime and calibrated trade data?
- **SRQ 2 (Prescriptive Coupling):** Does integrating stochastic upstream delay predictions into a bi-objective route optimizer deliver statistically significant reductions in vehicle idle waiting time and total transit cost compared to static FIFO planning?
- **SRQ 3 (Decarbonisation & Policy):** How resilient is the generated Pareto frontier to fluctuating EU ETS2 carbon prices (EUR 40 to EUR 120 per tonne) in achieving CSRD-aligned fleet emissions reductions?

---

## 2. System Architecture

IrishLogix operates across three tightly coupled technical components:

```
┌────────────────────────────────────────────────────────┐
│               IrishLogix Architecture                   │
├────────────────────────────────────────────────────────┤
│                                                        │
│  [Open CSO PxStat API]      [Calibrated Customs Data]  │
│  (TBQ01, TBQ04, TBQ05)      (CSO Trade Lane Matrix)   │
│           │                               │            │
│           ▼                               ▼            │
│  ┌──────────────────┐           ┌──────────────────┐   │
│  │   Component 1:   │           │   Component 2:   │   │
│  │ Port Congestion  │           │  Customs Delay   │   │
│  │ Classifier (XGB) │           │  Regressor (XGB) │   │
│  └────────┬─────────┘           └────────┬─────────┘   │
│           │ Dynamic Waiting Distributions│             │
│           └──────────────┬───────────────┘             │
│                          ▼                             │
│             ┌─────────────────────────┐                │
│             │      Component 3:       │                │
│             │ Carbon-Aware Multi-Obj  │                │
│             │ Pareto Optimizer (OSM)  │                │
│             └────────────┬────────────┘                │
│                          ▼                             │
│             ┌─────────────────────────┐                │
│             │ Interactive Dispatcher  │                │
│             │ Dashboard (Streamlit)   │                │
│             └─────────────────────────┘                │
└────────────────────────────────────────────────────────┘
```

1. **Component 1 (C1: Port Congestion Classifier):** XGBoost classifier predicting next-day port congestion risk (Low, Medium, High) using CSO maritime traffic (arrivals, Ro-Ro units, tonnage) and EMODnet vessel density.
2. **Component 2 (C2: Customs Delay Regressor):** XGBoost regressor predicting lane-specific customs clearance durations based on commodity risk (SPS/Agrifood vs manufactured) and post-Brexit trade origin.
3. **Component 3 (C3: Bi-Objective Pareto Route Optimizer):** Mathematical optimization engine balancing freight transit cost (€) against tailpipe carbon intensity ($g\text{CO}_2\text{e/km}$) subject to EC 561/2006 driver break constraints.

---

## 3. Repository Structure

```
irishlogix/
├── pyproject.toml                     # Modern PEP 621 packaging and dependencies
├── README.md                          # Project architecture and research documentation
├── .gitignore                         # Version control exclusions
├── NCI_MSc_Data_Analytics_Weekly_Progress_Report_Week1.pdf # Official Week 1 report
├── data/
│   ├── raw/cso/                       # Raw CSO PxStat tables (TBQ01, TBQ04, TBQ05)
│   └── processed/                     # Cleaned activity matrices and benchmark outputs
├── docs/
│   └── project_pitch_and_plan.md      # Pitch script and Gantt chart project plan
├── notebooks/
│   └── 01_week1_data_ingestion_and_exploration.ipynb # Interactive analysis notebook
├── src/irishlogix/
│   ├── data/cso_loader.py             # CSO PxStat API data ingestion
│   ├── network/corridor_network.py    # NetworkX Irish freight corridor network
│   ├── simulation/baseline_dispatcher.py # FIFO baseline simulation benchmark
│   └── utils/                         # Config, emissions, and cost metrics
├── scripts/
│   ├── run_data_ingestion.py          # CLI runner for CSO data ingestion
│   ├── run_baseline_benchmark.py      # CLI runner for baseline FIFO simulation
│   └── generate_reports_pdf_docx.py   # Report generation utility
└── tests/                             # Pytest automated test suite (9 passing tests)
```

---

## 4. Week 1 Technical Accomplishments & Milestone Status

- **Environment & Repository Setup:** Initialized Git version control and modern `pyproject.toml` configuration with strict testing and execution harnesses.
- **Automated Open Data Ingestion (`cso_loader.py`):** Successfully connected to the Central Statistics Office (CSO) PxStat REST API, downloading and parsing official maritime tables:
  - `TBQ01`: 444 vessel arrival records across Dublin, Cork, Rosslare, Shannon Foynes, and Waterford.
  - `TBQ04`: 2,331 Ro-Ro freight unit traffic records.
  - `TBQ05`: 3,600 records of goods handled by port and trade region (Great Britain vs EU).
- **Irish Freight Corridor Representation (`corridor_network.py`):** Implemented an undirected weighted network graph with 11 strategic nodes and 15 bidirectional corridor edges connecting key Irish ports and inland hubs.
- **Baseline FIFO Dispatcher Simulator (`baseline_dispatcher.py`):** Built the empirical baseline model representing traditional unbuffered scheduling.
- **Empirical Baseline Benchmark Results (N=50 test consignments):**
  - **Total Distance:** 8,636.5 km
  - **Active Driving Hours:** 104.4 hours
  - **Idle Waiting Hours:** 63.5 hours (*Average 1.27 hours wasted per trip due to lack of predictive scheduling*)
  - **Total Diesel Fuel:** 2,879.3 Litres
  - **Total Carbon Footprint:** 7,601.3 kg $\text{CO}_2\text{e}$ (Average 919.0 $g\text{CO}_2\text{e/km}$)
  - **Total Transport Operational Cost:** €14,791.21 (Average €295.82 per consignment)
- **Automated Test Suite:** 9 out of 9 unit tests passing (`pytest tests -v`).

---

## 5. Quickstart & How to Run

### Installation
```bash
# Clone the repository
git clone <repo-url>
cd "Athanasio submission"

# Install dependencies
pip install -e .
```

### Ingest CSO Maritime Data
```bash
python scripts/run_data_ingestion.py
```

### Run Baseline FIFO Benchmark
```bash
python scripts/run_baseline_benchmark.py
```

### Run Automated Unit Tests
```bash
python -m pytest tests -v
```

---

## 6. Regulatory & Ethical Framework
- **Data Governance:** Exclusively utilizes open secondary datasets (CSO, EMODnet AIS, OpenStreetMap) and calibrated synthetic trade distributions. No human participants or GDPR-sensitive driver telematics are used.
- **Regulatory Grounding:** Integrates **Regulation (EC) No 561/2006** (driver rest break limits), **Directive (EU) 2022/2464 (CSRD)**, and **Directive (EU) 2023/959 (ETS2)** carbon price bands.
