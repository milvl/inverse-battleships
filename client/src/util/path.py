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

    client_dir_id = 'client'

    # get the current working directory
    cwd = os.getcwd()
    
    # if the current working directory is the client directory
    if os.path.basename(cwd) == client_dir_id:
        return cwd
    else:
        # # the project has been compiled using PyInstaller
        # if hasattr(sys, '_MEIPASS'):
        #     base_path = sys._MEIPASS  # temporary directory for the executable when using PyInstaller
        # # the project is being run as a script from any directory
        # else:
        #     base_path = os.path.relpath(os.path.join(__file__, '..', '..', '..'))
        
        # try to find the 'client' directory in the path
        path_parts = cwd.split(os.sep)
        if client_dir_id in path_parts:
            client_index = path_parts.index(client_dir_id)
            base_path = os.sep.join(path_parts[:client_index + 1])
        
        # else if the 'client' directory is in the current directory
        elif client_dir_id in os.listdir(cwd):
            base_path = os.path.join(cwd, client_dir_id)
        
        else:
            raise FileNotFoundError(f"The program has been started from an unexpected directory: {cwd}. Launch the program from the 'client' directory.")

        return base_path
    

def is_valid_filename(filename: str) -> bool:
    """
    Check if the filename is valid.

    :param filename: The filename to check.
    :type filename: str
    :return: True if the filename is valid, False otherwise.
    :rtype: bool
    """

    invalid_chars = r'\/:*?"<>|'

    if any(char in filename for char in invalid_chars):
        return False

    # check if the filename is empty
    if not filename.strip():
        return False

    return True