"""
This module handles connections between the server and the clients.
"""

import socket
import threading
import time
import json
import sys
from typing import List
from const.loggers import MAIN_LOGGER_NAME
from util.loggers import get_logger

logger = get_logger(MAIN_LOGGER_NAME)


class GenericClient:
    """
    This class handles connections between the server and the clients.
    """


    __TIMEOUT_DURATION = 10
    """The duration of the timeout for the connection with the server."""
    

    def __init__(self, host, port):
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
    

    def send_message(self, message: str):
        """
        Sends a message to the server.

        :param message: The message.
        :type message: str
        """

        if not self.is_running:
            raise ConnectionError(f"Cannot send message to the server at {self.server_address}: not connected")
        
        try:
            self.__server_socket.sendall(message.encode())
        except socket.error as e:
            logger.error(f"Error sending message to the server at {self.server_address}: {e}")
            self.stop()


    def receive_expected_message(self, expected_message: str) -> bool:
        """
        Receives a message from the server and returns it if it matches the expected message.

        :param expected_message: The expected message.
        :type expected_message: str
        :return: True if the message matches the expected message, false otherwise.
        :rtype: bool
        """

        if not self.is_running:
            raise ConnectionError(f"Cannot receive message from the server at {self.server_address}: not connected")
        
        try:
            message = self.__server_socket.recv(len(expected_message)).decode()
            if message == expected_message:
                return True
            else:
                logger.error(f"Unexpected message from the server at {self.server_address}: {message}")
                return False
        
        except socket.error as e:
            logger.error(f"Error receiving message from the server at {self.server_address}: {e}")
            self.stop()
 
    
    def start(self):
        """
        Connects to the server.
        """

        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.settimeout(self.__TIMEOUT_DURATION)
        try:
            self.__server_socket.connect((self.__host, self.__port))
            self.__is_running = True
            logger.info(f"Connected to the server at {self.server_address}")
        except socket.error as e:
            logger.error(f"Error connecting to the server at {self.server_address}: {e}")
            self.__is_running = False
            self.__server_socket.close()
            self.__server_socket = None
    

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
            logger.info(f"Disconnected from the server at {self.server_address}")
    

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
    
    