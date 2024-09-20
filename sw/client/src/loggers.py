"""
Module with custom logger with advanced logging
"""

import json
import logging
import sys
from termcolor import colored

class NullLogger:
    """
    Null logger; represents disabled logging.
    """
    
    
    def __init__(self):
        """
        Does nothing.
        """
        
        pass
        
    
    def critical(self, *args):
        """
        Does nothing.
        """
        
        pass


    def exception(self, *args):
        """
        Does nothing.
        """
        
        pass
    
    
    def error(self, *args):
        """
        Does nothing.
        """
        
        pass


    def warning(self, *args):
        """
        Does nothing.
        """
        
        pass


    def warn(self, *args):
        """
        Does nothing.
        """
        
        pass
    
    
    def info(self, *args):
        """
        Does nothing.
        """
        
        pass


    def debug(self, *args):
        """
        Does nothing.
        """
        
        pass


""" Dictionary with loggers. """
__loggers: dict[str, logging.Logger] = {}

""" Implicit logger if needed. """
__implicit_logger = None

""" Temporary loggers for debug session. """
__temp_loggers: dict[str, logging.Logger|NullLogger] = {}

""" Flag if all loggers are ready for use. """
__ready: bool = False

LOG_COLORS = {
            'DEBUG': 'light_blue',
            'INFO': 'white', 
            'WARNING': 'yellow', 
            'ERROR': 'light_red', 
            'CRITICAL': 'red',
            '__TEMP': 'light_green'
    }


class ColoredFormater(logging.Formatter):
    """Formating of logging with colors."""

    def format(self, record):
        """
        Formats the record with specified color (invalid defaults to white).
        
        :param record: The record
        :return: Formated record.
        """
        
        log_message = super().format(record)
        return colored(log_message, LOG_COLORS.get(record.levelname, "white"))


def __create_handler(handler_config: dict) -> logging.Handler:
    """
    Creates a handler for logger.

    :param handler_config: Handler config
    :return: Handler
    """

    formater = None
    if handler_config['output'] == 'stdout' or handler_config['output'] == 'console':
        handler = logging.StreamHandler(sys.stdout)
        formatter = ColoredFormater(handler_config['format'], datefmt=handler_config['datefmt'])
    elif handler_config['output'] == 'stderr':
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(handler_config['format'], datefmt=handler_config['datefmt'])
    else:
        handler = logging.FileHandler(handler_config['output'])
        formatter = logging.Formatter(handler_config['format'], datefmt=handler_config['datefmt'])

    handler.setLevel(handler_config['level'])
    handler.setFormatter(formatter)

    return handler


def is_ready() -> bool:
    """
    Returns true if all loggers are ready, false otherwise.

    :return: True if all loggers are ready, false otherwise.
    """
    
    return __ready


def set_path_to_config_file(json_file_path: str):
    """
    Sets up a path to the file with loggers config.

    :param json_file_path: Path to the file with loggers config
    """
    
    with open(json_file_path, 'r') as file:
        config = json.load(file)

    # loggers creation
    for logger_name in config['loggers']:
        if logger_name not in __loggers:
            __loggers[logger_name] = logging.getLogger(logger_name)
            __loggers[logger_name].setLevel(logging.DEBUG)  # lowest logging level => arbitrary level throughput
    
    # for temp loggers
    if 'temp_loggers' in config:
        for logger_name, is_enabled in config['temp_loggers'].items():
            if logger_name not in __temp_loggers:
                if is_enabled:
                    __temp_loggers[logger_name] = logging.getLogger(logger_name)
                    __temp_loggers[logger_name].setLevel(logging.DEBUG)
                    handler = logging.StreamHandler()
                    formatter = logging.Formatter(colored('TEMP LOG (%(name)s) - [%(module)s:%(lineno)d] - "%(message)s"',
                                                          LOG_COLORS['__TEMP']))
                    handler.setFormatter(formatter)
                    __temp_loggers[logger_name].addHandler(handler)
                    
                # if is disabled
                else:
                    __temp_loggers[logger_name] = NullLogger()

    for handler_config_name, handler_config in config['logger_handler_configs'].items():
        logger_name, handler_name = handler_config_name.split('.')
        handler = __create_handler(handler_config)
        # assignment of general handler to each logger
        if logger_name in config['loggers_general']:
            for logger in __loggers.values():
                logger.addHandler(handler)
                
        # assignment of specified handler to specified logger
        else:
            if logger_name in __loggers:
                __loggers[logger_name].addHandler(handler)
                
    global __ready
    __ready = True


def get_logger(logger_name: str = '') -> logging.Logger:
    """
    Returns a logger configured from the config file.

    :param logger_name: Name of the logger
    :return: Logger
    """

    if not __ready:
        raise SystemError("Loggers are not ready yet.")
    
    if not isinstance(logger_name, str):
        raise TypeError(f"logger_name must be a string, not {type(logger_name).__name__}.")
    
    if logger_name == '':
        global __implicit_logger
        if not __implicit_logger:
            __implicit_logger = logging.getLogger()
            __implicit_logger.setLevel(logging.DEBUG)
            f = logging.Formatter('%(asctime)s.%(msecs)03d - [%(levelname)s] - (%(module)s - %(funcName)s:%(lineno)d) - \"%(message)s\"', datefmt='%H:%M:%S')
            h = logging.StreamHandler()
            h.setFormatter(f)
            __implicit_logger.addHandler(h)
            __implicit_logger.warning("Default logging.logger used.")
        return __implicit_logger
    
    if logger_name in __loggers:
        return __loggers[logger_name]
    else:
        raise ValueError(f"No logger configured with name '{logger_name}'.")


def get_temp_logger(name: str) -> logging.Logger|NullLogger:
    """
    Returns temp debug logger configured from the config file.

    :param name: Name of the temp logger
    :return: Temp logger
    """

    if not __ready:
        raise SystemError("Loggers are not ready yet.")
    
    if name in __temp_loggers:
        return __temp_loggers[name]
    else:
        raise ValueError(f"No temp logger with name '{name}' registered.")