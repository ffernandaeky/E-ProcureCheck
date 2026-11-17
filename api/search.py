"""Vercel function for exact item-code lookup."""

import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from Backend.data_sources import get_data_source


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query, keep_blank_values=True)
        code_values = query.get("code", [])
        code = code_values[0] if code_values else ""

        if not code:
            self.send_json(400, {"error": "Enter an item code."})
            return

        try:
            record = get_data_source().find_by_unique_code(code)
        except Exception:
            # Keep implementation details and tracebacks out of public responses.
            self.send_json(503, {"status": "unavailable", "error": "The data source is unavailable."})
            return

        if record is None:
            self.send_json(404, {"status": "not-found", "error": "Item code was not found."})
            return

        self.send_json(200, {"status": "found", "record": record})

    def do_POST(self):
        self.send_json(405, {"error": "Method not allowed."})

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
