"""
linear search for MOMO transaction
"""
import sys
from xml_parser import load_transactions

def linear_search(transactions, target_id):
    """
    this will loop through the transactions and find the one whose transaction id matches the target_id
    or returns None if no match is found
    """
    for transaction in transactions:
            if transaction["transaction_id"] == target_id:
                return transaction
    return None

def format_result(target_id: int, result) -> str:
    """Turn a search result into a one-line human-readable string."""
    if result is None:
        return f"id={target_id}: not found"
    return (
        f"Found id={target_id}: "
        f"{result['category']['name']}, "
        f"amount={result['amount']} RWF"
    )

def interactive_loop(transactions: list) -> None:
    """Prompt the user for IDs until they quit."""
    print("Enter a transaction ID to search (or 'q' to quit).")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if raw.lower() in ("q", "quit", "exit"):
            return
        try:
            target_id = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue
        print(format_result(target_id, linear_search(transactions, target_id)))

