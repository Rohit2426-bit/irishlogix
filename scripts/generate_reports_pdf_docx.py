"""
Report Generation Script: Compiles Markdown Weekly Reports into Executive PDF and DOCX.
Uses ReportLab and python-docx with professional NCI styling.
Compact, easy-to-read format without em-dashes, en-dashes, or proposal/ethics mentions.
"""

from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def create_docx_report(target_path: Path):
    doc = Document()

    # Margins: 0.6 inches for a clean, compact layout
    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # Title block
    title_p = doc.add_paragraph()
    r_t = title_p.add_run("NATIONAL COLLEGE OF IRELAND: SCHOOL OF COMPUTING")
    r_t.bold = True
    r_t.font.size = Pt(13)
    r_t.font.color.rgb = RGBColor(16, 44, 87)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_after = Pt(2)

    sub_p = doc.add_paragraph()
    r_sub = sub_p.add_run("MSc in Data Analytics: Research Practicum (MSCDAD_A_JAN26I)\nWEEKLY PROGRESS REPORT: WEEK 1")
    r_sub.bold = True
    r_sub.font.size = Pt(10.5)
    r_sub.font.color.rgb = RGBColor(60, 60, 60)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_p.paragraph_format.space_after = Pt(8)

    # Details Table
    table = doc.add_table(rows=6, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    details = [
        ("Student Name:", "Rohitkumar Amritlal Jaiswal"),
        ("Student ID:", "x25119613"),
        ("Supervisor:", "Dr. Thanos Staikopoulos"),
        ("Project Title:", "Coupling Port Congestion and Customs Delay Prediction with Carbon-Aware Multi-Objective Route Optimisation for Post-Brexit Irish Freight Logistics"),
        ("Reporting Period:", "Week 1 (Technical Kickoff & Baseline Simulation)"),
        ("Submission Date:", "Tuesday, 29 September 2026")
    ]

    for i, (label, val) in enumerate(details):
        row = table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(1.8)
        c1.width = Inches(5.2)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.size = Pt(9.0)
        set_cell_background(c0, "F0F4F8")

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(val)
        r1.font.size = Pt(9.0)
        set_cell_background(c1, "FFFFFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def add_heading(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(3)
        r = h.add_run(text)
        r.bold = True
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(16, 44, 87)

    # Section 1
    add_heading("1. Summary of Activities Completed This Week")
    bullets1 = [
        ("Project Pitch Preparation: ", "Prepared a 1-2 minute spoken pitch following the required format: Problem -> Gap -> Idea -> Method -> Contribution, ready for presentation on 1 October."),
        ("Code Repository Setup: ", "Initialized the project Git repository and created a clean Python package structure named irishlogix using pyproject.toml."),
        ("Public Data Ingestion (cso_loader.py): ", "Connected directly to the Central Statistics Office (CSO) PxStat API and downloaded quarterly maritime datasets from 2017 to 2026: TBQ01 (444 vessel arrival records), TBQ04 (2,331 Ro-Ro freight trailer units), and TBQ05 (3,600 trade region records). Built clean activity matrix in data/processed/cso_port_activity_matrix.csv."),
        ("Jupyter Notebook: ", "Created and executed notebooks/01_week1_data_ingestion_and_exploration.ipynb which downloads the data, plots port arrival trends, shows post-Brexit trade shifts, and runs the baseline route simulation."),
        ("Irish Road Corridor Network (corridor_network.py): ", "Built a road network graph in NetworkX with 11 nodes (Dublin, Cork, Rosslare, Athlone, Limerick, Galway, Waterford, Dundalk) and 15 road corridors with travel distances, speed limits, and tolls."),
        ("Baseline Dispatch Simulation (baseline_dispatcher.py): ", "Built an empirical baseline simulation representing how small Irish hauliers plan routes using simple spreadsheets without delay forecasting. Ran a test of 50 freight trips: total distance 8,636.5 km; active driving time 104.4 hours; idle waiting time 63.5 hours (average 1.27 hours wasted idling per trip at port gates and customs); total diesel used 2,879.3 Litres; carbon emissions 7,601.3 kg CO2e; total transport cost €14,791.21 (average €295.82 per trip)."),
        ("Unit Testing: ", "Created 9 unit tests across data loader, network graph, and simulator. All 9 tests passed.")
    ]
    for b_prefix, text in bullets1:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        r_b = p.add_run(b_prefix)
        r_b.bold = True
        r_b.font.size = Pt(8.5)
        r_t = p.add_run(text)
        r_t.font.size = Pt(8.5)

    # Section 2: Data Sources Table
    add_heading("2. Primary Public Dataset Sources & URLs")
    src_table = doc.add_table(rows=7, cols=3)
    src_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_headers = ["Dataset Name", "Source and Direct URL", "Role in Project"]
    for j, h in enumerate(s_headers):
        cell = src_table.rows[0].cells[j]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.0)
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "102C57")

    src_rows = [
        ("CSO Table TBQ01", "https://data.cso.ie/table/TBQ01", "Ship arrivals for Dublin, Cork, and Rosslare ports"),
        ("CSO Table TBQ02", "https://data.cso.ie/table/TBQ02", "Cargo tonnage categories (Ro-Ro and Lo-Lo)"),
        ("CSO Table TBQ04", "https://data.cso.ie/table/TBQ04", "Freight trailer counts across Irish ports"),
        ("CSO Table TBQ05", "https://data.cso.ie/table/TBQ05", "Post-Brexit trade volumes: Great Britain vs. EU"),
        ("EMODnet Vessel Density", "https://emodnet.ec.europa.eu/en/human-activities", "AIS marine traffic density maps"),
        ("OpenStreetMap Ireland", "https://download.geofabrik.de/europe/ireland-and-northern-ireland.html", "Road distances and speeds for Irish corridors")
    ]
    for i, (ds, url, purp) in enumerate(src_rows):
        row = src_table.rows[i + 1]
        for j, text in enumerate([ds, url, purp]):
            cell = row.cells[j]
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(text)
            r.font.size = Pt(7.5)
            set_cell_background(cell, "F9FAFC" if i % 2 == 1 else "FFFFFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Section 3: Reflection
    add_heading("3. Reflection and Key Findings")
    bullets2 = [
        ("The Problem is Real: ", "The baseline simulation shows that without delay prediction, trucks waste an average of 1.27 hours per shipment waiting at gates and customs. This proves that coupling delay prediction with route optimization can save real fuel, money, and emissions."),
        ("Data is Verified: ", "The CSO PxStat API provides clean, continuous historical data from 2017 to 2026, ensuring we have solid numbers to train the machine learning models."),
        ("Benchmark is Set: ", "Having this baseline simulator running in Week 1 gives us a clear benchmark to compare our future machine learning models against.")
    ]
    for b_prefix, text in bullets2:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        r_b = p.add_run(b_prefix)
        r_b.bold = True
        r_b.font.size = Pt(8.5)
        r_t = p.add_run(text)
        r_t.font.size = Pt(8.5)

    # Section 4: Planned Activities
    add_heading("4. Planned Activities for Next Week")
    bullets3 = [
        ("1. ", "Deliver the 1-2 minute oral pitch on 1 October."),
        ("2. ", "Review the Week 1 baseline results and refined project plan with Dr. Thanos Staikopoulos during our meeting."),
        ("3. ", "Ingest EMODnet AIS vessel density data for Irish waters."),
        ("4. ", "Start feature engineering for the Component 1 Port Congestion Classifier.")
    ]
    for b_prefix, text in bullets3:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(1.5)
        r_b = p.add_run(b_prefix)
        r_b.bold = True
        r_b.font.size = Pt(8.5)
        r_t = p.add_run(text)
        r_t.font.size = Pt(8.5)

    # Section 5: Milestones Table
    add_heading("5. Milestone Tracking")
    m_table = doc.add_table(rows=5, cols=4)
    m_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Milestone", "Target", "Status", "Summary"]
    for j, h_text in enumerate(headers):
        cell = m_table.rows[0].cells[j]
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(8.0)
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "102C57")

    m_data = [
        ("M1", "Week 3", "Ahead of Schedule", "Baseline simulator working, CSO data ingested, road network built"),
        ("M2", "Week 9", "Planned", "Train XGBoost delay models and connect to Pareto optimizer"),
        ("M3", "Week 13", "Planned", "Complete comparison against baseline and build Streamlit dashboard"),
        ("M4", "Week 15", "Planned", "Final dissertation, code repository, and viva presentation")
    ]
    for i, row_data in enumerate(m_data):
        row = m_table.rows[i + 1]
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(val)
            r.font.size = Pt(7.5)
            if j == 2 and "Ahead" in val:
                r.bold = True
                r.font.color.rgb = RGBColor(0, 128, 0)
            set_cell_background(cell, "F9FAFC" if i % 2 == 1 else "FFFFFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Section 6: Sign-off
    add_heading("6. Sign-Off")
    sig_p = doc.add_paragraph()
    sig_p.add_run("Student Signature: Rohitkumar Amritlal Jaiswal                      Date: 29 September 2026\n\nSupervisor Signature: ___________________________                   Date: ___________________________")
    sig_p.runs[0].font.size = Pt(8.5)

    doc.save(str(target_path))
    print(f"[SUCCESS] Saved DOCX report to {target_path}")


def create_pdf_report(target_path: Path):
    doc = SimpleDocTemplate(
        str(target_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=normal,
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14.5,
        textColor=colors.HexColor("#102C57"),
        alignment=1,
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=normal,
        fontName="Helvetica",
        fontSize=9,
        leading=11.5,
        textColor=colors.HexColor("#333333"),
        alignment=1,
        spaceAfter=6
    )
    heading_style = ParagraphStyle(
        "Heading2Custom",
        parent=normal,
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#102C57"),
        spaceBefore=6,
        spaceAfter=2.5
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=normal,
        fontName="Helvetica",
        fontSize=7.8,
        leading=10,
        textColor=colors.HexColor("#222222"),
        spaceAfter=2
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=normal,
        fontName="Helvetica",
        fontSize=7.2,
        leading=9
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=normal,
        fontName="Helvetica-Bold",
        fontSize=7.2,
        leading=9,
        textColor=colors.HexColor("#102C57")
    )

    story = []

    # Title block
    story.append(Paragraph("NATIONAL COLLEGE OF IRELAND: SCHOOL OF COMPUTING", title_style))
    story.append(Paragraph("MSc in Data Analytics: Research Practicum (MSCDAD_A_JAN26I)<br/><b>WEEKLY PROGRESS REPORT: WEEK 1</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#102C57"), spaceAfter=5))

    # Details table
    details_data = [
        [Paragraph("Student Name:", table_cell_bold), Paragraph("Rohitkumar Amritlal Jaiswal (ID: x25119613)", table_cell_style)],
        [Paragraph("Supervisor:", table_cell_bold), Paragraph("Dr. Thanos Staikopoulos", table_cell_style)],
        [Paragraph("Project Title:", table_cell_bold), Paragraph("Coupling Port Congestion & Customs Delay Prediction with Carbon-Aware Multi-Objective Route Optimisation", table_cell_style)],
        [Paragraph("Reporting Period / Date:", table_cell_bold), Paragraph("Week 1 (Technical Kickoff & Baseline Simulation) | Tuesday, 29 September 2026", table_cell_style)],
    ]
    t_details = Table(details_data, colWidths=[110, 430])
    t_details.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F0F4F8")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D7DE")),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_details)
    story.append(Spacer(1, 3))

    # Section 1
    story.append(Paragraph("1. Summary of Activities Completed This Week", heading_style))
    story.append(Paragraph("• <b>Project Pitch Preparation:</b> Prepared a 1-2 minute spoken pitch following the required format: Problem -> Gap -> Idea -> Method -> Contribution, ready for presentation on 1 October.", body_style))
    story.append(Paragraph("• <b>Code Repository Setup:</b> Initialized the project Git repository and created a clean Python package structure named <code>irishlogix</code> using <code>pyproject.toml</code>.", body_style))
    story.append(Paragraph("• <b>Public Data Ingestion (<code>cso_loader.py</code>):</b> Connected directly to Central Statistics Office (CSO) PxStat API and downloaded quarterly datasets from 2017 to 2026: TBQ01 (444 vessel arrivals), TBQ04 (2,331 Ro-Ro trailer units), and TBQ05 (3,600 trade region records). Built clean activity matrix in <code>data/processed/cso_port_activity_matrix.csv</code>.", body_style))
    story.append(Paragraph("• <b>Jupyter Notebook Development:</b> Created and ran <code>notebooks/01_week1_data_ingestion_and_exploration.ipynb</code> which downloads data, plots arrival trends, shows post-Brexit trade shifts, and runs the baseline route simulation.", body_style))
    story.append(Paragraph("• <b>Irish Road Corridor Network (<code>corridor_network.py</code>):</b> Built a road network graph in NetworkX with 11 nodes (Dublin, Cork, Rosslare, Athlone, Limerick, Galway, Waterford, Dundalk) and 15 road corridors with travel distances, speed limits, and tolls.", body_style))
    story.append(Paragraph("• <b>Baseline Dispatch Simulation (<code>baseline_dispatcher.py</code>):</b> Built an empirical baseline simulation representing how small Irish hauliers plan routes using simple spreadsheets without delay forecasting. Ran a test of 50 freight trips: total distance 8,636.5 km; active driving time 104.4 hours; <b>idle waiting time 63.5 hours</b> (trucks wasted an average of <b>1.27 hours idling per trip</b> at port gates and customs); total diesel used 2,879.3 Litres; carbon emissions 7,601.3 kg CO2e; total transport cost €14,791.21 (average €295.82 per trip).", body_style))
    story.append(Paragraph("• <b>Unit Testing:</b> Created 9 unit tests across data loader, network graph, and simulator. All 9 tests passed.", body_style))

    # Section 2: Data Sources Table
    story.append(Paragraph("2. Primary Public Dataset Sources & URLs", heading_style))
    s_headers = [Paragraph("Dataset Name", table_cell_bold), Paragraph("Source and Direct URL", table_cell_bold), Paragraph("Role in Project", table_cell_bold)]
    s_rows = [
        s_headers,
        [Paragraph("CSO Table TBQ01", table_cell_style), Paragraph("https://data.cso.ie/table/TBQ01", table_cell_style), Paragraph("Ship arrivals for Dublin, Cork, and Rosslare ports", table_cell_style)],
        [Paragraph("CSO Table TBQ02", table_cell_style), Paragraph("https://data.cso.ie/table/TBQ02", table_cell_style), Paragraph("Cargo tonnage categories (Ro-Ro and Lo-Lo)", table_cell_style)],
        [Paragraph("CSO Table TBQ04", table_cell_style), Paragraph("https://data.cso.ie/table/TBQ04", table_cell_style), Paragraph("Freight trailer counts across Irish ports", table_cell_style)],
        [Paragraph("CSO Table TBQ05", table_cell_style), Paragraph("https://data.cso.ie/table/TBQ05", table_cell_style), Paragraph("Post-Brexit trade volumes: Great Britain vs. EU", table_cell_style)],
        [Paragraph("EMODnet Vessel Density", table_cell_style), Paragraph("https://emodnet.ec.europa.eu/en/human-activities", table_cell_style), Paragraph("AIS marine traffic density maps", table_cell_style)],
        [Paragraph("OpenStreetMap Ireland", table_cell_style), Paragraph("https://download.geofabrik.de/europe/ireland-and-northern-ireland.html", table_cell_style), Paragraph("Road distances and speeds for Irish corridors", table_cell_style)],
    ]
    t_s = Table(s_rows, colWidths=[110, 250, 180])
    t_s.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#102C57")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D7DE")),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_s)
    story.append(Spacer(1, 3))

    # Section 3
    story.append(Paragraph("3. Reflection and Key Findings", heading_style))
    story.append(Paragraph("• <b>The Problem is Real:</b> The baseline simulation shows that without delay prediction, trucks waste an average of 1.27 hours per shipment waiting at gates and customs. This proves that coupling delay prediction with route optimization can save real fuel, money, and emissions.", body_style))
    story.append(Paragraph("• <b>Data is Verified:</b> The CSO PxStat API provides clean, continuous historical data from 2017 to 2026, ensuring we have solid numbers to train the machine learning models.", body_style))
    story.append(Paragraph("• <b>Benchmark is Set:</b> Having this baseline simulator running in Week 1 gives us a clear benchmark to compare our future machine learning models against.", body_style))

    # Section 4
    story.append(Paragraph("4. Planned Activities for Next Week", heading_style))
    story.append(Paragraph("1. Deliver the 1-2 minute oral pitch on 1 October.<br/>2. Review Week 1 baseline results and refined project plan with Dr. Thanos Staikopoulos during our meeting.<br/>3. Ingest EMODnet AIS vessel density data for Irish waters.<br/>4. Start feature engineering for the Component 1 Port Congestion Classifier.", body_style))

    # Section 5: Milestones
    story.append(Paragraph("5. Milestone Tracking", heading_style))
    m_headers = [Paragraph("Milestone", table_cell_bold), Paragraph("Target", table_cell_bold), Paragraph("Status", table_cell_bold), Paragraph("Summary", table_cell_bold)]
    m_rows = [
        m_headers,
        [Paragraph("M1", table_cell_style), Paragraph("Week 3", table_cell_style), Paragraph("<b>Ahead of Schedule</b>", table_cell_style), Paragraph("Baseline simulator working, CSO data ingested, road network built", table_cell_style)],
        [Paragraph("M2", table_cell_style), Paragraph("Week 9", table_cell_style), Paragraph("Planned", table_cell_style), Paragraph("Train XGBoost delay models and connect to Pareto optimizer", table_cell_style)],
        [Paragraph("M3", table_cell_style), Paragraph("Week 13", table_cell_style), Paragraph("Planned", table_cell_style), Paragraph("Complete comparison against baseline and build Streamlit dashboard", table_cell_style)],
        [Paragraph("M4", table_cell_style), Paragraph("Week 15", table_cell_style), Paragraph("Planned", table_cell_style), Paragraph("Final dissertation, code repository, and viva presentation", table_cell_style)],
    ]
    t_m = Table(m_rows, colWidths=[35, 45, 110, 350])
    t_m.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#102C57")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D7DE")),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TEXTCOLOR', (2,1), (2,1), colors.HexColor("#008000")),
    ]))
    story.append(t_m)

    story.append(Spacer(1, 5))
    # Signature
    story.append(Paragraph("<b>Student Signature:</b> Rohitkumar Amritlal Jaiswal &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> 29 September 2026", body_style))
    story.append(Paragraph("<b>Supervisor Signature:</b> ___________________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> ___________________________", body_style))

    doc.build(story)
    print(f"[SUCCESS] Saved PDF report to {target_path}")

def main():
    root = Path(".")
    pkg = root / "Submission_Package_Rohitkumar_Jaiswal_25119613"

    # Generate DOCX
    docx_path1 = root / "NCI_MSc_Data_Analytics_Weekly_Progress_Report_Week1.docx"
    docx_path2 = pkg / "NCI_MSc_Data_Analytics_Weekly_Progress_Report_Week1.docx"
    create_docx_report(docx_path1)
    create_docx_report(docx_path2)

    # Generate PDFs
    pdf1 = root / "NCI_MSc_Data_Analytics_Weekly_Progress_Report_Week1.pdf"
    pdf2 = root / "Weekly_Progress_Report_Tuesday_29Sep.pdf"
    pdf3 = pkg / "NCI_MSc_Data_Analytics_Weekly_Progress_Report_Week1.pdf"

    create_pdf_report(pdf1)
    create_pdf_report(pdf2)
    create_pdf_report(pdf3)

if __name__ == "__main__":
    main()
