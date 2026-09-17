#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convierte el índice del libro en enlaces válidos para EPUB y web."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_SECTIONS = ROOT / "sections"


def plain_text(value: str) -> str:
    value = re.sub(r"\[([^]]+)]\([^)]+\)", r"\1", value)
    value = value.replace("**", "").replace("__", "").replace("`", "")
    value = value.replace("*", "").replace("_", "")
    return re.sub(r"\s+", " ", value).strip()


def key(value: str) -> str:
    value = plain_text(value).replace("—", "-").replace("–", "-")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char)).lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def add_index_links(sections_dir: Path) -> int:
    manifest_path = sections_dir / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"No se encontró {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("order", [])

    index_entries = [entry for entry in entries if entry.get("kind") == "index"]
    if len(index_entries) != 1:
        raise SystemExit("El manifest debe contener exactamente una sección de tipo 'index'.")

    targets: dict[str, str] = {}
    for position, entry in enumerate(entries, start=1):
        if entry.get("kind") == "index":
            continue
        targets[key(entry["title"])] = f"sec_{position:03d}.xhtml"

    index_path = sections_dir / index_entries[0]["file"]
    output: list[str] = []
    linked = 0
    unresolved: list[str] = []

    for line in index_path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^(###\s+)(.+?)\s*$", line)
        if heading:
            raw = heading.group(2)
            if re.fullmatch(r"\[.+]\(sec_\d{3}\.xhtml\)", raw):
                output.append(line)
                linked += 1
                continue
            target = targets.get(key(raw))
            if target:
                output.append(f"{heading.group(1)}[{raw}]({target})")
                linked += 1
            else:
                output.append(line)
            continue

        bullet = re.match(r"^(\s*-\s+)(.+?)\s*$", line)
        if bullet:
            raw = bullet.group(2)
            if re.fullmatch(r"\[.+]\(sec_\d{3}\.xhtml\)", raw):
                output.append(line)
                linked += 1
                continue
            target = targets.get(key(raw))
            if target:
                output.append(f"{bullet.group(1)}[{raw}]({target})")
                linked += 1
            else:
                output.append(line)
                unresolved.append(plain_text(raw))
            continue

        output.append(line)

    index_path.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8", newline="\n")
    if unresolved:
        sample = "; ".join(unresolved[:5])
        raise SystemExit(f"Quedaron {len(unresolved)} entradas del índice sin destino: {sample}")
    print(f"[OK] Índice enlazado: {linked} destinos")
    return linked


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sections", type=Path, default=DEFAULT_SECTIONS)
    args = parser.parse_args()
    add_index_links(args.sections.resolve())


if __name__ == "__main__":
    main()
