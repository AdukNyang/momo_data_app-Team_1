# ============================================
# IMPORTS
# ============================================

# ElementTree helps us read and navigate XML files
# This is Python's built-in XML parser
import xml.etree.ElementTree as ET

# re stands for Regular Expressions
# It helps us search and extract patterns from text
import re

# json helps us export Python dictionaries
# into real JSON files
import json

# datetime helps us convert timestamps
# into real human readable dates
from datetime import datetime


# ============================================
# HELPER FUNCTION:
# CONVERT XML TIMESTAMPS INTO REAL DATES
# ============================================

def format_timestamp(timestamp_ms):

    """
    This function converts XML time stamps which are store in miliseconds, to a real Python date
    We divide by 1000 becuase python datetime expects seconds yet its miliseconds. 

    """

    # Convert milliseconds into seconds
    timestamp_seconds = int(timestamp_ms) / 1000

    # Convert into Python datetime object
    dt = datetime.fromtimestamp(timestamp_seconds)

    # Return readable date format
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# ============================================
# HELPER FUNCTION:
# MASK PHONE NUMBERS
# ============================================

def mask_phone_number(phone):

    """
    This function masks real phone numbers
    for security purposes e.g 250791666666 to 2507******66

    """

    # Convert phone number into string so that we can easily manipulate the content
    phone = str(phone)

    # Get the first 3 digits
    start = phone[:3]

    # Get the last 3 digits
    end = phone[-3:]

    # Calculate how many characters to hide
    hidden_length = len(phone) - 6

    # Create hidden stars
    hidden = "*" * hidden_length

    # Combine all parts together
    return start + hidden + end


# ============================================
# HELPER FUNCTION:
# MASK ACCOUNT NUMBERS
# ============================================

def mask_account_number(account):

    """
    This function helps to mask bank account numbers, which are one of the most sensitive pieces of information. 
    Example:
    36521838 -> *****838

    """

    # Convert into string
    account = str(account)

    # Last 3 digits
    visible = account[-3:]

    # Calculate hidden section
    hidden_length = len(account) - 3

    # Create stars
    hidden = "*" * hidden_length

    # Combine hidden and visible
    return hidden + visible


# ============================================
# HELPER FUNCTION:
# PROCESS IDENTIFIERS
# ============================================

def process_identifier(identifier_type, raw_value):

    """
    This function helps identify if a person is using the phone number, account number, or momo_code, which later helps in giving more details about the user
    """

    # Phone numbers
    if identifier_type == "phone":

        return {
            "type": "phone",
            "value": mask_phone_number(raw_value)
        }

    # Bank account numbers
    elif identifier_type == "account_number":

        return {
            "type": "account_number",
            "value": mask_account_number(raw_value)
        }

    # MoMo codes
    elif identifier_type == "momo_code":

        return {
            "type": "momo_code",
            "value": raw_value
        }

    # Already masked numbers
    elif identifier_type == "masked_phone":

        return {
            "type": "phone",
            "value": raw_value
        }

    # Unknown identifiers
    return {
        "type": "unknown",
        "value": None
    }


# ============================================
# HELPER FUNCTION:
# EXTRACT MONEY VALUES
# ============================================

def extract_money(pattern, text):

    """
    This function gets amounts from raw long texts using regular expressions, then turns them into real numbers
    Example: "20,000" to 20000.0

    """

    # Search for pattern
    match = re.search(pattern, text)

    # If value found
    if match:

        # Extract amount
        amount = match.group(1)

        # Remove commas
        amount = amount.replace(",", "")

        # Convert into float
        return float(amount)

    return 0.0


# ============================================
# HELPER FUNCTION:
# EXTRACT FINANCIAL TRANSACTION ID
# ============================================

def extract_financial_id(body):

    """
    Extract transaction IDs from SMS.
    This works for both TxId and Financial Transaction Id:
    """

    match = re.search(
        r'(?:TxId:|Financial Transaction Id:)\s*([0-9]+)',
        body
    )

    if match:
        return match.group(1)

    return None


# ============================================
# HELPER FUNCTION:
# DETECT TRANSACTION CATEGORY
# ============================================

def detect_category(body):

    """
    Detect transaction type using SMS keywords.
    """

    body_lower = body.lower()

    # Incoming money
    if "received" in body_lower:

        return {
            "name": "Incoming Money",
            "type": "credit",
            "direction": "IN"
        }

    # Merchant payments
    elif "payment" in body_lower:

        return {
            "name": "Merchant Payment",
            "type": "debit",
            "direction": "OUT"
        }

    # Transfers
    elif "transferred to" in body_lower:

        return {
            "name": "Money Transfer",
            "type": "debit",
            "direction": "OUT"
        }

    # Bank deposits
    elif "bank deposit" in body_lower:

        return {
            "name": "Bank Deposit",
            "type": "credit",
            "direction": "IN"
        }

    # Airtime payments
    elif "airtime" in body_lower:

        return {
            "name": "Airtime Purchase",
            "type": "debit",
            "direction": "OUT"
        }

    # Unknown category
    return {
        "name": "Unknown",
        "type": "unknown",
        "direction": "UNK"
    }


# ============================================
# HELPER FUNCTION:
# EXTRACT IDENTIFIERS
# ============================================

def extract_identifier(text):

    """
    This function extracts and classifys identifiers like sender, reciever, with their important data e.g phone numbers, account numbers, and momo codes, and sensitive data is maseked for security purposes
    
    """

    # ========================================
    # MASKED PHONE NUMBER
    # Example: (*********013)
    # ========================================

    masked_phone = re.search(
        r'\((\*{5,}\d{3})\)',
        text
    )

    if masked_phone:

        raw_value = masked_phone.group(1)

        return process_identifier(
            "masked_phone",
            raw_value
        )

    # ========================================
    # REAL PHONE NUMBER
    # Example: (250791666666)
    # ========================================

    real_phone = re.search(
        r'\((2507\d{8})\)',
        text
    )

    if real_phone:

        raw_value = real_phone.group(1)

        return process_identifier(
            "phone",
            raw_value
        )

    # ========================================
    # MOMO CODE
    # Example:Jane Smith "12845"
    # ========================================

    momo_code = re.search(
        r'to\s+[A-Za-z\s]+\s+(\d{5})',
        text
    )

    if momo_code:

        raw_value = momo_code.group(1)

        return process_identifier(
            "momo_code",
            raw_value
        )

    # ========================================
    # ACCOUNT NUMBER
    # Example: from 36521838
    # ========================================

    account_number = re.search(
        r'from\s+(\d{8,})',
        text
    )

    if account_number:

        raw_value = account_number.group(1)

        return process_identifier(
            "account_number",
            raw_value
        )

    # If nothing found
    return {
        "type": None,
        "value": None
    }


# ============================================
# HELPER FUNCTION:
# EXTRACT SENDER INFORMATION
# ============================================

def extract_sender(body):

    """
    Extract sender information from different SMS formats.
    """

    # Initial sender
    sender = {
        "name": None,
        "identifier": {
            "type": None,
            "value": None
        }
    }

    # ========================================
    # RECEIVED MONEY FORMAT
    # Example: from Jane Smith (*********013)
    # ========================================

    received_match = re.search(
        r'from\s+([A-Za-z\s]+)\s+\(',
        body
    )

    if received_match:

        sender["name"] = received_match.group(1).strip()

        sender["identifier"] = extract_identifier(body)

        return sender

    # ========================================
    # ACCOUNT TRANSFER FORMAT
    # Example: from 36521838
    # ========================================

    account_match = re.search(
        r'from\s+(\d{8,})',
        body
    )

    if account_match:

        sender["name"] = "Account Transfer"

        sender["identifier"] = extract_identifier(body)

        return sender

    return sender


# ============================================
# HELPER FUNCTION:
# EXTRACT RECEIVER INFORMATION
# ============================================

def extract_receiver(body):

    """
    Extract receiver information from different sms messages

    """

    # initial reciever
    receiver = {
        "name": None,
        "identifier": {
            "type": None,
            "value": None
        }
    }

    # ========================================
    # TRANSFER FORMAT
    # Example: transferred to Samuel Carter (250791666666)
    # ========================================

    transfer_match = re.search(
        r'transferred to\s+([A-Za-z\s]+)\s+\(',
        body
    )

    if transfer_match:

        receiver["name"] = transfer_match.group(1).strip()

        receiver["identifier"] = extract_identifier(body)

        return receiver

    # ========================================
    # PAYMENT FORMAT
    # Example:to Jane Smith 12845
    # ========================================

    payment_match = re.search(
        r'to\s+([A-Za-z\s]+)\s+\d{5}',
        body
    )

    if payment_match:

        receiver["name"] = payment_match.group(1).strip()

        receiver["identifier"] = extract_identifier(body)

        return receiver

    # ========================================
    # MERCHANT FORMAT
    # Example: by DIRECT PAYMENT LTD
    # ========================================

    merchant_match = re.search(
        r'by\s+([A-Za-z\s]+)',
        body
    )

    if merchant_match:

        receiver["name"] = merchant_match.group(1).strip()

        receiver["identifier"] = {
            "type": "merchant",
            "value": "MERCHANT"
        }

        return receiver

    return receiver


# ============================================
# MAIN FUNCTION:
# LOAD AND PARSE TRANSACTIONS
# ============================================

def load_transactions():

    """
    Reads the xml file, extracts important values, cleans and structures data, and stores them inside a dictionary.
    Each transaction is a value of unique interger keys, that will help in hash map lookups

    """

    # Load XML file
    tree = ET.parse("../data/raw/modified_sms_v2.xml")

    # Get root <smses> element
    root = tree.getroot()

    # Dictionary storage
    transactions = {}

    # Auto increment transaction ID
    transaction_id = 1

    # Loop through every SMS
    for sms in root.findall("sms"):

        # Get raw SMS body
        body = sms.get("body")

        # Extract amount
        amount = extract_money(
            r'(\d[\d,]*)\sRWF',
            body
        )

        # Extract fee
        fee = extract_money(
            r'Fee was[: ]\s*(\d[\d,]*)\sRWF',
            body
        )

        # Extract new balance
        new_balance = extract_money(
            r'(?:new balance|NEW BALANCE)\s*[: ]+\s*(\d[\d,]*)\sRWF',
            body
        )

        # Detect transaction category
        category = detect_category(body)

        # Extract sender
        sender = extract_sender(body)

        # Extract receiver
        receiver = extract_receiver(body)

        # Convert timestamp
        occurred_at = format_timestamp(
            sms.get("date")
        )

        # Extract financial transaction ID
        financial_id = extract_financial_id(body)

        # ====================================
        # CREATE CLEAN TRANSACTION OBJECT
        # ====================================

        transaction = {

            # Internal system transaction ID
            "transaction_id": transaction_id,

            # Financial transaction ID from SMS
            "financial_id": financial_id,

            # Transaction date
            "occurred_at": occurred_at,

            # Numeric values
            "amount": amount,
            "fee": fee,
            "new_balance": new_balance,

            # Transaction category
            "category": category,

            # Sender details
            "sender": sender,

            # Receiver details
            "receiver": receiver,

            # Original SMS body
            "body_raw": body,

            # Logs help debugging and monitoring
            "log": {
                "level": "INFO",
                "message": "Transaction parsed successfully.",
                "timestamp": occurred_at
            },

            # Boolean value
            "is_processed": True
        }

        # Store transaction inside dictionary
        # using transaction_id as key
        transactions[transaction_id] = transaction

        # Increase transaction ID
        transaction_id += 1

    return transactions


# ============================================
# EXPORT TRANSACTIONS TO JSON FILE
# ============================================

def export_to_json(transactions):

    """
    Export parsed transactions into a real JSON file.
    Indent=4 makes the JSON easy for humans to read.
    """

    with open("parsed_transactions.json", "w") as json_file:

        json.dump(
            transactions,
            json_file,
            indent=4
        )


# ============================================
# RUN THE PARSER
# ============================================

# Parse all transactions
transactions = load_transactions()

# Export transactions into JSON
export_to_json(transactions)

# Print formatted JSON in terminal
print(
    json.dumps(
        transactions,
        indent=4
    )
)