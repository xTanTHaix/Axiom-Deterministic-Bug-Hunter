"""
Sample Python file with resource leaks and off-by-one errors (for testing Layer 3 & Layer 4)
"""


def read_config_file(filepath: str) -> str:
    # Bug: Unmanaged open without with-statement
    f = open(filepath, "r")
    data = f.read()
    return data


def process_items(items: list) -> list:
    results = []
    # Bug: Off-by-one error with index access
    for i in range(len(items) - 1):
        results.append(items[i] + items[i + 1])
    return results


def risky_handler():
    try:
        x = 1 / 0
    except:
        pass
