"""
Module with the InfoScreen class, which shows the user information about the game.
"""

from typing import Any, Dict, List
import pygame
from const.typedefs import IBAssets
from graphics.menus.select_menu import MenuOption
from graphics.menus.select_menu import SelectMenu

class InfoScreen(SelectMenu):
    """
    InfoScreen class, which shows the user information about the game.

    :param SelectMenu: The parent class of InfoScreen.
    :type SelectMenu: class
    """

    @staticmethod
    def _draw_only_options(surface: pygame.Surface, 
                           options: List[MenuOption], 
                           assets: IBAssets, 
                           scale_option_rect_radius_to_surface_width: float = 0.1) -> List[pygame.Rect]:
        """
        Custom draw method for the InfoScreen that only draws the options.

        :param surface: The screen to draw the InfoScreen on.
        :type surface: pygame.Surface
        :param options: The options to draw.
        :type options: List[MenuOption]
        :param assets: The assets of the game.
        :type assets: IBAssets
        :param scale_option_rect_radius_to_surface_width: The scale of the option rect radius to the surface width.
        :type scale_option_rect_radius_to_surface_width: float
        :return: The update rectangles.
        :rtype: List[pygame.Rect]
        """

        update_rects = []
        surface_width, surface_height = surface.get_size()
        option_height = surface.get_height() / (len(options) + len(options) + 1)
        option_width = surface.get_width() * 0.5
        option_x = surface.get_width() // 2

        update_rects.extend(
            SelectMenu._draw_options(surface, 
                                     options, 
                                     0, 
                                     option_height, 
                                     option_width, 
                                     option_x, 
                                     scale_option_rect_radius_to_surface_width * surface_width,
                                     assets['colors']['white'],
                                     None)
        )
        
        return update_rects
    

    def __init__(self, surface: pygame.Surface, assets: IBAssets, info_text: str = ""):
        """
        Constructor method.

        :param surface: The screen to draw the InfoScreen on.
        :type surface: pygame.Surface
        :param assets: The assets of the game.
        :type assets: IBAssets
        :param info_text: The text to show on the InfoScreen.
        :type info_text: str
        """
        
        if not pygame.get_init():
            raise ValueError('The pygame module has not been initialized.')
        if not pygame.font.get_init():
            raise ValueError('The pygame.font module has not been initialized.')
        if not pygame.display.get_init():
            raise ValueError('The pygame.display module has not been initialized.')
        if not pygame.display.get_surface():
            raise ValueError('The pygame.display module has not have a surface to render to.')
        
        super().__init__(surface, assets, None, [MenuOption(info_text)])

        # force the InfoScreen to only draw the options
        self._draw_objects = lambda: __class__._draw_only_options(self._surface, 
                                                                    self._options, 
                                                                    self._assets)

        self._highlighted_option_index = -1


    def update(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the InfoScreen.

        :param events: The events that have occurred.
        :type events: Dict[str, Any]
        :return: The events that have occurred.
        :rtype: Dict[str, Any]
        """

        events['mouse_click'] = False
        res = super().update(events)
        res = {'graphics_update': res['graphics_update'], 'submit': res['submit'], 'escape': res['escape']}
        if events.get('return', False):
            res['submit'] = True
        self.unset_highlighted_option_index()

        return res

    # NOTE: rest of the methods are inherited from SelectMenu