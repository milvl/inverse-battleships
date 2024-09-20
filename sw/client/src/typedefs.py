from pydantic import BaseModel, ConfigDict
from typing import Dict, Tuple, List, Union, Optional
from dataclasses import dataclass, field
import pygame


########## For externally defined data ##########
class IBGameConfig(BaseModel):
    """
    Class that represents the configuration of the game.
    """

    model_config: ConfigDict = {'extra': 'forbid'}

    window_width: int
    window_height: int
    tick_speed: int
    players_count: int
    skip_intro: bool
    min_window_width: int
    min_window_height: int
    debug_mode: bool


class IBAssets(BaseModel):
    """
    Class that represents the assets of the game.
    """
    strings: Dict[str, str]
    colors: Dict[str, Tuple[int, int, int]]


########## For internally defined data ##########

@dataclass
class IBGameDebugInfo():
    """
    Class that represents the debug information of the game.

    :param game_state: The game state.
    :type game_state: str, defaults to None
    :param dimensions: The dimensions.
    :type dimensions: Tuple[int, int], defaults to None
    :param last_reg_key: The last registered key.
    :type last_reg_key: Optional[str], defaults to None
    """

    game_state: str = None
    dimensions: Tuple[int, int] = None
    last_reg_key: Optional[str] = None

    def __str__(self) -> str:
        """
        String representation of the class.

        :return: The string representation of the class.
        :rtype: str
        """

        return str(self.__dict__)


@dataclass
class PyGameEvents():
    """
    Class that represents the PyGame events.

    :param event_quit: The quit event.
    :type event_quit: Optional[pygame.event.Event]
    :param event_keydown: The keydown event.
    :type event_keydown: Optional[pygame.event.Event]
    :param event_keyup: The keyup event.
    :type event_keyup: Optional[pygame.event.Event]
    :param event_mousemotion: The mousemotion event.
    :type event_mousemotion: Optional[pygame.event.Event]
    :param event_mousebuttondown: The mousebuttondown event.
    :type event_mousebuttondown: Optional[pygame.event.Event]
    :param event_mousebuttonup: The mousebuttonup event.
    :type event_mousebuttonup: Optional[pygame.event.Event]
    :param event_videoresize: The videoresize event.
    :type event_videoresize: Optional[pygame.event.Event]
    """

    event_quit: Optional[pygame.event.Event] = None
    event_keydown: Optional[pygame.event.Event] = None
    event_keyup: Optional[pygame.event.Event] = None
    event_mousemotion: Optional[pygame.event.Event] = None
    event_mousebuttondown: Optional[pygame.event.Event] = None
    event_mousebuttonup: Optional[pygame.event.Event] = None
    event_videoresize: Optional[pygame.event.Event] = None


@dataclass
class IBGameUpdateResult():
    """
    Class that represents the result of the game update.

    :param exit: Whether to exit the game.
    :type exit: bool, defaults to False
    :param update_areas: The areas to update.
    :type update_areas: Optional[List[pygame.Surface]]
    """

    exit: bool = False
    update_areas: List[pygame.Surface] = field(default_factory=lambda: [])