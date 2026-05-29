"linear search for MOMO transaction "

from xml_parser import load_transactions

def linear_search(transactions, target_id):
    """
    this will loop throught the transactions and find the one whose transaction id matches the target_id
    """
    for transaction in transactions:
            if transaction["transaction_id"] == target_id:
                return transaction
    return None

