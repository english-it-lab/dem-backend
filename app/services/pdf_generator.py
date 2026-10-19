import os
from collections import defaultdict
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Register DejaVu fonts for Cyrillic support
_FONT_DIR = "/usr/share/fonts/ttf/dejavu"
if os.path.isdir(_FONT_DIR):
    pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(_FONT_DIR, "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuBold", os.path.join(_FONT_DIR, "DejaVuSans-Bold.ttf")))
    FONT = "DejaVu"
    FONT_BOLD = "DejaVuBold"
else:
    FONT = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

BLUE = colors.HexColor("#2C3E50")
LIGHT_BLUE = colors.HexColor("#3498DB")


class PDFGeneratorService:
    def _make_title_style(self, parent, font_size=16, bold=True, space_after=6, alignment=1):
        return ParagraphStyle(
            f"Custom{parent}",
            parent=parent,
            fontSize=font_size,
            fontName=FONT_BOLD if bold else FONT,
            spaceAfter=space_after,
            alignment=alignment,
        )

    def generate_event_program(self, program_data: dict) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        story = []
        styles = getSampleStyleSheet()

        event = program_data.get("event", {})
        committee = program_data.get("committee", [])
        sections = program_data.get("sections", [])

        self._build_title_page(story, styles, event)
        story.append(PageBreak())

        self._build_committee(story, styles, event, committee)
        story.append(PageBreak())

        self._build_schedule(story, styles, sections)
        story.append(PageBreak())

        panel_sections = [s for s in sections if s.get("section_type") != "poster_session"]
        poster_sections = [s for s in sections if s.get("section_type") == "poster_session"]

        for section in panel_sections:
            self._build_section(story, styles, section)
            story.append(PageBreak())

        if poster_sections:
            title_style = self._make_title_style(styles["Heading1"], font_size=16, space_after=30)
            story.append(Paragraph("POSTER SESSIONS", title_style))
            story.append(Spacer(1, 10))
            for section in poster_sections:
                self._build_section(story, styles, section)
                story.append(PageBreak())

        self._build_russian_sections(story, styles, sections)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _build_title_page(self, story, styles, event):
        centered = self._make_title_style(styles["Normal"], font_size=14, bold=True, space_after=8)
        lg_centered = self._make_title_style(styles["Normal"], font_size=16, bold=True, space_after=12)

        story.append(Paragraph("НАЦИОНАЛЬНЫЙ ИССЛЕДОВАТЕЛЬСКИЙ УНИВЕРСИТЕТ", centered))
        story.append(Spacer(1, 30))

        event_name = event.get("name", "")
        event_type = event.get("type", "")
        event_date = event.get("date", "")

        if event_type:
            story.append(Paragraph(f"{event_type}", centered))
        story.append(Paragraph(f"«{event_name}»", lg_centered))
        story.append(Spacer(1, 10))

        if event_date:
            story.append(Paragraph(f"{event_date}", centered))
        story.append(Spacer(1, 10))

        venue = event.get("venue", {})
        if venue:
            city = venue.get("city", "")
            if city:
                story.append(Paragraph(city, centered))

    def _build_committee(self, story, styles, event, committee):
        if not committee:
            return

        title_style = self._make_title_style(styles["Heading1"], font_size=14, space_after=20, alignment=1)
        event_name = event.get("name", "")
        story.append(Paragraph(f"Состав оргкомитета конференции «{event_name}»", title_style))
        story.append(Spacer(1, 15))

        grouped = defaultdict(list)
        for m in committee:
            grouped[m.get("committee_type", "organizing")].append(m)

        body_style = ParagraphStyle(
            "CommitteeBody", parent=styles["Normal"], fontName=FONT, fontSize=11, spaceAfter=6, leading=14
        )
        label_style = ParagraphStyle(
            "CommitteeLabel", parent=styles["Normal"], fontName=FONT_BOLD, fontSize=11, spaceAfter=4, spaceBefore=10
        )

        for ctype in ["organizing", "program"]:
            members = grouped.get(ctype, [])
            if not members:
                continue

            label = "Члены организационного комитета:" if ctype == "organizing" else "Члены программного комитета:"
            story.append(Paragraph(label, label_style))

            for m in sorted(members, key=lambda x: x.get("sort_order", 0)):
                parts = []
                name = m.get("full_name", "")
                if name:
                    parts.append(name)
                degree = m.get("degree") or m.get("title")
                if degree:
                    parts.append(f"({degree})")
                position = m.get("position")
                if position:
                    parts.append(f"— {position}")
                workplace = m.get("workplace")
                if workplace and workplace != position:
                    parts.append(f", {workplace}")

                line = " ".join(parts)
                role = m.get("role", "")
                if role:
                    line = f"{role}: {line}"
                story.append(Paragraph(line, body_style))

    def _build_schedule(self, story, styles, sections):
        if not sections:
            return

        title_style = self._make_title_style(styles["Heading1"], font_size=14, space_after=15, alignment=1)
        story.append(Paragraph("SCHEDULE", title_style))
        story.append(Spacer(1, 10))

        cell_style = ParagraphStyle("SchedCell", parent=styles["Normal"], fontName=FONT, fontSize=9)
        header_style = ParagraphStyle("SchedHeader", parent=styles["Normal"], fontName=FONT_BOLD, fontSize=9)

        rows = []
        current_date = None
        for s in sections:
            time_str = s.get("time", "")
            if time_str:
                try:
                    dt = datetime.fromisoformat(time_str)
                    date_str = dt.strftime("%B %d, %A")
                except (ValueError, TypeError):
                    date_str = ""
                time_fmt = dt.strftime("%H:%M") if "dt" in dir() else time_str
            else:
                date_str = ""
                time_fmt = ""

            if date_str and date_str != current_date:
                current_date = date_str
                rows.append([Paragraph(f"<b>{date_str}</b>", cell_style), "", ""])

            name = s.get("name", "")
            hall = s.get("lecture_hall", "")

            rows.append([time_fmt, Paragraph(name, cell_style), hall])

        if not rows:
            return

        table_data = [
            [
                Paragraph("<b>Time</b>", header_style),
                Paragraph("<b>Section</b>", header_style),
                Paragraph("<b>Room</b>", header_style),
            ]
        ] + rows
        col_widths = [3.5 * cm, 10 * cm, 4 * cm]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
                    ("FONTNAME", (0, 1), (-1, -1), FONT),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(table)

    def _build_section(self, story, styles, section):
        name = section.get("name", "")
        hall = section.get("lecture_hall", "")
        time_str = section.get("time", "")
        time_limit = section.get("time_limit")
        section_type = section.get("section_type", "")

        section_label = {
            "panel_discussion": "Panel Discussion",
            "poster_session": "Poster Session",
            "projects_session": "Projects Session",
        }.get(section_type, "Session")

        title_text = f"{section_label}: {name}"
        if hall:
            title_text += f" ({hall})"

        section_title = ParagraphStyle(
            "SectionTitle",
            parent=styles["Heading2"],
            fontName=FONT_BOLD,
            fontSize=13,
            textColor=BLUE,
            spaceAfter=6,
        )
        story.append(Paragraph(title_text, section_title))

        date_display = ""
        if time_str:
            try:
                dt = datetime.fromisoformat(time_str)
                date_display = dt.strftime("%d %B %Y")
            except (ValueError, TypeError):
                date_display = time_str

        info_style = ParagraphStyle("SectionInfo", parent=styles["Normal"], fontName=FONT, fontSize=10, spaceAfter=4)

        if date_display:
            story.append(Paragraph(date_display, info_style))
        if time_limit:
            story.append(Paragraph(f"Time-limit: {time_limit} minutes", info_style))

        juries = section.get("juries", [])
        if juries:
            story.append(Spacer(1, 6))
            story.append(Paragraph("<b>Chairpersons:</b>", info_style))
            for j in juries:
                jury_name = j.get("full_name", "")
                parts = [jury_name]
                degree = j.get("degree") or j.get("title")
                if degree:
                    parts.append(f"({degree})")
                workplace = j.get("workplace")
                if workplace:
                    parts.append(workplace)
                university = j.get("university")
                if university and university != workplace:
                    parts.append(university)
                story.append(Paragraph(", ".join(parts), info_style))

        story.append(Spacer(1, 12))

        participants = section.get("participants", [])
        for idx, p in enumerate(participants, 1):
            name = p.get("full_name", "")
            topic = p.get("presentation_topic", "")
            abstract = p.get("abstract", "")
            advisor = p.get("scientific_advisor")

            participant_style = ParagraphStyle(
                f"Part{idx}",
                parent=styles["Normal"],
                fontName=FONT,
                fontSize=10,
                spaceAfter=4,
                leading=13,
            )

            story.append(Paragraph(f"{idx}. {name}", participant_style))

            if topic:
                story.append(Paragraph(f"<i>{topic}</i>", participant_style))

            if abstract:
                story.append(Paragraph(abstract, participant_style))

            if advisor and advisor.get("full_name"):
                advisor_parts = [f"<b>Scientific Advisor:</b> {advisor['full_name']}"]
                adv_degree = advisor.get("degree") or advisor.get("title")
                if adv_degree:
                    advisor_parts.append(f"({adv_degree})")
                adv_workplace = advisor.get("workplace")
                if adv_workplace:
                    advisor_parts.append(adv_workplace)
                story.append(Paragraph(", ".join(advisor_parts), participant_style))

            story.append(Spacer(1, 6))

    def _build_russian_sections(self, story, styles, sections):
        if not sections:
            return

        title_style = self._make_title_style(styles["Heading1"], font_size=14, space_after=20, alignment=1)
        story.append(Paragraph("СЕКЦИИ", title_style))
        story.append(Spacer(1, 10))

        section_style = ParagraphStyle(
            "RuSection",
            parent=styles["Normal"],
            fontName=FONT_BOLD,
            fontSize=11,
            spaceAfter=6,
            spaceBefore=10,
        )
        part_style = ParagraphStyle(
            "RuParticipant",
            parent=styles["Normal"],
            fontName=FONT,
            fontSize=10,
            spaceAfter=3,
            leftIndent=20,
        )

        for section in sections:
            name = section.get("name", "")
            story.append(Paragraph(f"Секция: {name}", section_style))

            participants = section.get("participants", [])
            if not participants:
                story.append(Paragraph("Нет участников", part_style))
                continue

            for p in participants:
                name = p.get("full_name", "")
                faculty = p.get("faculty", "")
                university = p.get("university", "")
                topic = p.get("presentation_topic", "")

                parts = [name]
                if faculty or university:
                    place = ", ".join(filter(None, [university, faculty]))
                    parts.append(f" ({place})")
                if topic:
                    parts.append(f" — {topic}")

                story.append(Paragraph(" ".join(parts), part_style))

            story.append(Spacer(1, 8))
