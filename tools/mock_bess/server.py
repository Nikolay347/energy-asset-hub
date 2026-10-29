import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class BessRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path != "/telemetry":
            self.send_error(404, "Not Found")
            return
        payload = {
            "asset_id": "BESS-01",
            "timestamp": "2026-10-24T10:00:00+03:00",
            "soc_percent": 72.5,
            "power_kw": -120.0,
            "temperature_c": 28.3,
        }

        body = json.dumps(payload).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

def run_server(
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    server = HTTPServer(
        (host, port),
        BessRequestHandler,
    )

    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()


