"""
Module with paths to resources and configuration files.
"""

import os
from util.path import get_project_root

PROJECT_ROOT_PATH: str = get_project_root()
RESOURCES_DIR_PATH: str = os.path.relpath(os.path.join(PROJECT_ROOT_PATH, 'res'))
DEFAULT_CONFIG_PATH: str = os.path.relpath(os.path.join(PROJECT_ROOT_PATH, 'cfg', 'default_config.json'))
LOGGERS_CONFIG_PATH: str = os.path.relpath(os.path.join(PROJECT_ROOT_PATH, 'cfg', 'loggers_config.json'))
DEFAULT_USER_CONFIG_PATH: str = os.path.relpath(os.path.join(PROJECT_ROOT_PATH, 'cfg', 'default_user_config.json'))
USER_CONFIG_DIR_PATH: str = os.path.relpath(os.path.join(PROJECT_ROOT_PATH, 'cfg', 'user'))