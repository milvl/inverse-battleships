from typing import Any, Dict, List
import pygame
from pygame.rect import Rect
from const.typedefs import IBAssets
from graphics.menus.input_menu import InputMenu
from graphics.menus.primitives import MenuTitle
from graphics.viewport import Viewport


class SettingsMenu(InputMenu):      # Only one setting is needed for this game. For expanded functionality, this class should be reworked from scratch.
    # TODO DOC

    def __init__(self, viewport: Viewport, assets: IBAssets, label_text: str):
        # TODO DOC
        super().__init__(viewport, assets, label_text)
    

    # def redraw(self):
    #     # TODO DOC
    #     super().redraw()
    
    # def draw(self) -> Rect:
    #     # TODO DOC
    #     return super().draw()
    
    # def update(self, events: Dict[str, Any]) -> Dict[str, Any]:
    #     # TODO DOC
    #     return super().update(events)