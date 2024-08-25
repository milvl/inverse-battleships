from abc import ABC, abstractmethod
import pygame


class Viewport:
    """
    The Viewport class.
    """


    @abstractmethod
    def __init__(self, window: pygame.display):
        """
        Constructor for the Viewport class.

        :param window: The window to render the viewport to.
        :type window: pygame.display
        """

        pass


    @abstractmethod
    def render(self):
        """
        Renders the viewport.
        """

        pass


    @abstractmethod
    def update(self, events: pygame.event):
        """
        Updates the viewport.

        :param events: The events to update the viewport with.
        :type events: pygame.event
        """

        pass