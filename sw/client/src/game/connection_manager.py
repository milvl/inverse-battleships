"""
This module is responsible for managing the connection between the client and the server for the game Inverse Battleships.
"""

from dataclasses import dataclass
import socket
import threading
import time
import re
from typing import Any, List, Tuple
from util.generic_client import GenericClient
from const.server_communication import *
from util.loggers import get_logger
from const.loggers import MAIN_LOGGER_NAME


logger = get_logger(MAIN_LOGGER_NAME)


@dataclass
class ServerResponse:
    """
    This class represents a response from the server.
    """

    command: str
    """The response from the server."""
    params: List[Any]
    """Parameters of the response from the server."""


    def __str__(self) -> str:
        """
        Returns a string representation of the server response.

        :return: The string representation of the server response.
        :rtype: str
        """

        res = ""
        res += f"{MSG_HEADER}"
        res += f"{MSG_DELIMITER}"
        res += f"{self.command}"

        if self.params:
            res += f"{MSG_DELIMITER}"
            res += f"{MSG_DELIMITER.join([str(param) for param in self.params])}"
        res += f"{MSG_TERMINATOR}"

        return res


class ConnectionManager:
    """
    This class is responsible for managing the connection between the client and the server for the game Inverse Battleships.
    """

    KEEP_ALIVE_TIMEOUT = 10
    """The timeout for keeping the connection alive."""

    __WHOLE_MSG_TIMEOUT = 5
    """The timeout for receiving a whole message from the server."""

    @staticmethod
    def __to_net_message(parts: List[str]) -> str:
        """
        Returns a formatted message from the parts for the network communication.

        :param parts: The parts of the message.
        :type parts: List[str]
        :return: The message.
        :rtype: str
        """

        if not parts:
            return f"ERR;NONE{MSG_TERMINATOR}"

        for i, part in enumerate(parts):
            if MSG_TERMINATOR in part:
                raise ValueError(f"Message part {i}: '{part}' contains the message terminator '{MSG_TERMINATOR}'")
            parts[i] = part.replace(MSG_DELIMITER, f"\\{MSG_DELIMITER}")
        
        return f"{MSG_HEADER}{MSG_DELIMITER}{MSG_DELIMITER.join(parts)}{MSG_TERMINATOR}"
    

    @staticmethod
    def __from_net_message(message: str) -> List[str]:
        """
        Returns the parts of the message from the network communication.

        :param message: The message.
        :type message: str
        :return: The parts of the message.
        :rtype: List[str]
        """

        if not message.startswith(MSG_HEADER):
            raise ValueError(f"Invalid message header: '{message[:len(MSG_HEADER)]}'")
        
        parts = []
        part = []
        do_escape = False
        for char in message[(len(MSG_HEADER) + 1):]:    # skip the header and the first delimiter
            # end of part encountered
            if char == MSG_TERMINATOR:
                parts.append(''.join(part))
                break
            
            # escape character encountered
            if char == '\\':
                do_escape = True
                continue
            
            # escaping sequence
            if do_escape:
                part.append(char)
                do_escape = False
                continue
            # regular sequence
            else:
                if char == MSG_DELIMITER:
                    parts.append(''.join(part))
                    part = []
                else:
                    part.append(char)
        
        return parts
    

    @staticmethod
    def __escape_net_message(message: str) -> str:
        """
        Escapes the message for network communication.

        :param message: The message to escape.
        :type message: str
        :return: The escaped message.
        :rtype: str
        """

        # NOTE: UTF-8 encoding maybe will be changed to ASCII
        return message.encode('unicode_escape').decode('utf-8') 
    

    @staticmethod
    def __parse_parts(parts: List[str]) -> ServerResponse:
        """
        Parses the parts of a message from the server.

        :param parts: The parts of the message.
        :type parts: List[str]
        :return: The parsed message.
        :rtype: ServerResponse
        """

        if len(parts) == 0:
            raise ValueError("Empty message received")
        
        # NOTE: should always recieve valid commands (server response)
        command = parts[CMD_INDEX]

        if command in [CMD_PING, CMD_PONG, CMD_ACKW_VALID, CMD_CONFIRM_LEAVE, 
                       CMD_LOBBIES, CMD_GAME_LOSE, CMD_GAME_WIN, 
                       CMD_WAIT, CMD_CONTINUE, CMD_TKO, CMD_LOBBY_PAIRING, CMD_LOBBY_PAIRED,
                       CMD_PLAYER_TURN]:
            return ServerResponse(command, parts[CMD_INDEX + 1:])
        elif command == CMD_BOARD:
            board = []
            rows = parts[PARTS_BOARD_INDEX].split(SEQ_DELIMITER)
            for row in rows:
                board.append([int(c) for c in row.split(NUM_DELIMITER)])

            return ServerResponse(command, [board])

        
        # TODO parse various types
        
        
        raise ValueError(f"Invalid command received: '{command}'")


    def __init__(self, server_ip: str, server_port: int):
        """
        Initializes the connection manager.

        :param server_ip: The game server IP address.
        :type server_ip: str
        :param server_port: The game server port.
        :type server_port: int
        """

        self.__client = GenericClient(server_ip, server_port)
        self.__last_time_reply = None
        self.__lock = threading.RLock()
        self.__pending_messages = ""


    @property
    def is_running(self) -> bool:
        """
        Checks if the connection manager is running and is connected to the server.

        :return: True if the connection manager is running and is connected to the server, false otherwise.
        :rtype: bool
        """

        with self.__lock:
            return self.__client.is_running
    

    @property
    def server_ip(self) -> str:
        """
        Getter for server_ip.

        :return: The game server IP address.
        :rtype: str
        """

        return self.__client.host
    

    @property
    def port(self):
        """
        Getter for port.

        :return: The port of the game server.
        :rtype: int
        """

        return self.__client.port
    

    @property
    def server_address(self):
        """
        Getter for server_address.

        :return: The game server address
        :rtype: str
        """
        
        return self.__client.server_address
    

    @property
    def last_time_reply(self):
        """
        Getter for last_time_reply.

        :return: The time of the last reply from the server.
        :rtype: float
        """

        return self.__last_time_reply
    

    def start(self):
        """
        Connects to the server.
        """

        with self.__lock:
            try:
                self.__client.start()
                self.__last_time_reply = time.time()
            except Exception as e:
                raise ConnectionError(f"Error connecting to the server at {self.server_address}: {e}")
    

    def __try_disconnect(self) -> bool:
        """
        Sends a disconnect message to the game server.

        :return: True if the disconnect message was sent successfully, false otherwise.
        :rtype: bool
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot disconnect from the server at {self.server_address}: not connected")
            
            try:
                # send disconnect message
                self.__send_cmd([CMD_LEAVE])
            except Exception as e:
                logger.error(f"Error sending disconnect message to the server at {self.server_address}: {e}")
                return False

            # wait for the server to respond
            try:
                res = self.__receive_command_response(CMD_CONFIRM_LEAVE)
            except Exception as e:
                logger.error(f"Error receiving 'BYE' message from the server at {self.server_address}: {e}")
                return False

        if not res:
            logger.critical(f"Error receiving 'BYE' message from the server at {self.server_address}")
            return False
        
        return True
            

    def stop(self):
        """
        Disconnects from the server.
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot disconnect from the server at {self.server_address}: not connected")
        
            if not self.__try_disconnect():
                logger.error(f"Error disconnecting properly from the server at {self.server_address}. Forcing disconnection.")

            try:
                self.__client.stop()
            except ConnectionError as e:
                logger.error(f"Error disconnecting from the server at {self.server_address}: {e}")
                logger.warning(f"Attempted to disconnect from the server at {self.server_address}, but no active connection")
    

    def __send_cmd(self, parts: List[str]):
        """
        Sends a command to the game server.

        :param parts: The parts of the command.
        :type parts: List[str]
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot send message to the server at {self.server_address}: not connected")
            
            message = __class__.__to_net_message(parts)
    
            try:
                self.__client.send_message(message)
                logger.debug(f"Sent message to the server at {self.server_address}: '{__class__.__escape_net_message(message)}'")
            
            except ConnectionError as e:
                raise e
        
    
    def ping(self) -> bool:
        """
        Sends a ping message to the game server.

        :return: True if the ping message was sent and responded to successfully, false otherwise.
        :rtype: bool
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot send ping message to the server at {self.server_address}: not connected")

            try:
                self.__send_cmd([CMD_PING])
            except Exception as e:
                raise ConnectionError(f"Error sending ping message to the server at {self.server_address}: {e}")
                
            try:
                res = self.__receive_command_response(CMD_PONG, check_for_ping=False)
                if not res:
                    logger.error(f"Error receiving pong message from the server at {self.server_address}")
                    return False
            except Exception as e:
                raise ConnectionError(f"Error receiving pong message from the server at {self.server_address}: {e}")
                
        return True

    

    def pong(self):
        """
        Sends a pong message to the game server.
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot send pong message to the server at {self.server_address}: not connected")

            try:
                self.__send_cmd([CMD_PONG])
            except Exception as e:
                raise ConnectionError(f"Error sending pong message to the server at {self.server_address}: {e}")
    

    def get_lobbies(self) -> List[str]:
        """
        Requests the list of lobbies from the game server.

        :return: The list of lobbies.
        :rtype: List[str]
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot request lobbies from the server at {self.server_address}: not connected")
            
            try:
                self.__send_cmd([CMD_LOBBIES])
            except Exception as e:
                raise ConnectionError(f"Error sending lobbies request to the server at {self.server_address}: {e}")
            
            try:
                res = self.__receive_command_response(CMD_LOBBIES_RESP)
                if res.command != CMD_LOBBIES:
                    logger.error(f"Invalid response received from the server at {self.server_address}: {res.command}")
                    return []
            except Exception as e:
                raise ConnectionError(f"Error receiving lobbies from the server at {self.server_address}: {e}")
        
        return res.params


    def get_lobby(self) -> str:
        """
        Requests the lobby from the game server.

        :return: The lobby ID.
        :rtype: str
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot request lobby from the server at {self.server_address}: not connected")
            
            try:
                self.__send_cmd([CMD_LOBBY_CREATE])
            except Exception as e:
                raise ConnectionError(f"Error sending lobby request to the server at {self.server_address}: {e}")
            
            try:
                res = self.__receive_command_response(CMD_LOBBY_PAIRING)
                return res.params[PARAM_LOBBY_ID_INDEX]
            except TimeoutError:
                raise TimeoutError(f"Timeout while waiting for lobby from the server at {self.server_address}")
            except Exception as e:
                raise ConnectionError(f"Error receiving lobby from the server at {self.server_address}: {e}")
            

    def join_lobby(self, lobby_id: str) -> str:
        """
        Joins a lobby with the given ID.

        :param lobby_id: The ID of the lobby to join.
        :type lobby_id: str
        :return: The lobby ID.
        :rtype: str
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot request lobby from the server at {self.server_address}: not connected")
            
            try:
                self.__send_cmd([CMD_LOBBY, lobby_id])
            except Exception as e:
                raise ConnectionError(f"Error sending lobby request to the server at {self.server_address}: {e}")
            
            try:
                res = self.__receive_command_response(CMD_LOBBY_PAIRING)
                return res.params[PARAM_LOBBY_ID_INDEX]
            except TimeoutError:
                raise TimeoutError(f"Timeout while waiting for lobby from the server at {self.server_address}")
            except Exception as e:
                raise ConnectionError(f"Error receiving lobby from the server at {self.server_address}: {e}")
            

    def check_for_players(self) -> str:
        """
        Checks for players in the lobby.

        :return: Opponent's username.
        :rtype: str
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot check for players in the lobby at the server {self.server_address}: not connected")
            
            try: 
                res = self.__receive_command_response(CMD_LOBBY_PAIRED)
                return res.params[PARAM_PLAYER_ID_INDEX]
            except TimeoutError as e:
                raise e
            except Exception as e:
                raise ConnectionError(f"Error receiving players in the lobby from the server at {self.server_address}: {e}")
            

    def game_ready(self) -> str:
        """
        Sends a ready message to the game server and receives current player's username.

        :return: The username of the player whose turn it is.
        :rtype: str
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot send ready message to the server at {self.server_address}: not connected")
            
            try:
                self.__send_cmd([CMD_READY])
            except Exception as e:
                raise ConnectionError(f"Error sending ready message to the server at {self.server_address}: {e}")
            
            try:
                res = self.__receive_command_response(CMD_PLAYER_TURN)  # TODO TKO
                return res.params[PARAM_PLAYER_ID_INDEX]
            except TimeoutError as e:
                raise e
            except Exception as e:
                raise ConnectionError(f"Error receiving player's username from the server at {self.server_address}: {e}")
            

    def send_action(self, action: Tuple[int, int]) -> str:
        """
        Sends an action to the game server.

        :param action: The action to send.
        :type action: Tuple[int, int]
        :return: The response from the server.
        :rtype: str
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot send action to the server at {self.server_address}: not connected")
            
            try:
                self.__send_cmd([CMD_TURN_ACTION, f"{str(action[0])}{NUM_DELIMITER}{str(action[1])}"])
            except Exception as e:
                raise ConnectionError(f"Error sending action to the server at {self.server_address}: {e}")


    def __validate_connection(self) -> bool:
        """
        Authenticates the connection with the game server.
        It sends a handshake request to the server and waits for a response.
        Then, it validates the response and sends a confirmation message.

        :return: True if the connection was authenticated successfully, false otherwise.
        :rtype: bool
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot validate connection with the server at {self.server_address}: not connected")
        
            # send authentication message
            try:
                self.__send_cmd([CMD_TRY_VALID])
            except Exception as e:
                raise ConnectionError(f"Error sending 'HAND' message to the server at {self.server_address}: {e}")

            # wait for the server to respond
            try:
                res = self.__receive_command_response(CMD_ACKW_VALID)
                if not res:
                    logger.critical(f"Error receiving 'SHAKE' message from the server at {self.server_address}")
                    return False
            except Exception as e:
                raise ConnectionError(f"Error receiving 'SHAKE' message from the server at {self.server_address}: {e}")
            
            # send confirmation message
            try:
                self.__send_cmd([CMD_CONFIRM_VALID])
            except Exception as e:
                raise ConnectionError(f"Error sending 'DEAL' message to the server at {self.server_address}: {e}")
        
        return True
    

    def __get_complete_message(self, message: str) -> Tuple[bool, str, str]:
        """
        Checks if the message is complete and returns the complete message and the tail of the message.

        :param message: The message.
        :type message: str
        :return: True if the message is complete, the complete message and the tail of the message.
        :rtype: Tuple[bool, str, str]
        """

        i_end = message.find(MSG_TERMINATOR)
        if i_end == -1:
            return False, message, ""
        
        if i_end == len(message) - 1:
            return True, message[:i_end+1], ""      # include the terminator
        
        else:
            logger.warning(f"Received message with multiple parts: {__class__.__escape_net_message(message)}")
            return True, message[:i_end+1], message[(i_end + 1):]       # include the terminator
        

    def receive_message(self) -> ServerResponse:
        """
        Receives a message from the game server.
        Is blocking until a message is received or an error occurs or timeout.

        :return: The received message.
        :rtype: ServerResponse
        """

        message = ""
        time_start = time.time()
        while (True):
            if time.time() - time_start > __class__.__WHOLE_MSG_TIMEOUT:
                raise TimeoutError("Timeout while receiving whole message from the server")
            
            # handle any pending messages
            if self.__pending_messages:
                message += self.__pending_messages
                self.__pending_messages = ""

            # queue up any tail messages
            is_complete, parsed_msg, tail = self.__get_complete_message(message)
            if is_complete:
                message = parsed_msg
                self.__pending_messages = tail
                break

            # message is not complete, receive more data
            with self.__lock:
                if not self.is_running:
                    raise ConnectionError(f"Cannot receive message from the server at {self.server_address}: not connected")
            
                try:
                    message += self.__client.receive_message()
                except TimeoutError:
                    raise TimeoutError()
                except Exception as e:
                    raise ConnectionError(f"Error receiving message from the server at {self.server_address}: {e}")
        
        with self.__lock:
            self.__last_time_reply = time.time()
        
        logger.debug(f"Received complete message from the server: '{__class__.__escape_net_message(message)}'")
        parts = __class__.__from_net_message(message)
        res = None
        try:
            res = __class__.__parse_parts(parts)
        except ValueError as e:
            raise ValueError(f"Validation failed while parsing message from the server at {self.server_address}: {e}")

        return res
    

    def __receive_command_response(self, expected_command: str, check_for_ping: bool = True) -> ServerResponse:
        """
        Receives a response from the game server and returns it if it matches the expected command.
        It also handles the case when the server sends a ping message before the expected response.

        :param expected_command: The expected command.
        :type expected_command: str
        :return: The received response.
        :rtype: ServerResponse
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot receive message from the server at {self.server_address}: not connected")
        
            try:
                res = self.receive_message()
                # handle edge case when the server manages to send a ping message before the expected response
                if check_for_ping and res.command == CMD_PING:
                    self.pong()
                    res = self.receive_message()

                if res.command != expected_command:
                    logger.error(f"Invalid response received from the server at {self.server_address}: {res.command}")
                    return None
                
            except TimeoutError:
                raise TimeoutError(f"Timeout while waiting for response from the server at {self.server_address}")
            except Exception as e:
                raise ConnectionError(f"Error receiving message from the server at {self.server_address}: {e}")
        
        return res
    

    def login(self, username: str) -> bool:
        """
        Logs in to the game server with the given username.

        :param username: The username to log in with.
        :type username: str
        :return: True if the login was successful, false otherwise.
        :rtype: bool
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot login to the server at {self.server_address} - not connected")
    
            try:
                self.__send_cmd([CMD_TRY_VALID, username])
            except Exception as e:
                logger.error(f"Error sending login message to the server at {self.server_address} - {e}")
                
            try:
                res = self.__receive_command_response(CMD_ACKW_VALID, check_for_ping=False)
                if not res:
                    logger.error(f"Error logging in to the server at {self.server_address} - invalid server response")
                    return False
            except Exception as e:
                raise ConnectionError(f"Error receiving 'SHAKE' message from the server at {self.server_address} - {e}")

            try:    
                self.__send_cmd([CMD_CONFIRM_VALID])
            except Exception as e:
                raise ConnectionError(f"Error sending 'DEAL' message to the server at {self.server_address} - {e}")
            
        return True
        

    def logout(self) -> bool:
        """
        Logs out from the game server.

        :return: True if the logout was successful, false otherwise.
        :rtype: bool
        """

        with self.__lock:
            if not self.is_running:
                raise ConnectionError(f"Cannot logout from the server at {self.server_address}: not connected")
        
            try:
                self.__send_cmd([CMD_LEAVE])
            except Exception as e:
                raise ConnectionError(f"Error sending logout message to the server at {self.server_address}: {e}")

            try:
                res = self.__receive_command_response(CMD_CONFIRM_LEAVE)
                if not res:
                    raise ConnectionError(f"Error logging out from the server at {self.server_address} - invalid server response")
            except Exception as e:
                raise ConnectionError(f"Error receiving 'BYE' message from the server at {self.server_address}: {e}")
        
        return True