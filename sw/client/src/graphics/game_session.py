import threading
from typing import Any, Dict, List, Tuple
import pygame
from const.typedefs import IBAssets
from const.server_communication import BOARD_FREE_CELL, BOARD_PLAYER_CELL, BOARD_PLAYER_SHIP_LOST_CELL, BOARD_OPPONENT_SHIP_LOST_CELL
from const.server_communication import SCORE_SHIP_GAINED, SCORE_HIT, SCORE_LOST_SHIP
from graphics.viewport import Viewport
from util.graphics import get_rendered_text_with_size


class GameSession(Viewport):
    """Represents the game session graphics context."""


    BOARD_FREE = BOARD_FREE_CELL
    """The value of a free cell on the board."""
    BOARD_PLAYER = BOARD_PLAYER_CELL
    """The value of a player cell on the board."""
    BOARD_LOST = BOARD_PLAYER_SHIP_LOST_CELL
    """The value of an opponent cell on the board."""
    BOARD_OPPONENT_LOST = BOARD_OPPONENT_SHIP_LOST_CELL
    """The value of an opponent lost cell on the board."""
    TEXT_UNSET = "ERROR"
    """The text to display when the text is unset."""
    RATIO_BOARD_TO_SCREEN_WIDTH = 9/16
    """The ratio of the board width to the screen width."""
    RATIO_INFO_PANEL_TO_SCREEN_WIDTH = (1 - RATIO_BOARD_TO_SCREEN_WIDTH) / 2
    """The ratio of the info panel width to the screen width."""
    RATIO_INFO_PANEL_TO_SCREEN_HEIGHT = 0.5
    """The ratio of the info panel height to the screen height."""
    RATIO_TEXT_WIDTH_TO_PANEL_WIDTH = 0.8
    """The ratio of the text width to the panel width."""
    RATIO_TEXT_HEIGHT_TO_PANEL_HEIGHT = 0.8
    """The ratio of the text height to the panel height."""
    RATIO_OUTLINE_TO_CELL = 0.05
    """The ratio of the outline to the cell."""
    SYMBOLS_ROW = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    """The symbols for the rows of the board."""
    SYMBOLS_COLUMN = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    """The symbols for the columns of the board."""


    def __init__(self, 
                 surface: pygame.Surface, 
                 assets: IBAssets):

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
        self.__background_color = self.__assets['colors']['black']
        self.__background = pygame.Rect(0, 0, master_display.get_width(), master_display.get_height())
        self.__text_color = self.__assets['colors']['white']
        
        self.__last_action = ""
        self.__selected_cell = None
        self.__highlighted_cell = None
        self.__hit_check_cells = None
        self.__player_on_turn = None
        self.__player_name = None
        self.__opponent_name = None

    
    @property
    def surface(self):
        """
        Getter for the surface property.

        :return: The surface of the select menu.
        :rtype: pygame.Surface
        """

        return self.__surface
    

    @surface.setter
    def surface(self, surface: pygame.Surface):
        """
        Setter for the surface property.

        :param surface: The surface to set the select menu to.
        :type surface: pygame.Surface
        """

        self.__surface = surface


    @property
    def selected_cell(self) -> Tuple[int, int]:
        """
        Getter for the selected cell property.

        :return: The selected cell.
        :rtype: Tuple[int, int]
        """

        return self.__selected_cell


    def __get_score(self) -> int:
        """
        Gets the score of the game session.

        :return: The score.
        :rtype: int
        """

        score = 0
        if not self.__board:
            return score
        for row in self.__board:
            for cell in row:
                if cell == GameSession.BOARD_PLAYER:
                    score += SCORE_SHIP_GAINED
                elif cell == GameSession.BOARD_LOST:
                    score += SCORE_LOST_SHIP
                elif cell == GameSession.BOARD_OPPONENT_LOST:
                    score += SCORE_HIT

        return score


    def __get_panel(self, width: int, height: int) -> pygame.Surface:
        """
        Gets a panel for the game session.

        :param width: The width of the panel.
        :type width: int
        :param height: The height of the panel.
        :type height: int
        :return: The panel.
        :rtype: pygame.Surface
        """

        panel = pygame.Surface((width, height))
        panel.fill(self.__background_color)
        panel_rect = panel.get_rect()
        panel_rect.topleft = (0, 0)

        return panel


    def __get_player_turn_panel(self, info_panel_width, info_panel_height, text_border_max_width, text_border_max_height) -> pygame.Surface:
        """
        Gets the player turn panel for the game session.

        :param info_panel_width: The width of the info panel.
        :type info_panel_width: int
        :param info_panel_height: The height of the info panel.
        :type info_panel_height: int
        :return: The player turn panel.
        :rtype: pygame.Surface
        """

        player_turn_panel = self.__get_panel(info_panel_width, info_panel_height)

        player_turn_panel_text = GameSession.TEXT_UNSET
        if self.__player_on_turn == self.__player_name:
            player_turn_panel_text = self.__assets['strings']['player_turn_panel_player']
        elif self.__player_on_turn == self.__opponent_name:
            player_turn_panel_text = self.__assets['strings']['player_turn_panel_opponent'] + f"\"{self.__opponent_name}\""

        player_turn_panel_text_surface = get_rendered_text_with_size(player_turn_panel_text, 
                                                                     text_border_max_width, 
                                                                     text_border_max_height,
                                                                     color=self.__text_color)
        
        text_top_left = (info_panel_width - player_turn_panel_text_surface.get_width()) // 2, \
                        (info_panel_height - player_turn_panel_text_surface.get_height()) // 2
        
        # draw the text
        player_turn_panel.blit(player_turn_panel_text_surface, text_top_left)

        return player_turn_panel
    

    def __get_status_panel(self, info_panel_width, info_panel_height, text_border_max_width, text_border_max_height) -> pygame.Surface:
        """
        Gets the status panel for the game session.

        :param info_panel_width: The width of the info panel.
        :type info_panel_width: int
        :param info_panel_height: The height of the info panel.
        :type info_panel_height: int
        :return: The status panel.
        :rtype: pygame.Surface
        """

        status_panel = self.__get_panel(info_panel_width, info_panel_height)

        status_panel_text = GameSession.TEXT_UNSET
        if self.__player_on_turn == self.__player_name:
            status_panel_text = self.__assets['strings']['status_panel_take_turn_msg']
        elif self.__player_on_turn == self.__opponent_name:
            status_panel_text = self.__assets['strings']['status_panel_waiting_for_opponent_turn_msg']

        status_panel_text_surface = get_rendered_text_with_size(status_panel_text, 
                                                                text_border_max_width, 
                                                                text_border_max_height,
                                                                color=self.__text_color)
        
        text_top_left = (info_panel_width - status_panel_text_surface.get_width()) // 2, \
                        (info_panel_height - status_panel_text_surface.get_height()) // 2
        
        # draw the text
        status_panel.blit(status_panel_text_surface, text_top_left)

        return status_panel
    

    def __get_last_action_panel(self, info_panel_width, info_panel_height, text_border_max_width, text_border_max_height) -> pygame.Surface:
        """
        Gets the last action panel for the game session.

        :param info_panel_width: The width of the info panel.
        :type info_panel_width: int
        :param info_panel_height: The height of the info panel.
        :type info_panel_height: int
        :return: The last action panel.
        :rtype: pygame.Surface
        """

        last_action_panel = self.__get_panel(info_panel_width, info_panel_height)

        last_action_panel_text = GameSession.TEXT_UNSET
        last_action_panel_text = self.__last_action

        last_action_panel_text_surface = get_rendered_text_with_size(last_action_panel_text, 
                                                                    text_border_max_width, 
                                                                    text_border_max_height,
                                                                    color=self.__text_color)
        
        text_top_left = (info_panel_width - last_action_panel_text_surface.get_width()) // 2, \
                        (info_panel_height - last_action_panel_text_surface.get_height()) // 2
        last_action_panel.blit(last_action_panel_text_surface, text_top_left)

        return last_action_panel
    

    def __get_score_panel(self, info_panel_width, info_panel_height, text_border_max_width, text_border_max_height) -> pygame.Surface:
        """
        Gets the score panel for the game session.

        :param info_panel_width: The width of the info panel.
        :type info_panel_width: int
        :param info_panel_height: The height of the info panel.
        :type info_panel_height: int
        :return: The score panel.
        :rtype: pygame.Surface
        """

        score_panel = self.__get_panel(info_panel_width, info_panel_height)

        score_panel_text = GameSession.TEXT_UNSET
        score = self.__get_score()
        score_panel_text = self.__assets['strings']['score_panel_title'] + str(score)

        score_panel_text_surface = get_rendered_text_with_size(score_panel_text, 
                                                               text_border_max_width, 
                                                               text_border_max_height,
                                                               color=self.__text_color)
        
        text_top_left = (info_panel_width - score_panel_text_surface.get_width()) // 2, \
                        (info_panel_height - score_panel_text_surface.get_height()) // 2
        score_panel.blit(score_panel_text_surface, text_top_left)

        return score_panel


    def __get_info_panels(self, 
                          info_panel_width, 
                          info_panel_height, 
                          text_border_max_width, 
                          text_border_max_height) -> Tuple[pygame.Surface, pygame.Surface, pygame.Surface, pygame.Surface]:
        """
        Gets the info panels for the game session.

        :param info_panel_width: The width of the info panel.
        :type info_panel_width: int
        :param info_panel_height: The height of the info panel.
        :type info_panel_height: int
        :return: The info panels.
        :rtype: Tuple[pygame.Surface, pygame.Surface, pygame.Surface, pygame.Surface]
        """

        # player turn panel
        player_turn_panel = self.__get_player_turn_panel(info_panel_width, info_panel_height, text_border_max_width, text_border_max_height)
        # status panel
        status_panel = self.__get_status_panel(info_panel_width, info_panel_height, text_border_max_width, text_border_max_height)
        # last action panel
        last_action_panel = self.__get_last_action_panel(info_panel_width, info_panel_height, text_border_max_width, text_border_max_height)
        # score panel
        score_panel = self.__get_score_panel(info_panel_width, info_panel_height, text_border_max_width, text_border_max_height)
        
        return player_turn_panel, status_panel, last_action_panel, score_panel
    

    def __get_board(self, surface_width: int, surface_height: int) -> pygame.Surface:
        """
        Gets the board for the game session.

        :param surface_width: The width of the surface.
        :type surface_width: int
        :param surface_height: The height of the surface.
        :type surface_height: int
        :return: The board.
        :rtype: pygame.Surface
        """

        self.__hit_check_cells = []
        left_panel_width = surface_width * GameSession.RATIO_INFO_PANEL_TO_SCREEN_WIDTH
        board_width = surface_width * GameSession.RATIO_BOARD_TO_SCREEN_WIDTH
        board_height = surface_height
        board_surface = pygame.Surface((board_width, board_height))
        board_surface.fill(self.__background_color)
        board_surface_rect = board_surface.get_rect()
        board_surface_rect.topleft = (0, 0)

        # draw the board
        if not self.__board:
            raise ValueError('The board data is not set.')

        row_cells_count = len(self.__board) + 1
        columns_cells_count = len(self.__board[0]) + 1

        cell_width = board_width / columns_cells_count
        cell_height = board_height / row_cells_count

        for row in range(row_cells_count):
            hit_check_row = []
            for col in range(columns_cells_count):
                # skip the first cell
                if col == 0 and row == 0:
                    continue

                # draw the row symbols
                elif col == 0:
                    row_symbol = GameSession.SYMBOLS_ROW[row - 1]
                    row_symbol_surface = get_rendered_text_with_size(row_symbol, 
                                                                     cell_width, 
                                                                     cell_height,
                                                                     color=self.__text_color)
                    row_symbol_rect = row_symbol_surface.get_rect()
                    row_symbol_rect.topleft = (0 + (cell_width - row_symbol_rect.width) // 2, row * cell_height + (cell_height - row_symbol_rect.height) // 2)
                    board_surface.blit(row_symbol_surface, row_symbol_rect)

                # draw the column symbols
                elif row == 0:
                    col_symbol = GameSession.SYMBOLS_COLUMN[col - 1]
                    col_symbol_surface = get_rendered_text_with_size(col_symbol, 
                                                                    cell_width, 
                                                                    cell_height,
                                                                    color=self.__text_color)
                    col_symbol_rect = col_symbol_surface.get_rect()
                    col_symbol_rect.topleft = (col * cell_width + ((cell_width - col_symbol_rect.width) // 2), (0 + (cell_height - col_symbol_rect.height) // 2))
                    board_surface.blit(col_symbol_surface, col_symbol_rect)

                # draw the cells
                else:
                    cell = self.__board[row - 1][col - 1]
                    cell_rect = pygame.Rect((col * cell_width, row * cell_height), (cell_width, cell_height))
                    cell_inner_rect = pygame.Rect(cell_rect.left + (cell_width * GameSession.RATIO_OUTLINE_TO_CELL) / 2, 
                                                  cell_rect.top + (cell_height * GameSession.RATIO_OUTLINE_TO_CELL) / 2, 
                                                  cell_rect.width - (cell_width * GameSession.RATIO_OUTLINE_TO_CELL),
                                                  cell_rect.height - (cell_height * GameSession.RATIO_OUTLINE_TO_CELL))
                    color = self.__assets['colors']['silver']
                    if cell == GameSession.BOARD_PLAYER:
                        color = self.__assets['colors']['green']
                    elif cell == GameSession.BOARD_LOST:
                        color = self.__assets['colors']['red']
                    elif cell == GameSession.BOARD_OPPONENT_LOST:
                        color = self.__assets['colors']['orange']
                    elif self.__highlighted_cell and self.__highlighted_cell == (row - 1, col - 1):
                        color = self.__assets['colors']['white']

                    pygame.draw.rect(board_surface, self.__assets['colors']['black'], cell_rect)
                    pygame.draw.rect(board_surface, color, cell_inner_rect)
                    hit_check_rect = pygame.Rect((left_panel_width + cell_rect.left, cell_rect.top), cell_rect.size)
                    hit_check_row.append(hit_check_rect)
            
            if row != 0:
                self.__hit_check_cells.append(hit_check_row)
        
        return board_surface


    def __draw_objects(self) -> List[pygame.Rect]:
        """
        Draws the objects in the game session.

        :return: The rectangles of the objects.
        :rtype: List[pygame.Rect]
        """

        if not self.__player_name or not self.__opponent_name or not self.__player_on_turn or not self.__board:
            raise ValueError(f"The player name ({self.__player_name}), opponent name ({self.__opponent_name}), player on turn ({self.__player_on_turn}), or board ({self.__board}) is not set.")

        update_areas = []
        surface_width, surface_height = self.__surface.get_size()
        info_panel_width = surface_width * self.RATIO_INFO_PANEL_TO_SCREEN_WIDTH
        info_panel_height = surface_height * self.RATIO_INFO_PANEL_TO_SCREEN_HEIGHT
        text_border_max_width = info_panel_width * self.RATIO_TEXT_WIDTH_TO_PANEL_WIDTH
        text_border_max_height = info_panel_height * self.RATIO_TEXT_HEIGHT_TO_PANEL_HEIGHT

        # draw the info panels
        panel_surfaces = self.__get_info_panels(info_panel_width, info_panel_height, text_border_max_width, text_border_max_height)
        player_turn_panel, status_panel, last_action_panel, score_panel = panel_surfaces

        # calculate the positions of the info panels
        player_turn_panel_x_y = 0, 0
        status_panel_x_y = player_turn_panel_x_y[0], player_turn_panel.get_height()
        last_action_panel_x_y = surface_width - last_action_panel.get_width(), 0
        score_panel_x_y = last_action_panel_x_y[0], last_action_panel.get_height()

        # draw the info panels
        self.__surface.blit(player_turn_panel, player_turn_panel_x_y)
        self.__surface.blit(status_panel, status_panel_x_y)
        self.__surface.blit(last_action_panel, last_action_panel_x_y)
        self.__surface.blit(score_panel, score_panel_x_y)

        player_turn_panel_rect = pygame.Rect(player_turn_panel_x_y, (info_panel_width, info_panel_height))
        status_panel_rect = pygame.Rect(status_panel_x_y, (info_panel_width, info_panel_height))
        last_action_panel_rect = pygame.Rect(last_action_panel_x_y, (info_panel_width, info_panel_height))
        score_panel_rect = pygame.Rect(score_panel_x_y, (info_panel_width, info_panel_height))
        update_areas.extend([player_turn_panel_rect, status_panel_rect, last_action_panel_rect, score_panel_rect])

        # draw the board
        board_surface = self.__get_board(surface_width, surface_height)
        board_surface_x_y = info_panel_width, 0
        self.__surface.blit(board_surface, board_surface_x_y)
        board_surface_rect = pygame.Rect(board_surface_x_y, board_surface.get_size())
        update_areas.append(board_surface_rect)

        return update_areas


    def draw(self) -> List[pygame.Rect]:
        """
        Draws the game session. Returns the 
        bounding rectangles of the objects drawn.

        :return: The select menu.
        :rtype: pygame.Surface
        """

        return self.__draw_objects()
        

    def redraw(self):
        """
        Redraws the game session. Expects that the entire screen is redrawn 
        with pygame.display.flip() after this method is called.
        """

        # update and draw the background
        surface_width, surface_height = self.__surface.get_size()
        self.__background = pygame.Rect(0, 0, surface_width, surface_height)
        pygame.draw.rect(self.__surface, self.__background_color, self.__background)

        # draw the objects
        self.__draw_objects()


    def update(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the game session.

        :param events: The events that occurred.
        :type events: Dict[str, Any]
        :return: Relevant information about the update.
        :rtype: Dict[str, Any]
        """

        result = {'graphics_update': False, 
                  'escape': False}
        
        if events.get('board', None):
            self.__board = events['board']
            result['graphics_update'] = True
        if events.get('player_on_turn', None):
            self.__player_on_turn = events['player_on_turn']
            result['graphics_update'] = True
        if events.get('player_name', None):
            self.__player_name = events['player_name']
            result['graphics_update'] = True
        if events.get('opponent_name', None):
            self.__opponent_name = events['opponent_name']
            result['graphics_update'] = True

        
        if events.get('escape', False):
            result['escape'] = True
            result['graphics_update'] = True
        elif events.get('new_char', None):
            c = events['new_char']
            if c == 'p':
                result['switch'] = True
            elif c == 's':
                result['random_board'] = True
            result['graphics_update'] = True
        elif events.get('mouse_motion', None):
            if self.__highlighted_cell:
                self.__highlighted_cell = None
                result['graphics_update'] = True
            for row in range(len(self.__hit_check_cells)):
                for col in range(len(self.__hit_check_cells[row])):
                    if self.__hit_check_cells[row][col].collidepoint(events['mouse_motion']):
                        self.__highlighted_cell = (row, col)
                        result['graphics_update'] = True
                        break

        return result