#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Divide el manuscrito en unidades de lectura y crea sections/manifest.json."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "Lo_que_continua_indice.normalized.md"
DEFAULT_OUTPUT = ROOT / "sections"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
PART_RE = re.compile(r"^Parte\s+[IVXLCDM]+\b", re.IGNORECASE)
CHAPTER_RE = re.compile(r"^\d+\.\s+")
INTERLUDE_RE = re.compile(r"^Interludio\s+[IVXLCDM]+\b", re.IGNORECASE)
APPENDIX_RE = re.compile(r"^[A-E]\.\s+")


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-") or "seccion"


def section_kind(level: int, title: str) -> str | None:
    if level == 2 and title == "Índice":
        return "index"
    if level == 1 and (PART_RE.match(title) or title == "Apéndices"):
        return "part"
    if level == 2 and CHAPTER_RE.match(title):
        return "chapter"
    if level == 3 and INTERLUDE_RE.match(title):
        return "interlude"
    if level == 3 and title.startswith("Epílogo"):
        return "epilogue"
    if level == 2 and APPENDIX_RE.match(title):
        return "appendix"
    if level == 2:
        return "frontmatter"
    return None


def split_document(source: Path, output_dir: Path) -> dict:
    if not source.exists():
        raise SystemExit(f"No se encontró el Markdown normalizado: {source}")

    source_text = source.read_text(encoding="utf-8")
    lines = source_text.splitlines()
    sections: list[dict] = []
    current: dict | None = None
    current_part: str | None = None

    def flush() -> None:
        nonlocal current
        if current is None:
            return
        current["content"] = "\n".join(current["lines"]).strip() + "\n"
        del current["lines"]
        sections.append(current)
        current = None

    for line in lines:
        match = HEADING_RE.match(line)
        kind = None
        title = None
        level = None
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            kind = section_kind(level, title)

        if kind is not None:
            flush()
            if kind == "part":
                current_part = title
            current = {
                "title": title,
                "kind": kind,
                "part": current_part if kind != "part" else None,
                "source_level": level,
                "lines": [line],
            }
        elif current is not None:
            current["lines"].append(line)

    flush()

    if not sections or sections[0]["kind"] != "index":
        raise SystemExit("No se pudo detectar el índice como primera sección publicable.")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Retira únicamente artefactos declarados por una ejecución anterior.
    previous_manifest = output_dir / "manifest.json"
    if previous_manifest.exists():
        try:
            previous = json.loads(previous_manifest.read_text(encoding="utf-8"))
            for entry in previous.get("order", []):
                old_file = output_dir / entry.get("file", "")
                if old_file.is_file() and old_file.parent == output_dir:
                    old_file.unlink()
        except (json.JSONDecodeError, OSError):
            pass

    order = []
    used_names: set[str] = set()
    for position, section in enumerate(sections, start=1):
        base_slug = slugify(section["title"])
        slug = base_slug
        suffix = 2
        while slug in used_names:
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        used_names.add(slug)
        filename = f"{position:03d}_{slug}.md"
        (output_dir / filename).write_text(section["content"], encoding="utf-8", newline="\n")
        order.append(
            {
                "file": filename,
                "title": section["title"],
                "slug": slug,
                "kind": section["kind"],
                "part": section["part"],
                "source_level": section["source_level"],
            }
        )

    title_match = re.search(r"^#\s+(.+?)\s*$", source_text, re.MULTILINE)
    manifest = {
        "source": source.name,
        "title": title_match.group(1) if title_match else "Descompilando el mundo",
        "section_count": len(order),
        "order": order,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    counts = Counter(entry["kind"] for entry in order)
    details = ", ".join(f"{kind}: {count}" for kind, count in sorted(counts.items()))
    print(f"[OK] {len(order)} secciones creadas en {output_dir.name}/ ({details})")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    split_document(args.source.resolve(), args.out.resolve())


if __name__ == "__main__":
    main()
