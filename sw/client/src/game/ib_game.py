"""
Module that contains the main class of the game and 
all the logic related to the game itself.    
"""

import json
import os
import re
import socket
import threading
import time
from util.generic_client import GenericClient
from const.server_communication import *
from game.connection_manager import ConnectionManager, ServerResponse
from const.paths import DEFAULT_USER_CONFIG_PATH
from const.loggers import MAIN_LOGGER_NAME
from game.ib_game_state import IBGameState
from graphics.menus.settings_menu import SettingsMenu
from util import input_validators, loggers
from typing import Dict, Any, Callable
from graphics.menus.input_menu import InputMenu
from graphics.menus.select_menu import SelectMenu
from graphics.menus.primitives import MenuTitle, MenuOption
from graphics.menus.info_screen import InfoScreen
from util.etc import maintains_min_window_size
from util.path import get_project_root
from const.typedefs import IBGameDebugInfo, IBGameUpdateResult, PyGameEvents
from copy import deepcopy
import pygame
from pygame.locals import *


logger = loggers.get_logger(MAIN_LOGGER_NAME)
# TODO remove
tmp_logger = loggers.get_temp_logger('temp')
PROJECT_ROOT_DIR = get_project_root()


class IBGame:
    """
    The main class that represents the game (using concept of state machine).
    The main methods are start and update.
    """


    PLAYER_NICKNAME_MAX_LENGTH = 20
    """The maximum length of the player's nickname."""
    SERVER_ADDRESS_MAX_LENGTH = 18 # 9 IP, 5 port, 1 colon, 3 dots
    """The maximum length of the server address."""
    SERVER_CONNECTION_TIMEOUT = 5
    """The timeout for the server connection in seconds."""


    @staticmethod
    def __proccess_input(events: PyGameEvents, key_input_validator: Callable = lambda y, x: x, self = None) -> Dict[str, Any]:
        """
        Processes the input events into a dictionary.

        :param events: PyGame events.
        :type events: PyGameEvents
        :param key_input_validator: Function to validate the keyboard input 
        and return a valid event.
        :type key_input_validator: Callable
        :param self: The IBGame object (if needed), defaults to None
        :type self: IBGame
        :return: The processed input events.
        :rtype: Dict[str, Any]
        """
        
        res = {}
        if events.event_keyup:
            key_up = key_input_validator(self, events.event_keyup)
            if not key_up:
                logger.debug('Invalid keyup event, skipping...')
                return res
            if key_up.key == pygame.K_UP or \
                key_up.key == pygame.K_DOWN or \
                key_up.key == pygame.K_LEFT or \
                key_up.key == pygame.K_RIGHT:
                res['direction'] = events.event_keyup.key
            elif key_up.key == pygame.K_BACKSPACE:
                res['backspace'] = True
            elif key_up.key == pygame.K_RETURN:
                res['return'] = True
            elif key_up.key == pygame.K_ESCAPE:
                res['escape'] = True
            elif key_up.unicode.isprintable():
                res['new_char'] = events.event_keyup.unicode

            logger.debug(f'Processed keyup event: {pygame.key.name(events.event_keyup.key)}')
            
        elif events.event_mousebuttonup:
            res['mouse_click'] = events.event_mousebuttonup.pos
            logger.debug(f'Processed mousebuttonup event: {events.event_mousebuttonup.pos}')
        
        elif events.event_mousemotion:
            res['mouse_motion'] = events.event_mousemotion.pos
            # logger.debug(f'Processed mousemotion event: {events.event_mousemotion.pos}')
        
        return res
    

    @staticmethod
    def __create_user_cfg(player_name: str, server_address: str = None):
        """
        Creates a new user configuration file.

        :param player_name: The name of the player.
        :type player_name: str
        """

        user_cfg_path = os.path.join(PROJECT_ROOT_DIR, 'cfg', 'users', f'{player_name}.json')

        default_user_cfg = {}
        with open(DEFAULT_USER_CONFIG_PATH, 'r') as f:
            default_user_cfg.update(json.load(f))
        
        # create dirs if needed
        os.makedirs(os.path.dirname(user_cfg_path), exist_ok=True)
        new_user_cfg = {
            'nickname': player_name,
        }
        new_user_cfg.update(default_user_cfg)
        if server_address:
            new_user_cfg['server_address'] = server_address

        with open(user_cfg_path, 'w') as f:
            json.dump(new_user_cfg, f)

        
    @staticmethod
    def __is_settings_input_valid(text_input):
        """
        Validates the server address input.

        :param text_input: The text input to validate.
        :type text_input: str
        :return: True if the input is valid, False otherwise.
        :rtype: bool
        """

        address_regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}:\d{1,5}"

        return re.match(address_regex, text_input)


    @staticmethod
    def __attempt_connection(connection_manager: ConnectionManager):
        """
        Attempts to connect to the server.

        :param connection_manager: The connection manager.
        :type connection_manager: ConnectionManager
        """

        try:
            connection_manager.start()
        except Exception as e:
            raise ConnectionError(f'Failed to connect to the server: {e}')
        

    @staticmethod
    def __establish_connection(connection_manager: ConnectionManager, player_name: str, ready_event: threading.Event, failed_event: threading.Event):
        """
        Establishes the connection to the server.

        :param connection_manager: The connection manager.
        :type connection_manager: ConnectionManager
        :param player_name: The name of the player.
        :type player_name: str
        :param ready_event: The event that signals that the connection is ready.
        :type ready_event: threading.Event
        :param failed_event: The event that signals that the connection has failed.
        :type failed_event: threading.Event
        """

        try:
            tmp_logger.debug('Thread: Attempting to connect to the server...')
            __class__.__attempt_connection(connection_manager)
            tmp_logger.debug('Thread: Connection successful')

            # request the player to join the server
            res = connection_manager.login(player_name)
            if not res:
                raise ConnectionError('Failed to login to the server')
            
            ready_event.set()
            failed_event.clear()

        except Exception as e:
            tmp_logger.error(f'Thread: Connection attempt failed: {e}')
            logger.error(f'Connection attempt failed: {e}')
            failed_event.set()


    @staticmethod
    def __handle_server_communication_connection_menu(connection_manager: ConnectionManager, stop: threading.Event):
        """
        Handles the server communication in the CONNECTION_MENU state.

        :param connection_manager: The connection manager.
        :type connection_manager: ConnectionManager
        :param stop: The event that signals that the game should exit.
        :type stop: threading.Event
        """

        while not stop.is_set():
            # keep alive
            if time.time() - connection_manager.last_time_reply > 5:        # TODO MAGIC NUMBER
                logger.debug('Connection timeout, pinging the server...')
                try:
                    connection_manager.ping()
                except Exception as e:
                    raise ConnectionError(f'Failed to send ping to the server: {e}')

            # listen for messages
            else: 
                resp: ServerResponse = None
                try:
                    resp = connection_manager.receive_message()
                except ConnectionError as e:
                    logger.error(f'Error occurred while receiving message from the server: {e}')
                    raise ConnectionError(f'Error occurred while receiving message from the server: {e}')
                except TimeoutError:
                    continue
                    
                command = resp.command
                if command == CMD_PING:
                    try:
                        connection_manager.pong()
                    except Exception as e:
                        raise ConnectionError(f'Failed to send pong to the server: {e}')


    def __init__(self, config: Dict[str, Any], assets: Dict[str, Any]):
        """
        Creates a new instance of the IBGame class.

        :param config: The configuration of the game.
        :type config: Dict[Any]
        :param assets: The assets of the game.
        :type assets: Dict[Any]
        """

        self.config = deepcopy(config)
        self.assets = {'colors': deepcopy(assets['colors']), 'strings': deepcopy(assets['strings']), 'sprites': assets['sprites']}

        self.started = False
        self.debug_mode = False
    

    def start(self, window: pygame.Surface):
        """
        Initializes the game.

        :param window: The window of the game.
        :type window: pygame.Surface
        """

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
        
        self.context = None
        self.player_name = None
        self.server_ip = None
        self.server_port = None

        self.__connection_manager = None
        self.__exit = threading.Event()
        self.__exit.clear()

        self.update_result = IBGameUpdateResult()
        self.started = True


    def __get_debug_info_object(self):
        """
        Returns the debug info object. Used for debugging purposes.
        It is a pygame.Surface object with the debug info.

        :return: The debug info object.
        :rtype: pygame.Surface
        """

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
    

    def __set_up_user_session(self):
        """
        Prepares the data for the client session  
        based on user.
        """
        
        if not self.context:
            raise ValueError('The context has not been initialized yet.')
        if not self.context.text_input:
            raise ValueError('The user input has not been set yet.')
        
        self.player_name = self.context.text_input
        user_cfg_path = os.path.join(PROJECT_ROOT_DIR, 'cfg', 'users', f'{self.player_name}.json')
        if not os.path.exists(user_cfg_path):
            logger.info(f'User configuration file does not exist, creating a new one: {user_cfg_path}')
            __class__.__create_user_cfg(self.player_name)
        
        logger.debug(f'User configuration file found: {user_cfg_path}')
        with open(user_cfg_path, 'r') as f:
            user_cfg = json.load(f)
        server_address = user_cfg['server_address'].split(':')
        self.server_ip = server_address[0]
        self.server_port = int(server_address[1])
    

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

    
    def __handle_context_resize(self):
        """
        Handles the context resize event.
        """

        self.context.surface = self.presentation_surface
        self.context.redraw()

    
    def __prepare_init_state(self):
        """
        Prepares the initial state of the game.
        """

        label_text = self.assets['strings']['init_state_label']
        self.context = InputMenu(self.presentation_surface, self.assets, label_text)
            
        self.key_input_validator = input_validators.init_menu_key_input_validator
        self.context.redraw()
        self.update_result.update_areas.append(True)
    

    def __prepare_main_menu(self):
        """
        Prepares the main menu state of the game.
        """

        title = MenuTitle(self.assets['strings']['main_menu_title'])
        options = [
            MenuOption(self.assets['strings']['main_menu_option_play']),
            MenuOption(self.assets['strings']['main_menu_option_settings']),
            MenuOption(self.assets['strings']['main_menu_option_exit'])
        ]
        self.context = SelectMenu(self.presentation_surface, self.assets, title, options)

        # draw the menu for the first time
        self.context.redraw()
        self.update_result.update_areas.append(True)
        tmp_logger.debug('Main menu drawn for the first time')
        tmp_logger.debug(f'Player nick: {self.player_name}')
        tmp_logger.debug(f'Server address: {self.server_ip}:{self.server_port}')


    def __prepare_settings_menu(self):
        """
        Prepares the settings menu state of the game.
        """

        label_text = self.assets['strings']['settings_menu_label']
        server_address = self.server_ip + ':' + str(self.server_port)
        self.context = SettingsMenu(self.presentation_surface, self.assets, label_text, server_address)
            
        self.key_input_validator = input_validators.settings_key_input_validator
        self.context.redraw()
        self.update_result.update_areas.append(True)

    
    def __handle_update_feedback_init_state(self, res: Dict[str, Any]):
        """
        Handles the feedback from the update method in the INIT state.

        :param res: The feedback from the update method.
        :type res: Dict[str, Any]
        """

        # handle graphics update (text input)
        if res['graphics_update']:
            update_rect = self.context.draw()
            self.update_result.update_areas.append(update_rect)
        
        # handle the user input
        elif res['submit']:
            logger.info(f'User submitted the input: {self.context.text_input}')
            self.__set_up_user_session()
            self.context = None
            self.game_state.state = IBGameState.MAIN_MENU
            logger.info('Changing the state to MAIN_MENU')


    def __handle_update_feedback_connection_menu(self, res: Dict[str, Any]):
        """
        Handles the feedback from the update method in the CONNECTION_MENU state.

        :param res: The feedback from the update method.
        :type res: Dict[str, Any]
        """

        # handle connection attempt failed
        if self.__connection_failed_event and self.__connection_failed_event.is_set():
            if res['submit'] or res['escape']:
                logger.debug('User requested to go back to the main menu from failed connection')
                logger.info('Changing the state to MAIN_MENU')
                self.game_state.state = IBGameState.MAIN_MENU
                self.context = None
                self.__connection_failed_event = None
                self.__connection_manager = None
                self.update_result.update_areas.append(True)
                return
        
        # let the connection attempt finish
        elif self.__connection_ready_event or self.__connection_failed_event:
            return


        # handle graphics update (selection change)
        if res['graphics_update']:
            self.update_result.update_areas.extend(self.context.draw())
        
        # handle option selection
        elif res['submit']:
            logger.debug(f'User selected the option: {self.context.selected_option_text}')
            
            if self.context.selected_option_text == self.assets['strings']['connection_menu_lobby_select_label']:
                logger.info('Changing the state to LOBBY_SELECTION')
                self.game_state.state = IBGameState.LOBBY_SELECTION
            
            elif self.context.selected_option_text == self.assets['strings']['connection_menu_lobby_create_label']:
                logger.info('Changing the state to LOBBY')
                self.game_state.state = IBGameState.LOBBY

            else:
                logger.error('Unknown option selected.')
                raise ValueError('Unknown option selected.')
            
            self.context = None
            self.update_result.update_areas.append(True)
        
        elif res['escape']:
            logger.info('Changing the state to MAIN_MENU')
            self.__exit.set()
            self.__connection_manager.stop()
            self.__connection_manager = None
            self.game_state.state = IBGameState.MAIN_MENU
            self.context = None
            self.update_result.update_areas.append(True)


    def __handle_update_feedback_main_menu(self, res: Dict[str, Any]):
        """
        Handles the feedback from the update method in the MAIN_MENU state.

        :param res: The feedback from the update method.
        :type res: Dict[str, Any]
        :raises ValueError: If an unknown option is selected.
        """

        # handle graphics update (selection change)
        if res['graphics_update']:
            self.update_result.update_areas.extend(self.context.draw())
        
        # handle option selection
        elif res['submit']:
            logger.debug(f'User selected the option: {self.context.selected_option_text}')
            
            if self.context.selected_option_text == self.assets['strings']['main_menu_option_play']:
                logger.info('Changing the state to CONNECTION_MENU')
                self.game_state.state = IBGameState.CONNECTION_MENU
            
            elif self.context.selected_option_text == self.assets['strings']['main_menu_option_settings']:
                logger.info('Changing the state to SETTINGS_MENU')
                self.game_state.state = IBGameState.SETTINGS_MENU

            elif self.context.selected_option_text == self.assets['strings']['main_menu_option_exit']:
                logger.info('User requested to exit the game')
                self.update_result.exit = True
            
            else:
                logger.error('Unknown option selected.')
                raise ValueError('Unknown option selected.')
            
            self.context = None
            self.update_result.update_areas.append(True)
    

    def __handle_update_feedback_settings_menu(self, res: Dict[str, Any]):
        """
        Handles the feedback from the update method in the SETTINGS_MENU state.

        :param res: The feedback from the update method.
        :type res: Dict[str, Any]
        """

        # handle graphics update (text input)
        if res['graphics_update']:
            update_rect = self.context.draw()
            self.update_result.update_areas.append(update_rect)
        
        # handle the user input
        elif res['submit']:
            # TODO HERE better validate
            if __class__.__is_settings_input_valid(self.context.text_input):
                logger.info(f'User submitted the input: {self.context.text_input}')
                __class__.__create_user_cfg(self.player_name, self.context.text_input)
                ip, port = self.context.text_input.split(':')
                self.server_ip = ip
                self.server_port = int(port)
                logger.info(f'Server address set to: {self.server_ip}:{self.server_port}')
                logger.info('Changing the state to MAIN_MENU')
                self.game_state.state = IBGameState.MAIN_MENU
                self.context = None
            
            else:
                logger.error('Invalid server address input.')
                msg = {'invalid_input': True}
                self.context.update(msg)
                # will update in the next iteration
        
        elif res['escape']:
            logger.info('Changing the state to MAIN_MENU')
            self.game_state.state = IBGameState.MAIN_MENU
            self.context = None
            self.update_result.update_areas.append(True)


    def __update_init_state(self, events: PyGameEvents):
        """
        Handles the initialization state.
        
        :param events: The PyGame user input events.
        :type events: PyGameEvents
        """

        # initialize the context as needed
        if not self.context:
            self.__prepare_init_state()

        if events.event_videoresize:
            self.__handle_context_resize()

        # process the input
        inputs = self.__proccess_input(events, self.key_input_validator, self)
        
        # update the context and get the results
        res = self.context.update(inputs)
        self.__handle_update_feedback_init_state(res)
    

    def __update_game_session(self, events: PyGameEvents):
        raise NotImplementedError('The __update_game_session method has not been implemented yet.')
    

    def __update_connection_menu(self, events: PyGameEvents):
        # TODO DOC

        # if no context was drawn => no connection attempt was made yet so try to connect
        if not self.context and not self.__connection_manager:
            self.context = InfoScreen(self.presentation_surface, 
                                      self.assets, 
                                      self.assets['strings']['attempt_connection_msg'])
            self.__connection_manager = ConnectionManager(self.server_ip, self.server_port)
            self.__connection_ready_event = threading.Event()
            self.__connection_failed_event = threading.Event()
            self.__connection_thread = threading.Thread(target=__class__.__establish_connection, 
                                                        args=(self.__connection_manager, 
                                                             self.player_name, 
                                                             self.__connection_ready_event, 
                                                             self.__connection_failed_event))

            self.__connection_thread.start()
            self.context.redraw()
            self.update_result.update_areas.append(True)
        
        # connection attempt was successful => show the lobby selection menu
        if self.__connection_thread and self.__connection_ready_event and self.__connection_ready_event.is_set():
            self.context = SelectMenu(self.presentation_surface, 
                                      self.assets, 
                                      None,
                                      [MenuOption(self.assets['strings']['connection_menu_lobby_select_label']), MenuOption(self.assets['strings']['connection_menu_lobby_create_label'])])
            self.__connection_thread.join()
            self.__connection_ready_event = None
            self.__connection_failed_event = None

            # define connection thread to handle server requests
            self.__connection_thread = threading.Thread(target=__class__.__handle_server_communication_connection_menu, 
                                                        args=(self.__connection_manager,
                                                              self.__exit))
            self.__connection_thread.start()
            self.context.redraw()
            self.update_result.update_areas.append(True)
        
        # connection attempt failed
        elif self.__connection_thread and self.__connection_failed_event and self.__connection_failed_event.is_set():
            self.context = InfoScreen(self.presentation_surface, self.assets, self.assets['strings']['connection_failed_msg'])
            self.__connection_thread.join()
            self.__connection_thread = None
            self.__connection_ready_event = None
            self.context.redraw()
            self.update_result.update_areas.append(True)

        
        if events.event_videoresize:
            self.__handle_context_resize() 

        # process the input
        inputs = self.__proccess_input(events)

        # update the context and get the results
        res = self.context.update(inputs)
        self.__handle_update_feedback_connection_menu(res)

    def __update_lobby(self, events: PyGameEvents):
        raise NotImplementedError('The __update_lobby method has not been implemented yet.')


    def __update_lobby_selection(self, events: PyGameEvents):
        raise NotImplementedError('The __update_lobby_selection method has not been implemented yet.')


    def __update_game_end(self, events: PyGameEvents):
        raise NotImplementedError('The __update_game_end method has not been implemented yet.')


    def __update_main_menu(self, events: PyGameEvents):
        """
        Handles the main menu state.

        :param events: The PyGame user input events.
        :type events: PyGameEvents
        """

        # if no menu was drawn, prepare it and draw it
        if not self.context:
            self.__prepare_main_menu()

        # if the user resized the window, redraw the menu
        if events.event_videoresize:
            self.__handle_context_resize()
            # TODO figure it if return is needed here

        # process the input
        inputs = self.__proccess_input(events)

        # update the context and get the results
        res = self.context.update(inputs)
        self.__handle_update_feedback_main_menu(res)


    def __update_settings_menu(self, events: PyGameEvents):
        """
        Handles the settings menu state.

        :param events: The PyGame user input events.
        :type events: PyGameEvents
        """

        # initialize the context as needed
        if not self.context:
            self.__prepare_settings_menu()
        
        if events.event_videoresize:
            self.__handle_context_resize()

        # process the input
        inputs = self.__proccess_input(events, self.key_input_validator, self)
        
        # update the context and get the results
        res = self.context.update(inputs)
        self.__handle_update_feedback_settings_menu(res)

        
    def update(self) -> IBGameUpdateResult:
        """
        Updates the game state. This method should be called in the main loop 
        on each game tick. It uses priciples of state machine.

        :return: The update result.
        :rtype: IBGameUpdateResult
        """

        # sanity check
        if not self.started:
            logger.critical('The game has not been started yet so it cannot be updated')
            raise SystemError('The game has not been started yet.')

        # reset the update result
        self.update_result.update_areas = []
        events = self.__get_pygame_events()
        debug_info_updated = False
        
        # user requests to quit
        if events.event_quit:
            logger.info('User requested to exit the game')
            self.__exit.set()
            self.update_result.exit = True
            if self.__connection_thread:
                self.__connection_thread.join()
            return self.update_result
            
        # user attempts to resize the window
        elif events.event_videoresize:
            self.__handle_window_resize(events)
            debug_info_updated = True


        # capture the last key pressed for debugging purposes
        if self.debug_mode:
            if events.event_keydown:
                self.debug_info.last_reg_key = pygame.key.name(events.event_keydown.key)
                logger.debug(f'Last registered key: {self.debug_info.last_reg_key}')
                debug_info_updated = True
            
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

        elif self.game_state.state == IBGameState.INIT:
            self.__update_init_state(events)
        
        else:
            logger.critical('Unknown state.')
            raise SystemError('Unknown state.')

        # render the debug info if allowed
        if self.debug_mode and debug_info_updated:
            self.debug_surface.fill(self.assets['colors']['black'])
            self.debug_info.game_state = str(self.game_state)
            self.debug_info_render = self.__get_debug_info_object()
            new_rect_x = 0
            new_rect_y = self.window.get_height() - self.debug_info_render.get_height()
            self.debug_surface.blit(self.debug_info_render, (0, 0))
            new_rect = pygame.Rect(new_rect_x, new_rect_y, self.window.get_width(), self.debug_info_render.get_height())
            self.update_result.update_areas.append(new_rect)
        
        return self.update_result
