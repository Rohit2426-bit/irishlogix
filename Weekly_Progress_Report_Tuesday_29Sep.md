# NATIONAL COLLEGE OF IRELAND
## MSc in Data Analytics — Research Practicum (MSCDAD_A_JAN26I)
### WEEKLY PROGRESS REPORT

**Student Name:** Rohitkumar Amritlal Jaiswal  
**Student ID:** 25119613  
**Supervisor / Lecturer:** Dr. Thanos Staikopoulos  
**Date of Submission:** Tuesday, 29 September 2026  
**Project Title:** Coupling Port Congestion and Customs Delay Prediction with Carbon-Aware Multi-Objective Route Optimisation for Post-Brexit Irish Freight Logistics  
**Reporting Period:** Week 1 (Project Scoping, Proposal Finalization & Pitch Preparation)  

---

### 1. Summary of Activities Completed This Week
- **Proposal Finalisation:** Completed and formatted the comprehensive Project Proposal document (CA2, 4,691 words) incorporating supervisory feedback from CA1. Streamlined the architecture from eight overly broad modules down to three core coupled components (Port Congestion Classifier C1, Customs Delay Regressor C2, and Carbon-Aware Pareto Route Optimizer C3).
- **Literature Review & Reference Archive:** Curated and archived all 7 foundational research papers and EU legislative instruments (`Directive (EU) 2022/2464 (CSRD)`, `Directive (EU) 2023/959 (ETS2)`, `Regulation (EC) No 561/2006`, Cheng et al. 2024, Zamani et al. 2022, etc.) into `Literature_Review_References.zip`.
- **Ethics Consideration Submission:** Completed the NCI School of Computing Declaration of Ethics Consideration Form. Confirmed the project utilizes exclusively secondary public data (CSO, EMODnet AIS, OpenStreetMap) and calibrated synthetic data, strictly avoiding human participants or GDPR-sensitive driver telematics.
- **Pitch Formulation:** Developed a structured 1–2 minute project pitch adhering to the required sequence (*Problem → Gap → Idea → Method → Contribution*) in preparation for the 1 October presentation.

---

### 2. Milestone Progress & Timeline Health
- **Active Milestone:** Milestone 1 (M1: Baseline Model Development, System Architecture & Data Pipeline Foundation).
- **Status:** On Schedule.
- **Timeline Health:** Green / On Track (15-week plan).

---

### 3. Key Decisions & Technical Architecture
- **Algorithm Selection:** Finalized Gradient Boosting (XGBoost) for tabular predictive models (C1 & C2) over Deep Learning, owing to sample efficiency on tabular maritime/customs data, native missing value handling, and transparent feature attribution via SHAP.
- **Optimization Strategy:** Selected bi-objective Pareto optimization (SciPy / NetworkX) over weighted single-objective functions to allow transport dispatchers to visualize realistic trade-offs between freight operational cost (€) and carbon intensity ($g\text{CO}_2\text{e/km}$).
- **Evaluation Baseline:** Established a formal FIFO shortest-route spreadsheet simulation baseline to empirically prove whether machine-learning-informed dynamic routing yields statistically significant improvements.

---

### 4. Current Challenges & Risk Mitigation
- **Challenge:** Granular, shipment-level customs clearance durations across Irish sea corridors are commercially confidential and not published by Irish Revenue.
- **Mitigation:** Implemented a calibrated synthetic customs delay generator parameterised using published CSO aggregate cross-border trade statistics and literature-validated delay intervals; fully documented within the approved ethics declaration.

---

### 5. Planned Activities for the Coming Week
1. Deliver the 1–2 minute oral project pitch on **1 October**.
2. Discuss refined Research Questions and SMART Objectives with Dr. Thanos Staikopoulos during the scheduled supervisory review.
3. Ingest and preprocess initial CSO Port Traffic quarterly tables and EMODnet vessel density data.
4. Construct the OpenStreetMap graph network for Ireland's primary freight corridors (Dublin, Cork, Rosslare).
5. Initialize the project Git repository with automated experiment tracking.

---
**Student Signature:** Rohitkumar Amritlal Jaiswal  
**Date:** 29 September 2026
