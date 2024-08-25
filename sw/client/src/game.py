from typing import List, Dict, Tuple
from graphics.menus import SelectMenu
from utils import maintains_min_window_size
from typedefs import PongGameConfig, PongGameDebugInfo, PongGameUpdateResult, PyGameEvents
import random
from copy import deepcopy
from player import PongPlayer
import pygame
from pygame.locals import *

def debug_get_random_color() -> Tuple[int, int, int]:
    """
    Returns a random color.

    :return: A random color that is represented as a tuple of three integers.
    :rtype: Tuple[int, int, int]
    """

    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def __create_players(player_names: List[str]) -> List[PongPlayer]:
    # TODO magic num
    if len(player_names) != 2:
        raise ValueError('The number of players must be 2.')
    
    players = []
    is_left = True
    for name in player_names:
        players.append(PongPlayer(name, is_left))
        is_left = not is_left
    
    return players

class PongGameState:
    # TODO DOC
    INTRO_SEQUENCE = -1
    MAIN_MENU = 0
    SETTINGS_MENU = 1
    CONNECTION_MENU = 2
    LOBBY_SELECTION = 3
    LOBBY = 4
    GAME_SESSION = 5
    GAME_END = 6

    @staticmethod
    def get_state_name(state: int) -> str:
        """
        Returns the name of the state.

        :param state: The state.
        :type state: int
        :return: The name of the state.
        :rtype: str
        """

        return {
            PongGameState.INTRO_SEQUENCE: 'INTRO_SEQUENCE',
            PongGameState.MAIN_MENU: 'MAIN_MENU',
            PongGameState.SETTINGS_MENU: 'SETTINGS_MENU',
            PongGameState.CONNECTION_MENU: 'CONNECTION_MENU',
            PongGameState.LOBBY_SELECTION: 'LOBBY_SELECTION',
            PongGameState.LOBBY: 'LOBBY',
            PongGameState.GAME_SESSION: 'GAME_SESSION',
            PongGameState.GAME_END: 'GAME_END'
        }.get(state, 'UNKNOWN_STATE')


class PongGame:
    # TODO DOC

    def __init__(self, config: Dict, assets: Dict, display_debug_info: bool = False):
        # TODO DOC
        self.config = deepcopy(config)
        self.assets = deepcopy(assets)
        self.display_debug_info = display_debug_info

        self.started = False


    def __get_debug_info_object(self):
        # TODO DOC
        if not pygame.get_init():
            raise ValueError('The pygame module has not been initialized.')
        if not pygame.font.get_init():
            raise ValueError('The pygame.font module has not been initialized.')

        # display debug info in the bottom left corner of the window
        # create a new font object
        font = pygame.font.Font(None, 25)
        # create a new text surface
        text = font.render(str(self.debug_info), True, self.assets['colors']['white'], self.assets['colors']['black'])
        
        return text


    def start(self):
        pygame.init()
        pygame.font.init()
        self.window: pygame.display = pygame.display.set_mode((self.config['window_width'], self.config['window_height']), pygame.RESIZABLE)
        pygame.display.set_caption(self.assets['strings']['window_title'])
        
        self.state = PongGameState.INTRO_SEQUENCE
        # self.debug_info: PongGameDebugInfo = {'game_state': PongGameState.get_state_name(self.state), 'dimensions': self.window.get_size(), 'last_reg_key': None}
        self.debug_info: PongGameDebugInfo = PongGameDebugInfo(game_state=PongGameState.get_state_name(self.state), dimensions=self.window.get_size(), last_reg_key=None)
        self.debug_info_render = self.__get_debug_info_object()
        self.window.blit(self.debug_info_render, (0, self.window.get_height() - self.debug_info_render.get_height()))

        self.started = True

    
    def __get_pygame_events(self) -> PyGameEvents:
        """
        Returns the PyGame events.

        :return: The PyGame events.
        :rtype: PyGameEvents
        """

        events: PyGameEvents = PyGameEvents()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.event_quit = event
                continue

            if event.type == pygame.KEYDOWN:
                events.event_keydown = event
                continue

            if event.type == pygame.KEYUP:
                events.event_keyup = event
                continue

            if event.type == pygame.MOUSEMOTION:
                events.event_mousemotion = event
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                events.event_mousebuttondown = event
                continue

            if event.type == pygame.MOUSEBUTTONUP:
                events.event_mousebuttonup = event
                continue

            if event.type == pygame.VIDEORESIZE:
                if not maintains_min_window_size(event.dict['w'], event.dict['h'], self.config['min_window_width'], self.config['min_window_height']):
                    pygame.display.set_mode((self.config['min_window_width'], self.config['min_window_height']), pygame.RESIZABLE)
                events.event_videoresize = event
                continue

        return events
    

    def __update_game_session(self, events: PyGameEvents) -> PongGameUpdateResult:
        raise NotImplementedError('The __update_game_session method has not been implemented yet.')


    def __update_lobby(self, events: PyGameEvents) -> PongGameUpdateResult:
        raise NotImplementedError('The __update_lobby method has not been implemented yet.')


    def __update_lobby_selection(self, events: PyGameEvents) -> PongGameUpdateResult:
        raise NotImplementedError('The __update_lobby_selection method has not been implemented yet.')


    def __update_connection_menu(self, events: PyGameEvents) -> PongGameUpdateResult:
        raise NotImplementedError('The __update_connection_menu method has not been implemented yet.')


    def __update_game_end(self, events: PyGameEvents) -> PongGameUpdateResult:
        raise NotImplementedError('The __update_game_end method has not been implemented yet.')


    def __update_main_menu(self, events: PyGameEvents) -> PongGameUpdateResult:
        # if no menu was drawn, prepare it and draw it
        if not hasattr(self, 'menu'):
            self.menu = SelectMenu(self.window, self.assets)
            self.menu.add_options()
            
            self.menu.render()

        # catch input of user and update the menu accordingly


    def __update_settings_menu(self, events: PyGameEvents) -> PongGameUpdateResult:
        raise NotImplementedError('The __update_settings_menu method has not been implemented yet.')
    

    def update(self) -> PongGameUpdateResult:
        # sanity check
        if not self.started:
            raise ValueError('The game has not been started yet.')

        # result: PongGameUpdateResult = {'update': False, 'exit': False}
        result: PongGameUpdateResult = PongGameUpdateResult(update=False, exit=False)
        events = self.__get_pygame_events()
        
        # user requests to quit
        if events.event_quit:
            pygame.quit()
            result.exit = True
            return result
            
        # user attempts to resize the window
        elif events.event_videoresize:
            self.debug_info.dimensions = events.event_videoresize.dict['size']
            result.update = True

        # ignore all events that are not of interest
        if self.state == PongGameState.INTRO_SEQUENCE:
            if not getattr(self, 'last_time', None):
                self.last_time = pygame.time.get_ticks()
            else:
                if pygame.time.get_ticks() - self.last_time >= 5000:
                    self.state = PongGameState.MAIN_MENU
                    del self.last_time
                    result.update = True
        
        # handle events that are of interest
        else:
            # capture the last key pressed for debugging purposes
            if self.display_debug_info:
                if events.event_keydown:
                    self.debug_info.last_reg_key = pygame.key.name(events.event_keydown.key)
                    result.update = True

            # ordered by the most prioritized states (microoptimization)
            if self.state == PongGameState.GAME_SESSION:
                self.__update_game_session(events)
            elif self.state == PongGameState.LOBBY:
                self.__update_lobby(events)
            elif self.state == PongGameState.LOBBY_SELECTION:
                self.__update_lobby_selection(events)
            elif self.state == PongGameState.CONNECTION_MENU:
                self.__update_connection_menu(events)
            elif self.state == PongGameState.GAME_END:
                self.__update_game_end(events)
            elif self.state == PongGameState.MAIN_MENU:
                self.__update_main_menu(events)
            elif self.state == PongGameState.SETTINGS_MENU:
                self.__update_settings_menu(events)
            elif self.state == PongGameState.INTRO_SEQUENCE:
                raise SystemError('The INTRO_SEQUENCE state should have been handled before this point.')
            else:
                raise SystemError('Unknown state.')

        # additional render surface overlay
        if result.update:
            # render the debug info if allowed
            if self.display_debug_info:
                self.debug_info.game_state = PongGameState.get_state_name(self.state)
                self.debug_info_render = self.__get_debug_info_object()
                self.window.blit(self.debug_info_render, (0, self.window.get_height() - self.debug_info_render.get_height()))
        
        return result
