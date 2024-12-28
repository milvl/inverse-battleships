"""
A module containing the SettingsMenu class.
"""

import time
from typing import Any, Dict, List
import re
import pygame
from pygame.rect import Rect
from const.typedefs import IBAssets
from graphics.menus.input_menu import InputMenu


class SettingsMenu(InputMenu):      # Only one setting is needed for this game. For expanded functionality, this class should be reworked from scratch.
    """
    A class representing the settings menu. This menu is used to set the server IP address and port number.
    """

    INVALID_INPUT_BLINK_RATE = 0.25
    INVALID_INPUT_BLINK_DURATION = 2

    def __init__(self, surface: pygame.Surface, assets: IBAssets, label_text: str, server_address: str):
        """
        Initializes the settings menu.

        :param surface: The surface to draw the settings menu on.
        :type surface: pygame.Surface
        :param assets: The assets to use for the settings menu.
        :type assets: IBAssets
        :param label_text: The text to display as the label for the input field.
        :type label_text: str
        :param server_address: The server address to display in the input field.
        :type server_address: str
        """

        super().__init__(surface, assets, label_text, server_address)
        self.__invalid_input = False
        self.__invalid_input_state = None
        self.__last_time = None
    

    def redraw(self):
        """
        Redraws the input menu. Expects that the entire screen is redrawn with pygame.display.flip() after this method is called.
        """

        # implemented in parent class
        super().redraw()
    

    def draw(self) -> Rect:
        """
        Draws the input menu (input label, input field, and submit button).

        :return: The bounding rectangle of the input menu.
        :rtype: Rect
        """

        # implemented in parent class
        return super().draw()
    

    def update(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the settings menu based on the given events.

        :param events: The events to update the settings menu with.
        :type events: Dict[str, Any]
        :return: A dictionary containing the following
        :rtype: Dict[str, Any]
        """
        
        res = {'graphics_update': False, 'submit': False, 'escape': False}

        if events.get('invalid_input', False):
            self.__invalid_input = True
            self.__invalid_input_state = 0
            self.__last_time = time.time()
            self.__invalid_input_total_time = 0
            res['graphics_update'] = True
        
        elif super()._user_submitted(events, self._submit_button_bounds):
            res['submit'] = True
            
        elif events.get('new_char', False):
            self.__invalid_input_total_time = __class__.INVALID_INPUT_BLINK_DURATION
            super()._handle_new_char(events['new_char'])
            res['graphics_update'] = True
        
        elif events.get('backspace', False) and len(self.text_input) > 0:
            self.__invalid_input_total_time = __class__.INVALID_INPUT_BLINK_DURATION
            super()._handle_backspace()
            res['graphics_update'] = True
        
        elif events.get('escape', False):
            res['escape'] = True

        # time to update the cursor
        elif self._cursor_visible != self._input_rect.is_cursor_visible:
            self._cursor_visible = self._input_rect.is_cursor_visible
            res['graphics_update'] = True
        
        # handle invalid input feedback
        if self.__invalid_input:
            if time.time() - self.__last_time > __class__.INVALID_INPUT_BLINK_RATE:
                self.__invalid_input_total_time += __class__.INVALID_INPUT_BLINK_RATE
                self.__last_time = time.time()
                self.__invalid_input_state += 1

            # color switching
            if self.__invalid_input_state % 2 == 0:
                self._custom_text_color = self._assets['colors']['red']
            else:
                self._custom_text_color = None

            # check for the end of the invalid input feedback
            if self.__invalid_input_total_time >= __class__.INVALID_INPUT_BLINK_DURATION:
                self.__invalid_input = False
                self.__invalid_input_state = None
                self.__last_time = None
                self.__invalid_input_total_time = None
                self._custom_text_color = None
                
            res['graphics_update'] = True

        return res