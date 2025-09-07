import pygame
from const.loggers import MAIN_LOGGER_NAME
from util import loggers
from const.server_communication import *


logger = loggers.get_logger(MAIN_LOGGER_NAME)


def init_menu_key_input_validator(obj, key_event):
    """
    Validates the key input for the initial menu.

    :param key_event: The key event to validate.
    :type key_event: pygame.event.Event
    :return: The validated key event.
    :rtype: pygame.event.Event
    """

    if key_event.key == pygame.K_RETURN or key_event.key == pygame.K_BACKSPACE:
        return key_event
    elif key_event.unicode.isprintable() and len(obj.context.text_input) < PLAYER_NICKNAME_MAX_LENGTH:
            return key_event
    else:
        logger.warning(f'Invalid key pressed: {key_event.unicode} for the input: {obj.context.text_input}')


def settings_key_input_validator(self, key_event):
    """
    Validates the key input for the settings menu.

    :param key_event: The key event to validate.
    :type key_event: pygame.event.Event
    :return: The validated key event.
    :rtype: pygame.event.Event
    """

    if key_event.key == pygame.K_RETURN or key_event.key == pygame.K_BACKSPACE or key_event.key == pygame.K_ESCAPE:
        return key_event
    
    elif (key_event.unicode.isnumeric() or key_event.unicode in ['.', ':']) and \
        len(self.context.text_input) < SERVER_ADDRESS_MAX_LENGTH:
            return key_event
    else:
        logger.warning(f'Invalid key pressed: {key_event.unicode} for the input: {self.context.text_input}')