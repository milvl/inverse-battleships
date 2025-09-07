"""
Module with file utilities.
"""

import json
from typing import Any, Dict


def load_json(path: str) -> Dict[str, Any]:
    """
    Loads the JSON file from the given path.

    :param path: The path to the JSON file.
    :type path: str
    :return: The JSON file as a dictionary.
    :rtype: Dict
    """

    with open(path, 'r') as f:
        return json.load(f)
    

