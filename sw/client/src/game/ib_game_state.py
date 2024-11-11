"""
Module that contains the main class of the game and 
all the logic related to the game itself.    
"""

from const.loggers import MAIN_LOGGER_NAME
from util import loggers
from util.path import get_project_root
from pygame.locals import *


logger = loggers.get_logger(MAIN_LOGGER_NAME)


class IBGameState:
    # TODO DOC
    INIT = -1
    MAIN_MENU = 0
    SETTINGS_MENU = 1
    CONNECTION_MENU = 2
    LOBBY_SELECTION = 3
    LOBBY = 4
    GAME_SESSION = 5
    GAME_END = 6


    def __init__(self):
        # TODO DOC
        self.__state = IBGameState.INIT
        self.__state_names = {
            IBGameState.INIT: 'INIT',
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
        if new_state > IBGameState.GAME_END or new_state < IBGameState.INIT:
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


