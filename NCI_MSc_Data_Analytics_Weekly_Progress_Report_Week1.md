# NATIONAL COLLEGE OF IRELAND
## SCHOOL OF COMPUTING
### MSc in Data Analytics: Research Practicum (MSCDAD_A_JAN26I)
**WEEKLY PROGRESS REPORT: WEEK 1**

---

### Student and Project Details

| Field | Detail |
| :--- | :--- |
| **Student Name:** | Rohitkumar Amritlal Jaiswal |
| **Student ID:** | x25119613 |
| **Supervisor:** | Dr. Thanos Staikopoulos |
| **Project Title:** | Coupling Port Congestion and Customs Delay Prediction with Carbon-Aware Multi-Objective Route Optimisation for Post-Brexit Irish Freight Logistics |
| **Reporting Period:** | Week 1 (Technical Kickoff & Baseline Simulation) |
| **Submission Date:** | Tuesday, 29 September 2026 |

---

### 1. Summary of Activities Completed This Week

- **Project Pitch Preparation:** Prepared a 1-2 minute spoken pitch following the required format: Problem -> Gap -> Idea -> Method -> Contribution, ready for presentation on 1 October.
- **Code Repository Setup:** Initialized the project Git repository and created a clean Python package structure named `irishlogix` using `pyproject.toml`.
- **Public Data Ingestion (`cso_loader.py`):** Connected directly to the Central Statistics Office (CSO) PxStat API and downloaded quarterly maritime datasets from 2017 to 2026:
  - `TBQ01`: Vessel arrivals by port (444 records). URL: https://data.cso.ie/table/TBQ01
  - `TBQ04`: Ro-Ro freight trailer units (2,331 records). URL: https://data.cso.ie/table/TBQ04
  - `TBQ05`: Port tonnage split by trade region (3,600 records). URL: https://data.cso.ie/table/TBQ05
  - Built a clean port activity matrix saved in `data/processed/cso_port_activity_matrix.csv`.
- **Jupyter Notebook (`notebooks/01_week1_data_ingestion_and_exploration.ipynb`):** Created and ran a notebook that downloads the data, plots port arrival trends, shows post-Brexit trade shifts, and runs the baseline route simulation.
- **Irish Road Corridor Network (`corridor_network.py`):** Built a road network graph in NetworkX with 11 nodes (Dublin, Cork, Rosslare, Athlone, Limerick, Galway, Waterford, Dundalk) and 15 road corridors with travel distances, speed limits, and tolls.
- **Baseline Dispatch Simulation (`baseline_dispatcher.py`):** Built an empirical baseline simulation representing how small Irish hauliers plan routes using simple spreadsheets without delay forecasting. Ran a test of 50 freight trips and found:
  - Total distance: 8,636.5 km
  - Active driving time: 104.4 hours
  - **Idle waiting time: 63.5 hours** (trucks wasted an average of **1.27 hours idling per trip** at port gates and customs)
  - Total diesel used: 2,879.3 Litres
  - Total carbon emissions: 7,601.3 kg CO2e
  - Total transport cost: €14,791.21 (average €295.82 per trip)
- **Unit Testing:** Created 9 unit tests across the data loader, network graph, and simulator. All 9 tests passed.

---

### 2. Primary Public Dataset Sources & URLs

| Dataset Name | Source and Direct URL | Role in Project |
| :--- | :--- | :--- |
| **CSO Table TBQ01** | https://data.cso.ie/table/TBQ01 | Ship arrivals for Dublin, Cork, and Rosslare ports |
| **CSO Table TBQ02** | https://data.cso.ie/table/TBQ02 | Cargo tonnage categories (Ro-Ro and Lo-Lo) |
| **CSO Table TBQ04** | https://data.cso.ie/table/TBQ04 | Freight trailer counts across Irish ports |
| **CSO Table TBQ05** | https://data.cso.ie/table/TBQ05 | Post-Brexit trade volumes: Great Britain vs. EU |
| **EMODnet Vessel Density** | https://emodnet.ec.europa.eu/en/human-activities | AIS marine traffic density maps |
| **OpenStreetMap Ireland** | https://download.geofabrik.de/europe/ireland-and-northern-ireland.html | Road distances and speeds for Irish corridors |

---

### 3. Reflection and Key Findings

- **The Problem is Real:** The baseline simulation shows that without delay prediction, trucks waste an average of 1.27 hours per shipment waiting at gates and customs. This proves that coupling delay prediction with route optimization can save real fuel, money, and emissions.
- **Data is Verified:** The CSO PxStat API provides clean, continuous historical data from 2017 to 2026, ensuring we have solid numbers to train the machine learning models.
- **Benchmark is Set:** Having this baseline simulator running in Week 1 gives us a clear benchmark to compare our future machine learning models against.

---

### 4. Planned Activities for Next Week

1. Deliver the 1-2 minute oral pitch on 1 October.
2. Review the Week 1 baseline results and refined project plan with Dr. Thanos Staikopoulos during our meeting.
3. Ingest EMODnet AIS vessel density data for Irish waters.
4. Start feature engineering for the Component 1 Port Congestion Classifier.

---

### 5. Milestone Tracking

| Milestone | Target | Status | Summary |
| :---: | :---: | :---: | :--- |
| **M1** | Week 3 | **Ahead of Schedule** | Baseline simulator working, CSO data ingested, road network built |
| **M2** | Week 9 | Planned | Train XGBoost delay models and connect to Pareto optimizer |
| **M3** | Week 13 | Planned | Complete comparison against baseline and build Streamlit dashboard |
| **M4** | Week 15 | Planned | Final dissertation, code repository, and viva presentation |

---

### 6. Sign-Off

**Student Signature:** Rohitkumar Amritlal Jaiswal &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Date:** 29 September 2026  
**Supervisor Signature:** ___________________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Date:** ___________________________  
