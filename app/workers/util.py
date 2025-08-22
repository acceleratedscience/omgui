def deep_merge(dict1, dict2):
    """Recursively merges dict2 into dict1."""
    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            # If both values are dictionaries, merge them recursively
            deep_merge(dict1[key], value)
        else:
            # Otherwise, update or add the key-value pair
            dict1[key] = value
    return dict1
