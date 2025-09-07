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
IMAGES_DIR_PATH: str = 'img'
SPRITES_DIR_PATH: str = os.path.join(IMAGES_DIR_PATH, 'sprites')

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
    def __load_images(path: str) -> Dict:
        """
        Loads images from the given path.

        :param path: The path to the images directory.
        :type path: str
        :return: The images as a dictionary.
        :rtype: Dict
        """

        res: Dict = {}
        for file in [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]:
            img_name = file.split('.')[0]
            logger.debug(f'Loading img: {file}')
            res[img_name] = pygame.image.load(os.path.join(path, file))
            logger.debug(f'Loaded img: {file}:{res[img_name]}')
        
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
        general_images_path = os.path.abspath(os.path.join(self.resources_dir_path, IMAGES_DIR_PATH))
        logger.debug(f'Loading assets from: {self.resources_dir_path}')
        logger.debug(f'Loading strings from: {strings_path}')
        assets['strings'] = __class__.__load_text_resources(strings_path)
        logger.debug(f'Strings loaded.')
        logger.debug(f'Loading colors from: {colors_path}')
        assets['colors'] = __class__.__load_colors(colors_path)
        logger.debug(f'Colors loaded.')
        logger.debug(f'Loading sprites from: {sprites_path}')
        assets['sprites'] = __class__.__load_images(sprites_path)
        logger.debug(f'Sprites loaded.')
        logger.debug(f'Loading general images from: {general_images_path}')
        assets['images'] = __class__.__load_images(general_images_path)
        logger.debug(f'General images loaded.')

        logger.info(f'Loaded assets from: {self.resources_dir_path}.')
        logger.debug(f'Loaded assets: \n{pformat(assets, indent=4)}')

        return assets