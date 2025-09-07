from abc import ABC
import time
from typing import Tuple, Union
import pygame
from util.graphics import color_highlight, get_rendered_text_with_size


class RectText(ABC):
    """
    Represents a menu text (with additional rectangle with outline around it).
    """

    DEFAULT_TEXT_COLOR: tuple = (255, 255, 255)
    DEFAULT_FONT_SIZE: int = 36
    TEXT_ALIGN_CENTER: int = 0
    TEXT_ALIGN_LEFT: int = 1
    TEXT_ALIGN_RIGHT: int = 2


    def __init__(self, text: str):
        """
        Constructor for the MenuRectText class.
        
        :param text: The text of the object.
        :type text: str
        """

        self._text = text
        self.__rect = None


    @property
    def rect(self):
        """
        Getter for the rect property.

        :return: The rectangle of the text.
        :rtype: pygame.Rect
        """

        return self.__rect


    def render(self, 
               surface: pygame.display, 
               position: Tuple[int, int],
               height: int = DEFAULT_FONT_SIZE,
               width: int = DEFAULT_FONT_SIZE * 50,
               radius: int = -1,
               centered: bool = False,
               font_path: str = None, 
               color: Tuple[int, int, int] = DEFAULT_TEXT_COLOR,
               background_color: Union[Tuple[int, int, int], None] = None,
               outline_color: Union[Tuple[int, int, int], None] = None,
               text_align: int = TEXT_ALIGN_CENTER
               ) -> pygame.Rect:
        """
        Renders the text.
        Height is prefered because it is the implicit parameter for pygame.font.Font(None, height).

        :param surface: The surface to render the text to.
        :type surface: pygame.display
        :param position: The position to render the text at.
        :type position: tuple
        :param height: The height of the text, defaults to DEFAULT_FONT_SIZE
        :type height: int, optional
        :param width: The width of the text, defaults to DEFAULT_FONT_SIZE * 50
        :type width: int, optional
        :param radius: The radius of the rectangle, defaults to -1
        :type radius: int, optional
        :param centered: Whether to center the element, defaults to False
        :type centered: bool, optional
        :param font_path: The path to the font to use for rendering, defaults to None
        :type font_path: str, optional
        :param color: The color to use for rendering, defaults to DEFAULT_TEXT_COLOR
        :type color: tuple, optional
        :param background_color: The background color to use for rendering, defaults to None
        :type background_color: tuple, optional
        :param outline_color: The outline color to use for rendering, defaults to None
        :type outline_color: tuple, optional
        :param text_align: The text alignment, defaults to TEXT_ALIGN_CENTER
        :type text_align: int, optional
        :return: The rectangle of the rendered text.
        :rtype: pygame.Rect
        """

        text_to_rect_ratio: float = 0.8 if background_color else 1
        rect_to_outline_ratio: float = 0.9 if outline_color else 1

        rect_with_outline_height = height
        rect_with_outline_width = width if width else None
        rect_height = rect_with_outline_height * rect_to_outline_ratio
        rect_width = rect_with_outline_width * rect_to_outline_ratio if rect_with_outline_width else None
        text_height = rect_height * text_to_rect_ratio
        text_width = rect_width * text_to_rect_ratio if rect_width else None
        text_surface = get_rendered_text_with_size(self._text, text_width, text_height, font_path, color)

        pos_out_x, pos_out_y = position if not centered \
            else (position[0] - (rect_with_outline_width // 2), position[1] - (rect_with_outline_height // 2))
        
        pos_rect_x = pos_out_x + ((rect_with_outline_width - rect_width) // 2)
        pos_rect_y = pos_out_y + ((rect_with_outline_height - rect_height) // 2)

        # pos_text_x = pos_rect_x + ((rect_width - text_surface.get_width()) // 2)
        pos_text_x = pos_rect_x
        pos_text_y = pos_rect_y + ((rect_height - text_surface.get_height()) // 2)
        if text_align == RectText.TEXT_ALIGN_CENTER:
            pos_text_x += (rect_width - text_surface.get_width()) // 2
        elif text_align == RectText.TEXT_ALIGN_RIGHT:
            pos_text_x += rect_width - text_surface.get_width()


        # render the outline rectangle
        if outline_color:
            pygame.draw.rect(surface, 
                             outline_color, 
                             (pos_out_x, pos_out_y, rect_with_outline_width, rect_with_outline_height), 
                             border_radius=radius)

        # render the rectangle
        if background_color:
            pygame.draw.rect(surface, 
                             background_color, 
                             (pos_rect_x, pos_rect_y, rect_width, rect_height), 
                             border_radius=int(radius))

        # render the text
        surface.blit(text_surface, (pos_text_x, pos_text_y))

        self.__rect = pygame.Rect(pos_out_x, pos_out_y, rect_with_outline_width, rect_with_outline_height)
        return self.__rect


####################################################################################################
class MenuTitle(RectText):
    """
    Represents a menu title.
    """


    def __init__(self, text: str):
        """
        Constructor for the MenuTitle class.
        
        :param text: The text of the menu title.
        :type text: str
        """
        super().__init__(text)


####################################################################################################
class MenuOption(RectText):
    """
    Represents a menu option.
    """

    DEFAULT_FONT_SIZE = RectText.DEFAULT_FONT_SIZE
    DEFAULT_TEXT_COLOR = RectText.DEFAULT_TEXT_COLOR


    def __init__(self, text: str, highlighted: bool = False):
        """
        Constructor for the MenuOption class.
        
        :param text: The text of the menu option.
        :type text: str
        :param highlighted: Whether the menu option is highlighted, defaults to False
        :type highlighted: bool, optional
        """

        super().__init__(text)
        self.__highlighted = highlighted
    

    @property
    def text(self):
        """
        Getter for the text property.

        :return: The text of the menu option.
        :rtype: str
        """

        return self._text


    @property
    def highlighted(self):
        """
        Getter for the highlighted property.

        :return: Whether the menu option is highlighted.
        :rtype: bool
        """

        return self.__highlighted
    

    @highlighted.setter
    def highlighted(self, highlighted: bool):
        """
        Setter for the highlighted property.

        :param highlighted: Whether the menu option is highlighted.
        :type highlighted: bool
        """

        self.__highlighted = highlighted


    def render(self, 
               surface: pygame.Surface,
               position: 
               Tuple[int], 
               height: int = DEFAULT_FONT_SIZE, 
               width: int = DEFAULT_FONT_SIZE * 50, 
               radius: int = -1,
               centered: bool = False, 
               font_path: str = None, 
               color: Tuple[int] = DEFAULT_TEXT_COLOR, 
               background_color: Tuple[int] | None = None, 
               outline_color: Tuple[int] | None = None) -> pygame.Rect:
        """
        Renders the menu option.

        :param surface: The surface to render the menu option to.
        :type surface: pygame.Surface
        :param position: The position to render the menu option at.
        :type position: Tuple[int]
        :param height: The height of the menu option, defaults to DEFAULT_FONT_SIZE
        :type height: int, optional
        :param width: The width of the menu option, defaults to DEFAULT_FONT_SIZE * 50
        :type width: int, optional
        :param radius: The radius of the rectangle, defaults to -1 (90 degree corners)
        :type radius: int, optional
        :param centered: Whether to center the element, defaults to False
        :type centered: bool, optional
        :param font_path: The path to the font to use for rendering, defaults to None
        :type font_path: str, optional
        :param color: The color to use for rendering, defaults to DEFAULT_TEXT_COLOR
        :type color: Tuple[int], optional
        :param background_color: The background color to use for rendering, defaults to None
        :type background_color: Tuple[int] | None, optional
        :param outline_color: The outline color to use for rendering, defaults to None
        :type outline_color: Tuple[int] | None, optional
        :return: The rectangle of the rendered menu option.
        :rtype: pygame.Rect
        """

        res_bckg_color = background_color if not self.__highlighted else color_highlight(background_color)
        rect = super().render(surface, position, height, width, radius, centered, font_path, color, res_bckg_color, outline_color)

        return rect


####################################################################################################
class TextInput(RectText):
    """
    Represents a text input.
    """

    DEFAULT_FONT_SIZE = RectText.DEFAULT_FONT_SIZE
    DEFAULT_TEXT_COLOR = RectText.DEFAULT_TEXT_COLOR
    CURSOR = "|"
    CURSOR_BLINK_DELAY = 0.5


    def __init__(self, text: str, is_focused: bool = False):
        """
        Constructor for the TextInput class.

        :param text: The text of the text input.
        :type text: str
        :param is_focused: Whether the text input is focused, defaults to False
        :type is_focused: bool, optional
        """

        super().__init__(text)
        self.__is_focused = is_focused
        self.__last_time = time.time()
        self.__variants = [self._text, self._text + TextInput.CURSOR]
        self.__current_variant = 0
        self.__cursor_visible = False

    
    @property
    def is_focused(self):
        """
        Getter for the is_focused property.

        :return: Whether the text input is focused.
        :rtype: bool
        """

        return self.__is_focused
    

    @is_focused.setter
    def is_focused(self, is_focused: bool):
        """
        Setter for the is_focused property.

        :param is_focused: Whether the text input is focused.
        :type is_focused: bool
        """

        self.__is_focused = is_focused

    
    @property
    def text(self):
        """
        Getter for the text property.

        :return: The text of the text input.
        :rtype: str
        """

        return self._text
    

    @text.setter
    def text(self, text: str):
        """
        Setter for the text property.

        :param text: The text of the text input.
        :type text: str
        """

        self._text = text
        if self.__is_focused:
            self.__variants = [self._text, self._text + TextInput.CURSOR]
            self.__current_variant = 0
        
    
    @property
    def is_cursor_visible(self):
        """
        Getter for the is_cursor_visible property.

        :return: Whether the cursor is visible.
        :rtype: bool
        """

        if self.__is_focused:
            if time.time() - self.__last_time >= TextInput.CURSOR_BLINK_DELAY:
                self.__last_time = time.time()
                self.__current_variant = 1 - self.__current_variant
                self.__cursor_visible = not self.__cursor_visible
            
            self._text = self.__variants[self.__current_variant]

        return self.__cursor_visible

    
    def render(self, 
               surface: pygame.Surface, 
               position: Tuple[int], 
               height: int = DEFAULT_FONT_SIZE, 
               width: int = DEFAULT_FONT_SIZE * 50, 
               radius: int = -1, 
               centered: bool = False, 
               font_path: str = None, 
               color: Tuple[int] = DEFAULT_TEXT_COLOR, 
               background_color: Tuple[int] | None = None
               ) -> pygame.Rect:
        """
        Renders the text input.

        :param surface: The surface to render the text input to.
        :type surface: pygame.Surface
        :param position: The position to render the text input at.
        :type position: Tuple[int]
        :param height: The height of the text input, defaults to DEFAULT_FONT_SIZE
        :type height: int, optional
        :param width: The width of the text input, defaults to DEFAULT_FONT_SIZE * 50
        :type width: int, optional
        :param radius: The radius of the rectangle, defaults to -1 (90 degree corners)
        :type radius: int, optional
        :param centered: Whether to center the element, defaults to False
        :type centered: bool, optional
        :param font_path: The path to the font to use for rendering, defaults to None
        :type font_path: str, optional
        :param color: The color to use for rendering, defaults to DEFAULT_TEXT_COLOR
        :type color: Tuple[int], optional
        :param background_color: The background color to use for rendering, defaults to None
        :type background_color: Tuple[int] | None, optional
        :return: The rectangle of the rendered text input.
        :rtype: pygame.Rect
        """

        return super().render(surface, position, height, width, radius, centered, font_path, color, background_color, None, RectText.TEXT_ALIGN_LEFT)
