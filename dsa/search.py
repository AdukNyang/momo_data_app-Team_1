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

