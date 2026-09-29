# NATIONAL COLLEGE OF IRELAND
## MSc in Data Analytics: Research Practicum (MSCDAD_A_JAN26I)
### WEEKLY PROGRESS REPORT

**Student Name:** Rohitkumar Amritlal Jaiswal  
**Student ID:** 25119613  
**Supervisor / Lecturer:** Dr. Thanos Staikopoulos  
**Date of Submission:** Tuesday, 29 September 2026  
**Project Title:** Coupling Port Congestion and Customs Delay Prediction with Carbon-Aware Multi-Objective Route Optimisation for Post-Brexit Irish Freight Logistics  
**Reporting Period:** Week 1 (Kickoff, Technical Initialization & Baseline Benchmark)  

---

### 1. Summary of Activities Completed This Week
- **Project Pitch Formulation:** Developed a structured 1-2 minute project pitch adhering to the required sequence (Problem -> Gap -> Idea -> Method -> Contribution) in preparation for the 1 October presentation.
- **Repository Setup & Package Architecture:** Initialized the formal Git repository and structured the `irishlogix` Python package following modern PEP 621 packaging with `pyproject.toml`.
- **Automated CSO Data Pipeline Ingestion (`cso_loader.py`):** Successfully connected to Ireland's Central Statistics Office (CSO) PxStat REST API, downloading, cleaning, and caching:
  - `TBQ01`: 444 quarterly ship arrival records across Dublin, Cork, Rosslare, Shannon Foynes, and Waterford (URL: https://data.cso.ie/table/TBQ01).
  - `TBQ04`: 2,331 Ro-Ro freight unit traffic records (URL: https://data.cso.ie/table/TBQ04).
  - `TBQ05`: 3,600 trade region tonnage records covering Great Britain & NI vs EU trade lanes (URL: https://data.cso.ie/table/TBQ05).
  - Built unified port congestion matrix (`data/processed/cso_port_activity_matrix.csv`).
- **Jupyter Notebook Development (`notebooks/01_week1_data_ingestion_and_exploration.ipynb`):** Built and executed a complete Jupyter notebook presenting live data downloads, longitudinal charts (2017 to 2026), trade region shifts, and baseline routing metrics.
- **Irish Freight Corridor Road Network Graph (`corridor_network.py`):** Constructed a NetworkX road graph covering 11 critical Irish nodes and 15 bidirectional corridors with road classes, tolls, and Dijkstra distance matrices.
- **Baseline FIFO Dispatcher Simulation Engine (`baseline_dispatcher.py`):** Implemented and executed the empirical baseline simulation modeling traditional unbuffered SME haulage planning across 50 benchmark consignments:
  - *Benchmark Results:* 8,636.5 km traveled; 104.4 driving hours; **63.5 idle waiting hours** (*averaging 1.27 hours wasted idling per shipment*); 2,879.3 L diesel; 7,601.3 kg CO2e; €14,791.21 total cost (avg €295.82 per trip).
- **Unit Testing Suite:** 9 out of 9 unit tests passing (`pytest tests -v`).

---

### 2. Primary Public Dataset Sources & URLs
1. **CSO Table TBQ01 (Port Arrivals):** https://data.cso.ie/table/TBQ01
2. **CSO Table TBQ02 (Tonnage by Cargo):** https://data.cso.ie/table/TBQ02
3. **CSO Table TBQ04 (Ro-Ro Units):** https://data.cso.ie/table/TBQ04
4. **CSO Table TBQ05 (Trade Regions):** https://data.cso.ie/table/TBQ05
5. **EMODnet Vessel Density:** https://emodnet.ec.europa.eu/en/human-activities
6. **OpenStreetMap Irish Corridors:** https://download.geofabrik.de/europe/ireland-and-northern-ireland.html

---

### 3. Milestone Progress & Timeline Health
- **Active Milestone:** Milestone 1 (M1: Baseline Model Development, System Architecture & Data Pipeline Foundation).
- **Status:** Advanced / Ahead of Schedule (Core baseline simulator and CSO data ingestion completed during Week 1).
- **Timeline Health:** Green / On Track (15-week plan).

---

### 4. Key Decisions & Technical Architecture
- **Algorithm Selection:** Confirmed Gradient Boosting (XGBoost) for tabular predictive models (C1 & C2) over Deep Learning, owing to sample efficiency on tabular maritime/customs data, native missing value handling, and transparent feature attribution via SHAP.
- **Optimization Strategy:** Selected bi-objective Pareto optimization (SciPy / NetworkX) over weighted single-objective functions to allow transport dispatchers to visualize realistic trade-offs between freight operational cost (€) and carbon intensity ($g\text{CO}_2\text{e/km}$).
- **Empirical Baseline:** Formulated and validated the FIFO shortest-route spreadsheet simulation baseline, establishing the concrete benchmark against which coupled ML+Pareto routing will be quantified.

---

### 5. Current Challenges & Risk Mitigation
- **Challenge:** Granular shipment-level customs clearance durations across Irish sea corridors are commercially confidential and not published by Irish Revenue.
- **Mitigation:** Implemented a calibrated synthetic customs delay generator parameterised using published CSO aggregate cross-border trade statistics and literature-validated delay intervals; fully documented within the approved ethics declaration.

---

### 6. Planned Activities for the Coming Week
1. Deliver the 1-2 minute oral project pitch on **1 October**.
2. Discuss refined Research Questions, SMART Objectives, and baseline simulation findings with Dr. Thanos Staikopoulos during the scheduled supervisory review.
3. Ingest EMODnet AIS vessel density data and engineer maritime congestion lag features.
4. Finalize the calibrated synthetic customs clearance dataset generator (C2).

---
**Student Signature:** Rohitkumar Amritlal Jaiswal  
**Date:** 29 September 2026
