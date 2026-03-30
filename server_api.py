"""
Shipping API Server — no dependencies, uses Python built-ins only.
Run with:  python3 server_api.py
Endpoints:
  GET  /api/shipments             — return all shipments
  GET  /api/shipments?id=SHP1001  — return one shipment by ID
  POST /api/shipments             — add or overwrite a shipment (JSON body)
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime

PORT = 8080

# ── Notional dataset ──────────────────────────────────────────────────────────
shipments = {
    "SHP1001": {"shipping_id": "SHP1001", "date_of_departure": "2026-03-30", "date_of_arrival": "2026-04-02"},
    "SHP1002": {"shipping_id": "SHP1002", "date_of_departure": "2026-04-01", "date_of_arrival": "2026-04-05"},
    "SHP1003": {"shipping_id": "SHP1003", "date_of_departure": "2026-04-03", "date_of_arrival": "2026-04-07"},
    "SHP1004": {"shipping_id": "SHP1004", "date_of_departure": "2026-04-06", "date_of_arrival": "2026-04-10"},
    "SHP1005": {"shipping_id": "SHP1005", "date_of_departure": "2026-04-08", "date_of_arrival": "2026-04-12"},
    "SHP1006": {"shipping_id": "SHP1006", "date_of_departure": "2026-04-11", "date_of_arrival": "2026-04-15"},
    "SHP1007": {"shipping_id": "SHP1007", "date_of_departure": "2026-04-14", "date_of_arrival": "2026-04-18"},
    "SHP1008": {"shipping_id": "SHP1008", "date_of_departure": "2026-04-16", "date_of_arrival": "2026-04-20"},
    "SHP1009": {"shipping_id": "SHP1009", "date_of_departure": "2026-04-19", "date_of_arrival": "2026-04-23"},
    "SHP1010": {"shipping_id": "SHP1010", "date_of_departure": "2026-04-22", "date_of_arrival": "2026-04-26"},
    "SHP1011": {"shipping_id": "SHP1011", "date_of_departure": "2026-04-24", "date_of_arrival": "2026-04-28"},
    "SHP1012": {"shipping_id": "SHP1012", "date_of_departure": "2026-04-27", "date_of_arrival": "2026-05-01"},
}


def parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


class ShippingHandler(BaseHTTPRequestHandler):

    def send_json(self, code, data):
        body = json.dumps(data, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ── GET ───────────────────────────────────────────────────────────────────
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/shipments":
            self.send_json(404, {"status": 404, "error": "Not Found",
                                 "message": f"Unknown endpoint: {parsed.path}"})
            return

        params   = parse_qs(parsed.query)
        id_param = params.get("id", [None])[0]

        if id_param:
            filter_id = id_param.strip().upper()
            record    = shipments.get(filter_id)
            if not record:
                self.send_json(404, {"status": 404, "error": "Not Found",
                                     "message": f"No shipment found with id '{filter_id}'"})
                return
            self.send_json(200, {"status": 200, "count": 1, "data": [record]})
        else:
            self.send_json(200, {"status": 200, "count": len(shipments),
                                 "data": list(shipments.values())})

    # ── POST ──────────────────────────────────────────────────────────────────
    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/shipments":
            self.send_json(404, {"status": 404, "error": "Not Found",
                                 "message": f"Unknown endpoint: {parsed.path}"})
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length)) if length else {}
        except json.JSONDecodeError:
            self.send_json(400, {"status": 400, "error": "Bad Request",
                                 "message": "Request body must be valid JSON"})
            return

        shipping_id    = str(body.get("shipping_id",       "")).strip().upper()
        date_departure = str(body.get("date_of_departure", "")).strip()
        date_arrival   = str(body.get("date_of_arrival",   "")).strip()

        if not all([shipping_id, date_departure, date_arrival]):
            self.send_json(400, {"status": 400, "error": "Bad Request",
                                 "message": "All fields required: shipping_id, date_of_departure, date_of_arrival"})
            return

        dep_dt = parse_date(date_departure)
        arr_dt = parse_date(date_arrival)
        if not dep_dt or not arr_dt:
            self.send_json(400, {"status": 400, "error": "Bad Request",
                                 "message": "Dates must be in YYYY-MM-DD format"})
            return

        if arr_dt <= dep_dt:
            self.send_json(400, {"status": 400, "error": "Bad Request",
                                 "message": "date_of_arrival must be after date_of_departure"})
            return

        is_overwrite = shipping_id in shipments
        shipments[shipping_id] = {
            "shipping_id":       shipping_id,
            "date_of_departure": date_departure,
            "date_of_arrival":   date_arrival,
        }

        status_code = 200 if is_overwrite else 201
        message     = "Shipment updated (overwritten)" if is_overwrite else "Shipment created successfully"
        self.send_json(status_code, {"status": status_code, "message": message,
                                     "data": shipments[shipping_id]})

    def log_message(self, format, *args):
        print(f"  {self.address_string()} → {args[0]}")


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    server = HTTPServer(("", PORT), ShippingHandler)
    print(f"Shipping API running at http://localhost:{PORT}")
    print(f"  GET  http://localhost:{PORT}/api/shipments")
    print(f"  GET  http://localhost:{PORT}/api/shipments?id=SHP1001")
    print(f"  POST http://localhost:{PORT}/api/shipments")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
