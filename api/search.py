"""WSGI application for the Vercel deployment."""

import json
from pathlib import Path
from urllib.parse import parse_qs

from Backend.data_sources import get_data_source


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_FILES = {
    "/": (PROJECT_ROOT / "Frontend" / "index.html", "text/html; charset=utf-8"),
    "/styles.css": (PROJECT_ROOT / "Frontend" / "styles.css", "text/css; charset=utf-8"),
    "/app.js": (PROJECT_ROOT / "Frontend" / "app.js", "text/javascript; charset=utf-8"),
}


def _respond(start_response, status, body, content_type):
    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "no-store"),
    ]
    start_response(status, headers)
    return [body]


def _json_response(start_response, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    return _respond(start_response, status, body, "application/json; charset=utf-8")


def app(environ, start_response):
    """Serve the static frontend and exact-match lookup through one WSGI app."""
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/")

    if method not in {"GET", "HEAD"}:
        return _respond(start_response, "405 Method Not Allowed", b"Method not allowed.", "text/plain; charset=utf-8")

    if path == "/api/search":
        params = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
        codes = params.get("code", [])
        code = codes[0] if codes else ""
        if not code:
            return _json_response(start_response, "400 Bad Request", {"error": "Enter an item code."})

        try:
            record = get_data_source().find_by_unique_code(code)
        except Exception:
            # Keep internal paths and tracebacks out of public responses.
            return _json_response(
                start_response,
                "503 Service Unavailable",
                {"status": "unavailable", "error": "The data source is unavailable."},
            )

        if record is None:
            return _json_response(
                start_response,
                "404 Not Found",
                {"status": "not-found", "error": "Item code was not found."},
            )
        return _json_response(start_response, "200 OK", {"status": "found", "record": record})

    static_file = STATIC_FILES.get(path)
    if static_file:
        file_path, content_type = static_file
        try:
            body = file_path.read_bytes()
        except OSError:
            return _respond(start_response, "404 Not Found", b"Not found.", "text/plain; charset=utf-8")
        if method == "HEAD":
            body = b""
        return _respond(start_response, "200 OK", body, content_type)

    if path.startswith("/api/"):
        return _json_response(start_response, "404 Not Found", {"error": "API route not found."})
    return _respond(start_response, "404 Not Found", b"Not found.", "text/plain; charset=utf-8")
