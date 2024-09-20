import os
from typing import Dict
from const import MAIN_LOGGER_NAME
import loggers
from pprint import pformat
from utils import load_json, hex_to_tuple

STRINGS_FILE_PATH: str = 'strings.json'
COLORS_FILE_PATH: str = 'colors.json'

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
    def load_text_resources(path: str) -> Dict:
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
        strings_path = os.path.abspath(f'{self.resources_dir_path}/{STRINGS_FILE_PATH}')
        colors_path = os.path.abspath(f'{self.resources_dir_path}/{COLORS_FILE_PATH}')
        assets['strings'] = AssetsLoader.load_text_resources(strings_path)
        assets['colors'] = AssetsLoader.__load_colors(colors_path)

        logger.info(f'Loaded assets from: {self.resources_dir_path}.')
        logger.debug(f'Loaded assets: \n{pformat(assets, indent=4)}')

        return assets