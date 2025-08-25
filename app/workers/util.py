import json
import hashlib
import pandas as pd


def deep_merge(dict1, dict2):
    """
    Recursively merges dict2 into dict1.
    """

    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            # If both values are dictionaries, merge them recursively
            deep_merge(dict1[key], value)
        else:
            # Otherwise, update or add the key-value pair
            dict1[key] = value
    return dict1


def is_dates_v1(strings: list[str]) -> bool:
    """
    Checks if list of strings are all valid dates.

    Returns:
        bool: True if all strings are valid dates, False otherwise.
    """

    # Attempt to convert the list to a datetime Series.
    # errors='coerce' will turn any invalid dates into NaT.
    s = pd.to_datetime(strings, errors="coerce")

    # Check if there are any NaT values in the Series.
    # If there are, it means at least one string was not a valid date.
    return not s.isna().any()


from dateutil.parser import parse


def is_dates(strings: list[str]) -> bool:
    """
    Checks if list of strings are all valid dates.

    Args:
        strings (list[str]): A list of strings to check.

    Returns:
        bool: True if all strings are valid dates, False otherwise.
    """

    if not strings:
        return False

    for s in strings:
        try:
            parse(s, fuzzy=False)
        except (ValueError, TypeError):
            return False

    return True


def hash_data(data: dict) -> str:
    """
    Hashes a dictionary to create a deterministic ID.
    """

    data_string = json.dumps(data, sort_keys=True)
    full_hash = hashlib.sha256(data_string.encode("utf-8")).hexdigest()

    # For a 8 character hash, you need 23.7 million items to have
    # a 50% chance of collision, which is acceptable considering
    # this is not a multi-user high volume application.
    return full_hash[:8]
