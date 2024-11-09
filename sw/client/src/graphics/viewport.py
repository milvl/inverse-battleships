from abc import ABC, abstractmethod
from typing import Any, Dict
import pygame


class Viewport(ABC):
    """
    The Viewport class.
    """


    @abstractmethod
    def __init__(self, surface: pygame.display):
        """
        Constructor for the Viewport class.

        :param surface: The surface to render the viewport to.
        :type surface: pygame.display
        """

        raise NotImplementedError("Must be overridden by subclass.")
    

    @abstractmethod
    def draw(self) -> pygame.rect.Rect:
        """
        Draws the viewport.

        :return: The rectangle of the updated area.
        :rtype: pygame.rect.Rect
        """

        raise NotImplementedError("Must be overridden by subclass.")
    

    @abstractmethod
    def redraw(self):
        """
        Redraws the viewport.
        """

        raise NotImplementedError("Must be overridden by subclass.")


    @abstractmethod
    def update(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the viewport state.

        :param events: The events to update the viewport with.
        :type events: Dict[str, Any]
        :return: The relevant updates.
        :rtype: Dict[str, Any]
        """

        raise NotImplementedError("Must be overridden by subclass.")