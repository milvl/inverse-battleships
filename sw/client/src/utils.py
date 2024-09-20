from typing import Dict, Tuple, Union
import json
import pygame

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


def get_rendered_text_with_size(text: str, width: int, height: int, font_path: str = None, color: Tuple[int, int, int] = (255, 255, 255)) -> pygame.Surface:
    """
    Renders the text with the given width and height limits.

    :param text: The text to render.
    :type text: str
    :param width: The width limit.
    :type width: int
    :param height: The height limit.
    :type height: int
    :param font_path: The path to the font to use for rendering, defaults to None
    :type font_path: str, optional
    :param color: The color to use for rendering, defaults to (255, 255, 255) (white)
    :type color: Tuple[int, int, int], optional
    :return: The rendered text.
    :rtype: pygame.Surface
    """

    # sanity check
    if not pygame.get_init():
        raise SystemError("pygame has not been initialized")
    if not pygame.font.get_init():
        raise SystemError("pygame.font has not been initialized")

    font = pygame.font.Font(font_path, int(height))
    
    surface = font.render(text, False, color)
    while surface.get_width() > width:
        height -= 1
        font = pygame.font.Font(font_path, int(height))
        surface = font.render(text, False, color)

    return surface

def color_highlight(color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]) -> Union[Tuple[int, int, int], Tuple[int, int, int, int]]:
    """
    Highlights the given color by increasing or decreasing its brightness.

    :param color: The color to highlight.
    :type color: _type_
    :return: _description_
    :rtype: _type_
    """

    # using the formula: 0.299*R + 0.587*G + 0.114*B
    luminance = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
    luminance_threshold = 128
    max_color_value = 255
    min_color_value = 0
    brightness_change = 0
    value_change = 75
    color_limit = None
    limiting_function = None

    color_highlighted = list(color)
    
    # if the color is more towards the darker spectrum, increase its brightness
    if luminance < luminance_threshold:
        # increase brightness by adding a constant to each component, without exceeding 255
        brightness_change = value_change
        color_limit = max_color_value
        limiting_function = min
    
    # if it's on the lighter spectrum, decrease its brightness
    else:
        # decrease brightness by subtracting a constant from each component, without going below 0
        brightness_change = -value_change
        color_limit = min_color_value
        limiting_function = max

    color_highlighted[0] = limiting_function(color_limit, color_highlighted[0] + brightness_change)
    color_highlighted[1] = limiting_function(color_limit, color_highlighted[1] + brightness_change)
    color_highlighted[2] = limiting_function(color_limit, color_highlighted[2] + brightness_change)
    color_highlighted = tuple(color_highlighted)

    return color_highlighted