"""
Module with pre-defined menus.
"""

from typing import List, Dict, Tuple, Union, Any
from abc import ABC
from graphics.menus.primitives import MenuOption, MenuTitle, TextInput
from util.loggers import get_temp_logger
from util.graphics import get_rendered_text_with_size, color_highlight
from graphics.viewport import Viewport
from typedefs import IBAssets
import pygame

tmp_logger = get_temp_logger('temp')
tmp_logger.info('temp logger created')
# TODO remove


class SelectMenu(Viewport):
    """
    Represents the select menu.
    """


    @staticmethod
    def handle_exit(self):
        # TODO DOC

        self.update_result.exit = True


    @staticmethod
    def __draw_options(surface: pygame.Surface, 
                       options: List[MenuOption], 
                       top_offset: int, 
                       option_height: int, 
                       option_width: int, 
                       option_x: int, 
                       assets: IBAssets, 
                       radius: int = -1):
        # TODO DOC

        update_rects = []
        for i, option in enumerate(options):
            y_offset = i * option_height
            y_offset_to_center = option_height // 2
            y_offset_gaps = (i + 1) * option_height
            option_y = top_offset + y_offset + y_offset_gaps + y_offset_to_center
            update_rect = option.render(surface, 
                                        (option_x, option_y), 
                                        height=option_height,
                                        width=option_width, 
                                        radius=radius,
                                        centered=True,
                                        color=assets['colors']['black'],
                                        background_color=assets['colors']['white'])
            update_rects.append(update_rect)
        
        return update_rects


    @staticmethod
    def __draw_title_and_options(surface: pygame.Surface, 
                                 title: MenuTitle, 
                                 options: List[MenuOption],
                                 scale_title_rect_radius_to_surface_width: float = 0.05, 
                                 scale_option_rect_radius_to_surface_width: float = 0.1,
                                 scale_title_area_to_screen_height: float = 0.35, 
                                 assets: IBAssets = None) -> List[pygame.Rect]:
        # TODO DOC, MAGIC NUMBERS

        update_rects = []
        surface_width, surface_height = surface.get_size()
        title_area_height = surface_height * scale_title_area_to_screen_height
        title_height = title_area_height * (1 / 2)
        title_width = surface_width * 0.65
        options_area_height = surface_height - title_area_height
        option_height = options_area_height / (len(options) + len(options) + 1)
        option_width = surface_width * 0.5

        title_x = surface_width // 2
        title_y = title_area_height * (2 / 3)
        update_rect = title.render(surface, 
                                   (title_x, title_y), 
                                   height=title_height, 
                                   width=title_width,
                                   radius=surface_width * scale_title_rect_radius_to_surface_width,
                                   centered=True,
                                   color=assets['colors']['black'],
                                   background_color=assets['colors']['white'])
        update_rects.append(update_rect)
        
        option_x = surface.get_width() // 2
        update_rects.extend(
            SelectMenu.__draw_options(surface, 
                                      options, 
                                      title_area_height, 
                                      option_height, 
                                      option_width, 
                                      option_x, 
                                      assets, 
                                      scale_option_rect_radius_to_surface_width * surface_width)
        )

        return update_rects
            

    @staticmethod
    def __draw_only_options(surface: pygame.Surface, options: List[MenuOption], assets: IBAssets):
        # TODO DOC

        update_rects = []
        option_height = surface.get_height() / (len(options) + len(options) + 1)
        option_width = surface.get_width() * 0.5
        option_x = surface.get_width() // 2

        update_rects.extend(SelectMenu.__draw_options(surface, options, 0, option_height, option_width, option_x, assets))
        
        return update_rects


    def __init__(self, surface: pygame.Surface, assets: IBAssets, title: MenuTitle = None, options: List[MenuOption] = None, scale_title_area_to_screen_height: float = 0.25):
        # TODO DOC

        if not pygame.get_init():
            raise ValueError('The pygame module has not been initialized.')
        if not pygame.font.get_init():
            raise ValueError('The pygame.font module has not been initialized.')
        if not pygame.display.get_init():
            raise ValueError('The pygame.display module has not been initialized.')
        if not pygame.display.get_surface():
            raise ValueError('The pygame.display module has not have a surface to render to.')
        
        self.__surface = surface
        self.__assets = assets

        master_display = pygame.display.get_surface()
        self.__background = pygame.Rect(0, 0, master_display.get_width(), master_display.get_height())

        self.__title = title
        self.__options = options
        self.__highlighted_option_index = -1

        # if both title and options are present
        if self.__title and self.__options:
            self.__draw_objects = \
                lambda: SelectMenu.__draw_title_and_options(self.__surface, 
                                                            self.__title, 
                                                            self.__options, 
                                                            scale_title_area_to_screen_height=scale_title_area_to_screen_height, 
                                                            assets=self.__assets)

        # else if only options are present
        elif self.__options:
            self.__draw_objects = \
                lambda: SelectMenu.__draw_only_options(self.__surface, 
                                                       self.__options, 
                                                       self.__assets)
        
        # else if only title is present
        else:
            raise ValueError('The select menu must have at least one option otherwise it is useless.')

    
    @property
    def surface(self):
        """
        Getter for the surface property.

        :return: The surface of the select menu.
        :rtype: pygame.Surface
        """

        return self.__surface
    

    @property
    def selected_option_text(self):
        """
        Getter for the selected_option_text property.

        :return: The text of the selected option.
        :rtype: str
        """

        return self.__options[self.highlighted_option_index].text
    

    @surface.setter
    def surface(self, surface: pygame.Surface):
        """
        Setter for the surface property.

        :param surface: The surface to set the select menu to.
        :type surface: pygame.Surface
        """

        self.__surface = surface

    
    @property
    def highlighted_option_index(self):
        """
        Getter for the highlighted_option_index property.

        :return: The index of the highlighted option.
        :rtype: int
        """

        return self.__highlighted_option_index
    

    def set_highlighted_option_index(self, index: int):
        """
        Setter for the highlighted_option_index property.
        Keeps the index within the bounds of the options list.

        :param index: The index of the option to highlight.
        :type index: int
        """

        if self.__highlighted_option_index != -1:
            self.__options[self.__highlighted_option_index].highlighted = False
        index = index % len(self.__options)
        self.__highlighted_option_index = index
        self.__options[self.__highlighted_option_index].highlighted = True
    

    def unset_highlighted_option_index(self):
        """
        Unsets the highlighted option index.
        """

        if self.__highlighted_option_index != -1:
            self.__options[self.__highlighted_option_index].highlighted = False
            self.__highlighted_option_index = -1


    def draw(self):
        # TODO DOC

        return self.__draw_objects()
        

    def redraw(self):
        """
        Redraws the select menu. Expects that the entire screen is redrawn 
        with pygame.display.flip() after this method is called.
        """

        # update and draw the background
        surface_width, surface_height = self.__surface.get_size()
        self.__background = pygame.Rect(0, 0, surface_width, surface_height)
        pygame.draw.rect(self.__surface, self.__assets['colors']['black'], self.__background)

        # draw the objects
        self.__draw_objects()


    def update(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the select menu.

        :param events: The events that occurred.
        :type events: Dict[str, Any]
        :return: Relevant information about the update.
        :rtype: Dict[str, Any]
        """

        result = {'graphics_update': False, 
                  'option_selected': -1, 
                  'submit': False}

        result['option_selected'] = self.highlighted_option_index

        # handle possible option hover
        if events.get('mouse_motion', False):
            if self.highlighted_option_index != -1:
                self.unset_highlighted_option_index()
                result['graphics_update'] = True

            for i, option in enumerate(self.__options):
                if option.rect.collidepoint(events['mouse_motion']):
                    if not option.highlighted:
                        self.set_highlighted_option_index(i)
                        result['graphics_update'] = True
                    break
        
        # handle possible option click
        if events.get('mouse_click', False):
            if self.__options[self.highlighted_option_index].rect.collidepoint(events['mouse_click']):
                result['submit'] = True
                return result

        # handle keyboard input
        if events.get('direction', False):
            if self.highlighted_option_index != -1:
                if events['direction'] == pygame.K_DOWN:
                    self.set_highlighted_option_index(self.highlighted_option_index + 1)
                    result['graphics_update'] = True
                elif events['direction'] == pygame.K_UP:
                    self.set_highlighted_option_index(self.highlighted_option_index - 1)
                    result['graphics_update'] = True
            else:
                self.set_highlighted_option_index(0)
                result['graphics_update'] = True
        
        # handle enter key
        if events.get('return', False):
            result['submit'] = True
            return result

        return result
    

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
                                            color=obj.__assets['colors']['white'])
        
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
        obj.__input_rect.render(obj.__surface, 
                                input_rect_position, 
                                height=input_rect_dimensions[1], 
                                width=input_rect_dimensions[0], 
                                centered=False, 
                                color=obj.__assets['colors']['black'], 
                                background_color=obj.__assets['colors']['white'])
        
        # draw the submit button (sprite from __assets)
        obj.__submit_button = pygame.transform.scale(obj.__assets['sprites']['ok'], (submit_button_dimensions[0], submit_button_dimensions[1]))
        obj.__surface.blit(obj.__submit_button, submit_button_position)
        
        objects_bounds_rect = pygame.Rect(objects_rect_position[0], objects_rect_position[1], objects_rect_dimensions[0], objects_rect_dimensions[1])
        input_rect = pygame.Rect(input_rect_position[0], input_rect_position[1], input_rect_dimensions[0], input_rect_dimensions[1])
        button_rect = pygame.Rect(submit_button_position[0], submit_button_position[1], submit_button_dimensions[0], submit_button_dimensions[1])

        return {'bounding_rect': objects_bounds_rect, 'input_rect': input_rect, 'button_rect': button_rect}
    

    def __init__(self, 
                 surface: pygame.Surface, 
                 assets: IBAssets, 
                 label_text: str):
        # TODO DOC
        

        if not pygame.get_init():
            raise ValueError('The pygame module has not been initialized.')
        if not pygame.font.get_init():
            raise ValueError('The pygame.font module has not been initialized.')
        if not pygame.display.get_init():
            raise ValueError('The pygame.display module has not been initialized.')
        if not pygame.display.get_surface():
            raise ValueError('The pygame.display module has not have a surface to render to.')
        
        self.__surface = surface
        self.__assets = assets
        self.__label_text = label_text

        self.__text_input = ''
        self.__input_rect = None
        self.__input_rect_bounds = None
        self.__submit_button_bounds = None
        self.__cursor_visible = None

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
        Getter for the text_input property.

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
        pygame.draw.rect(self.__surface, self.__assets['colors']['black'], self.__background)

        if not self.__input_rect:
            self.__input_rect = TextInput('', True)
            self.__cursor_visible = self.__input_rect.is_cursor_visible

        res = __class__.__draw_content(self)
        self.__input_rect_bounds = res['input_rect']
        self.__submit_button_bounds = res['button_rect']
    
    
    def draw(self):
        """
        Draws the input menu (input label, input field, and submit button).

        :return: The bounding rectangle of the input menu.
        :rtype: pygame.Rect
        """

        res = __class__.__draw_content(self)
        self.__input_rect_bounds = res['input_rect']
        self.__submit_button_bounds = res['button_rect']

        return res['bounding_rect']
    

    def update(self, events: Dict[str, Any]):
        # TODO DOC

        res = {'graphics_update': False, 'submit': False}

        # submitting the input
        if events.get('mouse_click', False):
            if self.__submit_button_bounds.collidepoint(events['mouse_click']):
                res['submit'] = True
                return res

        elif events.get('return', False):
            res['submit'] = True
            return res

        # non state changing events
        elif events.get('new_char', False):
            self.__text_input += events['new_char']
            if len(self.__input_rect.text) > 0 and self.__input_rect.text[-1] == TextInput.CURSOR:
                self.__input_rect.text = self.__input_rect.text[:-1] + events['new_char']
            else:
                self.__input_rect.text += events['new_char']
            res['graphics_update'] = True
        
        elif events.get('backspace', False) and len(self.__text_input) > 0:
            self.__text_input = self.__text_input[:-1]
            if self.__input_rect.text[-1] == TextInput.CURSOR:
                self.__input_rect.text = self.__input_rect.text[:-2]
            else:
                self.__input_rect.text = self.__input_rect.text[:-1]
            res['graphics_update'] = True

        # time to update the cursor
        elif self.__cursor_visible != self.__input_rect.is_cursor_visible:
            self.__cursor_visible = self.__input_rect.is_cursor_visible
            res['graphics_update'] = True

        return res