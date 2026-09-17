#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normaliza el manuscrito sin alterar su estructura Markdown."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "Lo_que_continua_indice.md"
DEFAULT_OUTPUT = ROOT / "Lo_que_continua_indice.normalized.md"


def normalize_file(source: Path, output: Path) -> Path:
    if not source.exists():
        raise SystemExit(f"No se encontró el manuscrito: {source}")

    # utf-8-sig elimina un BOM si el editor lo agregó. splitlines normaliza
    # CRLF/LF sin tocar los dos espacios finales que Markdown usa como salto.
    text = source.read_text(encoding="utf-8-sig")
    normalized = "\n".join(text.splitlines()).rstrip("\n") + "\n"

    if "# Descompilando el mundo" not in normalized:
        raise SystemExit("El manuscrito no contiene el título esperado: '# Descompilando el mundo'.")
    if "## Índice" not in normalized:
        raise SystemExit("El manuscrito no contiene la sección '## Índice'.")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(normalized, encoding="utf-8", newline="\n")
    print(f"[OK] Markdown normalizado: {output.name}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    normalize_file(args.source.resolve(), args.out.resolve())


if __name__ == "__main__":
    main()
