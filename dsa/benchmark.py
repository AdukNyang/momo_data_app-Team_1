"""
Here we setup dictionary lookup
We Comparing two ways to find a transaction by id:
    1. Linear search   — walk the list one item at a time. O(n).
    2. Dictionary lookup — jump straight to the value by key. O(1) average.
"""
import time
from xml_parser import load_transactions
from search import linear_search

def dict_lookup(transactions, target_id):
    """Look up a transaction by id in a dict. O(1) average."""
    return transactions.get(target_id)

def time_search(search_fn, data, ids, repeats):
    """
    Run search_fn(data, id) for every id in 'ids', repeated 'repeats' times.
    Returns the total seconds taken.
    """
    start = time.perf_counter()
    for _ in range(repeats):
        for tid in ids:
            search_fn(data, tid)
    return time.perf_counter() - start