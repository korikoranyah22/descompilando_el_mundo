#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sirve la edición web localmente y, salvo indicación, abre el navegador."""

from __future__ import annotations

import argparse
import functools
import http.server
import threading
import time
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_FILE = "Descompilando_el_mundo.html"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8432)
    parser.add_argument("--no-browser", action="store_true", help="No abrir el navegador automáticamente")
    args = parser.parse_args()

    web_file = ROOT / DEFAULT_FILE
    if not web_file.exists():
        raise SystemExit(f"No se encontró {DEFAULT_FILE}; ejecutá primero: python run_pipeline.py")

    url = f"http://127.0.0.1:{args.port}/{DEFAULT_FILE}"
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler)

    if not args.no_browser:
        def open_browser() -> None:
            time.sleep(0.5)
            webbrowser.open(url)

        threading.Thread(target=open_browser, daemon=True).start()

    print(f"Descompilando el mundo: {url}")
    print("  Ctrl+C para cerrar")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor cerrado.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
