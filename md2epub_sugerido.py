#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye un EPUB 3 desde las secciones y el manifest del pipeline."""

import argparse
import json
import os
import re
import shutil
import uuid as uuidlib
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
import zipfile

try:
    import markdown as mdlib  # type: ignore
except Exception:
    mdlib = None


CSS = r'''
@page { margin: 2em; }
html, body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Ubuntu, Cantarell, "Noto Sans", "Helvetica Neue", Arial, sans-serif; line-height: 1.55; }
body { margin: 0; padding: 0 0 1rem 0; }
article { padding: 0 1rem; }
h1, h2, h3 { font-family: "Iowan Old Style", "Georgia", serif; }
h1 { font-size: 1.8rem; margin: 1.2rem 0 0.6rem; }
h2 { font-size: 1.4rem; margin: 1rem 0 0.5rem; }
h3 { font-size: 1.2rem; margin: 0.8rem 0 0.4rem; }
p { margin: 0.75rem 0; }
hr { border: none; border-top: 1px solid #ccc; margin: 1.2rem 0; }
.center { text-align: center; }
.small { font-size: .9rem; color: #666; }
blockquote { margin: 0.8rem 1rem; padding-left: .8rem; border-left: 3px solid #ddd; }
.subtitle { max-width: 28em; margin: 1rem auto; color: #555; font-style: italic; }
figure.cover { margin: 0; padding: 0; }
figure.cover img { width: 100%; height: auto; display:block; }
nav ol { list-style: none; padding-left: 0; }
a { color: #6b3e26; text-decoration-thickness: .08em; text-underline-offset: .12em; }
table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: .92rem; }
th, td { border: 1px solid #bbb; padding: .35rem .45rem; text-align: left; vertical-align: top; }
th { background: #eee; }
code { font-family: ui-monospace, "Cascadia Mono", Consolas, monospace; }
'''

NAV_TEMPLATE = """<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="{lang}" lang="{lang}">
<head>
  <meta charset="utf-8" />
  <title>Índice</title>
  <link rel="stylesheet" href="styles/stylesheet.css" />
</head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>Índice</h1>
    <ol>
      {items}
    </ol>
  </nav>
</body>
</html>
"""

CHAPTER_TEMPLATE = """<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{lang}" lang="{lang}">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <link rel="stylesheet" href="styles/stylesheet.css" />
</head>
<body>
  <article>
  {body}
  </article>
</body>
</html>
"""

TITLEPAGE_TEMPLATE = """<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{lang}" lang="{lang}">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <link rel="stylesheet" href="styles/stylesheet.css" />
</head>
<body>
  <article class="center">
    <h1>{title}</h1>
    <p class="subtitle">Cosmogonía íntima, ensayo, ficción política y diálogo con una voz artificial</p>
    <p class="small">{author}</p>
  </article>
</body>
</html>
"""

COVERPAGE_TEMPLATE = """<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{lang}" lang="{lang}">
<head>
  <meta charset="utf-8" />
  <title>Portada</title>
  <link rel="stylesheet" href="styles/stylesheet.css" />
</head>
<body>
  <figure class="cover">
    <img src="images/{cover_name}" alt="Portada"/>
  </figure>
</body>
</html>
"""

OPF_TEMPLATE = """<?xml version='1.0' encoding='utf-8'?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="3.0" xml:lang="{lang}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:identifier id="bookid">urn:uuid:{uuid}</dc:identifier>
    <dc:title>{title}</dc:title>
    <dc:language>{lang}</dc:language>
    <dc:creator id="creator">{author}</dc:creator>
    <meta property="dcterms:modified">{modified}</meta>
    {cover_meta}
  </metadata>
  <manifest>
    <item id="css" href="styles/stylesheet.css" media-type="text/css"/>
    {cover_xhtml_item}
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    {items}
    {cover_item}
  </manifest>
  <spine>
    {spine_prefix}
    <itemref idref="titlepage"/>
    {spine}
  </spine>
</package>
"""

CONTAINER_XML = """<?xml version='1.0' encoding='utf-8'?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""


def require_markdown():
    if mdlib is None:
        raise SystemExit("Falta el paquete 'markdown'. Instalá con: pip install markdown")


def md_to_xhtml(md_text: str) -> str:
    """Convierte Markdown a XHTML (fragmento) usando python-markdown."""
    require_markdown()
    return mdlib.markdown(
        md_text,
        # El manuscrito ya contiene comillas y rayas Unicode. Evitamos la
        # extensión "smarty" porque genera entidades HTML (&rsquo;, &hellip;)
        # que no están definidas en XML y vuelven inválido el XHTML del EPUB.
        extensions=['extra', 'sane_lists', 'toc'],
        extension_configs={'toc': {'marker': ''}},
        output_format='xhtml1',
    )


def remove_first_heading(md_text: str) -> str:
    """Quita el primer heading (#/##/###...) para evitar título duplicado."""
    return re.sub(r"^\s*#{1,6}\s+.+\n+", "", md_text, count=1)


def heading_fallback(md_text: str) -> str | None:
    m = re.search(r"^\s*#{1,6}\s+(.+?)\s*$", md_text, re.M)
    return m.group(1).strip() if m else None


def cover_media_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in ('.jpg', '.jpeg'):
        return 'image/jpeg'
    if ext == '.png':
        return 'image/png'
    if ext == '.webp':
        return 'image/webp'
    raise SystemExit("Portada no soportada: usa .png/.jpg/.jpeg/.webp")


def build_epub(sections_dir: Path, title: str, author: str, lang: str, out_file: Path, cover_path: Path | None, uuid: str | None):
    sections_dir = sections_dir.resolve()
    out_file = out_file.resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    if uuid is None:
        uuid = str(uuidlib.uuid4())

    manifest_path = sections_dir / 'manifest.json'
    if not manifest_path.exists():
        raise SystemExit(f"No se encontró manifest.json en {sections_dir}")
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    items = manifest.get('order', [])
    if not items:
        raise SystemExit("manifest.json no contiene 'order' o está vacío.")

    # Estructura temporal
    build = sections_dir.parent / (sections_dir.name + '_epub_build')
    if build.exists():
        shutil.rmtree(build)
    (build / 'META-INF').mkdir(parents=True)
    (build / 'OEBPS' / 'styles').mkdir(parents=True)
    (build / 'OEBPS' / 'images').mkdir(parents=True)

    # Archivos base
    (build / 'mimetype').write_text('application/epub+zip', encoding='ascii')
    (build / 'META-INF' / 'container.xml').write_text(CONTAINER_XML, encoding='utf-8')
    (build / 'OEBPS' / 'styles' / 'stylesheet.css').write_text(CSS, encoding='utf-8')

    # Portada opcional
    cover_item = ''
    cover_meta = ''
    cover_xhtml_item = ''
    spine_prefix = ''

    if cover_path and cover_path.exists():
        mt = cover_media_type(cover_path)
        dst = build / 'OEBPS' / 'images' / cover_path.name
        shutil.copyfile(cover_path, dst)

        cover_xhtml = COVERPAGE_TEMPLATE.format(lang=lang, cover_name=escape(cover_path.name))
        (build / 'OEBPS' / 'cover.xhtml').write_text(cover_xhtml, encoding='utf-8')

        cover_xhtml_item = '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>'
        spine_prefix = '<itemref idref="cover"/>'

        cover_item = f'<item id="cover-image" href="images/{escape(cover_path.name)}" media-type="{mt}" properties="cover-image"/>'
        cover_meta = '<meta name="cover" content="cover-image"/>'

    # Página de título
    titlepage_xhtml = TITLEPAGE_TEMPLATE.format(title=escape(title), author=escape(author), lang=lang)
    (build / 'OEBPS' / 'titlepage.xhtml').write_text(titlepage_xhtml, encoding='utf-8')

    # Convertir capítulos
    spine_items = []
    manifest_items = ['<item id="titlepage" href="titlepage.xhtml" media-type="application/xhtml+xml"/>']
    nav_entries = []

    for i, entry in enumerate(items, start=1):
        src = sections_dir / entry['file']
        raw = src.read_text(encoding='utf-8')

        chapter_title = entry.get('title') or heading_fallback(raw) or Path(entry['file']).stem

        raw_body = remove_first_heading(raw)
        body = f"<h1>{escape(chapter_title)}</h1>\n" + md_to_xhtml(raw_body)
        xhtml = CHAPTER_TEMPLATE.format(title=escape(chapter_title), body=body, lang=lang)

        out_name = f"sec_{i:03d}.xhtml"
        (build / 'OEBPS' / out_name).write_text(xhtml, encoding='utf-8')

        manifest_items.append(f'<item id="sec_{i:03d}" href="{out_name}" media-type="application/xhtml+xml"/>')
        spine_items.append(f'<itemref idref="sec_{i:03d}"/>')
        nav_entries.append(f'<li><a href="{out_name}">{escape(chapter_title)}</a></li>')

    # nav.xhtml
    nav_xhtml = NAV_TEMPLATE.format(items="\n".join(nav_entries), lang=lang)
    (build / 'OEBPS' / 'nav.xhtml').write_text(nav_xhtml, encoding='utf-8')

    # content.opf
    opf = OPF_TEMPLATE.format(
        lang=lang,
        uuid=uuid,
        title=escape(title),
        author=escape(author),
        modified=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        items="\n    ".join(manifest_items),
        spine="\n    ".join(spine_items),
        cover_item=cover_item,
        cover_meta=cover_meta,
        cover_xhtml_item=cover_xhtml_item,
        spine_prefix=spine_prefix,
    )
    (build / 'OEBPS' / 'content.opf').write_text(opf, encoding='utf-8')

    # Empaquetado .epub
    with zipfile.ZipFile(out_file, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        # mimetype primero y sin compresión
        zinfo = zipfile.ZipInfo('mimetype')
        zinfo.compress_type = zipfile.ZIP_STORED
        zf.writestr(zinfo, (build / 'mimetype').read_bytes())

        for root, _, files in os.walk(build):
            for fn in files:
                full = Path(root) / fn
                rel = full.relative_to(build).as_posix()
                if rel == 'mimetype':
                    continue
                zf.write(full, rel)

    shutil.rmtree(build)
    print(f"[OK] EPUB creado: {out_file.name}")


def main():
    ap = argparse.ArgumentParser(description="Construye un EPUB 3 desde secciones .md")
    ap.add_argument('--sections', required=True, help='Carpeta con .md y manifest.json')
    ap.add_argument('--title', required=True)
    ap.add_argument('--author', required=True)
    ap.add_argument('--lang', default='es')
    ap.add_argument('--cover', default=None, help='Ruta a la imagen de portada (png/jpg/jpeg/webp)')
    ap.add_argument('--uuid', default=None, help='UUID opcional; si no, se genera')
    ap.add_argument('--out', required=True, help='Archivo .epub de salida')
    args = ap.parse_args()

    build_epub(
        sections_dir=Path(args.sections),
        title=args.title,
        author=args.author,
        lang=args.lang,
        out_file=Path(args.out),
        cover_path=Path(args.cover) if args.cover else None,
        uuid=args.uuid,
    )


if __name__ == '__main__':
    main()
