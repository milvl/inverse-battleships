from typing import Dict
import json

def load_json(path: str) -> Dict:
    """
    Loads the JSON file from the given path.

    :param path: The path to the JSON file.
    :type path: str
    :return: The JSON file as a dictionary.
    :rtype: Dict
    """

    with open(path, 'r') as f:
        return json.load(f)


def hex_to_tuple(hex_str: str) -> tuple:
    """
    Converts a hexadecimal string to a tuple of integers.

    :param hex_str: The hexadecimal string.
    :type hex_str: str
    :return: The tuple of integers.
    :rtype: tuple
    """

    base = 16
    interval = 2
    iterable = (1, 3, 5)    # skip the '#' character
    return tuple(int(hex_str[i:i + interval], base) for i in iterable)
