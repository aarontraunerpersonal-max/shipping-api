"""
Shipping API Server — no dependencies, uses Python built-ins only.
Run locally:  python3 server_api.py
Endpoints:
  GET  /api/shipments             — return all shipments
  GET  /api/shipments?id=SHP1001  — return one shipment by ID
  POST /api/shipments             — add or overwrite a shipment (JSON body)
                                    existing fields are preserved if not included
"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime

PORT = int(os.environ.get("PORT", 8080))

# ── Notional dataset ──────────────────────────────────────────────────────────
shipments = {
    "SHP1001": {
        "shipping_id": "SHP1001",
        "manufacturer": "Acme Anvils Co.",
        "manufacturer_email": "contact@acmeanvils.co",
        "shipping_company": "SwiftShip Logistics",
        "shipping_company_email": "ops@swiftshiplogistics.com",
        "date_of_departure": "2026-03-30",
        "date_of_arrival": "2026-04-02"
    },
    "SHP1002": {
        "shipping_id": "SHP1002",
        "manufacturer": "Bolt & Byte Industries",
        "manufacturer_email": "hello@boltandbyte.io",
        "shipping_company": "Quantum Freight",
        "shipping_company_email": "support@quantumfreight.io",
        "date_of_departure": "2026-04-01",
        "date_of_arrival": "2026-04-05"
    },
    "SHP1003": {
        "shipping_id": "SHP1003",
        "manufacturer": "Nutorious Parts Ltd.",
        "manufacturer_email": "aarontrauner.personal@gmail.com",
        "shipping_company": "RapidRoute Carriers",
        "shipping_company_email": "aarontrauner.personal@gmail.com",
        "date_of_departure": "2026-04-03",
        "date_of_arrival": "2026-04-07"
    },
    "SHP1004": {
        "shipping_id": "SHP1004",
        "manufacturer": "Widget Wizards Inc.",
        "manufacturer_email": "magic@widgetwizards.dev",
        "shipping_company": "BlueSky Shipping",
        "shipping_company_email": "contact@blueskyshipping.com",
        "date_of_departure": "2026-04-06",
        "date_of_arrival": "2026-04-10"
    },
    "SHP1005": {
        "shipping_id": "SHP1005",
        "manufacturer": "Gearbox & Sons",
        "manufacturer_email": "info@gearboxsons.com",
        "shipping_company": "IronHorse Transport",
        "shipping_company_email": "freight@ironhorsetransport.co",
        "date_of_departure": "2026-04-08",
        "date_of_arrival": "2026-04-12"
    },
    "SHP1006": {
        "shipping_id": "SHP1006",
        "manufacturer": "Sprocket Science LLC",
        "manufacturer_email": "lab@sprocketscience.ai",
        "shipping_company": "Velocity Freight",
        "shipping_company_email": "speed@velocityfreight.com",
        "date_of_departure": "2026-04-11",
        "date_of_arrival": "2026-04-15"
    },
    "SHP1007": {
        "shipping_id": "SHP1007",
        "manufacturer": "Circuit Circus Co.",
        "manufacturer_email": "ringmaster@circuitcircus.io",
        "shipping_company": "Nova Logistics",
        "shipping_company_email": "hello@novalogistics.io",
        "date_of_departure": "2026-04-14",
        "date_of_arrival": "2026-04-18"
    },
    "SHP1008": {
        "shipping_id": "SHP1008",
        "manufacturer": "TurboTonic Works",
        "manufacturer_email": "boost@turbotonic.co",
        "shipping_company": "Apex Shipping Co.",
        "shipping_company_email": "apex@apexshipping.com",
        "date_of_departure": "2026-04-16",
        "date_of_arrival": "2026-04-20"
    },
    "SHP1009": {
        "shipping_id": "SHP1009",
        "manufacturer": "Flux Capacitor Corp.",
        "manufacturer_email": "time@fluxcapacitor.tech",
        "shipping_company": "TimeTrack Transport",
        "shipping_company_email": "timeline@timetracktransit.com",
        "date_of_departure": "2026-04-19",
        "date_of_arrival": "2026-04-23"
    },
    "SHP1010": {
        "shipping_id": "SHP1010",
        "manufacturer": "MegaMold Makers",
        "manufacturer_email": "mold@megamoldmakers.com",
        "shipping_company": "Titan Freight Lines",
        "shipping_company_email": "cargo@titanfreightlines.com",
        "date_of_departure": "2026-04-22",
        "date_of_arrival": "2026-04-26"
    },
    "SHP1011": {
        "shipping_id": "SHP1011",
        "manufacturer": "Piston & Co.",
        "manufacturer_email": "revs@pistonco.com",
        "shipping_company": "EagleEye Carriers",
        "shipping_company_email": "view@eagleeyecarriers.com",
        "date_of_departure": "2026-04-24",
        "date_of_arrival": "2026-04-28"
    },
    "SHP1012": {
        "shipping_id": "SHP1012",
        "manufacturer": "Alloy All-Stars Ltd.",
        "manufacturer_email": "team@alloyallstars.io",
        "shipping_company": "Horizon Haulage",
        "shipping_company_email": "route@horizonhaulage.com",
        "date_of_departure": "2026-04-27",
        "date_of_arrival": "2026-05-01"
    },
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

        shipping_id = str(body.get("shipping_id", "")).strip().upper()

        if not shipping_id:
            self.send_json(400, {"status": 400, "error": "Bad Request",
                                 "message": "shipping_id is required"})
            return

        # Load existing record as base (if overwriting), otherwise start fresh
        is_overwrite = shipping_id in shipments
        existing = shipments[shipping_id].copy() if is_overwrite else {
            "shipping_id":            shipping_id,
            "manufacturer":           "",
            "manufacturer_email":     "",
            "shipping_company":       "",
            "shipping_company_email": "",
            "date_of_departure":      "",
            "date_of_arrival":        "",
        }

        # Only update fields that are explicitly provided in the request
        optional_fields = [
            "manufacturer", "manufacturer_email",
            "shipping_company", "shipping_company_email"
        ]
        for field in optional_fields:
            if field in body:
                existing[field] = str(body[field]).strip()

        date_departure = str(body.get("date_of_departure", existing["date_of_departure"])).strip()
        date_arrival   = str(body.get("date_of_arrival",   existing["date_of_arrival"])).strip()

        # Validate dates only if provided or required (new record)
        if not is_overwrite and not all([date_departure, date_arrival]):
            self.send_json(400, {"status": 400, "error": "Bad Request",
                                 "message": "date_of_departure and date_of_arrival are required for new shipments"})
            return

        if date_departure and date_arrival:
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

        existing["date_of_departure"] = date_departure
        existing["date_of_arrival"]   = date_arrival
        existing["shipping_id"]       = shipping_id
        shipments[shipping_id]        = existing

        status_code = 200 if is_overwrite else 201
        message     = "Shipment updated (missing fields kept from previous record)" if is_overwrite else "Shipment created successfully"
        self.send_json(status_code, {"status": status_code, "message": message,
                                     "data": shipments[shipping_id]})

    def log_message(self, format, *args):
        print(f"  {self.address_string()} → {args[0]}")


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), ShippingHandler)
    print(f"Shipping API running on port {PORT}")
    print(f"  GET  /api/shipments")
    print(f"  GET  /api/shipments?id=SHP1001")
    print(f"  POST /api/shipments")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
