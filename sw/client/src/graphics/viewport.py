from abc import ABC, abstractmethod
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
    def draw(self):
        """
        Draws the viewport.
        """

        raise NotImplementedError("Must be overridden by subclass.")
    

    @abstractmethod
    def redraw(self):
        """
        Redraws the viewport.
        """

        raise NotImplementedError("Must be overridden by subclass.")


    @abstractmethod
    def update(self, events: pygame.event):
        """
        Updates the viewport state.

        :param events: The events to update the viewport with.
        :type events: pygame.event
        """

        raise NotImplementedError("Must be overridden by subclass.")