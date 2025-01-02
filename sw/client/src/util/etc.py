"""
Module with miscellaneous utilities.
"""

def maintains_min_window_size(width: int, height: int, min_width: int, min_height: int) -> bool:
    """
    Checks if the given width and height are greater than or equal to the given minimum width and height.

    :param width: The width.
    :type width: int
    :param height: The height.
    :type height: int
    :param min_width: The minimum width.
    :type min_width: int
    :param min_height: The minimum height.
    :type min_height: int
    :return: True if the width and height are greater than or equal to the minimum width and height, False otherwise.
    :rtype: bool
    """
    
    return width >= min_width and height >= min_height


def get_scaled_resolution(width, height, ratio):
    """
    Calculate a scaled resolution based on the smaller dimension
    and a given aspect ratio as a float.

    Parameters:
    width (int): The width of the screen.
    height (int): The height of the screen.
    ratio (float): The aspect ratio as width / height.

    Returns:
    tuple: The scaled resolution (scaled_width, scaled_height).
    """
    if width / height < ratio:  # width is the limiting dimension
        scaled_width = width
        scaled_height = int(width / ratio)
    else:  # height is the limiting dimension
        scaled_width = int(height * ratio)
        scaled_height = height

    return scaled_width, scaled_height


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
