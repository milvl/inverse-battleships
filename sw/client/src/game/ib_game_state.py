"""
Module that contains the main class of the game and 
all the logic related to the game itself.    
"""

from dataclasses import dataclass
from const.loggers import MAIN_LOGGER_NAME
from util import loggers
from util.path import get_project_root
from pygame.locals import *


logger = loggers.get_logger(MAIN_LOGGER_NAME)


@dataclass
class ConnectionStatus:
    """
    This class represents the status of the connection.
    """

    NOT_RUNNING = 0
    """The connection is not running."""
    CONNECTING = 1
    """The connection is being established."""
    CONNECTED = 2
    """The connection is established."""
    CONNECTED_IN_PROGRESS = 3
    """The connection is in progress."""
    FAILED = 4
    """The connection failed."""
    REQUESTED_LOBBIES = 5
    """The connection requested the lobbies."""
    WAITING_FOR_LOBBIES = 6
    """The connection is waiting for the lobbies."""
    RECEIVED_LOBBIES = 7
    """The connection received the lobbies."""

    status: int = NOT_RUNNING
    """The status of the connection."""


class IBGameState:
    """
    Class that represents the state of the game.

    :raises ValueError: If the state to set is invalid.
    :return: The state of the game.
    :rtype: int
    """

    INIT = -1
    MAIN_MENU = 0
    SETTINGS_MENU = 1
    CONNECTION_MENU = 2
    LOBBY_SELECTION = 3
    LOBBY = 4
    GAME_SESSION = 5
    GAME_END = 6
    ALERT = 7


    def __init__(self):
        """
        Constructor method.
        """

        self.__state = IBGameState.INIT
        self.__state_names = {
            IBGameState.INIT: 'INIT',
            IBGameState.MAIN_MENU: 'MAIN_MENU',
            IBGameState.SETTINGS_MENU: 'SETTINGS_MENU',
            IBGameState.CONNECTION_MENU: 'CONNECTION_MENU',
            IBGameState.LOBBY_SELECTION: 'LOBBY_SELECTION',
            IBGameState.LOBBY: 'LOBBY',
            IBGameState.GAME_SESSION: 'GAME_SESSION',
            IBGameState.GAME_END: 'GAME_END',
            IBGameState.ALERT: 'ALERT'
        }
        self.__connection_status_names = {
            ConnectionStatus.NOT_RUNNING: 'NOT_RUNNING',
            ConnectionStatus.CONNECTING: 'CONNECTING',
            ConnectionStatus.CONNECTED: 'CONNECTED',
            ConnectionStatus.CONNECTED_IN_PROGRESS: 'CONNECTED_IN_PROGRESS',
            ConnectionStatus.FAILED: 'FAILED',
            ConnectionStatus.REQUESTED_LOBBIES: 'REQUESTED_LOBBIES',
            ConnectionStatus.WAITING_FOR_LOBBIES: 'WAITING_FOR_LOBBIES',
            ConnectionStatus.RECEIVED_LOBBIES: 'RECEIVED_LOBBIES'
        }
        self.__connection_status = ConnectionStatus()
        logger.debug(f'IBGameState initialized with state: {str(self)}')


    @property
    def state(self) -> int:
        """
        Represents the current state of the game.
        """

        return self.__state


    @state.setter
    def state(self, new_state: int):
        """
        Sets the state of the game.

        :param new_state: The new state of the game.
        :type new_state: int
        """

        # sanity check simplified based on contract
        if new_state > IBGameState.GAME_END or new_state < IBGameState.INIT:
            raise ValueError('Invalid state to set.')
        
        if new_state == self.__state:
            return
    
        self.__state = new_state

    
    @property
    def connection_status(self) -> ConnectionStatus:
        """
        Represents the current connection status.
        """

        return self.__connection_status.status
    

    @connection_status.setter
    def connection_status(self, new_status: ConnectionStatus):
        """
        Sets the connection status.

        :param new_status: The new connection status.
        :type new_status: ConnectionStatus
        """

        self.__connection_status.status = new_status


    def __str__(self) -> str:
        """
        Returns the name of the state.

        :return: The name of the state.
        :rtype: str
        """

        return f"State: {self.__state_names.get(self.__state, 'UNKNOWN')}, " +\
               f"Connection Status: {self.__connection_status_names.get(self.__connection_status.status, 'UNKNOWN')}"


