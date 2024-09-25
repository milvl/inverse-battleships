from const import MAIN_LOGGER_NAME
from utils import loggers
from pprint import pformat
from typing import List, Dict, Tuple, Union, Optional
from graphics.menus import SelectMenu, MenuTitle, MenuOption
from utils import maintains_min_window_size, color_make_seethrough
from typedefs import IBGameDebugInfo, IBGameUpdateResult, PyGameEvents
import random
from copy import deepcopy
from player import IBPlayer
import pygame
from pygame.locals import *

logger = loggers.get_logger(MAIN_LOGGER_NAME)
# TODO remove
tmp_logger = loggers.get_temp_logger('temp')


def debug_get_random_color() -> Tuple[int, int, int]:
    """
    Returns a random color.

    :return: A random color that is represented as a tuple of three integers.
    :rtype: Tuple[int, int, int]
    """

    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def __create_players(player_names: List[str]) -> List[IBPlayer]:
    # TODO magic num
    if len(player_names) != 2:
        raise ValueError('The number of players must be 2.')
    
    players = []
    is_left = True
    for name in player_names:
        players.append(IBPlayer(name, is_left))
        is_left = not is_left
    
    return players

class IBGameState:
    # TODO DOC
    INTRO_SEQUENCE = -1
    MAIN_MENU = 0
    SETTINGS_MENU = 1
    CONNECTION_MENU = 2
    LOBBY_SELECTION = 3
    LOBBY = 4
    GAME_SESSION = 5
    GAME_END = 6


    def __init__(self):
        # TODO DOC
        self.__state = IBGameState.INTRO_SEQUENCE
        self.__state_names = {
            IBGameState.INTRO_SEQUENCE: 'INTRO_SEQUENCE',
            IBGameState.MAIN_MENU: 'MAIN_MENU',
            IBGameState.SETTINGS_MENU: 'SETTINGS_MENU',
            IBGameState.CONNECTION_MENU: 'CONNECTION_MENU',
            IBGameState.LOBBY_SELECTION: 'LOBBY_SELECTION',
            IBGameState.LOBBY: 'LOBBY',
            IBGameState.GAME_SESSION: 'GAME_SESSION',
            IBGameState.GAME_END: 'GAME_END'
        }
        logger.debug(f'IBGameState initialized with state: {str(self)}')


    @property
    def state(self) -> int:
        # TODO DOC
        return self.__state


    @state.setter
    def state(self, new_state: int):
        # TODO DOC

        # sanity check simplified based on contract
        if new_state > IBGameState.GAME_END or new_state < IBGameState.INTRO_SEQUENCE:
            raise ValueError('Invalid state to set.')
        
        if new_state == self.__state:
            return
    
        # logging handled near the call location
        self.__state = new_state


    def __str__(self) -> str:
        """
        Returns the name of the state.

        :return: The name of the state.
        :rtype: str
        """

        return self.__state_names.get(self.__state, 'UNKNOWN_STATE')


class IBGame:
    # TODO DOC

    CLEAR_BACKGROUND = (0, 0, 0, 0)

    def __init__(self, config: Dict, assets: Dict):
        # TODO DOC
        self.config = deepcopy(config)
        self.assets = deepcopy(assets)

        self.started = False
        self.debug_mode = False


    def __get_debug_info_object(self):
        # TODO DOC
        if not pygame.get_init():
            raise ValueError('The pygame module has not been initialized.')
        if not pygame.font.get_init():
            raise ValueError('The pygame.font module has not been initialized.')

        # display debug info in the bottom left corner of the window
        # create a new font object
        font = pygame.font.Font(None, int(pygame.display.get_desktop_sizes()[0][1] * 1/45))
        # create a new text surface
        text = font.render(str(self.debug_info), 
                           True, 
                           self.assets['colors']['white'], 
                        #    color_make_seethrough(self.assets['colors']['black']))
        )
        
        return text


    def start(self, window: pygame.Surface):
        # TODO DOC

        self.window = window
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(self.assets['strings']['window_title'])
        
        self.game_state = IBGameState()

        self.presentation_surface = self.window.subsurface(self.window.get_rect())
        if self.config.get('debug_mode', False):
            logger.info('Debug mode is enabled')
            self.debug_mode = True
            self.debug_info: IBGameDebugInfo = IBGameDebugInfo(str(self.game_state), self.window.get_size())
            self.debug_info_render: pygame.Surface = self.__get_debug_info_object()
            self.debug_surface = self.window.subsurface(0, self.window.get_height() - self.debug_info_render.get_height(), self.window.get_width(), self.debug_info_render.get_height())
            self.debug_surface.blit(self.debug_info_render, (0, 0))
            pygame.display.flip()

        self.update_result = IBGameUpdateResult()
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
                logger.debug('Quit event registered')
                continue

            if event.type == pygame.KEYDOWN:
                events.event_keydown = event
                logger.debug(f'Keydown event registered: {pygame.key.name(event.key)}')
                continue

            if event.type == pygame.KEYUP:
                events.event_keyup = event
                logger.debug(f'Keyup event registered: {pygame.key.name(event.key)}')
                continue

            if event.type == pygame.MOUSEMOTION:
                events.event_mousemotion = event
                # logger.debug(f'Mousemotion event registered: {event.pos}')
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                events.event_mousebuttondown = event
                logger.debug(f'Mousebuttondown event registered: {event.pos}')
                continue

            if event.type == pygame.MOUSEBUTTONUP:
                events.event_mousebuttonup = event
                logger.debug(f'Mousebuttonup event registered: {event.pos}')
                continue

            if event.type == pygame.VIDEORESIZE:
                events.event_videoresize = event
                logger.debug(f'Videoresize event registered: {event.dict["size"]}')
                continue

        return events
    

    def __update_game_session(self, events: PyGameEvents) -> IBGameUpdateResult:
        raise NotImplementedError('The __update_game_session method has not been implemented yet.')


    def __update_lobby(self, events: PyGameEvents) -> IBGameUpdateResult:
        raise NotImplementedError('The __update_lobby method has not been implemented yet.')


    def __update_lobby_selection(self, events: PyGameEvents) -> IBGameUpdateResult:
        raise NotImplementedError('The __update_lobby_selection method has not been implemented yet.')


    def __update_connection_menu(self, events: PyGameEvents) -> IBGameUpdateResult:
        raise NotImplementedError('The __update_connection_menu method has not been implemented yet.')


    def __update_game_end(self, events: PyGameEvents) -> IBGameUpdateResult:
        raise NotImplementedError('The __update_game_end method has not been implemented yet.')


    def __update_main_menu(self, events: PyGameEvents):
        # TODO DOC

        # if no menu was drawn, prepare it and draw it
        if not hasattr(self, 'menu'):
            title = MenuTitle(self.assets['strings']['main_menu_title'])
            options = [
                MenuOption(self.assets['strings']['main_menu_option_play'], lambda: print('Play menu')),
                MenuOption(self.assets['strings']['main_menu_option_settings'], lambda: print('Settings menu')),
                MenuOption(self.assets['strings']['main_menu_option_exit'], lambda: SelectMenu.handle_exit(self))
            ]
            self.menu = SelectMenu(self.presentation_surface, self.assets, title, options)

            # draw the menu for the first time
            self.menu.redraw()
            self.update_result.update_areas.append(True)

        # if the user resized the window, redraw the menu
        if events.event_videoresize:
            self.menu.surface = self.presentation_surface
            self.menu.redraw()
            return
        
        # catch update
        if self.menu.update(events):
            self.update_result.update_areas.extend(self.menu.draw())


    def __update_settings_menu(self, events: PyGameEvents) -> IBGameUpdateResult:
        raise NotImplementedError('The __update_settings_menu method has not been implemented yet.')
    

    def __handle_intro_sequence(self) -> bool:
        """
        Handles the intro sequence.

        :return: True if the intro sequence has been completed and 
        debug info should be updated, False otherwise.
        :rtype: bool
        """

        #TODO magic num
        
        if not getattr(self, 'last_time', None):
            self.last_time = pygame.time.get_ticks()
    
        if pygame.time.get_ticks() - self.last_time >= 2000:
            self.game_state.state = IBGameState.MAIN_MENU
            logger.info('Intro sequence completed, switching state to MAIN_MENU')
            del self.last_time

            if self.debug_mode:
                return True
            
        return False


    def __handle_window_resize(self, events) -> bool:
        """
        Handles the window resize event.

        :param events: The PyGame events.
        :type events: PyGameEvents
        :return: True if the debug info should be updated, False otherwise.
        """

        logger.debug('User attempted to resize the window')
        event = events.event_videoresize
        if not maintains_min_window_size(event.dict['w'], event.dict['h'], self.config['min_window_width'], self.config['min_window_height']):
                logger.warning('The window size is below the minimum allowed size, resizing the window to the minimum size')
                pygame.display.set_mode((self.config['min_window_width'], self.config['min_window_height']), pygame.RESIZABLE)
        self.presentation_surface = self.window.subsurface(self.window.get_rect())
        
        logger.debug(f'Window resized to: {events.event_videoresize.dict["size"]}')
        self.update_result.update_areas.append(True)

        if self.debug_mode:
            self.debug_info.dimensions = events.event_videoresize.dict['size']
            self.debug_surface = self.window.subsurface(0, self.window.get_height() - self.debug_info_render.get_height(), self.window.get_width(), self.debug_info_render.get_height())
            return True
        
        return False

        
    def update(self) -> IBGameUpdateResult:
        # TODO DOC

        # sanity check
        if not self.started:
            logger.critical('The game has not been started yet so it cannot be updated')
            raise SystemError('The game has not been started yet.')

        self.update_result.update_areas = []
        events = self.__get_pygame_events()

        debug_update = False
        
        # user requests to quit
        if events.event_quit:
            self.update_result.exit = True
            logger.info('User requested to exit the game')
            return self.update_result
            
        # user attempts to resize the window
        elif events.event_videoresize:
            debug_update = self.__handle_window_resize(events)



        # ignore all events that are not of interest
        if self.game_state.state == IBGameState.INTRO_SEQUENCE:
            if not debug_update:
                debug_update = self.__handle_intro_sequence()
        
        # handle events that are of interest
        else:

            # capture the last key pressed for debugging purposes
            if self.debug_mode:
                if events.event_keydown:
                    self.debug_info.last_reg_key = pygame.key.name(events.event_keydown.key)
                    logger.debug(f'Last registered key: {self.debug_info.last_reg_key}')
                    debug_update = True

            # ordered by the most prioritized states (microoptimization)
            if self.game_state.state == IBGameState.GAME_SESSION:
                self.__update_game_session(events)

            elif self.game_state.state == IBGameState.LOBBY:
                self.__update_lobby(events)

            elif self.game_state.state == IBGameState.LOBBY_SELECTION:
                self.__update_lobby_selection(events)

            elif self.game_state.state == IBGameState.CONNECTION_MENU:
                self.__update_connection_menu(events)

            elif self.game_state.state == IBGameState.GAME_END:
                self.__update_game_end(events)

            elif self.game_state.state == IBGameState.MAIN_MENU:
                self.__update_main_menu(events)

            elif self.game_state.state == IBGameState.SETTINGS_MENU:
                self.__update_settings_menu(events)

            elif self.game_state.state == IBGameState.INTRO_SEQUENCE:
                logger.critical('The INTRO_SEQUENCE state should have been handled before this point.')
                raise SystemError('The INTRO_SEQUENCE state should have been handled before this point.')
            
            else:
                logger.critical('Unknown state.')
                raise SystemError('Unknown state.')

        # render the debug info if allowed
        if debug_update:
            self.debug_surface.fill(self.assets['colors']['black'])
            self.debug_info.game_state = str(self.game_state)
            self.debug_info_render = self.__get_debug_info_object()
            new_rect_x = 0
            new_rect_y = self.window.get_height() - self.debug_info_render.get_height()
            self.debug_surface.blit(self.debug_info_render, (0, 0))
            new_rect = pygame.Rect(new_rect_x, new_rect_y, self.window.get_width(), self.debug_info_render.get_height())
            self.update_result.update_areas.append(new_rect)
        
        return self.update_result
