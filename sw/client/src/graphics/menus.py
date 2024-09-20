from typing import List, Dict, Tuple, Union
from abc import ABC, ABCMeta, abstractmethod
from sys import path

from loggers import get_temp_logger
tmp_logger = get_temp_logger('temp')
# TODO remove

from utils import get_rendered_text_with_size, color_highlight
from graphics.viewport import Viewport
from typedefs import IBAssets, PyGameEvents
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

        self.__text = text
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
        :return: The rectangle of the rendered text.
        """

        text_to_rect_ratio: float = 0.8 if background_color else 1
        rect_to_outline_ratio: float = 0.9 if outline_color else 1

        rect_with_outline_height = height
        rect_with_outline_width = width if width else None
        rect_height = rect_with_outline_height * rect_to_outline_ratio
        rect_width = rect_with_outline_width * rect_to_outline_ratio if rect_with_outline_width else None
        text_height = rect_height * text_to_rect_ratio
        text_width = rect_width * text_to_rect_ratio if rect_width else None
        text_surface = get_rendered_text_with_size(self.__text, text_width, text_height, font_path, color)

        pos_out_x, pos_out_y = position if not centered \
            else (position[0] - (rect_with_outline_width // 2), position[1] - (rect_with_outline_height // 2))
        pos_rect_x = pos_out_x + ((rect_with_outline_width - rect_width) // 2)
        pos_rect_y = pos_out_y + ((rect_with_outline_height - rect_height) // 2)
        pos_text_x = pos_rect_x + ((rect_width - text_surface.get_width()) // 2)
        pos_text_y = pos_rect_y + ((rect_height - text_surface.get_height()) // 2)

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

    DEFAULT_FONT_SIZE = MenuRectText.DEFAULT_FONT_SIZE
    DEFAULT_TEXT_COLOR = MenuRectText.DEFAULT_TEXT_COLOR


    def __init__(self, text: str, function: callable, highlighted: bool = False):
        """
        Constructor for the MenuOption class.
        
        :param text: The text of the menu option.
        :type text: str
        :param function: The function to execute when the menu option is selected.
        :type function: callable
        :param highlighted: Whether the menu option is highlighted, defaults to False
        :type highlighted: bool, optional
        """

        super().__init__(text)
        self.__function = function
        self.__highlighted = highlighted


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
        # TODO DOC
        res_bckg_color = background_color if not self.__highlighted else color_highlight(background_color)
        rect = super().render(surface, position, height, width, radius, centered, font_path, color, res_bckg_color, outline_color)

        return rect

    
    def execute(self):
        """
        Executes the function of the menu option.
        """

        self.__function()


####################################################################################################
class SelectMenu(Viewport):
    """
    Represents the select menu.
    """

    @staticmethod
    def __draw_options(surface: pygame.Surface, 
                       options: List[MenuOption], 
                       top_offset: int, 
                       option_height: int, 
                       option_width: int, 
                       option_x: int, 
                       assets: IBAssets, 
                       radius: int = -1):
        # TODO DOC

        update_rects = []
        for i, option in enumerate(options):
            y_offset = i * option_height
            y_offset_to_center = option_height // 2
            y_offset_gaps = (i + 1) * option_height
            option_y = top_offset + y_offset + y_offset_gaps + y_offset_to_center
            update_rect = option.render(surface, 
                                        (option_x, option_y), 
                                        height=option_height,
                                        width=option_width, 
                                        radius=radius,
                                        centered=True,
                                        color=assets['colors']['black'],
                                        background_color=assets['colors']['white'])
            update_rects.append(update_rect)
        
        return update_rects

    @staticmethod
    def __draw_title_and_options(surface: pygame.Surface, 
                                 title: MenuTitle, 
                                 options: List[MenuOption],
                                 scale_title_rect_radius_to_surface_width: float = 0.05, 
                                 scale_option_rect_radius_to_surface_width: float = 0.1,
                                 scale_title_area_to_screen_height: float = 0.35, 
                                 assets: IBAssets = None) -> List[pygame.Rect]:
        # TODO DOC, MAGIC NUMBERS

        update_rects = []
        surface_width, surface_height = surface.get_size()
        title_area_height = surface_height * scale_title_area_to_screen_height
        title_height = title_area_height * (1 / 2)
        title_width = surface_width * 0.65
        options_area_height = surface_height - title_area_height
        option_height = options_area_height / (len(options) + len(options) + 1)
        option_width = surface_width * 0.5

        title_x = surface_width // 2
        title_y = title_area_height * (2 / 3)
        update_rect = title.render(surface, 
                                   (title_x, title_y), 
                                   height=title_height, 
                                   width=title_width,
                                   radius=surface_width * scale_title_rect_radius_to_surface_width,
                                   centered=True,
                                   color=assets['colors']['black'],
                                   background_color=assets['colors']['white'])
        update_rects.append(update_rect)
        
        option_x = surface.get_width() // 2
        update_rects.extend(
            SelectMenu.__draw_options(surface, 
                                      options, 
                                      title_area_height, 
                                      option_height, 
                                      option_width, 
                                      option_x, 
                                      assets, 
                                      scale_option_rect_radius_to_surface_width * surface_width)
        )

        return update_rects
            

    @staticmethod
    def __draw_only_options(surface: pygame.Surface, options: List[MenuOption], assets: IBAssets):
        # TODO DOC

        update_rects = []
        option_height = surface.get_height() / (len(options) + len(options) + 1)
        option_width = surface.get_width() * 0.5
        option_x = surface.get_width() // 2

        update_rects.extend(SelectMenu.__draw_options(surface, options, 0, option_height, option_width, option_x, assets))


    def __init__(self, surface: pygame.Surface, assets: IBAssets, title: MenuTitle = None, options: List[MenuOption] = None, scale_title_area_to_screen_height: float = 0.25):
        # TODO DOC

        if not pygame.get_init():
            raise ValueError('The pygame module has not been initialized.')
        if not pygame.font.get_init():
            raise ValueError('The pygame.font module has not been initialized.')
        if not pygame.display.get_init():
            raise ValueError('The pygame.display module has not been initialized.')
        if not pygame.display.get_surface():
            raise ValueError('The pygame.display module has not have a surface to render to.')
        
        self.__surface = surface
        self.__assets = assets

        master_display = pygame.display.get_surface()
        self.__background = pygame.Rect(0, 0, master_display.get_width(), master_display.get_height())

        self.__title = title
        self.__options = options

        # if both title and options are present
        if self.__title and self.__options:
            self.__draw_objects = \
                lambda: SelectMenu.__draw_title_and_options(self.__surface, 
                                                            self.__title, 
                                                            self.__options, 
                                                            scale_title_area_to_screen_height=scale_title_area_to_screen_height, 
                                                            assets=self.__assets)

        # else if only options are present
        elif self.__options:
            self.__draw_objects = \
                lambda: SelectMenu.__draw_only_options(self.__surface, 
                                                       self.__options, 
                                                       self.__assets)
        
        # else if only title is present
        else:
            raise ValueError('The select menu must have at least one option otherwise it is useless.')

    
    @property
    def surface(self):
        """
        Getter for the surface property.

        :return: The surface of the select menu.
        :rtype: pygame.Surface
        """

        return self.__surface
    

    @surface.setter
    def surface(self, surface: pygame.Surface):
        """
        Setter for the surface property.

        :param surface: The surface to set the select menu to.
        :type surface: pygame.Surface
        """

        self.__surface = surface


    def draw(self):
        # TODO DOC

        return self.__draw_objects()
        

    def redraw(self):
        """
        Redraws the select menu. Expects that the entire screen is redrawn 
        with pygame.display.flip() after this method is called.
        """

        # update and draw the background
        surface_width, surface_height = self.__surface.get_size()
        self.__background = pygame.Rect(0, 0, surface_width, surface_height)
        pygame.draw.rect(self.__surface, self.__assets['colors']['black'], self.__background)
        tmp_logger.debug(f'Background: {self.__background}')

        # draw the objects
        self.__draw_objects()


    def update(self, events: PyGameEvents):
        """
        Updates the select menu.
        """

        updated = False

        if events.event_mousemotion:
            updated = True
            for option in self.__options:
                if option.rect.collidepoint(events.event_mousemotion.pos):
                    option.highlighted = True
                else:
                    option.highlighted = False
        
        return updated
        