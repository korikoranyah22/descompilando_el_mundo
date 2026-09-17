#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera un único HTML offline a partir de sections/manifest.json."""

from __future__ import annotations

import argparse
import base64
import html
import json
import re
from pathlib import Path

from md2epub_sugerido import md_to_xhtml, remove_first_heading


ROOT = Path(__file__).resolve().parent
DEFAULT_SECTIONS = ROOT / "sections"
DEFAULT_OUTPUT = ROOT / "Descompilando_el_mundo.html"
DEFAULT_COVER = ROOT / "cover.jpg"
DEFAULT_EPUB_HREF = "Descompilando_el_mundo.epub"
DEFAULT_PDF_HREF = "output/pdf/Descompilando_el_mundo.pdf"

PAGE_TEMPLATE = r'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="author" content="@@AUTHOR_ATTR@@">
  <meta name="description" content="Edición web de @@TITLE_ATTR@@">
  <title>@@TITLE@@</title>
  <style>
    :root {
      color-scheme: light;
      --paper: #f4efe6;
      --paper-deep: #e7dfd2;
      --ink: #251f1a;
      --muted: #6f655b;
      --accent: #a95f3a;
      --accent-dark: #70402b;
      --line: rgba(55, 44, 35, .18);
      --panel: rgba(249, 246, 239, .94);
      --sidebar: 20rem;
      --serif: Iowan Old Style, Baskerville, Georgia, Cambria, "Times New Roman", serif;
      --sans: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body { margin: 0; color: var(--ink); background: var(--paper); font-family: var(--serif); line-height: 1.72; }
    body::before { content: ""; position: fixed; inset: 0; pointer-events: none; opacity: .24; background-image: radial-gradient(#6b5947 0.45px, transparent 0.55px); background-size: 5px 5px; }
    a { color: var(--accent-dark); text-decoration-color: rgba(112,64,43,.38); text-underline-offset: .16em; }
    a:hover { color: var(--accent); text-decoration-color: currentColor; }
    #progress { position: fixed; z-index: 50; inset: 0 auto auto 0; width: 0; height: 3px; background: var(--accent); }
    .sidebar { position: fixed; z-index: 20; inset: 0 auto 0 0; width: var(--sidebar); padding: 1.35rem 1rem 2rem; overflow-y: auto; background: var(--panel); border-right: 1px solid var(--line); backdrop-filter: blur(12px); }
    .brand { display: block; padding: .35rem .5rem 1rem; color: var(--ink); font-family: var(--sans); font-size: .78rem; font-weight: 760; letter-spacing: .12em; line-height: 1.35; text-decoration: none; text-transform: uppercase; }
    .search { width: 100%; margin: 0 0 1rem; padding: .7rem .8rem; color: var(--ink); background: rgba(255,255,255,.55); border: 1px solid var(--line); border-radius: .35rem; font: .9rem var(--sans); outline: none; }
    .search:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(169,95,58,.12); }
    .toc { margin: 0; padding: 0; list-style: none; font-family: var(--sans); }
    .toc li { margin: 0; }
    .toc a { display: block; padding: .42rem .55rem; border-radius: .25rem; color: var(--muted); font-size: .81rem; line-height: 1.32; text-decoration: none; }
    .toc a:hover { color: var(--ink); background: rgba(169,95,58,.09); }
    .toc li.part { margin-top: .72rem; border-top: 1px solid var(--line); padding-top: .62rem; }
    .toc li.part a { color: var(--accent-dark); font-size: .72rem; font-weight: 800; letter-spacing: .055em; text-transform: uppercase; }
    .toc li.interlude a, .toc li.epilogue a { padding-left: 1rem; font-style: italic; }
    .layout { margin-left: var(--sidebar); }
    .hero { min-height: 92vh; display: grid; grid-template-columns: minmax(18rem, 34rem) minmax(20rem, 36rem); place-content: center; gap: clamp(2rem, 7vw, 7rem); padding: 6rem clamp(2rem, 7vw, 8rem); color: #f7f0e7; background: radial-gradient(circle at 65% 35%, #263039 0, #101419 45%, #080a0c 100%); }
    .hero-cover { width: min(100%, 31rem); max-height: 78vh; object-fit: contain; box-shadow: 0 2rem 6rem rgba(0,0,0,.55); }
    .hero-copy { align-self: center; }
    .eyebrow { color: #d9a27d; font: 700 .75rem/1.3 var(--sans); letter-spacing: .18em; text-transform: uppercase; }
    .hero h1 { margin: .6rem 0 1.2rem; font-size: clamp(3.2rem, 7vw, 7rem); font-weight: 500; letter-spacing: -.045em; line-height: .91; }
    .hero .author { margin-top: 2.2rem; color: #d8cec2; font: 500 1rem/1.5 var(--sans); letter-spacing: .05em; }
    .downloads { display: flex; flex-wrap: wrap; gap: .7rem; margin-top: 2rem; }
    .download { display: inline-flex; align-items: center; justify-content: center; min-width: 10.5rem; padding: .82rem 1rem; border: 1px solid rgba(247,240,231,.42); border-radius: 999px; color: #f7f0e7; background: rgba(247,240,231,.08); font: 750 .78rem/1 var(--sans); letter-spacing: .06em; text-decoration: none; text-transform: uppercase; transition: transform .18s ease, background .18s ease, border-color .18s ease; }
    .download:hover { color: #101419; background: #f7f0e7; border-color: #f7f0e7; transform: translateY(-2px); }
    .download:focus-visible { outline: 3px solid #d9a27d; outline-offset: 3px; }
    main { width: min(100% - 3rem, 51rem); margin: 0 auto; padding: 6rem 0 10rem; }
    .book-section { scroll-margin-top: 2rem; padding: 2.5rem 0 5rem; border-bottom: 1px solid var(--line); }
    .book-section > h2 { margin: 0 0 2.4rem; font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 520; letter-spacing: -.025em; line-height: 1.08; }
    .book-section h3 { margin: 2.8rem 0 1rem; color: #4c362a; font-size: 1.5rem; line-height: 1.25; }
    .book-section h4 { margin: 2.2rem 0 .7rem; font-size: 1.15rem; }
    .book-section p { margin: 1rem 0; }
    .book-section blockquote { margin: 1.7rem 0; padding: .2rem 0 .2rem 1.4rem; border-left: 3px solid var(--accent); color: #4e443b; font-size: 1.08em; }
    .book-section hr { width: 5rem; margin: 3rem auto; border: 0; border-top: 1px solid var(--accent); }
    .book-section li { margin: .38rem 0; }
    .book-section img { max-width: 100%; height: auto; }
    .book-section table { display: block; width: 100%; margin: 1.6rem 0; overflow-x: auto; border-collapse: collapse; font-family: var(--sans); font-size: .82rem; line-height: 1.45; }
    .book-section th, .book-section td { min-width: 9rem; padding: .65rem .7rem; border: 1px solid var(--line); text-align: left; vertical-align: top; }
    .book-section th { background: var(--paper-deep); }
    .book-section code { font: .88em ui-monospace, "Cascadia Mono", Consolas, monospace; }
    .book-section.part { min-height: 72vh; display: grid; place-content: center; border: 0; text-align: center; }
    .book-section.part > h2 { max-width: 13em; margin: 0; color: var(--accent-dark); font-size: clamp(2.8rem, 7vw, 5.5rem); }
    .book-section.interlude { color: #3f3832; }
    .book-section.interlude > h2 { font-style: italic; }
    .top { position: fixed; right: 1.2rem; bottom: 1.2rem; width: 2.7rem; height: 2.7rem; display: grid; place-items: center; border: 1px solid var(--line); border-radius: 50%; color: var(--ink); background: var(--panel); font: 1.1rem var(--sans); text-decoration: none; box-shadow: 0 .4rem 1.5rem rgba(38,29,23,.12); }
    .menu { display: none; }
    @media (max-width: 900px) {
      .sidebar { transform: translateX(-102%); transition: transform .25s ease; box-shadow: .5rem 0 2rem rgba(0,0,0,.18); }
      body.menu-open .sidebar { transform: translateX(0); }
      .layout { margin-left: 0; }
      .menu { position: fixed; z-index: 30; top: .8rem; left: .8rem; display: grid; place-items: center; width: 2.8rem; height: 2.8rem; border: 1px solid var(--line); border-radius: 50%; color: var(--ink); background: var(--panel); font-size: 1.2rem; cursor: pointer; }
      .hero { min-height: auto; grid-template-columns: 1fr; padding: 5.5rem 1.5rem 4rem; }
      .hero-cover { width: min(100%, 24rem); margin: auto; }
      .hero-copy { text-align: center; }
      .downloads { justify-content: center; }
      main { width: min(100% - 2rem, 48rem); padding-top: 3rem; }
    }
    @media print {
      .sidebar, .menu, .top, #progress, .downloads { display: none; }
      .layout { margin: 0; }
      .hero { min-height: auto; display: block; padding: 2rem; color: #000; background: #fff; text-align: center; }
      .hero-cover { max-height: 70vh; box-shadow: none; }
      main { width: 100%; padding: 0; }
      .book-section { break-before: page; border: 0; }
      a { color: inherit; }
    }
  </style>
</head>
<body id="inicio">
  <div id="progress" aria-hidden="true"></div>
  <button class="menu" type="button" aria-label="Abrir índice" aria-controls="sidebar">☰</button>
  <aside class="sidebar" id="sidebar">
    <a class="brand" href="#inicio">@@TITLE@@</a>
    <input class="search" id="toc-search" type="search" placeholder="Filtrar índice…" aria-label="Filtrar índice">
    <nav aria-label="Índice del libro"><ol class="toc">@@NAV@@</ol></nav>
  </aside>
  <div class="layout">
    <header class="hero">
      @@COVER@@
      <div class="hero-copy">
        <div class="eyebrow">Edición web</div>
        <h1>@@TITLE@@</h1>
        <div class="author">@@AUTHOR@@</div>
        <div class="downloads" aria-label="Descargas del libro">
          <a class="download" href="@@EPUB_HREF@@" download>Descargar EPUB</a>
          <a class="download" href="@@PDF_HREF@@" download>Descargar PDF</a>
        </div>
      </div>
    </header>
    <main>@@SECTIONS@@</main>
  </div>
  <a class="top" href="#inicio" aria-label="Volver arriba">↑</a>
  <script>
    const body = document.body;
    const menu = document.querySelector('.menu');
    menu.addEventListener('click', () => body.classList.toggle('menu-open'));
    document.querySelectorAll('.toc a').forEach(a => a.addEventListener('click', () => body.classList.remove('menu-open')));
    const search = document.getElementById('toc-search');
    search.addEventListener('input', () => {
      const query = search.value.toLocaleLowerCase('es').trim();
      document.querySelectorAll('.toc li').forEach(item => {
        item.hidden = query && !item.dataset.search.includes(query);
      });
    });
    const progress = document.getElementById('progress');
    const updateProgress = () => {
      const available = document.documentElement.scrollHeight - innerHeight;
      progress.style.width = (available > 0 ? scrollY / available * 100 : 0) + '%';
    };
    addEventListener('scroll', updateProgress, { passive: true });
    updateProgress();
  </script>
</body>
</html>
'''


def cover_data_uri(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    media_types = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
    media_type = media_types.get(path.suffix.lower())
    if media_type is None:
        raise SystemExit("La portada web debe ser JPG, PNG o WEBP.")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<img class="hero-cover" src="data:{media_type};base64,{encoded}" alt="Portada de la obra">'


def webify_fragment(fragment: str, position: int) -> str:
    prefix = f"sec-{position:03d}"
    fragment = re.sub(
        r'\bid="([^"]+)"',
        lambda match: f'id="{prefix}-{match.group(1)}"',
        fragment,
    )
    fragment = re.sub(
        r'href="#([^"]+)"',
        lambda match: f'href="#{prefix}-{match.group(1)}"',
        fragment,
    )

    def cross_link(match: re.Match) -> str:
        target = f"sec-{match.group(1)}"
        if match.group(2):
            target += f"-{match.group(2)}"
        return f'href="#{target}"'

    return re.sub(r'href="sec_(\d{3})\.xhtml(?:#([^"]+))?"', cross_link, fragment)


def build_web(
    sections_dir: Path,
    output_file: Path,
    title: str,
    author: str,
    cover_path: Path | None = None,
    epub_href: str = DEFAULT_EPUB_HREF,
    pdf_href: str = DEFAULT_PDF_HREF,
) -> Path:
    manifest_path = sections_dir / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"No se encontró {manifest_path}; ejecutá primero split_md.py.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("order", [])
    if not entries:
        raise SystemExit("El manifest no contiene secciones.")

    nav_items: list[str] = []
    rendered_sections: list[str] = []
    for position, entry in enumerate(entries, start=1):
        source = sections_dir / entry["file"]
        if not source.exists():
            raise SystemExit(f"Falta una sección declarada en el manifest: {source.name}")
        section_id = f"sec-{position:03d}"
        section_title = entry["title"]
        kind = entry.get("kind", "chapter")
        search_value = html.escape(section_title.lower(), quote=True)
        nav_items.append(
            f'<li class="{html.escape(kind)}" data-search="{search_value}">'
            f'<a href="#{section_id}">{html.escape(section_title)}</a></li>'
        )

        raw = source.read_text(encoding="utf-8")
        body = webify_fragment(md_to_xhtml(remove_first_heading(raw)), position)
        rendered_sections.append(
            f'<section class="book-section {html.escape(kind)}" id="{section_id}">'
            f'<h2>{html.escape(section_title)}</h2>{body}</section>'
        )

    page = PAGE_TEMPLATE
    replacements = {
        "@@TITLE@@": html.escape(title),
        "@@TITLE_ATTR@@": html.escape(title, quote=True),
        "@@AUTHOR@@": html.escape(author),
        "@@AUTHOR_ATTR@@": html.escape(author, quote=True),
        "@@NAV@@": "\n".join(nav_items),
        "@@SECTIONS@@": "\n".join(rendered_sections),
        "@@COVER@@": cover_data_uri(cover_path),
        "@@EPUB_HREF@@": html.escape(epub_href, quote=True),
        "@@PDF_HREF@@": html.escape(pdf_href, quote=True),
    }
    for marker, value in replacements.items():
        page = page.replace(marker, value)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(page, encoding="utf-8", newline="\n")
    print(f"[OK] Web creada: {output_file.name} ({output_file.stat().st_size // 1024} KB)")
    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sections", type=Path, default=DEFAULT_SECTIONS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--title", default="Descompilando el mundo")
    parser.add_argument("--author", default="Miyu Rory Schrank y Vera")
    parser.add_argument("--cover", type=Path, default=DEFAULT_COVER)
    parser.add_argument("--epub-href", default=DEFAULT_EPUB_HREF)
    parser.add_argument("--pdf-href", default=DEFAULT_PDF_HREF)
    args = parser.parse_args()
    build_web(
        args.sections.resolve(),
        args.out.resolve(),
        args.title,
        args.author,
        args.cover.resolve() if args.cover else None,
        args.epub_href,
        args.pdf_href,
    )


if __name__ == "__main__":
    main()
