from typing import Any, Dict, List, Tuple
import pygame
from util.graphics import get_rendered_text_with_size
from graphics.viewport import Viewport
from const.typedefs import IBAssets
from graphics.menus.primitives import MenuOption, MenuTitle


class LobbySelect(Viewport):
    """
    Represents the lobby select screen.
    """

    def __init__(self, surface: pygame.Surface, assets: IBAssets, lobbies: List[MenuOption] = None):
        """
        Constructor method.

        :param surface: The surface to draw the lobby select screen on.
        :type surface: pygame.Surface
        :param assets: The assets of the game.
        :type assets: IBAssets
        :param lobbies: The lobbies to display.
        :type lobbies: List[MenuOption]
        """


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

        # if no options are present
        if lobbies is None:
            raise ValueError('No lobbies were provided.')
        self.__lobbies = lobbies
        self.__lobby_index = 0

        self.__left_arrow_rect = None
        self.__right_arrow_rect = None


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

    
    @property
    def selected_lobby_name(self) -> str:
        """
        Getter for the selected lobby name.

        :return: The name of the selected lobby.
        :rtype: str
        """

        return self.__lobbies[self.__lobby_index].text


    def __draw_objects(self):
        """
        Draws the objects on the lobby select screen.

        :return: The update rectangles.
        :rtype: List[pygame.Rect]
        """

        update_rects = []

        # define all availible positionings
        surface_width, surface_height = self.__surface.get_size()
        
        option_height = surface_height / 10
        option_width = surface_width * 0.5
        option_x = surface_width / 2        # MenuOption can center itself
        option_y = surface_height / 2
        
        title_height_bounds = surface_height / 5
        title_width_bounds = surface_width * 0.75
        # get the real title size
        title_surface = get_rendered_text_with_size(self.__assets['strings']['lobbies_label'], 
                                                    title_width_bounds,
                                                    title_height_bounds,
                                                    color=self.__assets['colors']['white'])
        title_width, title_height = title_surface.get_size()

        title_x = (surface_width / 2) - (title_width / 2)
        title_y = option_y - (option_height / 2) - title_height
        
        arrow_side = min(option_height, surface_width * 0.125)      # arrow will be sprite so it is based on upper left corner
        left_arrow_x = option_x - (option_width / 2) - arrow_side
        left_arrow_y = option_y - (option_height / 2)
        right_arrow_x = option_x + (option_width / 2)
        right_arrow_y = left_arrow_y

        # register user input bounding boxes
        self.__left_arrow_rect = pygame.Rect(left_arrow_x, left_arrow_y, arrow_side, arrow_side)
        self.__right_arrow_rect = pygame.Rect(right_arrow_x, right_arrow_y, arrow_side, arrow_side)

        # get the current lobby
        current_option = self.__lobbies[self.__lobby_index]
        
        # load the arrow sprite
        right_arrow_surface = pygame.transform.scale(self.__assets['sprites']['arrow'], (int(arrow_side), int(arrow_side)))
        left_arrow_surface = pygame.transform.flip(right_arrow_surface, True, False)

        # draw the objects
        # title
        self.__surface.blit(title_surface, (title_x, title_y))
        update_rects.append(pygame.Rect(title_x, title_y, title_width, title_height))
        
        # option
        option_rect = current_option.render(self.__surface, 
                                            (option_x, option_y), 
                                            option_height, 
                                            option_width, 
                                            centered=True,
                                            color=self.__assets['colors']['black'],
                                            background_color=self.__assets['colors']['white'],
                                            radius=option_height // 2
                                            )
        update_rects.append(option_rect)

        # arrows
        left_arrow_rect = self.__surface.blit(left_arrow_surface, (left_arrow_x, left_arrow_y))
        update_rects.append(left_arrow_rect)
        right_arrow_rect = self.__surface.blit(right_arrow_surface, (right_arrow_x, right_arrow_y))
        update_rects.append(right_arrow_rect)

        return update_rects


    def draw(self):
        """
        Draws the select menu.

        :return: The select menu.
        :rtype: pygame.Surface
        """

        return self.__draw_objects()
        

    def redraw(self):
        """
        Redraws the select menu. Expects that the entire screen is redrawn 
        with pygame.display.flip() after this method is called.
        """

        # update and draw the background
        surface_width, surface_height = self.__surface.get_size()
        self._background = pygame.Rect(0, 0, surface_width, surface_height)
        pygame.draw.rect(self.__surface, self.__assets['colors']['black'], self.__background)

        # draw the objects
        self.__draw_objects()

    
    def change_lobbies(self, lobbies: List[MenuOption], lobby_increment: int = 0):
        """
        Changes the lobbies displayed.

        :param lobbies: The new lobbies to display.
        :type lobbies: List[MenuOption]
        :param lobby_increment: The amount to increment the lobby index by.
        :type lobby_increment: int
        """

        self.__lobbies = lobbies
        self.__lobby_index = (self.__lobby_index + lobby_increment) % len(self.__lobbies)


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
                  'submit': False,
                  'escape': False}
        
        current_option = self.__lobbies[self.__lobby_index]
        
        # handle possible option click
        if events.get('mouse_click', False):
            if current_option.rect.collidepoint(events['mouse_click']):
                result['submit'] = True
                return result
            elif self.__left_arrow_rect.collidepoint(events['mouse_click']):
                self.change_lobbies(self.__lobbies, -1)
                result['graphics_update'] = True
            elif self.__right_arrow_rect.collidepoint(events['mouse_click']):
                self.change_lobbies(self.__lobbies, 1)
                result['graphics_update'] = True

        # handle keyboard input
        if events.get('direction', False):
            if events['direction'] == pygame.K_LEFT:
                self.change_lobbies(self.__lobbies, -1)
                result['graphics_update'] = True
            elif events['direction'] == pygame.K_RIGHT:
                self.change_lobbies(self.__lobbies, 1)
                result['graphics_update'] = True
        
        # handle enter key
        elif events.get('return', False):
            result['submit'] = True
            return result
        
        elif events.get('escape', False):
            result['escape'] = True
            return result

        return result
