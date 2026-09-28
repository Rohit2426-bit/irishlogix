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
| **Reporting Period / Date:** | Week 1 (Kickoff & Pitch Preparation) \| Tuesday, 29 September 2026 |
| **Meeting Mode & Duration:** | Formal Submission & Progress Review (45 Minutes) |

---

### 1. Activities Completed This Week (What?)
*NCI Reflective Prompt: Reflect on what has happened in your project this week. Detail concrete technical, analytical, or literature tasks completed.*

- **Proposal Finalisation (CA2):** Refined and compiled the 4,691-word Research in Computing Proposal PDF incorporating CA1 supervisory feedback. Streamlined the project architecture from eight overly broad modules down to three tightly coupled core components: (C1) Port Congestion Classifier, (C2) Customs Delay Regressor, and (C3) Carbon-Aware Pareto Route Optimizer.
- **Literature Review Reference Archiving:** Curated, validated, and archived all 7 foundational peer-reviewed papers and EU legislative instruments (`Directive (EU) 2022/2464 (CSRD)`, `Directive (EU) 2023/959 (ETS2)`, `Regulation (EC) No 561/2006`, Cheng et al. 2024, Zamani et al. 2022, etc.) into `Literature_Review_References.zip`.
- **Ethics Consideration Submission:** Completed and signed the official NCI School of Computing Declaration of Ethics Consideration Form, verifying no human participants and documenting all open public secondary data sources (CSO, EMODnet AIS, OpenStreetMap) and synthetic data generators.
- **Project Pitch Script Formulation:** Structured a strict 5-stage verbal pitch (`Problem → Gap → Idea → Method → Contribution`) and anticipated technical defense responses for the scheduled 1 October panel.

---

### 2. Evaluation & Critical Reflection (So What?)
*NCI Reflective Prompt: Consider what that meant for your project progress. What were your successes? What challenges or bottlenecks still remain?*

- **Scope Streamlining & Feasibility:** The reflection on CA1 feedback proved that the initial 8-module scope was too expansive for a single-semester MSc Practicum. Pruning driver tachograph and telematics modules successfully eliminated GDPR and privacy risks while establishing a realistic, rigorous technical scope.
- **Technical Risk Assessment & Synthetic Data:** Identified that shipment-level customs clearance durations across Irish sea corridors are commercially confidential and strictly restricted by Irish Revenue. Rather than relying on guesswork, creating a calibrated synthetic dataset based on aggregate CSO trade statistics provides a reproducible, ethically compliant approach.
- **Methodological Alignment:** Confirmed that Gradient Boosting (XGBoost) is optimal for tabular port and customs delay data, while bi-objective Pareto optimization (minimizing operational cost vs. carbon intensity) accurately captures the economic and environmental trade-offs required under CSRD and ETS2.

---

### 3. Action Plan & Next Steps (Now What?)
*NCI Reflective Prompt: What concrete steps will you take next to address challenges and progress toward the next milestone?*

- **Oral Pitch Delivery (1 October):** Deliver the 1–2 minute project idea pitch to the panel and technical peers, adhering to the timed 100-second delivery structure.
- **Supervisor Consultation:** Discuss and align on refined Primary Research Questions, Sub-Questions, and SMART Objectives with Dr. Thanos Staikopoulos during the supervisory review.
- **Data Pipeline Ingestion:** Begin Phase 1 data ingestion: download CSO Port Traffic tables, extract EMODnet vessel density data, and construct the Irish corridor road network graph via OpenStreetMap.
- **Baseline Simulation Model:** Develop the FIFO shortest-route spreadsheet simulation baseline planner against which the machine learning and route optimization model will be benchmarked.

---

### 4. Supervisor Meeting Log & Agreed Actions

| Field | Record |
| :--- | :--- |
| **Agenda Items Discussed:** | 1. CA2 Proposal Submission & Literature Reference Package.<br>2. Presentation strategy for the 1 October Project Pitch.<br>3. Updated 15-week Gantt Chart milestones and deliverable timeline. |
| **Supervisor Guidance & Feedback:** | • Ensure the pitch clearly articulates the gap between prediction and optimization.<br>• Maintain strict focus on the 3 core components (C1, C2, C3).<br>• Prepare for Q&A regarding synthetic customs data calibration. |
| **Agreed Action Items & Deadlines:** | 1. Deliver 1–2 minute pitch on 1 October 2026.<br>2. Refine Research Title, RQ, and SMART Objectives for next meeting.<br>3. Submit weekly progress updates every Tuesday. |
| **Target Date for Next Meeting:** | Week 2 Scheduled Supervision Catch-up (Tuesday, 6 October 2026) |

---

### 5. Project Milestone & Gantt Tracking

| Milestone | Target Week | Current Status | Deliverable Summary |
| :---: | :---: | :---: | :--- |
| **Milestone 1 (M1)** | Week 3 | **IN PROGRESS** | Baseline FIFO model + CSO/EMODnet data pipeline complete |
| **Milestone 2 (M2)** | Week 9 | **PLANNED** | XGBoost models (C1, C2) coupled with Pareto Optimizer (C3) |
| **Milestone 3 (M3)** | Week 13 | **PLANNED** | Dual-system comparative evaluation & Streamlit UI dashboard |
| **Milestone 4 (M4)** | Week 15 | **PLANNED** | Final MSc Dissertation, code repository, and Viva Voce |

---

### 6. Formal Declaration & Sign-Off

**Student Signature:** Rohitkumar Amritlal Jaiswal  
**Date:** 29 September 2026  

**Supervisor Signature:** ___________________________  
**Date:** ___________________________  
