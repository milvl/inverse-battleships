"""
This module handles connections between the server and the clients.
"""

import socket
import threading
from const.loggers import MAIN_LOGGER_NAME
from util.loggers import get_logger

logger = get_logger(MAIN_LOGGER_NAME)


class GenericClient:
    """
    This class handles connections between the server and the clients.
    """


    TIMEOUT_DURATION = 1
    """The duration of the timeout for the connection with the server."""

    BUFFER_SIZE = 1024
    """The size of the buffer for the connection with the server."""
    

    def __init__(self, host: str, port: int):
        """
        Creates a new ConnectionManager object.

        :param host: The host of the server.
        :type host: str
        :param port: The port of the server.
        :type port: int
        """

        self.__host: str = host
        self.__port: int = port
        self.__server_socket = None
        self.__is_running: bool = False
    

    @property
    def is_running(self):
        """
        Returns true if the client is running and is connected to the server, false otherwise.

        :return: True if the client is running and is connected to the server, false otherwise.
        :rtype: bool
        """

        return self.__is_running
    

    @property
    def host(self):
        """
        Getter for host.

        :return: The host of the server.
        :rtype: str
        """

        return self.__host
    

    @property
    def port(self):
        """
        Getter for port.

        :return: The port of the server.
        :rtype: int
        """

        return self.__port
    

    @property
    def server_address(self):
        """
        Getter for server_address.

        :return: The server
        :rtype: str
        """
        
        return f"{self.__host}:{self.__port}"
    

    def start(self):
        """
        Connects to the server.
        """

        if self.is_running:
            raise ConnectionError(f"Cannot connect to the server at {self.server_address}: already connected")
        
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.settimeout(self.TIMEOUT_DURATION)
        try:
            self.__server_socket.connect((self.__host, self.__port))
            self.__is_running = True
        except socket.error as e:
            raise ConnectionError(f"Error connecting to the server at {self.server_address}: {e}")
    

    def stop(self):
        """
        Disconnects from the server.
        """

        if not self.is_running:
            raise ConnectionError(f"Cannot disconnect from the server at {self.server_address}: not connected")

        self.__is_running = False
        if self.__server_socket is not None:
            self.__server_socket.close()
            self.__server_socket = None
    

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
        except ConnectionError as e:
            logger.warning(f"Attempted to disconnect from the server at {self.server_address}, but no active connection.")
            logger.error(e)
    

    def send_message(self, message: str):
        """
        Sends a message to the server.

        :param message: The message.
        :type message: str
        :raises ConnectionError: If an error occurs while sending the message.
        :raises ValueError: If the message is too long to send.
        """

        if not self.is_running:
            raise ConnectionError(f"Cannot send message to the server at {self.server_address}: not connected")
        
        if len(message) > self.BUFFER_SIZE:
            raise ValueError(f"Message too long to send to the server at {self.server_address}: {message}")

        try:
            self.__server_socket.sendall(message.encode())
        except socket.error as e:
            raise ConnectionError(f"Error sending message to the server at {self.server_address}: {e}")


    # def receive_expected_message(self, expected_message: str) -> bool:
    #     """
    #     Receives a message from the server and returns it if it matches the expected message.

    #     :param expected_message: The expected message.
    #     :type expected_message: str
    #     :return: True if the message matches the expected message, false otherwise.
    #     :rtype: bool
    #     :raises ConnectionError: If an error occurs while receiving the message
    #     """

    #     message = ""
    #     if not self.is_running:
    #         raise ConnectionError(f"Cannot receive message from the server at {self.server_address}: not connected")
        
    #     try:
    #         expected_size = len(expected_message)
    #         data = b""
    #         while len(data) < expected_size:
    #             chunk = self.__server_socket.recv(expected_size - len(data))
    #             if not chunk:  # connection closed
    #                 break
    #             data += chunk
    #         message = data.decode()

    #     except socket.error as e:
    #         raise ConnectionError(f"Error receiving message from the server at {self.server_address}: {e}")    
            
    #     if message == expected_message:
    #         return True
    #     else:
    #         logger.error(f"Unexpected message from the server at {self.server_address}: \"{message}\", expected \"{expected_message}\"")
    #         return False
    

    def receive_message(self) -> str:
        """
        Receives a message from the server.

        :return: The message.
        :rtype: str
        :raises ValueError: If no data is received.
        :raises ConnectionError: If an error occurs while receiving the message.
        """

        message = ""
        data = b""
        if not self.is_running:
            raise ConnectionError(f"Cannot receive message from the server at {self.server_address}: not connected")
        
    
        try:
            data = self.__server_socket.recv(self.BUFFER_SIZE)
        except TimeoutError:
            raise TimeoutError()
        except socket.error as e:
            raise ConnectionError(f"Error receiving message from the server at {self.server_address}: {e}")    
            
        # will not happen
        # if not data:
        #     raise ValueError(f"Error receiving message from the server at {self.server_address}: no data received")

        message = data.decode()
        return message
    