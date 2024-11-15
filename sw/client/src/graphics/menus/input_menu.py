"""
Module with pre-defined menus.
"""

from typing import Dict, Any
from graphics.menus.primitives import TextInput
from util.loggers import get_temp_logger
from util.graphics import get_rendered_text_with_size
from graphics.viewport import Viewport
from const.typedefs import IBAssets
import pygame

tmp_logger = get_temp_logger('temp')
tmp_logger.info('temp logger created')
# TODO remove
    

class InputMenu(Viewport):
    """
    Represents the input menu.
    """


    __OBJECTS_RECT_SCALE = 0.5
    __INPUT_RECT_WIDTH_SCALE = 0.75
    __INPUT_RECT_HEIGHT_SCALE = 0.25
    __LABEL_RECT_SCALE = 1 - __INPUT_RECT_HEIGHT_SCALE
    __IN_BTTN_GAP_W_SCALE_TO_LBL_H = 0.25
    __LBL_IN_GAP_H_SCALE_TO_BTTN_W = 0.5


    @staticmethod
    def __draw_content(obj):
        # TODO DOC

        surface_dimensions = obj.__surface.get_size()
        surface_center = surface_dimensions[0] // 2, surface_dimensions[1] // 2
        surface_width, surface_height = surface_dimensions

        # rect that will contain the label and input
        objects_rect_dimensions = surface_width * __class__.__OBJECTS_RECT_SCALE, surface_height * __class__.__OBJECTS_RECT_SCALE
        objects_rect_position = (surface_center[0] - objects_rect_dimensions[0] // 2, surface_center[1] - objects_rect_dimensions[1] // 2)

        # input rect
        input_rect_dimensions_w = objects_rect_dimensions[0] * __class__.__INPUT_RECT_WIDTH_SCALE
        input_rect_dimensions_h = objects_rect_dimensions[1] * __class__.__INPUT_RECT_HEIGHT_SCALE
        input_rect_dimensions = input_rect_dimensions_w, input_rect_dimensions_h

        # submit button
        submit_button_dimensions = input_rect_dimensions[1], input_rect_dimensions[1]

        # input label
        label_rect_desired_dimensions = objects_rect_dimensions[0], objects_rect_dimensions[1] * __class__.__LABEL_RECT_SCALE
        # get real dimensions
        label = get_rendered_text_with_size(obj.__label_text, 
                                            label_rect_desired_dimensions[0], 
                                            label_rect_desired_dimensions[1], 
                                            color=obj._assets['colors']['white'])
        
        # positionings
        label_input_gap_height = label.get_height() * __class__.__LBL_IN_GAP_H_SCALE_TO_BTTN_W
        label_rect_position_x = objects_rect_position[0] + (objects_rect_dimensions[0] - label.get_width()) // 2
        label_rect_position_y = objects_rect_position[1] + (objects_rect_dimensions[1] - label.get_height() - input_rect_dimensions[1] - label_input_gap_height) // 2
        label_rect_position = label_rect_position_x, label_rect_position_y
        input_button_gap_width = submit_button_dimensions[0] * __class__.__IN_BTTN_GAP_W_SCALE_TO_LBL_H
        input_rect_position_x = objects_rect_position[0] + (objects_rect_dimensions[0] - input_rect_dimensions[0] - submit_button_dimensions[0] - input_button_gap_width) // 2
        input_rect_position_y = label_rect_position[1] + label.get_height() + label_input_gap_height
        input_rect_position = input_rect_position_x, input_rect_position_y
        submit_button_position = input_rect_position[0] + input_rect_dimensions[0] + input_button_gap_width, input_rect_position[1]

        # draw the label
        obj.__surface.blit(label, label_rect_position)

        # draw the input
        color = obj._assets['colors']['black'] if not obj._custom_text_color else obj._custom_text_color
        obj._input_rect.render(obj.__surface, 
                                input_rect_position, 
                                height=input_rect_dimensions[1], 
                                width=input_rect_dimensions[0], 
                                centered=False, 
                                color=color,
                                background_color=obj._assets['colors']['white'])
        
        # draw the submit button (sprite from _assets)
        obj.__submit_button = pygame.transform.scale(obj._assets['sprites']['ok'], (submit_button_dimensions[0], submit_button_dimensions[1]))
        obj.__surface.blit(obj.__submit_button, submit_button_position)
        
        objects_bounds_rect = pygame.Rect(objects_rect_position[0], objects_rect_position[1], objects_rect_dimensions[0], objects_rect_dimensions[1])
        input_rect = pygame.Rect(input_rect_position[0], input_rect_position[1], input_rect_dimensions[0], input_rect_dimensions[1])
        button_rect = pygame.Rect(submit_button_position[0], submit_button_position[1], submit_button_dimensions[0], submit_button_dimensions[1])

        return {'bounding_rect': objects_bounds_rect, 'input_rect': input_rect, 'button_rect': button_rect}


    @staticmethod
    def _user_submitted(events: Dict[str, Any], submit_button_bounds: pygame.Rect):
        """
        Tests if the user has submitted the input.

        :param events: The events dictionary.
        :type events: Dict[str, Any]
        :param submit_button_bounds: The bounding rectangle of the submit button.
        :type submit_button_bounds: pygame.Rect
        :return: True if the user has submitted the input, False otherwise.
        :rtype: bool
        """

        if events.get('mouse_click', False):
            if submit_button_bounds.collidepoint(events['mouse_click']):
                return True
        elif events.get('return', False):
            return True
        

    def _handle_backspace(self):
        """
        Handles the backspace event.
        """

        self.__text_input = self.__text_input[:-1]
        if self._input_rect.text[-1] == TextInput.CURSOR:
            self._input_rect.text = self._input_rect.text[:-2]
        else:
            self._input_rect.text = self._input_rect.text[:-1]

    
    def _handle_new_char(self, new_char: str):
        """
        Handles the new character event.

        :param new_char: The new character to handle.
        :type new_char: str
        """

        self.__text_input += new_char
        if len(self._input_rect.text) > 0 and self._input_rect.text[-1] == TextInput.CURSOR:
            self._input_rect.text = self._input_rect.text[:-1] + new_char
        else:
            self._input_rect.text += new_char
    

    def __init__(self, 
                 surface: pygame.Surface, 
                 assets: IBAssets, 
                 label_text: str,
                 initial_text: str = ''):
        """
        Creates an instance of the InputMenu class.

        :param surface: The surface to render the input menu to.
        :type surface: pygame.Surface
        :param assets: The assets dictionary.
        :type assets: IBAssets
        :param label_text: The text of the input label.
        :type label_text: str
        :param initial_text: The initial text of the input field, defaults to ''.
        :type initial_text: str, optional
        """
        

        if not pygame.get_init():
            raise ValueError('The pygame module has not been initialized.')
        if not pygame.font.get_init():
            raise ValueError('The pygame.font module has not been initialized.')
        if not pygame.display.get_init():
            raise ValueError('The pygame.display module has not been initialized.')
        if not pygame.display.get_surface():
            raise ValueError('The pygame.display module has not have a surface to render to.')
        
        self.__surface = surface
        self._assets = assets
        self.__label_text = label_text

        self.__text_input = initial_text
        self._custom_text_color = None
        self._input_rect = None
        self.__input_rect_bounds = None
        self._submit_button_bounds = None
        self._cursor_visible = None

        master_display = pygame.display.get_surface()
        self.__background = pygame.Rect(0, 0, master_display.get_width(), master_display.get_height())
    

    @property
    def surface(self):
        """
        Getter for the surface property.

        :return: The surface of the input menu.
        :rtype: pygame.Surface
        """

        return self.__surface
    

    @surface.setter
    def surface(self, surface: pygame.Surface):
        """
        Setter for the surface property.

        :param surface: The surface to set the input menu to.
        :type surface: pygame.Surface
        """

        self.__surface = surface

    
    @property
    def text_input(self):
        """
        Getter for the text_input property. Represents the 
        text input of the input menu without the cursor.

        :return: The text input of the input menu.
        :rtype: str
        """

        return self.__text_input
        

    def redraw(self):
        """
        Redraws the input menu. Expects that the entire screen is redrawn 
        with pygame.display.flip() after this method is called.
        """

        # update and draw the background
        surface_dimensions = self.__surface.get_size()
        self.__background = pygame.Rect(0, 0, surface_dimensions[0], surface_dimensions[1])
        pygame.draw.rect(self.__surface, self._assets['colors']['black'], self.__background)

        if not self._input_rect:
            self._input_rect = TextInput(self.__text_input, True)
            self._cursor_visible = self._input_rect.is_cursor_visible

        res = __class__.__draw_content(self)
        self.__input_rect_bounds = res['input_rect']
        self._submit_button_bounds = res['button_rect']
    
    
    def draw(self):
        """
        Draws the input menu (input label, input field, and submit button).

        :return: The bounding rectangle of the input menu.
        :rtype: pygame.Rect
        """

        res = __class__.__draw_content(self)
        self.__input_rect_bounds = res['input_rect']
        self._submit_button_bounds = res['button_rect']

        return res['bounding_rect']
    

    def update(self, events: Dict[str, Any]):
        """
        Updates the input menu. Based on the events dictionary, the method
        returns a dictionary with keys 
        and values:
            - 'graphics_update' (bool): True if the graphics need to be updated,
            False otherwise.
            - 'submit' (bool): True if the user has submitted the input, False
            otherwise.

        :param events: The events dictionary.
        :type events: Dict[str, Any]
        :return: A dictionary with the keys 'graphics_update' and 'submit'.
        :rtype: Dict[str, Any]
        """

        res = {'graphics_update': False, 'submit': False}

        # submitting the input
        if __class__._user_submitted(events, self._submit_button_bounds) and len(self.__text_input) > 0:
            res['submit'] = True

        # non state changing events
        elif events.get('new_char', False):
            self._handle_new_char(events['new_char'])
            res['graphics_update'] = True
        
        elif events.get('backspace', False) and len(self.__text_input) > 0:
            self._handle_backspace()
            res['graphics_update'] = True

        # time to update the cursor
        elif self._cursor_visible != self._input_rect.is_cursor_visible:
            self._cursor_visible = self._input_rect.is_cursor_visible
            res['graphics_update'] = True

        return res