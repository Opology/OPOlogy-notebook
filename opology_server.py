#!/usr/bin/env python3
"""Local, dependency-free autosave server for OPOlogy Outline Notebook."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional


APP_DIR = Path(__file__).resolve().parent
HTML_FILE = APP_DIR / "OPOlogy_Outline_Notebook.html"
DEFAULT_DATA_DIR = APP_DIR / "data"
MAX_BODY_BYTES = 200 * 1024 * 1024


class NotebookStore:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.data_file = data_dir / "opology_notebook.json"
        self.previous_file = data_dir / "opology_notebook.previous.json"
        self.lock = threading.RLock()
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _read_unlocked(self, path: Path) -> Optional[Dict[str, Any]]:
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as handle:
                value = json.load(handle)
            return value if isinstance(value, dict) else None
        except (OSError, json.JSONDecodeError):
            return None

    def load(self) -> Dict[str, Any]:
        with self.lock:
            record = self._read_unlocked(self.data_file)
            if not record:
                return {"ok": True, "revision": 0, "savedAt": None, "data": None}
            return {
                "ok": True,
                "revision": int(record.get("revision", 0)),
                "savedAt": record.get("savedAt"),
                "data": record.get("data"),
            }

    @staticmethod
    def _validate_notebook(value: Any) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("Notebook data must be a JSON object.")
        if not isinstance(value.get("tree"), list):
            raise ValueError("Notebook data must contain a tree array.")
        if value.get("schema") not in (None, "opology-outline-notebook"):
            raise ValueError("Unsupported notebook schema.")
        if "assets" in value and not isinstance(value["assets"], dict):
            raise ValueError("Notebook assets must be a JSON object.")
        return value

    def save(self, incoming: Dict[str, Any]) -> Dict[str, Any]:
        notebook = incoming.get("data", incoming)
        notebook = self._validate_notebook(notebook)
        with self.lock:
            current = self._read_unlocked(self.data_file) or {}
            revision = int(current.get("revision", 0)) + 1
            record = {
                "revision": revision,
                "savedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "clientId": incoming.get("clientId"),
                "reason": incoming.get("reason", "autosave"),
                "data": notebook,
            }

            if self.data_file.exists():
                previous_temp = self.previous_file.with_suffix(".json.tmp")
                shutil.copy2(self.data_file, previous_temp)
                os.replace(previous_temp, self.previous_file)

            descriptor, temporary_name = tempfile.mkstemp(
                prefix="opology-notebook-", suffix=".tmp", dir=str(self.data_dir)
            )
            try:
                with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                    json.dump(record, handle, ensure_ascii=False, separators=(",", ":"))
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary_name, self.data_file)
            finally:
                if os.path.exists(temporary_name):
                    os.unlink(temporary_name)

            return {
                "ok": True,
                "revision": revision,
                "savedAt": record["savedAt"],
            }


class OPOlogyServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], store: NotebookStore) -> None:
        super().__init__(address, OPOlogyHandler)
        self.store = store


class OPOlogyHandler(BaseHTTPRequestHandler):
    server: OPOlogyServer
    server_version = "OPOlogyNotebook/1.0"

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, status: int, value: Dict[str, Any]) -> None:
        body = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, include_body: bool = True) -> None:
        try:
            body = HTML_FILE.read_bytes()
        except OSError as error:
            self._send_json(500, {"ok": False, "error": str(error)})
            return
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_HEAD(self) -> None:  # noqa: N802
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/index.html", "/OPOlogy_Outline_Notebook.html"):
            self._send_html(include_body=False)
        else:
            self.send_error(404)

    def do_GET(self) -> None:  # noqa: N802
        path = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
        if path in ("/", "/index.html", "/OPOlogy_Outline_Notebook.html"):
            self._send_html()
            return
        if path in ("/load", "/api/load"):
            self._send_json(200, self.server.store.load())
            return
        if path in ("/health", "/api/health"):
            loaded = self.server.store.load()
            self._send_json(
                200,
                {
                    "ok": True,
                    "service": "OPOlogy Notebook",
                    "revision": loaded.get("revision", 0),
                    "savedAt": loaded.get("savedAt"),
                },
            )
            return
        if path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self._send_json(404, {"ok": False, "error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
        if path not in ("/save", "/api/save"):
            self._send_json(404, {"ok": False, "error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0:
            self._send_json(400, {"ok": False, "error": "Empty request body"})
            return
        if length > MAX_BODY_BYTES:
            self._send_json(413, {"ok": False, "error": "Notebook exceeds 200 MB"})
            return
        try:
            incoming = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(incoming, dict):
                raise ValueError("Request body must be a JSON object.")
            result = self.server.store.save(incoming)
            self._send_json(200, result)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            self._send_json(400, {"ok": False, "error": str(error)})
        except OSError as error:
            self._send_json(500, {"ok": False, "error": str(error)})

    def log_message(self, format_string: str, *args: Any) -> None:
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {self.address_string()} {format_string % args}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the OPOlogy local notebook and autosave API.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address; default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=9000, help="API port; default: 9000")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="Folder for saved notebook JSON")
    parser.add_argument("--open", action="store_true", help="Open the notebook in the default browser")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not HTML_FILE.exists():
        print(f"Missing notebook file: {HTML_FILE}", file=sys.stderr)
        return 2
    store = NotebookStore(args.data_dir.resolve())
    try:
        server = OPOlogyServer((args.host, args.port), store)
    except OSError as error:
        print(f"Could not start OPOlogy on {args.host}:{args.port}: {error}", file=sys.stderr)
        print("Close the other program using port 9000, or choose another port with --port.", file=sys.stderr)
        return 1

    browser_host = "127.0.0.1" if args.host in ("0.0.0.0", "::") else args.host
    url = f"http://{browser_host}:{args.port}/"
    print("OPOlogy Outline Notebook")
    print(f"Notebook: {url}")
    print(f"Load API: {url}load")
    print(f"Save API: {url}save")
    print(f"Data file: {store.data_file}")
    print("Press Ctrl+C to stop the server. Your saved data remains on disk.")
    if args.open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        print("\nStopping OPOlogy server…")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
