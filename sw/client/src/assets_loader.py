from typing import Dict
from utils import load_json, hex_to_tuple

STRINGS_FILE_PATH: str = 'strings.json'
COLORS_FILE_PATH: str = 'colors.json'


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

        res: Dict = load_json(path)
        for key, value in res.items():
            res[key] = hex_to_tuple(value)
        
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
        assets['strings'] = load_json(f'{self.resources_dir_path}/{STRINGS_FILE_PATH}')
        assets['colors'] = AssetsLoader.__load_colors(f'{self.resources_dir_path}/{COLORS_FILE_PATH}')

        return assets