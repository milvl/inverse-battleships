"""
This module is responsible for managing the connection between the client and the server for the game Inverse Battleships.
"""

from typing import List
from util.generic_client import GenericClient
from util.loggers import get_logger
from const.loggers import MAIN_LOGGER_NAME


logger = get_logger(MAIN_LOGGER_NAME)


class ConnectionManager:
    """
    This class is responsible for managing the connection between the client and the server for the game Inverse Battleships.
    """

    __MSG_DELIMITER = ';'
    """The delimiter used to separate the parts of the messages sent between the server and the clients."""
    __MSG_TERMINATOR = '\n'
    """The terminator used to mark the end of the messages sent between the server and the clients."""
    __MSG_HEADER = 'IBGAME'
    """The header of the messages sent between the server and the clients."""
    __CMD_PING = 'PING'
    """The ping command."""
    __CMD_PONG = 'PONG'
    """The pong command."""
    __CMD_TRY_VALID = 'HAND'
    """The hand command."""
    __CMD_ACKW_VALID = 'SHAKE'
    """The shake command."""
    __CMD_CONFIRM_VALID = 'DEAL'
    """The deal command."""
    __CMD_LEAVE = 'LEAVE'
    """The leave command."""
    __CMD_CONFIRM_LEAVE = 'BYE'
    """The bye command."""


    @staticmethod
    def __to_net_message(parts: List[str]) -> str:
        """
        Returns a formatted message from the parts for the network communication.

        :param parts: The parts of the message.
        :type parts: List[str]
        :return: The message.
        :rtype: str
        """

        for i, part in enumerate(parts):
            if __class__.__MSG_TERMINATOR in part:
                raise ValueError(f"Message part {i}: '{part}' contains the message terminator '{__class__.__MSG_TERMINATOR}'")
            parts[i] = part.replace(__class__.__MSG_DELIMITER, f"\\{__class__.__MSG_DELIMITER}")

        
        return f"{__class__.__MSG_HEADER}{__class__.__MSG_DELIMITER}{__class__.__MSG_DELIMITER.join(parts)}{__class__.__MSG_TERMINATOR}"
    

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
        return message.encode('unicode_escape').decode('utfs-8') 


    def __init__(self, server_ip: str, server_port: int):
        """
        Initializes the connection manager.

        :param server_ip: The game server IP address.
        :type server_ip: str
        :param server_port: The game server port.
        :type server_port: int
        """

        self.__client = GenericClient(server_ip, server_port)


    @property
    def is_running(self) -> bool:
        """
        Checks if the connection manager is running and is connected to the server.

        :return: True if the connection manager is running and is connected to the server, false otherwise.
        :rtype: bool
        """

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
    

    def __send_cmd(self, parts: List[str]):
        """
        Sends a command to the game server.

        :param parts: The parts of the command.
        :type parts: List[str]
        """

        if not self.is_running:
            raise ConnectionError(f"Cannot send message to the server at {self.server_address}: not connected")
        
        message = __class__.__to_net_message(parts)
        
        try:
            self.__client.send_message(message)
            logger.debug(f"Sent message to the server at {self.server_address}: {__class__.__escape_net_message(message)}")
        except ConnectionError as e:
            logger.critical(f"Could not send message to the server at {self.server_address}: {e}")
            self.__client.stop()
    

    def __receive_expected_response(self, expected_parts: List[str]) -> bool:
        """
        Receives a response from the game server and returns it if it matches the expected format.

        :param expected_parts: The expected parts of the command.
        :type expected_parts: List[str]
        :return: True if the response matches the expected format, false otherwise.
        :rtype: bool
        """

        if not self.is_running:
            raise ConnectionError(f"Cannot receive message from the server at {self.server_address}: not connected")
        
        expected_resp = __class__.__to_net_message(expected_parts)
        try:
            if self.__client.receive_expected_message(expected_resp):
                return True
            else:
                logger.critical(f"Received unexpected response from the server at {self.server_address}")
                logger.debug(f"Expected: {__class__.__escape_net_message(expected_resp)}")
                logger.debug(f"Received: {__class__.__escape_net_message(self.__client.last_received_message)}")
                return False
        
        except Exception as e:
            logger.critical(f"Error receiving message from the server at {self.server_address}: {e}")
            self.__client.stop()
            return False
        
    
    def __ping(self) -> bool:
        """
        Sends a ping message to the game server.

        :return: True if the ping message was sent and responded to successfully, false otherwise.
        :rtype: bool
        """

        if self.is_running:
            try:
                self.__send_cmd([__class__.__CMD_PING])
                
                if not self.__receive_expected_response([__class__.__CMD_PONG]):
                    logger.error(f"Error receiving pong message from the server at {self.server_address}")
                    self.stop()
                    return False
                
                return True

            except Exception as e:
                logger.critical(f"Error sending ping message to the server at {self.server_address}: {e}")
                self.stop()
                return False
    

    def __pong(self):
        """
        Sends a pong message to the game server.
        """

        if self.is_running:
            try:
                self.__send_cmd([__class__.__CMD_PONG])
            except Exception as e:
                logger.critical(f"Error sending pong message to the server at {self.server_address}: {e}")
                self.stop()
    

    def __try_disconnect(self) -> bool:
        """
        Sends a disconnect message to the game server.

        :return: True if the disconnect message was sent successfully, false otherwise.
        :rtype: bool
        """

        if self.is_running:
            try:
                # send disconnect message
                self.__send_cmd([__class__.__CMD_LEAVE])

                # wait for the server to respond
                if not self.__receive_expected_response([__class__.__CMD_CONFIRM_LEAVE]):
                    logger.critical(f"Error receiving 'BYE' message from the server at {self.server_address}")
                    return False
                
                return True
                
            except Exception as e:
                logger.error(f"Error sending disconnect message to the server at {self.server_address}: {e}")
                return False
    

    def __validate_connection(self) -> bool:
        """
        Authenticates the connection with the game server.
        It sends a handshake request to the server and waits for a response.
        Then, it validates the response and sends a confirmation message.

        :return: True if the connection was authenticated successfully, false otherwise.
        :rtype: bool
        """

        if not self.is_running:
            raise ConnectionError(f"Cannot validate connection with the server at {self.server_address}: not connected")
        
        try:
            # send authentication message
            self.__send_cmd([__class__.__CMD_TRY_VALID])

            # wait for the server to respond
            if not self.__receive_expected_response([__class__.__CMD_ACKW_VALID]):
                logger.critical(f"Error receiving 'SHAKE' message from the server at {self.server_address}")
                return False
            
            self.__send_cmd([__class__.__CMD_CONFIRM_VALID])
            return True
            
        except Exception as e:
            logger.critical(f"Error validating connection with the server at {self.server_address}: {e}")
            self.stop()
            return False
        

    def start(self):
        """
        Connects to the server.
        """

        try:
            self.__client.start()
            logger.info(f"Connected to the server at {self.server_address}")
        except Exception as e:
            logger.critical(f"Error connecting to the server at {self.server_address}: {e}")
            self.__client.stop()
    

    def stop(self):
        """
        Disconnects from the server.
        """

        if not self.is_running:
            raise ConnectionError(f"Cannot disconnect from the server at {self.server_address}: not connected")
        
        if not self.__try_disconnect():
            logger.error(f"Error disconnecting properly from the server at {self.server_address}. Forcing disconnection.")

        try:
            self.__client.stop()
        except ConnectionError as e:
            logger.error(f"Error disconnecting from the server at {self.server_address}: {e}")
            logger.warning(f"Attempted to disconnect from the server at {self.server_address}, but no active connection")
    

    def __enter__(self):
        """
        Called when entering the context manager.
        """

        self.start()
        return self
    

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Called when exiting the context manager.
        """

        try:
            self.stop()
        except Exception as e:
            logger.error(e)
        

    def test_connection(self) -> bool:
        """
        Tests the connection with the server.

        :return: True if the connection is valid and responsive, false otherwise.
        :rtype: bool
        """

        if not self.is_running:
            raise ConnectionError(f"Cannot test connection with the server at {self.server_address}: not connected")
        
        try:
            if self.__validate_connection():
                logger.info(f"Connection with the server at {self.server_address} is valid")
            else:
                logger.critical(f"Connection with the server at {self.server_address} is invalid")
                return False
            
            if self.__ping():
                logger.info(f"Connection with the server at {self.server_address} is responsive")
            else:
                logger.critical(f"Connection with the server at {self.server_address} is unresponsive")
                return False

            # context manager will handle the disconnection
            return True
            
        except Exception as e:
            logger.critical(f"Error testing connection with the server at {self.server_address}: {e}")
            return False