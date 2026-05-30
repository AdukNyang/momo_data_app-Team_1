"""search algorithms for MOMO transactions: linear search and dictionary lookup"""
import sys
import time
from xml_parser import load_transactions


def linear_search(transactions, target_id):
    """this will loop through the transactions and find the one whose transaction id matches the target_id
    or returns None if no match is found"""
    for transaction in transactions:
        if transaction["transaction_id"] == target_id:
            return transaction
    return None


def dict_lookup(transactions, target_id):
    """look up a transaction directly by its id in the dictionary
    or returns None if no match is found"""
    return transactions.get(target_id)


def format_result(target_id: int, result) -> str:
    """Turn a search result into a one-line human-readable string"""
    if result is None:
        return f"id={target_id}: not found"
    return (
        f"Found id={target_id}: "
        f"{result['category']['name']}, "
        f"amount={result['amount']} RWF"
    )


def prompt_for_method():
    """Ask the user which search method they want to use
    Returns 'linear' or 'dict'"""
    print("Which search method do you want to use?")
    print("  [1] Linear search     - walks the list one item at a time. Slow on big data.")
    print("  [2] Dictionary lookup - jumps straight to the answer using a key. Fast.")
    while True:
        choice = input("Choose 1 or 2 (default 1): ").strip()
        if choice == "" or choice == "1":
            return "linear"
        if choice == "2":
            return "dict"
        print("Please enter 1 or 2.")


def interactive_loop(transactions_dict: dict, transactions_list: list) -> None:
    """Ask the user which method to use, then prompt for IDs until they quit"""
    method = prompt_for_method()
    if method == "dict":
        data, search_fn, label = transactions_dict, dict_lookup, "Dict lookup"
    else:
        data, search_fn, label = transactions_list, linear_search, "Linear search"

    print(f"\nYou picked: {label}.\n")
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

        start = time.perf_counter()
        result = search_fn(data, target_id)
        elapsed = time.perf_counter() - start

        print(f"[{label}] {elapsed:.6f}s")
        print(format_result(target_id, result))


if __name__ == "__main__":
    transactions_dict = load_transactions()
    transactions_list = list(transactions_dict.values())
    print(f"Loaded {len(transactions_list)} transactions.\n")

    if len(sys.argv) < 2:
        # No ID given — drop into interactive mode (which asks for method)
        interactive_loop(transactions_dict, transactions_list)
    else:
        # ID given on command line — one-shot search
        try:
            target_id = int(sys.argv[1])
        except ValueError:
            print(f"Error: '{sys.argv[1]}' is not a valid id.")
            sys.exit(1)

        # Method is optional second arg, defaults to 'linear'
        method = sys.argv[2].lower() if len(sys.argv) > 2 else "linear"

        if method == "dict":
            data, search_fn, label = transactions_dict, dict_lookup, "Dict lookup"
        elif method == "linear":
            data, search_fn, label = transactions_list, linear_search, "Linear search"
        else:
            print(f"Unknown method '{method}'. Use 'linear' or 'dict'.")
            sys.exit(1)

        start = time.perf_counter()
        result = search_fn(data, target_id)
        elapsed = time.perf_counter() - start

        print(f"[{label}] {elapsed:.6f}s")
        print(format_result(target_id, result))
