import threading
from typing import Any, Dict, List, Tuple
import pygame
from const.typedefs import IBAssets
from graphics.viewport import Viewport
from util.graphics import get_rendered_text_with_size


class GameSession(Viewport):
    """Represents the game session graphics context."""


    TEXT_UNSET = "ERROR"
    """The text to display when the text is unset."""
    RATIO_BOARD_TO_SCREEN_WIDTH = 0.8
    """The ratio of the board width to the screen width."""
    RATIO_INFO_PANEL_TO_SCREEN_WIDTH = (1 - RATIO_BOARD_TO_SCREEN_WIDTH) / 2
    """The ratio of the info panel width to the screen width."""
    RATIO_INFO_PANEL_TO_SCREEN_HEIGHT = 0.5
    """The ratio of the info panel height to the screen height."""
    RATIO_TEXT_WIDTH_TO_PANEL_WIDTH = 0.8
    """The ratio of the text width to the panel width."""
    RATIO_TEXT_HEIGHT_TO_PANEL_HEIGHT = 0.8
    """The ratio of the text height to the panel height."""


    def __init__(self, 
                 surface: pygame.Surface, 
                 assets: IBAssets, 
                 rlock: threading.RLock,
                 shared_data: Dict[str, Any]):

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
        self.__rlock = rlock

        master_display = pygame.display.get_surface()
        self.__background_color = self.__assets['colors']['black']
        self.__background = pygame.Rect(0, 0, master_display.get_width(), master_display.get_height())
        self.__text_color = self.__assets['colors']['white']

        with self.__rlock:
            self.__player_name = shared_data['player_name']
            self.__opponent_name = shared_data['opponent_name']
            self.__board = shared_data['board']
            self.__player_on_turn = shared_data['player_on_turn']
        
        self.__last_action = ""

    
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


    def __get_panel(self, width: int, height: int) -> pygame.Surface:
        """
        Gets a panel for the game session.

        :param width: The width of the panel.
        :type width: int
        :param height: The height of the panel.
        :type height: int
        :return: The panel.
        :rtype: pygame.Surface
        """

        panel = pygame.Surface((width, height))
        panel.fill(self.__background_color)
        panel_rect = panel.get_rect()
        panel_rect.topleft = (0, 0)

        return panel


    def __get_player_turn_panel(self, info_panel_width, info_panel_height, text_border_max_width, text_border_max_height) -> pygame.Surface:
        """
        Gets the player turn panel for the game session.

        :param info_panel_width: The width of the info panel.
        :type info_panel_width: int
        :param info_panel_height: The height of the info panel.
        :type info_panel_height: int
        :return: The player turn panel.
        :rtype: pygame.Surface
        """

        player_turn_panel = self.__get_panel(info_panel_width, info_panel_height)

        player_turn_panel_text = GameSession.TEXT_UNSET
        with self.__rlock:
            if self.__player_on_turn == self.__player_name:
                player_turn_panel_text = self.__assets['strings']['player_turn_panel_player']
            elif self.__player_on_turn == self.__opponent_name:
                player_turn_panel_text = self.__assets['strings']['player_turn_panel_opponent'] + self.__opponent_name

        player_turn_panel_text = f"{player_turn_panel_text}"
        player_turn_panel_text_surface = get_rendered_text_with_size(player_turn_panel_text, 
                                                                     text_border_max_width, 
                                                                     text_border_max_height,
                                                                     self.__text_color)
        
        text_top_left = (info_panel_width - player_turn_panel_text_surface.get_width()) // 2, \
                        (info_panel_height - player_turn_panel_text_surface.get_height()) // 2
        player_turn_panel.blit(player_turn_panel_text_surface, text_top_left)

        return player_turn_panel
    

    def __get_status_panel(self, info_panel_width, info_panel_height, text_border_max_width, text_border_max_height) -> pygame.Surface:
        """
        Gets the status panel for the game session.

        :param info_panel_width: The width of the info panel.
        :type info_panel_width: int
        :param info_panel_height: The height of the info panel.
        :type info_panel_height: int
        :return: The status panel.
        :rtype: pygame.Surface
        """

        status_panel = self.__get_panel(info_panel_width, info_panel_height)

        status_panel_text = GameSession.TEXT_UNSET
        with self.__rlock:
            if self.__player_on_turn == self.__player_name:
                status_panel_text = self.__assets['strings']['status_panel_take_turn_msg']
            elif self.__player_on_turn == self.__opponent_name:
                status_panel_text = self.__assets['strings']['status_panel_waiting_for_opponent_turn_msg']

        status_panel_text = f"{status_panel_text}"
        status_panel_text_surface = get_rendered_text_with_size(status_panel_text, 
                                                                text_border_max_width, 
                                                                text_border_max_height,
                                                                self.__text_color)
        
        text_top_left = (info_panel_width - status_panel_text_surface.get_width()) // 2, \
                        (info_panel_height - status_panel_text_surface.get_height()) // 2
        status_panel.blit(status_panel_text_surface, text_top_left)

        return status_panel
    

    def __get_last_action_panel(self, info_panel_width, info_panel_height, text_border_max_width, text_border_max_height) -> pygame.Surface:
        """
        Gets the last action panel for the game session.

        :param info_panel_width: The width of the info panel.
        :type info_panel_width: int
        :param info_panel_height: The height of the info panel.
        :type info_panel_height: int
        :return: The last action panel.
        :rtype: pygame.Surface
        """

        last_action_panel = self.__get_panel(info_panel_width, info_panel_height)

        last_action_panel_text = GameSession.TEXT_UNSET
        with self.__rlock:
            last_action_panel_text = self.__last_action

        last_action_panel_text = f"{last_action_panel_text}"
        last_action_panel_text_surface = get_rendered_text_with_size(last_action_panel_text, 
                                                                    text_border_max_width, 
                                                                    text_border_max_height,
                                                                    self.__text_color)
        
        text_top_left = (info_panel_width - last_action_panel_text_surface.get_width()) // 2, \
                        (info_panel_height - last_action_panel_text_surface.get_height()) // 2
        last_action_panel.blit(last_action_panel_text_surface, text_top_left)

        return last_action_panel
    

    def __get_score_panel(self, info_panel_width, info_panel_height, text_border_max_width, text_border_max_height) -> pygame.Surface:
        # TODO: Implement this method
        pass


    def __get_info_panels(self, 
                          info_panel_width, 
                          info_panel_height, 
                          text_border_max_width, 
                          text_border_max_height) -> Tuple[pygame.Surface, pygame.Surface, pygame.Surface, pygame.Surface]:
        """
        Gets the info panels for the game session.

        :param info_panel_width: The width of the info panel.
        :type info_panel_width: int
        :param info_panel_height: The height of the info panel.
        :type info_panel_height: int
        :return: The info panels.
        :rtype: Tuple[pygame.Surface, pygame.Surface, pygame.Surface, pygame.Surface]
        """

        # player turn panel
        player_turn_panel = self.__get_player_turn_panel(info_panel_width, info_panel_height, text_border_max_width, text_border_max_height)

        # status panel
        status_panel = self.__get_status_panel(info_panel_width, info_panel_height, text_border_max_width, text_border_max_height)

        # last action panel
        last_action_panel = self.__get_last_action_panel(info_panel_width, info_panel_height, text_border_max_width, text_border_max_height)

        # score panel
        score_panel = self.__get_score_panel(info_panel_width, info_panel_height, text_border_max_width, text_border_max_height)

        return player_turn_panel, status_panel, last_action_panel, score_panel



    def __draw_objects(self):
        """
        Draws the objects in the game session.

        :return: The select menu.
        :rtype: pygame.Surface
        """

        surface_width, surface_height = self.__surface.get_size()
        info_panel_width = surface_width * self.RATIO_INFO_PANEL_TO_SCREEN_WIDTH
        info_panel_height = surface_height * self.RATIO_INFO_PANEL_TO_SCREEN_HEIGHT
        text_border_max_width = info_panel_width * self.RATIO_TEXT_WIDTH_TO_PANEL_WIDTH
        text_border_max_height = info_panel_height * self.RATIO_TEXT_HEIGHT_TO_PANEL_HEIGHT

        # draw the info panels
        plyer_turn_panel, status_panel, last_action_panel, score_panel = self.__get_info_panels(info_panel_width, info_panel_height, text_border_max_width, text_border_max_height)


    def draw(self):
        """
        Draws the game session.

        :return: The select menu.
        :rtype: pygame.Surface
        """

        return self.__draw_objects()
        

    def redraw(self):
        """
        Redraws the game session. Expects that the entire screen is redrawn 
        with pygame.display.flip() after this method is called.
        """

        # update and draw the background
        surface_width, surface_height = self._surface.get_size()
        self.__background = pygame.Rect(0, 0, surface_width, surface_height)
        pygame.draw.rect(self._surface, self.__background_color, self.__background)

        # draw the objects
        self.__draw_objects()


    def update(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the game session.

        :param events: The events that occurred.
        :type events: Dict[str, Any]
        :return: Relevant information about the update.
        :rtype: Dict[str, Any]
        """

        result = {'graphics_update': False, 
                  'escape': False}


        return result