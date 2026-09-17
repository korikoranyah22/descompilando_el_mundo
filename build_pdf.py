#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera la edición PDF de «Descompilando el mundo»."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

try:
    from pypdf import PdfReader
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        BaseDocTemplate,
        Flowable,
        Frame,
        HRFlowable,
        KeepTogether,
        LongTable,
        PageBreak,
        PageTemplate,
        Paragraph,
        Spacer,
        TableStyle,
    )
    from reportlab.lib.utils import ImageReader
except ImportError as exc:  # pragma: no cover - mensaje para instalación local
    raise SystemExit("Faltan dependencias PDF. Ejecutá: python -m pip install -r requirements.txt") from exc


ROOT = Path(__file__).resolve().parent
DEFAULT_SECTIONS = ROOT / "sections"
DEFAULT_OUTPUT = ROOT / "output" / "pdf" / "Descompilando_el_mundo.pdf"
DEFAULT_COVER = ROOT / "cover.jpg"

INK = colors.HexColor("#251F1A")
MUTED = colors.HexColor("#6F655B")
ACCENT = colors.HexColor("#A95F3A")
ACCENT_DARK = colors.HexColor("#70402B")
PAPER_DEEP = colors.HexColor("#E7DFD2")
LINE = colors.HexColor("#CFC2B4")


def register_fonts() -> tuple[str, str, str, str]:
    candidates = [
        (
            Path("C:/Windows/Fonts/georgia.ttf"),
            Path("C:/Windows/Fonts/georgiab.ttf"),
            Path("C:/Windows/Fonts/georgiai.ttf"),
            Path("C:/Windows/Fonts/georgiaz.ttf"),
        ),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf"),
        ),
    ]
    for regular, bold, italic, bold_italic in candidates:
        if all(path.exists() for path in (regular, bold, italic, bold_italic)):
            pdfmetrics.registerFont(TTFont("BookSerif", str(regular)))
            pdfmetrics.registerFont(TTFont("BookSerif-Bold", str(bold)))
            pdfmetrics.registerFont(TTFont("BookSerif-Italic", str(italic)))
            pdfmetrics.registerFont(TTFont("BookSerif-BoldItalic", str(bold_italic)))
            pdfmetrics.registerFontFamily(
                "BookSerif",
                normal="BookSerif",
                bold="BookSerif-Bold",
                italic="BookSerif-Italic",
                boldItalic="BookSerif-BoldItalic",
            )
            return "BookSerif", "BookSerif-Bold", "BookSerif-Italic", "BookSerif-BoldItalic"
    return "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic"


REGULAR_FONT, BOLD_FONT, ITALIC_FONT, BOLD_ITALIC_FONT = register_fonts()


def make_styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "body": ParagraphStyle(
            "BookBody",
            parent=sample["BodyText"],
            fontName=REGULAR_FONT,
            fontSize=10.6,
            leading=16.2,
            textColor=INK,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            allowWidows=0,
            allowOrphans=0,
        ),
        "quote": ParagraphStyle(
            "BookQuote",
            parent=sample["BodyText"],
            fontName=ITALIC_FONT,
            fontSize=10.2,
            leading=15.5,
            textColor=colors.HexColor("#4E443B"),
            leftIndent=13,
            rightIndent=8,
            borderColor=ACCENT,
            borderWidth=0,
            borderPadding=(2, 0, 2, 10),
            spaceBefore=7,
            spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "SectionTitle",
            parent=sample["Heading1"],
            fontName=REGULAR_FONT,
            fontSize=24,
            leading=28,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=22,
            keepWithNext=1,
        ),
        "part": ParagraphStyle(
            "PartTitle",
            parent=sample["Heading1"],
            fontName=REGULAR_FONT,
            fontSize=32,
            leading=37,
            textColor=ACCENT_DARK,
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "h3": ParagraphStyle(
            "Heading3",
            parent=sample["Heading2"],
            fontName=BOLD_FONT,
            fontSize=15.5,
            leading=19,
            textColor=colors.HexColor("#4C362A"),
            spaceBefore=18,
            spaceAfter=8,
            keepWithNext=1,
        ),
        "h4": ParagraphStyle(
            "Heading4",
            parent=sample["Heading3"],
            fontName=BOLD_FONT,
            fontSize=12,
            leading=15,
            textColor=INK,
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=1,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=sample["BodyText"],
            fontName=REGULAR_FONT,
            fontSize=10.2,
            leading=15,
            leftIndent=17,
            firstLineIndent=-9,
            textColor=INK,
            spaceAfter=4,
        ),
        "number": ParagraphStyle(
            "Number",
            parent=sample["BodyText"],
            fontName=REGULAR_FONT,
            fontSize=10.2,
            leading=15,
            leftIndent=19,
            firstLineIndent=-12,
            textColor=INK,
            spaceAfter=4,
        ),
        "table": ParagraphStyle(
            "TableCell",
            parent=sample["BodyText"],
            fontName=REGULAR_FONT,
            fontSize=7.2,
            leading=9.1,
            textColor=INK,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=sample["BodyText"],
            fontName=BOLD_FONT,
            fontSize=7.3,
            leading=9.2,
            textColor=INK,
        ),
        "title": ParagraphStyle(
            "BookTitle",
            parent=sample["Title"],
            fontName=REGULAR_FONT,
            fontSize=38,
            leading=43,
            textColor=INK,
            alignment=TA_CENTER,
            spaceAfter=22,
        ),
        "subtitle": ParagraphStyle(
            "BookSubtitle",
            parent=sample["BodyText"],
            fontName=ITALIC_FONT,
            fontSize=13,
            leading=18,
            textColor=MUTED,
            alignment=TA_CENTER,
            leftIndent=25 * mm,
            rightIndent=25 * mm,
            spaceAfter=24,
        ),
        "author": ParagraphStyle(
            "BookAuthor",
            parent=sample["BodyText"],
            fontName=REGULAR_FONT,
            fontSize=12,
            leading=16,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }


STYLES = make_styles()


class FullPageCover(Flowable):
    def __init__(self, image_path: Path, page_size: tuple[float, float]):
        super().__init__()
        self.image_path = image_path
        self.page_width, self.page_height = page_size

    def wrap(self, avail_width: float, avail_height: float) -> tuple[float, float]:
        self.width = avail_width
        self.height = avail_height
        return avail_width, avail_height

    def draw(self) -> None:
        reader = ImageReader(str(self.image_path))
        image_width, image_height = reader.getSize()
        scale = min(self.page_width / image_width, self.page_height / image_height)
        draw_width = image_width * scale
        draw_height = image_height * scale
        x = -self._doctemplate.leftMargin + (self.page_width - draw_width) / 2
        y = -self._doctemplate.bottomMargin + (self.page_height - draw_height) / 2
        self.canv.setFillColor(colors.HexColor("#080A0C"))
        self.canv.rect(
            -self._doctemplate.leftMargin,
            -self._doctemplate.bottomMargin,
            self.page_width,
            self.page_height,
            stroke=0,
            fill=1,
        )
        self.canv.drawImage(reader, x, y, width=draw_width, height=draw_height, mask="auto")


class BookDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, *, title: str, author: str, cover_path: Path | None):
        self.book_title = title
        self.book_author = author
        self.cover_path = cover_path
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=24 * mm,
            rightMargin=22 * mm,
            topMargin=22 * mm,
            bottomMargin=22 * mm,
            title=title,
            author=author,
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="book-frame",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(PageTemplate(id="book", frames=[frame], onPage=self._draw_page))

    def _draw_page(self, canvas, doc) -> None:
        canvas.setTitle(self.book_title)
        canvas.setAuthor(self.book_author)
        canvas.setSubject("Edición PDF de Descompilando el mundo")
        if canvas.getPageNumber() <= 2:
            return
        visible_page = canvas.getPageNumber() - 2
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.45)
        canvas.line(self.leftMargin, 15 * mm, A4[0] - self.rightMargin, 15 * mm)
        canvas.setFillColor(MUTED)
        canvas.setFont(REGULAR_FONT, 8)
        canvas.drawString(self.leftMargin, 10.5 * mm, self.book_title)
        canvas.drawRightString(A4[0] - self.rightMargin, 10.5 * mm, str(visible_page))
        canvas.restoreState()

    def afterFlowable(self, flowable: Flowable) -> None:
        bookmark = getattr(flowable, "bookmark_name", None)
        if not bookmark:
            return
        title = getattr(flowable, "bookmark_title", bookmark)
        level = getattr(flowable, "bookmark_level", 0)
        self.canv.bookmarkPage(bookmark)
        self.canv.addOutlineEntry(title, bookmark, level=level, closed=level == 0)


def section_destination(href: str) -> str:
    match = re.fullmatch(r"sec_(\d{3})\.xhtml(?:#.*)?", href)
    return f"#sec_{match.group(1)}" if match else href


def inline_markup(text: str) -> str:
    text = html.escape(text.strip(), quote=True)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"(?<!_)_([^_]+?)_(?!_)", r"<i>\1</i>", text)

    def link(match: re.Match) -> str:
        label, href = match.group(1), html.unescape(match.group(2))
        destination = html.escape(section_destination(href), quote=True)
        return f'<a href="{destination}" color="#70402B"><u>{label}</u></a>'

    return re.sub(r"\[([^]]+)]\(([^)]+)\)", link, text)


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def table_flowable(rows: list[list[str]], available_width: float) -> LongTable:
    column_count = max(len(row) for row in rows)
    normalized = [row + [""] * (column_count - len(row)) for row in rows]
    data = []
    for row_index, row in enumerate(normalized):
        style = STYLES["table_header"] if row_index == 0 else STYLES["table"]
        data.append([Paragraph(inline_markup(cell), style) for cell in row])
    table = LongTable(
        data,
        colWidths=[available_width / column_count] * column_count,
        repeatRows=1,
        splitByRow=1,
        splitInRow=1,
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PAPER_DEEP),
                ("TEXTCOLOR", (0, 0), (-1, -1), INK),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def markdown_flowables(markdown_text: str, available_width: float) -> list[Flowable]:
    lines = markdown_text.splitlines()
    flowables: list[Flowable] = []
    index = 0

    def paragraph_from(block: list[str], style: ParagraphStyle) -> None:
        joined = " ".join(part.strip() for part in block if part.strip())
        if joined:
            flowables.append(Paragraph(inline_markup(joined), style))

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", stripped)
        if heading:
            level = len(heading.group(1))
            style = STYLES["h3"] if level <= 3 else STYLES["h4"]
            flowables.append(Paragraph(inline_markup(heading.group(2)), style))
            index += 1
            continue

        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", stripped):
            flowables.append(HRFlowable(width="30%", thickness=0.7, color=ACCENT, spaceBefore=14, spaceAfter=18))
            index += 1
            continue

        if stripped.startswith(">"): 
            quote_lines = []
            while index < len(lines) and (lines[index].strip().startswith(">") or not lines[index].strip()):
                current = lines[index].strip()
                if current.startswith(">"):
                    quote_lines.append(current[1:].strip())
                index += 1
            paragraph_from(quote_lines, STYLES["quote"])
            continue

        if "|" in stripped and index + 1 < len(lines) and is_table_separator(lines[index + 1]):
            rows = [[cell.strip() for cell in stripped.strip("|").split("|")]]
            index += 2
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
                index += 1
            flowables.append(Spacer(1, 5))
            flowables.append(table_flowable(rows, available_width))
            flowables.append(Spacer(1, 9))
            continue

        bullet = re.match(r"^\s*[-+*]\s+(.+)$", line)
        if bullet:
            flowables.append(Paragraph(f"•&nbsp;&nbsp;{inline_markup(bullet.group(1))}", STYLES["bullet"]))
            index += 1
            continue

        numbered = re.match(r"^\s*(\d+)\.\s+(.+)$", line)
        if numbered:
            flowables.append(
                Paragraph(f"{numbered.group(1)}.&nbsp;&nbsp;{inline_markup(numbered.group(2))}", STYLES["number"])
            )
            index += 1
            continue

        block = [line]
        index += 1
        while index < len(lines) and lines[index].strip():
            candidate = lines[index]
            if re.match(r"^(#{1,6})\s+", candidate.strip()):
                break
            if re.match(r"^\s*([-+*]\s+|\d+\.\s+|>)", candidate):
                break
            if "|" in candidate and index + 1 < len(lines) and is_table_separator(lines[index + 1]):
                break
            block.append(candidate)
            index += 1
        paragraph_from(block, STYLES["body"])

    return flowables


def outline_level(kind: str) -> int:
    if kind in {"index", "frontmatter", "part"}:
        return 0
    if kind in {"chapter", "epilogue", "appendix"}:
        return 1
    return 2


def build_pdf(
    sections_dir: Path,
    output_file: Path,
    title: str,
    author: str,
    cover_path: Path | None = None,
) -> Path:
    manifest_path = sections_dir / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"No se encontró {manifest_path}; ejecutá primero split_md.py.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("order", [])
    if not entries:
        raise SystemExit("El manifest no contiene secciones.")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    document = BookDocTemplate(
        str(output_file),
        title=title,
        author=author,
        cover_path=cover_path,
    )
    story: list[Flowable] = []

    if cover_path is not None and cover_path.exists():
        cover = FullPageCover(cover_path, A4)
        story.extend([cover, PageBreak()])

    story.extend(
        [
            Spacer(1, 48 * mm),
            Paragraph(html.escape(title), STYLES["title"]),
            Paragraph(
                "Cosmogonía íntima, ensayo, ficción política y diálogo con una voz artificial",
                STYLES["subtitle"],
            ),
            Paragraph(html.escape(author), STYLES["author"]),
            PageBreak(),
        ]
    )

    for position, entry in enumerate(entries, start=1):
        if position > 1:
            story.append(PageBreak())
        kind = entry.get("kind", "chapter")
        if kind == "part":
            story.append(Spacer(1, 72 * mm))
            title_style = STYLES["part"]
        else:
            title_style = STYLES["h2"]

        title_flowable = Paragraph(inline_markup(entry["title"]), title_style)
        title_flowable.bookmark_name = f"sec_{position:03d}"
        title_flowable.bookmark_title = entry["title"]
        title_flowable.bookmark_level = outline_level(kind)
        story.append(title_flowable)

        source = sections_dir / entry["file"]
        raw = source.read_text(encoding="utf-8")
        raw = re.sub(r"^\s*#{1,6}\s+.+?\n+", "", raw, count=1)
        story.extend(markdown_flowables(raw, document.width))

    document.build(story)
    validate_pdf(output_file, title)
    print(f"[OK] PDF creado: {output_file} ({output_file.stat().st_size // 1024} KB)")
    return output_file


def validate_pdf(pdf_path: Path, expected_title: str) -> int:
    reader = PdfReader(str(pdf_path))
    if reader.is_encrypted:
        raise SystemExit("PDF inválido: el archivo quedó cifrado.")
    if len(reader.pages) < 100:
        raise SystemExit(f"PDF incompleto: sólo contiene {len(reader.pages)} páginas.")
    metadata_title = (reader.metadata.title or "").strip() if reader.metadata else ""
    if metadata_title != expected_title:
        raise SystemExit(f"PDF inválido: título de metadatos inesperado: {metadata_title!r}")
    title_page_text = reader.pages[1].extract_text() or ""
    if expected_title not in title_page_text:
        raise SystemExit("PDF inválido: la página de título no contiene el título de la obra.")
    return len(reader.pages)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sections", type=Path, default=DEFAULT_SECTIONS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--title", default="Descompilando el mundo")
    parser.add_argument("--author", default="Miyu Rory Schrank y Vera")
    parser.add_argument("--cover", type=Path, default=DEFAULT_COVER)
    args = parser.parse_args()
    build_pdf(
        args.sections.resolve(),
        args.out.resolve(),
        args.title,
        args.author,
        args.cover.resolve() if args.cover else None,
    )


if __name__ == "__main__":
    main()
