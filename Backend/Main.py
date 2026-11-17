"""Small web application for exact procurement-code lookup."""

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from Backend.data_sources import get_data_source


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT / "Frontend"), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/search":
            self.handle_search(parse_qs(parsed.query, keep_blank_values=True))
            return
        if parsed.path == "/api/summary":
            self.handle_summary()
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def handle_search(self, query):
        code_values = query.get("code", [])
        code = code_values[0] if code_values else ""
        if not code:
            self.send_json(400, {"error": "Masukkan Unique Code terlebih dahulu."})
            return
        try:
            result = get_data_source().find_by_unique_code(code)
        except (FileNotFoundError, KeyError, ValueError, NotImplementedError) as error:
            self.send_json(500, {"error": f"Sumber data belum siap: {error}"})
            return
        if result is None:
            self.send_json(404, {"error": "Unique Code tidak ditemukan."})
            return
        self.send_json(200, {"record": result})

    def handle_summary(self):
        try:
            summary = get_data_source().get_summary()
        except Exception:
            # Keep internal file paths and tracebacks out of the user-facing response.
            self.send_json(503, {"status": "unavailable", "error": "Sumber data tidak dapat diakses."})
            return
        self.send_json(200, summary)

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8000), RequestHandler)
    print("Aplikasi siap di http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer dihentikan.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
