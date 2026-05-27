"""
XML Parser for MoMo SMS data.

Reads the raw SMS XML file, extracts the useful fields from each message
(amount, fee, sender, receiver, category, etc.), masks sensitive identifiers,
and returns everything as a dictionary keyed by transaction_id.
"""

import xml.etree.ElementTree as ET
import re
import json
import os
from datetime import datetime


# ---------- Project paths ----------
# Build paths relative to THIS file, so the parser works no matter where
# you run it from. __file__ is the full path to xml_parser.py itself.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))           # .../dsa
PROJECT_ROOT = os.path.dirname(THIS_DIR)                        # project root
DEFAULT_XML_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "modified_sms_v2.xml")
DEFAULT_JSON_OUTPUT = os.path.join(THIS_DIR, "parsed_transactions.json")


# ---------- Helpers ----------

def format_timestamp(timestamp_ms):
    """Convert milliseconds (as stored in the XML) into a readable date string."""
    seconds = int(timestamp_ms) / 1000
    return datetime.fromtimestamp(seconds).strftime("%Y-%m-%d %H:%M:%S")


def mask_phone_number(phone):
    """Hide the middle of a phone number. e.g. 250791666666 -> 250******666"""
    phone = str(phone)
    start = phone[:3]
    end = phone[-3:]
    hidden = "*" * (len(phone) - 6)
    return start + hidden + end


def mask_account_number(account):
    """Hide everything but the last 3 digits of an account number."""
    account = str(account)
    visible = account[-3:]
    hidden = "*" * (len(account) - 3)
    return hidden + visible


def process_identifier(identifier_type, raw_value):
    """Wrap an identifier (phone, account, momo code) in a consistent dict."""
    if identifier_type == "phone":
        return {"type": "phone", "value": mask_phone_number(raw_value)}
    if identifier_type == "account_number":
        return {"type": "account_number", "value": mask_account_number(raw_value)}
    if identifier_type == "momo_code":
        return {"type": "momo_code", "value": raw_value}
    if identifier_type == "masked_phone":
        return {"type": "phone", "value": raw_value}
    return {"type": "unknown", "value": None}


def extract_money(pattern, text):
    """Pull a money amount out of the SMS text using a regex pattern."""
    match = re.search(pattern, text)
    if match:
        amount = match.group(1).replace(",", "")
        return float(amount)
    return 0.0


def extract_financial_id(body):
    """Find the TxId or Financial Transaction Id inside an SMS body."""
    match = re.search(r'(?:TxId:|Financial Transaction Id:)\s*([0-9]+)', body)
    if match:
        return match.group(1)
    return None


def detect_category(body):
    """Figure out what kind of transaction this SMS is describing."""
    body_lower = body.lower()

    if "received" in body_lower:
        return {"name": "Incoming Money", "type": "credit", "direction": "IN"}
    if "payment" in body_lower:
        return {"name": "Merchant Payment", "type": "debit", "direction": "OUT"}
    if "transferred to" in body_lower:
        return {"name": "Money Transfer", "type": "debit", "direction": "OUT"}
    if "bank deposit" in body_lower:
        return {"name": "Bank Deposit", "type": "credit", "direction": "IN"}
    if "airtime" in body_lower:
        return {"name": "Airtime Purchase", "type": "debit", "direction": "OUT"}

    return {"name": "Unknown", "type": "unknown", "direction": "UNK"}


def extract_identifier(text):
    """Find a sender/receiver identifier in the SMS text and classify it."""
    masked_phone = re.search(r'\((\*{5,}\d{3})\)', text)
    if masked_phone:
        return process_identifier("masked_phone", masked_phone.group(1))

    real_phone = re.search(r'\((2507\d{8})\)', text)
    if real_phone:
        return process_identifier("phone", real_phone.group(1))

    momo_code = re.search(r'to\s+[A-Za-z\s]+\s+(\d{5})', text)
    if momo_code:
        return process_identifier("momo_code", momo_code.group(1))

    account_number = re.search(r'from\s+(\d{8,})', text)
    if account_number:
        return process_identifier("account_number", account_number.group(1))

    return {"type": None, "value": None}


def extract_sender(body):
    """Pull out who sent the money from the SMS body."""
    sender = {"name": None, "identifier": {"type": None, "value": None}}

    received_match = re.search(r'from\s+([A-Za-z\s]+)\s+\(', body)
    if received_match:
        sender["name"] = received_match.group(1).strip()
        sender["identifier"] = extract_identifier(body)
        return sender

    account_match = re.search(r'from\s+(\d{8,})', body)
    if account_match:
        sender["name"] = "Account Transfer"
        sender["identifier"] = extract_identifier(body)
        return sender

    return sender


def extract_receiver(body):
    """Pull out who received the money from the SMS body."""
    receiver = {"name": None, "identifier": {"type": None, "value": None}}

    transfer_match = re.search(r'transferred to\s+([A-Za-z\s]+)\s+\(', body)
    if transfer_match:
        receiver["name"] = transfer_match.group(1).strip()
        receiver["identifier"] = extract_identifier(body)
        return receiver

    payment_match = re.search(r'to\s+([A-Za-z\s]+)\s+\d{5}', body)
    if payment_match:
        receiver["name"] = payment_match.group(1).strip()
        receiver["identifier"] = extract_identifier(body)
        return receiver

    merchant_match = re.search(r'by\s+([A-Za-z\s]+)', body)
    if merchant_match:
        receiver["name"] = merchant_match.group(1).strip()
        receiver["identifier"] = {"type": "merchant", "value": "MERCHANT"}
        return receiver

    return receiver


# ---------- Main parsing function ----------

def load_transactions(xml_path=None):
    """
    Parse the XML file and return a dictionary of transactions keyed by
    a sequential transaction_id (1, 2, 3, ...).
    If no path is given, uses the default project location.
    """
    if xml_path is None:
        xml_path = DEFAULT_XML_PATH

    tree = ET.parse(xml_path)
    root = tree.getroot()

    transactions = {}
    transaction_id = 1

    for sms in root.findall("sms"):
        body = sms.get("body")

        amount = extract_money(r'(\d[\d,]*)\sRWF', body)
        fee = extract_money(r'Fee was[: ]\s*(\d[\d,]*)\sRWF', body)
        new_balance = extract_money(
            r'(?:new balance|NEW BALANCE)\s*[: ]+\s*(\d[\d,]*)\sRWF', body
        )

        category = detect_category(body)
        sender = extract_sender(body)
        receiver = extract_receiver(body)
        occurred_at = format_timestamp(sms.get("date"))
        financial_id = extract_financial_id(body)

        transaction = {
            "transaction_id": transaction_id,
            "financial_id": financial_id,
            "occurred_at": occurred_at,
            "amount": amount,
            "fee": fee,
            "new_balance": new_balance,
            "category": category,
            "sender": sender,
            "receiver": receiver,
            "body_raw": body,
            "log": {
                "level": "INFO",
                "message": "Transaction parsed successfully.",
                "timestamp": occurred_at,
            },
            "is_processed": True,
        }

        transactions[transaction_id] = transaction
        transaction_id += 1

    return transactions


def export_to_json(transactions, output_path=None):
    """Write the parsed transactions out to a JSON file."""
    if output_path is None:
        output_path = DEFAULT_JSON_OUTPUT

    with open(output_path, "w") as f:
        json.dump(transactions, f, indent=4)


# ---------- Run as a script ----------

if __name__ == "__main__":
    transactions = load_transactions()
    export_to_json(transactions)
    print(json.dumps(transactions, indent=4))
    print(f"\nParsed {len(transactions)} transactions.")
    print(f"Saved to: {DEFAULT_JSON_OUTPUT}")