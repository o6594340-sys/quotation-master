from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.services.quotation_service import create_job, get_job_status


class QuotationHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return

        if self.path.startswith("/jobs/"):
            job_id = self.path.split("/", 2)[2]
            job = get_job_status(job_id)
            if job is None:
                self._send_json(404, {"error": "job not found"})
                return
            self._send_json(200, job)
            return

        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/jobs":
            self._send_json(404, {"error": "not found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8")
        payload = json.loads(body or "{}")
        job = create_job(payload)
        self._send_json(201, job)

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = HTTPServer((host, port), QuotationHandler)
    print(f"Starting server on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
