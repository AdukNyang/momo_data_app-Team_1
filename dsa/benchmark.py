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

if __name__ == "__main__":
    transactions_dict = load_transactions()
    transactions_list = list(transactions_dict.values())
    print(f"Loaded {len(transactions_list)} transactions.\n")

    test_ids = list(range(1, 1000, 40))
    test_ids.append(999999)
    repeats = 100

    print(f"Testing {len(test_ids)} ids, {repeats} repeats each.\n")

    linear_time = time_search(linear_search, transactions_list, test_ids, repeats)
    dict_time = time_search(dict_lookup, transactions_dict, test_ids, repeats)

    print(f"Linear search total time: {linear_time:.6f} seconds")
    print(f"Dict lookup total time:   {dict_time:.6f} seconds")
    print(f"Dict lookup is {linear_time / dict_time:.1f}x faster than linear search.")