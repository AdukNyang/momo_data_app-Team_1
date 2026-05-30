"""Benchmark: linear search vs dictionary lookup for MoMo transactions."""
import time
from xml_parser import load_transactions
from search import linear_search, dict_lookup


def time_search(search_fn, data, ids, repeats):
    """Run search_fn(data, id) for every id in 'ids', repeated 'repeats' times.
    Returns the total seconds taken."""
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
