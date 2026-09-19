"""Render the manual from trusted editable JSON; see README.md for build instructions."""

import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description="Build the versioned user manual")
parser.add_argument("--font-dir", type=Path, default=Path("/usr/share/fonts/truetype/dejavu"))
parser.add_argument("--output", type=Path, default=HERE.parent / "Agentic_Data_Ops_User_Manual.pdf")
args = parser.parse_args()
OUT = args.output
FONT = args.font_dir
for name, file in [
    ("Sans", "DejaVuSans.ttf"),
    ("SansBold", "DejaVuSans-Bold.ttf"),
    ("SansItalic", "DejaVuSans-Oblique.ttf"),
    ("Mono", "DejaVuSansMono.ttf"),
]:
    pdfmetrics.registerFont(TTFont(name, str(FONT / file)))
pdfmetrics.registerFontFamily(
    "Sans", normal="Sans", bold="SansBold", italic="SansItalic", boldItalic="SansBold"
)
NAVY = colors.HexColor("#133047")
TEAL = colors.HexColor("#007F83")
INK = colors.HexColor("#233A4A")
MUTED = colors.HexColor("#566B78")
LIGHT = colors.HexColor("#EFF5F7")
LINE = colors.HexColor("#CCDBE2")
styles = {
    "body": ParagraphStyle(
        "body", fontName="Sans", fontSize=10, leading=14, textColor=INK, spaceAfter=8
    ),
    "small": ParagraphStyle(
        "small", fontName="Sans", fontSize=8.6, leading=12, textColor=INK, spaceAfter=6
    ),
    "h2": ParagraphStyle(
        "h2",
        fontName="SansBold",
        fontSize=12,
        leading=16,
        textColor=TEAL,
        spaceBefore=8,
        spaceAfter=6,
        keepWithNext=True,
    ),
    "title": ParagraphStyle(
        "title", fontName="SansBold", fontSize=23, leading=28, textColor=NAVY, spaceAfter=15
    ),
    "eyebrow": ParagraphStyle(
        "eyebrow", fontName="SansBold", fontSize=8, leading=11, textColor=TEAL, spaceAfter=8
    ),
    "code": ParagraphStyle(
        "code", fontName="Mono", fontSize=7.7, leading=10.6, textColor=INK, spaceAfter=0
    ),
    "cell": ParagraphStyle("cell", fontName="Sans", fontSize=8.6, leading=11.8, textColor=INK),
    "th": ParagraphStyle(
        "th", fontName="SansBold", fontSize=8.6, leading=11.8, textColor=colors.white
    ),
    "note": ParagraphStyle("note", fontName="Sans", fontSize=9.3, leading=13.2, textColor=NAVY),
}
sections = []
current = []


def page(title, subtitle):
    global current
    current = []
    sections.append((title, subtitle, current))


def p(text):
    current.append(Paragraph(text, styles["body"]))


def h(text):
    current.append(Paragraph(text, styles["h2"]))


def small(text):
    current.append(Paragraph(text, styles["small"]))


def code(text):
    text = text.strip("\n")
    for line in text.splitlines():
        assert pdfmetrics.stringWidth(line, "Mono", 7.7) < 488, ("Long code line", line)
    t = Table([[Preformatted(text, styles["code"])]], colWidths=[516])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    current.extend([t, Spacer(1, 10)])


def note(title, text):
    t = Table([[Paragraph("<b>" + title + "</b><br/>" + text, styles["note"])]], colWidths=[516])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E8F4F2")),
                ("LINEBEFORE", (0, 0), (0, -1), 3, TEAL),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    current.extend([t, Spacer(1, 10)])


def table(headers, rows, widths=None):
    data = [[Paragraph(escape(x), styles["th"]) for x in headers]]
    data += [[Paragraph(x, styles["cell"]) for x in row] for row in rows]
    t = Table(
        data, colWidths=widths or [516 / len(headers)] * len(headers), repeatRows=1, hAlign="LEFT"
    )
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, -1), (-1, -1), 0.5, LINE),
            ]
        )
    )
    current.extend([t, Spacer(1, 10)])


renderers = {"p": p, "h": h, "small": small, "code": code, "note": note, "table": table}
for chapter in json.loads((HERE / "content.json").read_text(encoding="utf-8")):
    page(chapter["title"], chapter["subtitle"])
    for block in chapter["blocks"]:
        renderers[block["type"]](*block["args"])


class Manual(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if getattr(flowable, "anchor", None):
            self.canv.bookmarkPage(flowable.anchor)
            self.canv.addOutlineEntry(flowable.getPlainText(), flowable.anchor, 0, False)


def footer(c, doc):
    c.saveState()
    if doc.page > 1:
        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        c.line(48, 751, 564, 751)
        c.setFont("SansBold", 7.5)
        c.setFillColor(MUTED)
        c.drawString(48, 762, "AGENTIC DATA OPS  /  USER MANUAL")
        c.drawRightString(564, 762, "MVP 0.1.2")
        c.line(48, 39, 564, 39)
        c.setFont("Sans", 7.4)
        c.drawString(48, 25, "Installation, assessment and continuous improvement")
        c.drawRightString(564, 25, f"{doc.page:02d}  /  {len(sections) + 2:02d}")
    else:
        c.setFillColor(NAVY)
        c.rect(0, 0, 612, 792, fill=1, stroke=0)
        c.setFillColor(TEAL)
        c.rect(0, 0, 18, 792, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor("#2D5368"))
        c.setLineWidth(1)
        for x in range(350, 610, 38):
            for y in range(95, 340, 38):
                c.circle(x, y, 2, fill=0, stroke=1)
        c.setFillColor(colors.HexColor("#92DAD7"))
        c.setFont("SansBold", 11)
        c.drawString(54, 714, "PRACTICAL OPERATING GUIDE")
        c.setFillColor(colors.white)
        c.setFont("SansBold", 38)
        c.drawString(54, 609, "Agentic Data Ops")
        c.setFont("Sans", 31)
        c.drawString(54, 561, "User manual")
        c.setFont("Sans", 12)
        c.setFillColor(colors.HexColor("#CCDCE5"))
        for i, line in enumerate(
            [
                "Install the capability. Understand the evidence.",
                "Resolve ambiguity. Reassess with confidence.",
            ]
        ):
            c.drawString(56, 510 - i * 21, line)
        c.setFillColor(colors.HexColor("#92DAD7"))
        c.setFont("SansBold", 9)
        c.drawString(56, 397, "DATA MATURITY AGENT 0.1.2")
        c.setFillColor(colors.white)
        c.setFont("Sans", 10)
        c.drawString(56, 371, "Comprehensive installation and usage reference")
        c.drawString(56, 351, "Prepared 19 September 2026")
        c.setFont("Sans", 8.5)
        c.setFillColor(colors.HexColor("#CCDCE5"))
        c.drawString(56, 93, "Local-first Python CLI  |  Excel, CSV and TSV")
        c.drawString(56, 75, "Includes worked examples, command reference and troubleshooting")
    c.restoreState()


story = [Spacer(1, 1), PageBreak()]
story.append(Paragraph("How to use this manual", styles["title"]))
story.append(
    Paragraph(
        "Start with installation and the synthetic quickstart. The middle chapters cover real assessments and the human feedback loop; the final chapters are the operating reference. Click a contents entry to jump to it.",
        styles["body"],
    )
)
toc = []
for i, (title, _sub, _content) in enumerate(sections):
    label = f"{i + 1:02d}  {title}"
    toc.append(
        [
            Paragraph(
                f'<link href="#s{i + 1}" color="#233A4A">{escape(label)}</link>', styles["small"]
            ),
            Paragraph(str(i + 3), styles["small"]),
        ]
    )
t = Table(toc, colWidths=[477, 39])
t.setStyle(
    TableStyle(
        [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 2.3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.3),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ]
    )
)
story.append(t)
story.append(Spacer(1, 9))
story.append(
    Paragraph(
        "Conventions: commands run from the repository root in an active virtual environment unless stated otherwise. Replace uppercase placeholders and use a new output folder for every run. Linux/macOS commands use a backslash for line continuation; Windows PowerShell uses a backtick.",
        styles["small"],
    )
)
for i, (title, subtitle, content) in enumerate(sections):
    story.append(PageBreak())
    story.append(Paragraph(f"CHAPTER {i + 1:02d}", styles["eyebrow"]))
    titleflow = Paragraph(title, styles["title"])
    titleflow.anchor = f"s{i + 1}"
    story.append(titleflow)
    story.append(Paragraph(subtitle, styles["small"]))
    story.append(Spacer(1, 8))
    while content and isinstance(content[-1], Spacer):
        content.pop()
    story.extend(content)
OUT.parent.mkdir(parents=True, exist_ok=True)
doc = Manual(
    str(OUT),
    pagesize=(612, 792),
    rightMargin=48,
    leftMargin=48,
    topMargin=61,
    bottomMargin=54,
    title="Agentic Data Ops - User Manual",
    author="Agentic Data Ops",
    subject="Installation and operating manual for Data Maturity Agent 0.1.2",
    invariant=1,
)
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
print("Expected pages:", len(sections) + 2)

# One page per chapter keeps the contents and footer page counts correct.

reader = PdfReader(OUT)
if len(reader.pages) != len(sections) + 2 or any(
    reader.get_destination_page_number(entry) != index + 2
    for index, entry in enumerate(reader.outline)
):
    raise ValueError("Manual overflow: shorten the affected chapter before publishing")
