"""
REST API for MoMo SMS transactions.

A plain-Python HTTP server (no Django, no Flask) that exposes CRUD endpoints
for the transactions parsed out of the SMS XML file.

Endpoints:
    GET    /transactions         -> list all transactions
    GET    /transactions/{id}    -> get one transaction
    POST   /transactions         -> add a new transaction
    PUT    /transactions/{id}    -> update an existing transaction
    DELETE /transactions/{id}    -> delete a transaction

Run from anywhere with:
    python api/server.py
or:
    python server.py    (if you're already inside api/)
"""

import json
import base64
import sys
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# ------------- Credentials ------------
VALID_USERNAME = "admin"
VALID_PASSWORD = "password123"

def check_auth(handler):
    auth_header = handler.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Basic "):
        return False
    encoded = auth_header.split(" ")[1]
    decoded = base64.b64decode(encoded).decode("utf-8")
    username, password = decoded.split(":", 1)
    return username == VALID_USERNAME and password == VALID_PASSWORD

# ---------- Make the parser importable from anywhere ----------
THIS_DIR = os.path.dirname(os.path.abspath(__file__))   # .../api
PROJECT_ROOT = os.path.dirname(THIS_DIR)                # project root

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dsa.xml_parser import load_transactions


# ---------- In-memory data store ----------
transactions = load_transactions()
next_id = max(transactions.keys()) + 1 if transactions else 1


# ---------- Required fields for POST ----------
# Just the essentials a user actually thinks about when logging a transaction.
# Everything else gets sensible defaults.
REQUIRED_FIELDS = ["amount", "category", "sender", "receiver"]


def build_transaction(data, transaction_id):
    """
    Take the simple input the user sent and produce a full transaction record
    that matches the shape produced by the XML parser. The user only sends
    the basics; we fill in the rest.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "transaction_id": transaction_id,
        "financial_id": data.get("financial_id"),
        "occurred_at": data.get("occurred_at", now),
        "amount": float(data["amount"]),
        "fee": float(data.get("fee", 0.0)),
        "new_balance": float(data.get("new_balance", 0.0)),
        "category": {
            "name": data["category"],
            "type": "unknown",
            "direction": "UNK",
        },
        "sender": {
            "name": data["sender"],
            "identifier": {"type": None, "value": None},
        },
        "receiver": {
            "name": data["receiver"],
            "identifier": {"type": None, "value": None},
        },
        "body_raw": data.get("body_raw", ""),
        "log": {
            "level": "INFO",
            "message": "Transaction created via API.",
            "timestamp": now,
        },
        "is_processed": True,
    }


# ---------- Request handler ----------

class TransactionHandler(BaseHTTPRequestHandler):
    """
    Handles every incoming HTTP request.
    The server creates a new instance per request and calls do_GET / do_POST /
    do_PUT / do_DELETE depending on the HTTP method.
    """

    # ----- Small utilities used by every handler -----

    def send_json(self, status_code, data):
        """Send a JSON response with the given status code."""
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json_body(self):
        """Read and parse the request body as JSON. Returns None on failure."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def get_id_from_path(self):
        """Pull the transaction id out of a URL like /transactions/5."""
        parts = self.path.strip("/").split("/")
        if len(parts) != 2:
            return None
        try:
            return int(parts[1])
        except ValueError:
            return None

    # ----- GET -----

    def do_GET(self):
        if not check_auth(self):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="MOMO API"')
            self.end_headers()
            return
        if self.path == "/transactions":
            self.send_json(200, list(transactions.values()))
            return

        if self.path.startswith("/transactions/"):
            tid = self.get_id_from_path()
            if tid is None:
                self.send_json(400, {"error": "Invalid transaction id"})
                return
            if tid not in transactions:
                self.send_json(404, {"error": f"Transaction {tid} not found"})
                return
            self.send_json(200, transactions[tid])
            return

        self.send_json(404, {"error": "Route not found"})

    # ----- POST -----

    def do_POST(self):
        if not check_auth(self):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="MOMO API"')
            self.end_headers()
            return
        if self.path != "/transactions":
            self.send_json(404, {"error": "Route not found"})
            return

        data = self.read_json_body()
        if data is None:
            self.send_json(400, {"error": "Request body must be valid JSON"})
            return

        # Make sure the four basics are there
        missing = [f for f in REQUIRED_FIELDS if f not in data]
        if missing:
            self.send_json(400, {
                "error": f"Missing required fields: {', '.join(missing)}"
            })
            return

        global next_id
        new_id = next_id
        next_id += 1

        transaction = build_transaction(data, new_id)
        transactions[new_id] = transaction

        self.send_json(201, {"message": "Transaction created", "data": transaction})

    # ----- PUT -----

    def do_PUT(self):
        if not check_auth(self):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="MOMO API"')
            self.end_headers()
            return
        if not self.path.startswith("/transactions/"):
            self.send_json(404, {"error": "Route not found"})
            return

        tid = self.get_id_from_path()
        if tid is None:
            self.send_json(400, {"error": "Invalid transaction id"})
            return
        if tid not in transactions:
            self.send_json(404, {"error": f"Transaction {tid} not found"})
            return

        data = self.read_json_body()
        if data is None:
            self.send_json(400, {"error": "Request body must be valid JSON"})
            return

        # PUT is a partial update — only update whatever the client sent
        transactions[tid].update(data)
        # Never let the client change the id
        transactions[tid]["transaction_id"] = tid

        self.send_json(200, {"message": "Transaction updated", "data": transactions[tid]})

    # ----- DELETE -----

    def do_DELETE(self):
        if not check_auth(self):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="MOMO API"')
            self.end_headers()
            return
        if not self.path.startswith("/transactions/"):
            self.send_json(404, {"error": "Route not found"})
            return

        tid = self.get_id_from_path()
        if tid is None:
            self.send_json(400, {"error": "Invalid transaction id"})
            return
        if tid not in transactions:
            self.send_json(404, {"error": f"Transaction {tid} not found"})
            return

        del transactions[tid]
        self.send_json(200, {"message": f"Transaction {tid} deleted"})

    # ----- Cleaner terminal logging -----

    def log_message(self, format, *args):
        print(f"[{self.command}] {self.path} -> {args[1]}")


# ---------- Entry point ----------

def run(host="localhost", port=8000):
    server = HTTPServer((host, port), TransactionHandler)
    print(f"Server running at http://{host}:{port}")
    print(f"Loaded {len(transactions)} transactions into memory.")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    run()