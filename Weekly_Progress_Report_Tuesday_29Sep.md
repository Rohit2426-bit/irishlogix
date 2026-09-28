# NATIONAL COLLEGE OF IRELAND
## MSc in Data Analytics — Research Practicum (MSCDAD_A_JAN26I)
### WEEKLY PROGRESS REPORT

**Student Name:** Rohitkumar Amritlal Jaiswal  
**Student ID:** 25119613  
**Supervisor / Lecturer:** Dr. Thanos Staikopoulos  
**Date of Submission:** Tuesday, 29 September 2026  
**Project Title:** Coupling Port Congestion and Customs Delay Prediction with Carbon-Aware Multi-Objective Route Optimisation for Post-Brexit Irish Freight Logistics  
**Reporting Period:** Week 1 (Kickoff, Technical Initialization & Baseline Benchmark)  

---

### 1. Summary of Activities Completed This Week
- **Proposal & Ethics Finalisation:** Refined and compiled the CA2 Research in Computing Proposal PDF (4,691 words) incorporating CA1 supervisory feedback. Streamlined the architecture from eight modules down to three core coupled components (Port Congestion Classifier C1, Customs Delay Regressor C2, Carbon-Aware Pareto Optimizer C3). Curated all 7 foundational research papers into `Literature_Review_References.zip` and signed the Ethics Consideration Form verifying open/synthetic data use.
- **Project Pitch Formulation:** Developed a structured 1–2 minute project pitch adhering to the required sequence (*Problem → Gap → Idea → Method → Contribution*) in preparation for the 1 October presentation.
- **Repository Setup & Package Architecture:** Initialized the formal Git repository and structured the `irishlogix` Python package following modern PEP 621 packaging with `pyproject.toml`.
- **Automated CSO Data Pipeline Ingestion (`cso_loader.py`):** Successfully connected to Ireland's Central Statistics Office (CSO) PxStat REST API, downloading, cleaning, and caching:
  - `TBQ01`: 444 quarterly ship arrival records across Dublin, Cork, Rosslare, Shannon Foynes, and Waterford.
  - `TBQ04`: 2,331 Ro-Ro freight unit traffic records.
  - `TBQ05`: 3,600 trade region tonnage records (Great Britain & NI vs. EU).
  - Built unified port congestion matrix (`data/processed/cso_port_activity_matrix.csv`).
- **Irish Freight Corridor Road Network Graph (`corridor_network.py`):** Constructed a NetworkX road graph covering 11 critical Irish nodes and 15 bidirectional corridors with road classes, tolls, and Dijkstra distance matrices.
- **Baseline FIFO Dispatcher Simulation Engine (`baseline_dispatcher.py`):** Implemented and executed the empirical baseline simulation modeling traditional unbuffered SME haulage planning across 50 benchmark consignments:
  - *Benchmark Results:* 8,636.5 km traveled; 104.4 driving hours; **63.5 idle waiting hours** (*averaging 1.27 hours wasted idling per shipment*); 2,879.3 L diesel; 7,601.3 kg CO2e; €14,791.21 total cost (avg €295.82 per trip).
- **Unit Testing Suite:** 9 out of 9 unit tests passing (`pytest tests -v`).

---

### 2. Milestone Progress & Timeline Health
- **Active Milestone:** Milestone 1 (M1: Baseline Model Development, System Architecture & Data Pipeline Foundation).
- **Status:** Advanced / Ahead of Schedule (Core baseline simulator and CSO data ingestion completed during Week 1).
- **Timeline Health:** Green / On Track (15-week plan).

---

### 3. Key Decisions & Technical Architecture
- **Algorithm Selection:** Confirmed Gradient Boosting (XGBoost) for tabular predictive models (C1 & C2) over Deep Learning, owing to sample efficiency on tabular maritime/customs data, native missing value handling, and transparent feature attribution via SHAP.
- **Optimization Strategy:** Selected bi-objective Pareto optimization (SciPy / NetworkX) over weighted single-objective functions to allow transport dispatchers to visualize realistic trade-offs between freight operational cost (€) and carbon intensity ($g\text{CO}_2\text{e/km}$).
- **Empirical Baseline:** Formulated and validated the FIFO shortest-route spreadsheet simulation baseline, establishing the concrete benchmark against which coupled ML+Pareto routing will be quantified.

---

### 4. Current Challenges & Risk Mitigation
- **Challenge:** Granular shipment-level customs clearance durations across Irish sea corridors are commercially confidential and not published by Irish Revenue.
- **Mitigation:** Implemented a calibrated synthetic customs delay generator parameterised using published CSO aggregate cross-border trade statistics and literature-validated delay intervals; fully documented within the approved ethics declaration.

---

### 5. Planned Activities for the Coming Week
1. Deliver the 1–2 minute oral project pitch on **1 October**.
2. Discuss refined Research Questions, SMART Objectives, and baseline simulation findings with Dr. Thanos Staikopoulos during the scheduled supervisory review.
3. Ingest EMODnet AIS vessel density data and engineer maritime congestion lag features.
4. Finalize the calibrated synthetic customs clearance dataset generator (C2).

---
**Student Signature:** Rohitkumar Amritlal Jaiswal  
**Date:** 29 September 2026
