"""
Here we setup dictionary lookup

"""
import time
from xml_parser import load_transactions
from search import linear_search

def dict_lookup(transactions, target_id):
    """Look up a transaction by id in a dict. O(1) average."""
    return transactions.get(target_id)