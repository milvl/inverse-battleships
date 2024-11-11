"""
Module that handles loading assets for the game (based on Pygame).
"""

import os
from typing import Dict

import pygame
from const.loggers import MAIN_LOGGER_NAME
from util import loggers
from pprint import pformat
from util.file import load_json
from util.etc import hex_to_tuple

STRINGS_FILE_PATH: str = 'strings.json'
COLORS_FILE_PATH: str = 'colors.json'
SPRITES_DIR_PATH: str = os.path.join('img', 'sprites')

logger = loggers.get_logger(MAIN_LOGGER_NAME)


class AssetsLoader:
    """
    Class that handles loading assets for the game.
    """

    @staticmethod
    def __load_colors(path: str) -> Dict:
        """
        Loads the colors from the given path.

        :param path: The path to the colors file.
        :type path: str
        :return: The colors as a dictionary.
        :rtype: Dict
        """

        logger.debug(f'Loading colors from: {path}')
        res: Dict = load_json(path)
        for key, value in res.items():
            res[key] = hex_to_tuple(value)


        logger.info(f'Loaded colors from: {path}.')
        
        return res
    

    @staticmethod
    def __load_text_resources(path: str) -> Dict:
        """
        Loads the text resources from the given path.

        :param path: The path to the text resources file.
        :type path: str
        :return: The text resources as a dictionary.
        :rtype: Dict
        """

        logger.debug(f'Loading text resources from: {path}')
        res: Dict = load_json(path)
        logger.info(f'Loaded text resources from: {path}.')
        
        return res
    

    @staticmethod
    def __load_sprites(path: str) -> Dict:
        """
        Loads the sprites from the given path.

        :param path: The path to the sprites directory.
        :type path: str
        :return: The sprites as a dictionary.
        :rtype: Dict
        """

        logger.debug(f'Loading sprites from: {path}')
        res: Dict = {}
        for root, _, files in os.walk(path):
            for file in files:
                sprite_name = file.split('.')[0]
                res[sprite_name] = pygame.image.load(os.path.join(root, file))
                logger.debug(f'Loaded sprite: {res[sprite_name]}')

        logger.info(f'Loaded sprites from: {path}.')
        
        return res


    def __init__(self, resources_dir_path: str) -> None:
        """
        Constructor for the AssetsLoader class.

        :param resources_dir_path: The path to the resources directory.
        :type resources_dir_path: str
        """

        self.assets = {}
        self.resources_dir_path = resources_dir_path
    

    def load(self) -> Dict:
        """
        Loads all assets from the resources directory.

        :return: The assets as a dictionary.
        :rtype: Dict
        """

        assets = {}
        strings_path = os.path.abspath(os.path.join(self.resources_dir_path, STRINGS_FILE_PATH))
        colors_path = os.path.abspath(os.path.join(self.resources_dir_path, COLORS_FILE_PATH))
        sprites_path = os.path.abspath(os.path.join(self.resources_dir_path, SPRITES_DIR_PATH))
        assets['strings'] = __class__.__load_text_resources(strings_path)
        assets['colors'] = __class__.__load_colors(colors_path)
        assets['sprites'] = __class__.__load_sprites(sprites_path)

        logger.info(f'Loaded assets from: {self.resources_dir_path}.')
        logger.debug(f'Loaded assets: \n{pformat(assets, indent=4)}')

        return assets