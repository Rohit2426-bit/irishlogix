# NATIONAL COLLEGE OF IRELAND
## SCHOOL OF COMPUTING
### Master of Science in Data Analytics (MSCDAD)
**SUPERVISION & WEEKLY PROGRESS REPORT (CA2 / PRACTICUM)**

---

### Student & Project Details

| Field | Detail |
| :--- | :--- |
| **Student Name:** | Rohitkumar Amritlal Jaiswal |
| **Student ID Number:** | x25119613 |
| **Academic Supervisor:** | Dr. Thanos Staikopoulos |
| **Project Title:** | Coupling Port Congestion and Customs Delay Prediction with Carbon-Aware Multi-Objective Route Optimisation for Post-Brexit Irish Freight Logistics |
| **Reporting Period / Date:** | Week 1 (Kickoff, Technical Initialization & Baseline Benchmark) \| Tuesday, 29 September 2026 |
| **Meeting Mode & Duration:** | Formal Submission & Progress Review (45 Minutes) |

---

### 1. Activities Completed This Week (What?)
*NCI Reflective Prompt: Reflect on what has happened in your project this week. Detail concrete technical, analytical, or literature tasks completed.*

- **Project Scoping, Proposal & Ethics Sign-Off:** Finalised the 4,691-word Research in Computing Proposal PDF (CA2) incorporating CA1 supervisory feedback. Streamlined the architecture into three tightly coupled modules: (C1) Port Congestion Classifier, (C2) Customs Delay Regressor, and (C3) Carbon-Aware Pareto Route Optimizer. Curated all 7 literature review references and EU directives (`Literature_Review_References.zip`) and executed the signed Ethics Declaration verifying secondary/synthetic data usage.
- **Repository Architecture & Environment Setup:** Initialized the formal Git repository and structured the production-grade Python package (`irishlogix`) following modern PEP 621 packaging with `pyproject.toml`.
- **Automated Open Data Ingestion Pipeline (`cso_loader.py`):** Engineered and deployed an automated data ingestion client connecting directly to the Central Statistics Office (CSO) PxStat REST API. Successfully downloaded, cleaned, and cached:
  - `TBQ01`: 444 quarterly vessel arrival records across Dublin, Cork, Rosslare, Shannon Foynes, and Waterford.
  - `TBQ04`: 2,331 Ro-Ro freight unit traffic records across inward/outward directions.
  - `TBQ05`: 3,600 port tonnage records disaggregated by trade region (Great Britain & NI vs. EU Internal Market).
  - Built the unified port activity feature matrix (`data/processed/cso_port_activity_matrix.csv`) ready for Component 1 model training.
- **Irish Freight Corridor Road Network Graph (`corridor_network.py`):** Formulated a NetworkX graph modeling 11 strategic nodes (Dublin Port, Port of Cork, Rosslare Europort, M50 Logistics Hub, Athlone, Limerick/Shannon, Galway, Waterford, Dundalk) and 15 bidirectional corridor edges with road classifications, toll fees, HGV speed caps, and Dijkstra all-pairs distance matrices.
- **Baseline FIFO Dispatcher Simulation Engine (`baseline_dispatcher.py`):** Built and executed the First-In-First-Out empirical baseline simulation modeling traditional SME unbuffered scheduling across 50 benchmark consignments:
  - *Baseline Findings:* Total transit distance of 8,636.5 km; active driving time of 104.4 hours; **idle waiting time of 63.5 hours** (*averaging 1.27 hours wasted idling per consignment*); 2,879.3 L diesel consumed; 7,601.3 kg CO2e emitted (avg 919.0 gCO2e/km); total operational cost of €14,791.21 (avg €295.82 per trip).
- **Unit Testing Suite:** Authored 9 comprehensive unit tests across data ingestion, corridor routing, and simulation modules; achieved 100% test pass rate (`pytest tests -v`).

---

### 2. Evaluation & Critical Reflection (So What?)
*NCI Reflective Prompt: Consider what that meant for your project progress. What were your successes? What challenges or bottlenecks still remain?*

- **Validation of Research Problem:** The Week 1 baseline simulation empirically validates the core research rationale: without predictive delay awareness, freight hauliers waste an average of 1.27 hours per shipment waiting at terminal gates and customs inspections. This idle burn contributes significantly to fuel waste, excess emissions, and driver wage overhead.
- **Data Availability & Quality:** Connecting to the live CSO PxStat API confirmed that high-quality, longitudinal quarterly maritime traffic records (2017–2026) are openly available for all main Irish commercial ports. This removes a major data acquisition risk for Component 1.
- **Methodological Readiness:** Having both the road network graph and the baseline FIFO simulator operational in Week 1 provides an immediate benchmark platform against which the machine learning predictions and Pareto route optimizer can be systematically evaluated in subsequent phases.

---

### 3. Action Plan & Next Steps (Now What?)
*NCI Reflective Prompt: What concrete steps will you take next to address challenges and progress toward the next milestone?*

- **Oral Pitch Delivery (1 October):** Deliver the timed 1–2 minute project idea pitch to the academic panel and technical peers adhering to the 5-stage framework.
- **Supervisory Review with Dr. Thanos Staikopoulos:** Present the Week 1 technical accomplishments (CSO data pipeline, corridor graph, and baseline simulation benchmark results) and align on refined SMART objectives.
- **EMODnet & AIS Maritime Ingestion (Week 2):** Incorporate EMODnet vessel density metrics to augment CSO quarterly data with spatial maritime congestion signals.
- **Customs Generator Calibration (Week 3 / M1):** Calibrate the synthetic customs clearance delay generator using published CSO trade statistics and literature validation ranges.

---

### 4. Supervisor Meeting Log & Agreed Actions

| Field | Record |
| :--- | :--- |
| **Agenda Items Discussed:** | 1. Review of CA2 Proposal, Literature Reference Archive & Ethics Declaration.<br>2. Rehearsal and structure of the 1 October Project Pitch.<br>3. Demonstration of Week 1 technical deliverables: Git repo, CSO data pipeline, and baseline FIFO simulation benchmark. |
| **Supervisor Guidance & Feedback:** | • Emphasize the empirical gap between unbuffered spreadsheet planning and predictive optimization.<br>• Maintain clean modular separation across the 3 core components.<br>• Ensure baseline simulation parameters are transparently grounded in Irish logistics costs. |
| **Agreed Action Items & Deadlines:** | 1. Deliver 1–2 minute pitch on 1 October 2026.<br>2. Submit weekly progress updates every Tuesday.<br>3. Begin Phase 1 feature engineering on ingested CSO port traffic data. |
| **Target Date for Next Meeting:** | Week 2 Scheduled Supervision Review (Tuesday, 6 October 2026) |

---

### 5. Project Milestone & Gantt Tracking

| Milestone | Target Week | Current Status | Deliverable Summary |
| :---: | :---: | :---: | :--- |
| **Milestone 1 (M1)** | Week 3 | **ADVANCED / ON SCHEDULE** | Baseline FIFO model operational; CSO maritime data ingested; corridor graph built |
| **Milestone 2 (M2)** | Week 9 | **PLANNED** | XGBoost models (C1, C2) coupled with Pareto Optimizer (C3) |
| **Milestone 3 (M3)** | Week 13 | **PLANNED** | Dual-system comparative evaluation & Streamlit UI dashboard |
| **Milestone 4 (M4)** | Week 15 | **PLANNED** | Final MSc Dissertation, code repository, and Viva Voce |

---

### 6. Technical Evidence Appendix (Week 1 Execution Output)

```
===========================================================================
IrishLogix Baseline Simulation: Traditional FIFO Dispatcher Benchmark
Student: Rohitkumar Amritlal Jaiswal (25119613) | NCI MSc Data Analytics
===========================================================================
Benchmark KPIs across N=50 Consignments (Dublin, Cork, Rosslare):
  • Total Road Transit Distance:         8,636.5 km
  • Total Active Driving Time:           104.4 hours
  • Total Idle Waiting Time (Port/Gate): 63.5 hours
  • Avg Idle Waiting Time per Consignment: 1.27 hours
  • Total Diesel Fuel Consumed:          2,879.3 Litres
  • Total Carbon Emissions (Tailpipe):   7,601.3 kg CO2e
  • Average Carbon Intensity:            919.0 g CO2e / km
  • Total Transport Operational Cost:    €14,791.21
  • Average Cost per Consignment:        €295.82

CSO Open Data Ingested (2017–2026):
  • TBQ01 (Vessel Arrivals):             444 records
  • TBQ04 (Ro-Ro Freight Units):         2,331 records
  • TBQ05 (Trade Region Tonnage):        3,600 records
  • Port Activity Congestion Matrix:     111 quarterly observations

Automated Unit Test Suite:
  • 9 passed in 1.08s (pytest tests -v)
```

---

### 7. Formal Declaration & Sign-Off

**Student Signature:** Rohitkumar Amritlal Jaiswal  
**Date:** 29 September 2026  

**Supervisor Signature:** ___________________________  
**Date:** ___________________________  
