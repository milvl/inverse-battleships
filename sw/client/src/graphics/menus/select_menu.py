from typing import Any, Dict, List
import pygame
from sw.client.src.graphics.viewport import Viewport
from const.typedefs import IBAssets
from graphics.menus.primitives import MenuOption, MenuTitle


class SelectMenu(Viewport):
    """
    Represents the select menu.
    """


    @staticmethod
    def handle_exit(self):
        # TODO DOC

        self.update_result.exit = True


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
        
        return update_rects


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
        self.__highlighted_option_index = -1

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
    

    @property
    def selected_option_text(self):
        """
        Getter for the selected_option_text property.

        :return: The text of the selected option.
        :rtype: str
        """

        return self.__options[self.highlighted_option_index].text
    

    @surface.setter
    def surface(self, surface: pygame.Surface):
        """
        Setter for the surface property.

        :param surface: The surface to set the select menu to.
        :type surface: pygame.Surface
        """

        self.__surface = surface

    
    @property
    def highlighted_option_index(self):
        """
        Getter for the highlighted_option_index property.

        :return: The index of the highlighted option.
        :rtype: int
        """

        return self.__highlighted_option_index
    

    def set_highlighted_option_index(self, index: int):
        """
        Setter for the highlighted_option_index property.
        Keeps the index within the bounds of the options list.

        :param index: The index of the option to highlight.
        :type index: int
        """

        if self.__highlighted_option_index != -1:
            self.__options[self.__highlighted_option_index].highlighted = False
        index = index % len(self.__options)
        self.__highlighted_option_index = index
        self.__options[self.__highlighted_option_index].highlighted = True
    

    def unset_highlighted_option_index(self):
        """
        Unsets the highlighted option index.
        """

        if self.__highlighted_option_index != -1:
            self.__options[self.__highlighted_option_index].highlighted = False
            self.__highlighted_option_index = -1


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

        # draw the objects
        self.__draw_objects()


    def update(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the select menu.

        :param events: The events that occurred.
        :type events: Dict[str, Any]
        :return: Relevant information about the update.
        :rtype: Dict[str, Any]
        """

        result = {'graphics_update': False, 
                  'option_selected': -1, 
                  'submit': False}

        result['option_selected'] = self.highlighted_option_index

        # handle possible option hover
        if events.get('mouse_motion', False):
            if self.highlighted_option_index != -1:
                self.unset_highlighted_option_index()
                result['graphics_update'] = True

            for i, option in enumerate(self.__options):
                if option.rect.collidepoint(events['mouse_motion']):
                    if not option.highlighted:
                        self.set_highlighted_option_index(i)
                        result['graphics_update'] = True
                    break
        
        # handle possible option click
        if events.get('mouse_click', False):
            if self.__options[self.highlighted_option_index].rect.collidepoint(events['mouse_click']):
                result['submit'] = True
                return result

        # handle keyboard input
        if events.get('direction', False):
            if self.highlighted_option_index != -1:
                if events['direction'] == pygame.K_DOWN:
                    self.set_highlighted_option_index(self.highlighted_option_index + 1)
                    result['graphics_update'] = True
                elif events['direction'] == pygame.K_UP:
                    self.set_highlighted_option_index(self.highlighted_option_index - 1)
                    result['graphics_update'] = True
            else:
                self.set_highlighted_option_index(0)
                result['graphics_update'] = True
        
        # handle enter key
        if events.get('return', False):
            result['submit'] = True
            return result

        return result
