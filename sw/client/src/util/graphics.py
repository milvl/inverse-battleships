"""
Module with graphics utilities (some dependent on Pygame).
"""

import random
from typing import Tuple, Union
import pygame


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

    scale_ratio = 0.8

    font = pygame.font.Font(font_path, int(height))
    
    surface = font.render(text, False, color)
    while surface.get_width() > width:
        height *= scale_ratio
        font = pygame.font.Font(font_path, int(height))
        surface = font.render(text, False, color)

    return surface


def color_highlight(color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]) -> Union[Tuple[int, int, int], Tuple[int, int, int, int]]:
    """
    Highlights the given color by increasing or decreasing its brightness.

    :param color: The color to highlight.
    :type color: Tuple[int, int, int]
    :return: The highlighted color.
    :rtype: Tuple[int, int, int]
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


def color_make_seethrough(color: Union[Tuple[int, int, int], Tuple[int, int, int, int]], alpha: int = 20) -> Union[Tuple[int, int, int], Tuple[int, int, int, int]]:
    """
    Makes the given color seethrough by adding an alpha value.

    :param color: The color to make seethrough.
    :type color: Tuple[int, int, int]
    :param alpha: The alpha value to add, defaults to 50
    :type alpha: int, optional
    :return: The seethrough color.
    :rtype: Tuple[int, int, int, int]
    """

    if len(color) == 3:
        return color + (alpha,)
    elif len(color) == 4:
        return color[:3] + (alpha,)
    else:
        raise ValueError("Invalid color tuple length")
    

def debug_get_random_color() -> Tuple[int, int, int]:
    """
    Returns a random color.

    :return: A random color that is represented as a tuple of three integers.
    :rtype: Tuple[int, int, int]
    """

    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))