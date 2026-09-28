"""
Report Generation Script: Compiles Markdown Weekly Reports into Executive PDF and DOCX.
Uses ReportLab and python-docx with professional NCI styling.
"""

import os
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def create_docx_report(target_path: Path):
    doc = Document()

    # Set margins
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Header title
    title_p = doc.add_paragraph()
    title_run = title_p.add_run("NATIONAL COLLEGE OF IRELAND\nSCHOOL OF COMPUTING")
    title_run.bold = True
    title_run.font.size = Pt(14)
    title_run.font.color.rgb = RGBColor(16, 44, 87)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run("Master of Science in Data Analytics (MSCDAD)\nRESEARCH PRACTICUM (MSCDAD_A_JAN26I) — WEEKLY PROGRESS REPORT")
    sub_run.bold = True
    sub_run.font.size = Pt(11)
    sub_run.font.color.rgb = RGBColor(50, 50, 50)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Student Details Table
    table = doc.add_table(rows=6, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    details = [
        ("Student Name:", "Rohitkumar Amritlal Jaiswal"),
        ("Student ID Number:", "x25119613"),
        ("Academic Supervisor:", "Dr. Thanos Staikopoulos"),
        ("Project Title:", "Coupling Port Congestion and Customs Delay Prediction with Carbon-Aware Multi-Objective Route Optimisation for Post-Brexit Irish Freight Logistics"),
        ("Reporting Period / Date:", "Week 1 (Kickoff, Technical Initialization & Baseline Benchmark) | Tuesday, 29 September 2026"),
        ("Meeting Mode & Duration:", "Formal Submission & Progress Review (45 Minutes)")
    ]

    for i, (label, val) in enumerate(details):
        row = table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.7)

        p0 = c0.paragraphs[0]
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.size = Pt(9.5)
        set_cell_background(c0, "F0F4F8")

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(val)
        r1.font.size = Pt(9.5)
        set_cell_background(c1, "FFFFFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    def add_section_heading(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)
        r = h.add_run(text)
        r.bold = True
        r.font.size = Pt(11.5)
        r.font.color.rgb = RGBColor(16, 44, 87)

    # Section 1
    add_section_heading("1. Activities Completed This Week (What?)")
    bullets1 = [
        ("Project Scoping, Proposal & Ethics Sign-Off: ", "Finalised the 4,691-word Research in Computing Proposal PDF (CA2) incorporating CA1 supervisory feedback. Streamlined the architecture into three tightly coupled modules: (C1) Port Congestion Classifier, (C2) Customs Delay Regressor, and (C3) Carbon-Aware Pareto Route Optimizer. Curated all 7 literature review references and EU directives (Literature_Review_References.zip) and executed the signed Ethics Declaration verifying secondary/synthetic data usage."),
        ("Repository Architecture & Environment Setup: ", "Initialized the formal Git repository and structured the production-grade Python package (irishlogix) following modern PEP 621 packaging with pyproject.toml."),
        ("Automated Open Data Ingestion Pipeline (cso_loader.py): ", "Engineered and deployed an automated data ingestion client connecting directly to the Central Statistics Office (CSO) PxStat REST API. Successfully downloaded, cleaned, and cached: TBQ01 (444 vessel arrival records), TBQ04 (2,331 Ro-Ro freight unit traffic records), and TBQ05 (3,600 port tonnage records disaggregated by trade region - Great Britain vs. EU). Constructed the unified port activity matrix ready for C1 training."),
        ("Irish Freight Corridor Road Network Graph (corridor_network.py): ", "Formulated a NetworkX graph modeling 11 strategic nodes (Dublin Port, Port of Cork, Rosslare Europort, M50 Logistics Hub, Athlone, Limerick/Shannon, Galway, Waterford, Dundalk) and 15 bidirectional corridor edges with road classifications, toll fees, HGV speed caps, and Dijkstra all-pairs distance matrices."),
        ("Baseline FIFO Dispatcher Simulation Engine (baseline_dispatcher.py): ", "Built and executed the First-In-First-Out empirical baseline simulation modeling traditional SME unbuffered scheduling across 50 benchmark consignments: 8,636.5 km transit distance; 104.4 driving hours; 63.5 idle waiting hours (averaging 1.27 hours wasted idling per consignment); 2,879.3 L diesel consumed; 7,601.3 kg CO2e emitted; total operational cost of €14,791.21 (avg €295.82 per trip)."),
        ("Unit Testing Suite: ", "Authored 9 comprehensive unit tests across data ingestion, corridor routing, and simulation modules; achieved 100% test pass rate (pytest tests -v).")
    ]
    for bold_prefix, text in bullets1:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        r_b = p.add_run(bold_prefix)
        r_b.bold = True
        r_b.font.size = Pt(9.5)
        r_t = p.add_run(text)
        r_t.font.size = Pt(9.5)

    # Section 2
    add_section_heading("2. Evaluation & Critical Reflection (So What?)")
    bullets2 = [
        ("Validation of Research Problem: ", "The Week 1 baseline simulation empirically validates the core research rationale: without predictive delay awareness, freight hauliers waste an average of 1.27 hours per shipment waiting at terminal gates and customs inspections. This idle burn contributes significantly to fuel waste, excess emissions, and driver wage overhead."),
        ("Data Availability & Quality: ", "Connecting to the live CSO PxStat API confirmed that high-quality, longitudinal quarterly maritime traffic records (2017–2026) are openly available for all main Irish commercial ports. This removes a major data acquisition risk for Component 1."),
        ("Methodological Readiness: ", "Having both the road network graph and the baseline FIFO simulator operational in Week 1 provides an immediate benchmark platform against which the machine learning predictions and Pareto route optimizer can be systematically evaluated in subsequent phases.")
    ]
    for bold_prefix, text in bullets2:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        r_b = p.add_run(bold_prefix)
        r_b.bold = True
        r_b.font.size = Pt(9.5)
        r_t = p.add_run(text)
        r_t.font.size = Pt(9.5)

    # Section 3
    add_section_heading("3. Action Plan & Next Steps (Now What?)")
    bullets3 = [
        ("Oral Pitch Delivery (1 October): ", "Deliver the timed 1–2 minute project idea pitch to the academic panel and technical peers adhering to the 5-stage framework."),
        ("Supervisory Review with Dr. Thanos Staikopoulos: ", "Present the Week 1 technical accomplishments (CSO data pipeline, corridor graph, and baseline simulation benchmark results) and align on refined SMART objectives."),
        ("EMODnet & AIS Maritime Ingestion (Week 2): ", "Incorporate EMODnet vessel density metrics to augment CSO quarterly data with spatial maritime congestion signals."),
        ("Customs Generator Calibration (Week 3 / M1): ", "Calibrate the synthetic customs clearance delay generator using published CSO trade statistics and literature validation ranges.")
    ]
    for bold_prefix, text in bullets3:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        r_b = p.add_run(bold_prefix)
        r_b.bold = True
        r_b.font.size = Pt(9.5)
        r_t = p.add_run(text)
        r_t.font.size = Pt(9.5)

    # Section 4 - Supervisor Log Table
    add_section_heading("4. Supervisor Meeting Log & Agreed Actions")
    log_table = doc.add_table(rows=4, cols=2)
    log_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    log_details = [
        ("Agenda Items Discussed:", "1. Review of CA2 Proposal, Literature Reference Archive & Ethics Declaration.\n2. Rehearsal and structure of the 1 October Project Pitch.\n3. Demonstration of Week 1 technical deliverables: Git repo, CSO data pipeline, and baseline FIFO simulation benchmark."),
        ("Supervisor Guidance & Feedback:", "• Emphasize the empirical gap between unbuffered spreadsheet planning and predictive optimization.\n• Maintain clean modular separation across the 3 core components.\n• Ensure baseline simulation parameters are transparently grounded in Irish logistics costs."),
        ("Agreed Action Items & Deadlines:", "1. Deliver 1–2 minute pitch on 1 October 2026.\n2. Submit weekly progress updates every Tuesday.\n3. Begin Phase 1 feature engineering on ingested CSO port traffic data."),
        ("Target Date for Next Meeting:", "Week 2 Scheduled Supervision Review (Tuesday, 6 October 2026)")
    ]
    for i, (label, val) in enumerate(log_details):
        row = log_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.7)

        p0 = c0.paragraphs[0]
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.size = Pt(9.0)
        set_cell_background(c0, "F0F4F8")

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(val)
        r1.font.size = Pt(9.0)
        set_cell_background(c1, "FFFFFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Section 5 - Milestones Table
    add_section_heading("5. Project Milestone & Gantt Tracking")
    m_table = doc.add_table(rows=5, cols=4)
    m_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Milestone", "Target Week", "Current Status", "Deliverable Summary"]
    hdr_row = m_table.rows[0]
    for j, h_text in enumerate(headers):
        cell = hdr_row.cells[j]
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(9.0)
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "102C57")

    m_data = [
        ("Milestone 1 (M1)", "Week 3", "ADVANCED / ON SCHEDULE", "Baseline FIFO model operational; CSO maritime data ingested; corridor graph built"),
        ("Milestone 2 (M2)", "Week 9", "PLANNED", "XGBoost models (C1, C2) coupled with Pareto Optimizer (C3)"),
        ("Milestone 3 (M3)", "Week 13", "PLANNED", "Dual-system comparative evaluation & Streamlit UI dashboard"),
        ("Milestone 4 (M4)", "Week 15", "PLANNED", "Final MSc Dissertation, code repository, and Viva Voce")
    ]
    for i, row_data in enumerate(m_data):
        row = m_table.rows[i + 1]
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if j == 2 and "ADVANCED" in val:
                r.bold = True
                r.font.color.rgb = RGBColor(0, 128, 0)
            set_cell_background(cell, "F9FAFC" if i % 2 == 1 else "FFFFFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Section 6 - Signatures
    add_section_heading("6. Formal Declaration & Sign-Off")
    sig_p = doc.add_paragraph()
    sig_p.add_run("Student Signature: Rohitkumar Amritlal Jaiswal                      Date: 29 September 2026\n\nSupervisor Signature: ___________________________                   Date: ___________________________")
    sig_p.runs[0].font.size = Pt(9.5)

    doc.save(str(target_path))
    print(f"[SUCCESS] Saved DOCX report to {target_path}")


def create_pdf_report(target_path: Path):
    doc = SimpleDocTemplate(
        str(target_path),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=normal,
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#102C57"),
        alignment=1,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=normal,
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#333333"),
        alignment=1,
        spaceAfter=10
    )
    heading_style = ParagraphStyle(
        "Heading2Custom",
        parent=normal,
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor("#102C57"),
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=normal,
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#222222"),
        spaceAfter=3
    )
    bold_prefix_style = ParagraphStyle(
        "BoldPrefixCustom",
        parent=body_style,
        fontName="Helvetica-Bold"
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=normal,
        fontName="Helvetica",
        fontSize=8,
        leading=10.5
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=normal,
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#102C57")
    )

    story = []

    # Title block
    story.append(Paragraph("NATIONAL COLLEGE OF IRELAND — SCHOOL OF COMPUTING", title_style))
    story.append(Paragraph("Master of Science in Data Analytics (MSCDAD) | Research Practicum<br/><b>WEEKLY PROGRESS REPORT — WEEK 1</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#102C57"), spaceAfter=8))

    # Details table
    details_data = [
        [Paragraph("Student Name:", table_cell_bold), Paragraph("Rohitkumar Amritlal Jaiswal (ID: x25119613)", table_cell_style)],
        [Paragraph("Supervisor / Lecturer:", table_cell_bold), Paragraph("Dr. Thanos Staikopoulos", table_cell_style)],
        [Paragraph("Project Title:", table_cell_bold), Paragraph("Coupling Port Congestion & Customs Delay Prediction with Carbon-Aware Multi-Objective Route Optimisation", table_cell_style)],
        [Paragraph("Reporting Period / Date:", table_cell_bold), Paragraph("Week 1 (Kickoff, Technical Initialization & Baseline Benchmark) | Tuesday, 29 September 2026", table_cell_style)],
    ]
    t_details = Table(details_data, colWidths=[130, 400])
    t_details.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F0F4F8")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D7DE")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_details)
    story.append(Spacer(1, 6))

    # Section 1
    story.append(Paragraph("1. Activities Completed This Week (What?)", heading_style))
    story.append(Paragraph("• <b>Project Proposal & Ethics Sign-Off:</b> Finalised the 4,691-word Research in Computing Proposal PDF (CA2) streamlining scope into 3 coupled modules (C1, C2, C3). Curated 7 peer-reviewed reference papers and signed the official Ethics Consideration Form.", body_style))
    story.append(Paragraph("• <b>Repository Architecture & Packaging:</b> Initialized the formal Git repository with modern PEP 621 packaging (<code>irishlogix</code> v0.1.0) and automated testing harness.", body_style))
    story.append(Paragraph("• <b>Automated CSO Data Pipeline (<code>cso_loader.py</code>):</b> Integrated the Central Statistics Office (CSO) PxStat API; successfully ingested and parsed 444 vessel arrivals (TBQ01), 2,331 Ro-Ro freight records (TBQ04), and 3,600 trade region records (TBQ05). Created unified port congestion matrix.", body_style))
    story.append(Paragraph("• <b>Irish Freight Corridor Graph (<code>corridor_network.py</code>):</b> Implemented NetworkX road network graph with 11 strategic nodes (Dublin, Cork, Rosslare, M50, Athlone, Limerick, Galway, Waterford, Dundalk) and 15 bidirectional corridors with tolls, speed limits, and distance matrices.", body_style))
    story.append(Paragraph("• <b>Baseline FIFO Dispatcher Simulator (<code>baseline_dispatcher.py</code>):</b> Coded and executed empirical baseline simulation across 50 benchmark consignments: 8,636.5 km distance, 104.4 driving hrs, <b>63.5 idle waiting hrs</b> (averaging <b>1.27 hrs wasted idling per trip</b>), 2,879.3 L diesel, 7,601.3 kg CO2e, and €14,791.21 total cost (avg €295.82/trip).", body_style))
    story.append(Paragraph("• <b>Unit Test Suite:</b> Authored 9 unit tests across data ingestion, graph routing, and simulation; 100% passing (<code>pytest tests -v</code> in 1.08s).", body_style))

    # Section 2
    story.append(Paragraph("2. Evaluation & Critical Reflection (So What?)", heading_style))
    story.append(Paragraph("• <b>Validation of Research Gap:</b> The Week 1 baseline simulation empirically validates the core research rationale: without predictive delay awareness, freight hauliers waste an average of 1.27 hours per shipment waiting at terminal gates and customs inspections, creating direct financial and carbon penalties.", body_style))
    story.append(Paragraph("• <b>Data Grounding:</b> Live CSO PxStat API data guarantees verified, open historical maritime records (2017–2026) for Dublin, Cork, and Rosslare, de-risking Component 1 model development.", body_style))

    # Section 3
    story.append(Paragraph("3. Action Plan & Next Steps (Now What?)", heading_style))
    story.append(Paragraph("• <b>Oral Pitch (1 October):</b> Deliver the timed 1–2 minute project pitch adhering to Problem → Gap → Idea → Method → Contribution.", body_style))
    story.append(Paragraph("• <b>Supervisory Alignment:</b> Present Week 1 code and benchmark findings to Dr. Thanos Staikopoulos during scheduled supervisory review.", body_style))
    story.append(Paragraph("• <b>EMODnet & AIS Ingestion:</b> Incorporate EMODnet vessel density metrics into the maritime congestion feature store.", body_style))

    # Section 4 - Supervisor Log Table
    story.append(Paragraph("4. Supervisor Meeting Log & Agreed Actions", heading_style))
    log_data = [
        [Paragraph("Agenda Items:", table_cell_bold), Paragraph("1. CA2 Proposal & Ethics sign-off.<br/>2. 1 October Pitch rehearsal.<br/>3. Demonstration of Week 1 technical deliverables: Git repo, CSO pipeline, baseline FIFO simulation.", table_cell_style)],
        [Paragraph("Supervisor Guidance:", table_cell_bold), Paragraph("• Emphasize empirical gap between unbuffered spreadsheet planning and predictive optimization.<br/>• Ensure baseline simulation parameters are grounded in Irish logistics economics.", table_cell_style)],
        [Paragraph("Agreed Actions:", table_cell_bold), Paragraph("1. Deliver 1–2 minute pitch on 1 October.<br/>2. Submit weekly progress updates every Tuesday.<br/>3. Begin feature engineering on ingested CSO port traffic data.", table_cell_style)],
    ]
    t_log = Table(log_data, colWidths=[110, 420])
    t_log.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F0F4F8")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D7DE")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_log)

    # Section 5 - Milestones Table
    story.append(Paragraph("5. Project Milestone & Gantt Tracking", heading_style))
    m_headers = [Paragraph("Milestone", table_cell_bold), Paragraph("Target", table_cell_bold), Paragraph("Status", table_cell_bold), Paragraph("Deliverable Summary", table_cell_bold)]
    m_rows = [
        m_headers,
        [Paragraph("M1", table_cell_style), Paragraph("Week 3", table_cell_style), Paragraph("<b>ADVANCED / ON SCHEDULE</b>", table_cell_style), Paragraph("Baseline FIFO model operational; CSO data ingested; corridor graph built", table_cell_style)],
        [Paragraph("M2", table_cell_style), Paragraph("Week 9", table_cell_style), Paragraph("PLANNED", table_cell_style), Paragraph("XGBoost models (C1, C2) coupled with Pareto Optimizer (C3)", table_cell_style)],
        [Paragraph("M3", table_cell_style), Paragraph("Week 13", table_cell_style), Paragraph("PLANNED", table_cell_style), Paragraph("Dual-system comparative evaluation & Streamlit UI dashboard", table_cell_style)],
        [Paragraph("M4", table_cell_style), Paragraph("Week 15", table_cell_style), Paragraph("PLANNED", table_cell_style), Paragraph("Final MSc Dissertation, code repository, and Viva Voce", table_cell_style)],
    ]
    t_m = Table(m_rows, colWidths=[40, 50, 140, 300])
    t_m.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#102C57")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D7DE")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TEXTCOLOR', (2,1), (2,1), colors.HexColor("#008000")),
    ]))
    story.append(t_m)

    story.append(Spacer(1, 8))
    # Signature
    story.append(Paragraph("<b>Student Signature:</b> Rohitkumar Amritlal Jaiswal &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> 29 September 2026", body_style))
    story.append(Paragraph("<b>Supervisor Signature:</b> ___________________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> ___________________________", body_style))

    doc.build(story)
    print(f"[SUCCESS] Saved PDF report to {target_path}")

def main():
    root = Path(".")
    pkg = root / "Submission_Package_Rohitkumar_Jaiswal_25119613"

    # Generate DOCX
    docx_path = root / "NCI_MSc_Data_Analytics_Weekly_Progress_Report_Week1.docx"
    create_docx_report(docx_path)

    # Generate PDFs
    pdf1 = root / "NCI_MSc_Data_Analytics_Weekly_Progress_Report_Week1.pdf"
    pdf2 = root / "Weekly_Progress_Report_Tuesday_29Sep.pdf"
    pdf3 = pkg / "NCI_MSc_Data_Analytics_Weekly_Progress_Report_Week1.pdf"

    create_pdf_report(pdf1)
    create_pdf_report(pdf2)
    create_pdf_report(pdf3)

if __name__ == "__main__":
    main()
