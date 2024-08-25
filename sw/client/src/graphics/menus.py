from typing import List, Dict, Tuple, Union
from abc import ABC, abstractmethod

from viewport import Viewport
from ..typedefs import PongGameAssets, PyGameEvents
import pygame


####################################################################################################
class MenuRectText(ABC):
    """
    Represents a menu text (with additional rectangle with outline around it).
    """

    DEFAULT_TEXT_COLOR: tuple = (255, 255, 255)
    DEFAULT_FONT_SIZE: int = 36


    def __init__(self, text: str):
        """
        Constructor for the MenuRectText class.
        
        :param text: The text of the object.
        :type text: str
        """

        self.text = text


    def render(self, 
               window: pygame.display, 
               position: Tuple[int, int],
               font: pygame.font.Font = None, 
               color: Tuple[int, int, int] = DEFAULT_TEXT_COLOR,
               background_color: Union[Tuple[int, int, int], None] = None,
               outline_color: Union[Tuple[int, int, int], None] = None,
               ):
        """
        Renders the text.

        :param window: The window to render the text to.
        :type window: pygame.display
        :param position: The position to render the text at.
        :type position: tuple
        :param font: The font to use for rendering, defaults to None
        :type font: pygame.font.Font, optional
        :param color: The color to use for rendering, defaults to DEFAULT_TEXT_COLOR
        :type color: tuple, optional
        """

        rect_to_text_ratio: float = 1.5
        rect_with_outline_to_rect_ratio: float = 1.1

        pos_x, pos_y = position

        if not font:
            font = pygame.font.Font(None, MenuOption.DEFAULT_FONT_SIZE)

        font_size = font.size(self.text)
        background_rect_outline = pygame.Rect(position, (font_size[0] * rect_to_text_ratio * rect_with_outline_to_rect_ratio, font_size[1] * rect_to_text_ratio * rect_with_outline_to_rect_ratio))
        rect_width = font_size[0] * rect_to_text_ratio
        rect_height = font_size[1] * rect_to_text_ratio
        rect_pos = (pos_x + (background_rect_outline.width - rect_width) // 2, pos_y + (background_rect_outline.height - rect_height) // 2)
        background_rect = pygame.Rect(rect_pos, (rect_width, rect_height))

        if outline_color:
            pygame.draw.rect(window, outline_color, background_rect_outline)
        if background_color:
            if not outline_color:
                pygame.draw.rect(window, color, background_rect_outline)
            pygame.draw.rect(window, background_color, background_rect)
        
        text = font.render(self.text, True, color)
        window.blit(text, (pos_x + (background_rect.width - font_size[0]) // 2, pos_y + (background_rect.height - font_size[1]) // 2))


####################################################################################################
class MenuTitle(MenuRectText):
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
class MenuOption(MenuRectText):
    """
    Represents a menu option.
    """


    def __init__(self, text: str, function: callable):
        """
        Constructor for the MenuOption class.
        
        :param text: The text of the menu option.
        :type text: str
        :param function: The function to execute when the menu option is selected.
        :type function: callable
        """
        super().__init__(text)
        self.function = function
    
    
    def execute(self):
        """
        Executes the function of the menu option.
        """

        self.function()


####################################################################################################
class SelectMenu(Viewport):
    """
    Represents the select menu.
    """

    def __init__(self, window: pygame.Surface, assets: PongGameAssets, title: MenuTitle = None, options: List[MenuOption] = None):
        # TODO DOC

        if not pygame.get_init():
            raise ValueError('The pygame module has not been initialized.')
        if not pygame.font.get_init():
            raise ValueError('The pygame.font module has not been initialized.')
        if not pygame.display.get_init():
            raise ValueError('The pygame.display module has not been initialized.')
        if not pygame.display.get_surface():
            raise ValueError('The pygame.display module has not have a surface to render to.')
        
        self.window = window
        self.assets = assets

        self.background = pygame.Surface(self.window.get_size())
        self.background.fill(self.assets['colors']['black'])

        self.title = title
        self.options = options
        

    def render(self, scale_title_to_options: float = 1.5):
        """
        Renders the select menu.

        :param scale_title_to_options: The scale factor to use to scale the title to the options, defaults to 1.5
        :type scale_title_to_options: float, optional
        """

        # draw the background
        self.window.blit(self.background, (0, 0))

        # check for drawables
        # if both title and options are present
        if self.title and self.options:

            return

        # else if only title is present
        elif self.title:
            return

        # else if only options are present
        elif self.options:
            return

        # else if neither title nor options are present
        else:
            return


    def update(self, events: PyGameEvents):
        """
        Updates the select menu.
        """

        pass