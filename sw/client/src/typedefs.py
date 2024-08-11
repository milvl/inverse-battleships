from pydantic import BaseModel
from typing import Dict, Tuple


########## For externally defined data ##########
class PongGameConfig(BaseModel):
    """
    Class that represents the configuration of the game.
    """

    window_width: int
    window_height: int
    tick_speed: int
    players_count: int


class PongGameAssets(BaseModel):
    """
    Class that represents the assets of the game.
    """
    strings: Dict[str, str]
    colors: Dict[str, Tuple[int, int, int]]


########## For internally defined data ##########
class PongGameDebugInfo():
    """
    Class that represents the debug information of the game
    """

    def __init__(self, game_state: str = None, dimensions: Tuple = None, last_reg_key: str = None):
        self.game_state = game_state
        self.dimensions = dimensions
        self.last_reg_key = last_reg_key

    def __str__(self) -> str:
        """
        String representation of the class.

        :return: The string representation of the class.
        :rtype: str
        """

        return str(self.__dict__)
    
    def __repr__(self):
        """
        String representation of the class.

        :return: The string representation of the class.
        :rtype: str
        """

        return self.__str__()
    

class PyGameEvents():
    """
    Class that represents the PyGame events.
    """

    def __init__(self):
        """
        Constructor for the PyGameEvents class.
        """

        self.event_quit = None
        self.event_keydown = None
        self.event_keyup = None
        self.event_mousemotion = None
        self.event_mousebuttondown = None
        self.event_mousebuttonup = None
        self.event_videoresize = None


class PongGameUpdateResult():
    """
    Class that represents the result of the game update.
    """

    def __init__(self, exit: bool = None, update: bool = None):
        self.exit = exit
        self.update = update