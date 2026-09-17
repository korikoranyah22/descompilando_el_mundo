#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pipeline completo de «Descompilando el mundo»: Markdown a EPUB y web."""

from __future__ import annotations

import argparse
import os
import posixpath
import re
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

from build_index_links import add_index_links
from build_pdf import build_pdf
from build_web import build_web
from md2epub_sugerido import build_epub
from normalize_md import normalize_file
from split_md import split_document


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "Lo_que_continua_indice.md"
DEFAULT_NORMALIZED = ROOT / "Lo_que_continua_indice.normalized.md"
DEFAULT_SECTIONS = ROOT / "sections"
DEFAULT_COVER = ROOT / "cover.jpg"
DEFAULT_EPUB = ROOT / "Descompilando_el_mundo.epub"
DEFAULT_PDF = ROOT / "output" / "pdf" / "Descompilando_el_mundo.pdf"
DEFAULT_HTML = ROOT / "Descompilando_el_mundo.html"
DEFAULT_AUTHOR = "Miyu Rory Schrank y Vera"


def manuscript_title(source: Path) -> str:
    text = source.read_text(encoding="utf-8-sig")
    match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    if not match:
        raise SystemExit("No se encontró un título H1 en el manuscrito.")
    return match.group(1).strip()


def validate_epub(epub_path: Path, expected_sections: int) -> None:
    with zipfile.ZipFile(epub_path) as archive:
        names = archive.namelist()
        name_set = set(names)
        if not names or names[0] != "mimetype":
            raise SystemExit("EPUB inválido: 'mimetype' no es la primera entrada.")
        mimetype = archive.getinfo("mimetype")
        if mimetype.compress_type != zipfile.ZIP_STORED:
            raise SystemExit("EPUB inválido: 'mimetype' debe guardarse sin compresión.")
        if archive.read("mimetype") != b"application/epub+zip":
            raise SystemExit("EPUB inválido: contenido de 'mimetype' incorrecto.")
        if archive.testzip() is not None:
            raise SystemExit("EPUB inválido: el ZIP contiene datos corruptos.")

        chapter_names = [name for name in names if re.fullmatch(r"OEBPS/sec_\d{3}\.xhtml", name)]
        if len(chapter_names) != expected_sections:
            raise SystemExit(
                f"EPUB incompleto: se esperaban {expected_sections} secciones y hay {len(chapter_names)}."
            )
        documents: dict[str, ElementTree.Element] = {}
        xml_names = tuple(
            name for name in names if name.endswith((".xml", ".opf", ".xhtml"))
        )
        for name in xml_names:
            documents[name] = ElementTree.fromstring(archive.read(name))

        ids_by_document = {
            name: {element.attrib["id"] for element in root.iter() if "id" in element.attrib}
            for name, root in documents.items()
        }
        for name, root in documents.items():
            if not name.endswith(".xhtml"):
                continue
            for element in root.iter():
                href = element.attrib.get("href")
                if not href:
                    continue
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc:
                    continue
                target_name = name
                if parsed.path:
                    target_name = posixpath.normpath(
                        posixpath.join(posixpath.dirname(name), unquote(parsed.path))
                    )
                    if target_name not in name_set:
                        raise SystemExit(f"EPUB inválido: {name} enlaza un recurso inexistente: {href}")
                if parsed.fragment and parsed.fragment not in ids_by_document.get(target_name, set()):
                    raise SystemExit(f"EPUB inválido: {name} enlaza un ancla inexistente: {href}")


def validate_web(
    html_path: Path,
    expected_sections: int,
    epub_path: Path,
    pdf_path: Path,
    epub_href: str,
    pdf_href: str,
) -> None:
    page = html_path.read_text(encoding="utf-8")
    found = len(re.findall(r'<section class="book-section [^"]+" id="sec-\d{3}">', page))
    if found != expected_sections:
        raise SystemExit(f"Web incompleta: se esperaban {expected_sections} secciones y hay {found}.")
    if re.search(r'href="sec_\d{3}\.xhtml', page):
        raise SystemExit("Web inválida: quedaron enlaces internos con formato EPUB.")
    identifiers = set(re.findall(r'\bid="([^"]+)"', page))
    internal_targets = set(re.findall(r'href="#([^"]+)"', page))
    missing_targets = sorted(internal_targets - identifiers)
    if missing_targets:
        raise SystemExit(f"Web inválida: hay anclas sin destino: {', '.join(missing_targets[:5])}")
    for label, artifact_path, href in (
        ("EPUB", epub_path, epub_href),
        ("PDF", pdf_path, pdf_href),
    ):
        if not artifact_path.exists():
            raise SystemExit(f"Web inválida: no existe el archivo descargable {label}: {artifact_path}")
        expected_link = f'href="{href}" download'
        if expected_link not in page:
            raise SystemExit(f"Web inválida: falta el botón de descarga {label}.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Manuscrito Markdown de entrada")
    parser.add_argument("--author", default=DEFAULT_AUTHOR, help="Autoría para los metadatos")
    parser.add_argument("--title", default=None, help="Título; por defecto se toma del primer H1")
    parser.add_argument("--cover", type=Path, default=DEFAULT_COVER, help="Portada JPG/PNG/WEBP")
    parser.add_argument("--epub-out", type=Path, default=DEFAULT_EPUB)
    parser.add_argument("--pdf-out", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--html-out", type=Path, default=DEFAULT_HTML)
    args = parser.parse_args()

    source = args.source.resolve()
    title = args.title or manuscript_title(source)
    cover = args.cover.resolve() if args.cover else None
    if cover is not None and not cover.exists():
        raise SystemExit(f"No se encontró la portada: {cover}")

    epub_out = args.epub_out.resolve()
    pdf_out = args.pdf_out.resolve()
    html_out = args.html_out.resolve()
    try:
        epub_href = os.path.relpath(epub_out, html_out.parent).replace(os.sep, "/")
        pdf_href = os.path.relpath(pdf_out, html_out.parent).replace(os.sep, "/")
    except ValueError as exc:
        raise SystemExit("El EPUB, el PDF y el HTML deben estar en la misma unidad de disco.") from exc

    print("[1/7] Normalizando el manuscrito")
    normalize_file(source, DEFAULT_NORMALIZED)

    print("[2/7] Separando unidades de lectura")
    manifest = split_document(DEFAULT_NORMALIZED, DEFAULT_SECTIONS)

    print("[3/7] Enlazando el índice")
    add_index_links(DEFAULT_SECTIONS)

    print("[4/7] Generando el EPUB")
    build_epub(
        sections_dir=DEFAULT_SECTIONS,
        title=title,
        author=args.author,
        lang="es",
        out_file=epub_out,
        cover_path=cover,
        uuid=None,
    )

    print("[5/7] Generando el PDF")
    build_pdf(
        sections_dir=DEFAULT_SECTIONS,
        output_file=pdf_out,
        title=title,
        author=args.author,
        cover_path=cover,
    )

    print("[6/7] Generando la edición web")
    build_web(
        sections_dir=DEFAULT_SECTIONS,
        output_file=html_out,
        title=title,
        author=args.author,
        cover_path=cover,
        epub_href=epub_href,
        pdf_href=pdf_href,
    )

    print("[7/7] Verificando los artefactos")
    expected = manifest["section_count"]
    validate_epub(epub_out, expected)
    validate_web(html_out, expected, epub_out, pdf_out, epub_href, pdf_href)

    epub_kb = epub_out.stat().st_size // 1024
    pdf_kb = pdf_out.stat().st_size // 1024
    html_kb = html_out.stat().st_size // 1024
    print(
        f"[OK] Pipeline completo: {epub_out.name} ({epub_kb} KB) + "
        f"{pdf_out.name} ({pdf_kb} KB) + {html_out.name} ({html_kb} KB)"
    )


if __name__ == "__main__":
    main()
