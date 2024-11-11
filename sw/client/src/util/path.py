"""
Module with path utilities.
"""

import os
import sys


def get_project_root() -> str:
    """
    Gets the current working directory is the project root.

    :return: The project root path.
    :rtype: str
    """

    # get the current working directory
    cwd = os.getcwd()
    
    # if the current working directory is the client directory
    if os.path.basename(cwd) == 'client':
        return cwd
    else:
        # the project has been compiled using PyInstaller
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS  # temporary directory for the executable when using PyInstaller
        # the project is being run as a script from any directory
        else:
            base_path = os.path.relpath(os.path.join(__file__, '..', '..', '..'))

        return base_path