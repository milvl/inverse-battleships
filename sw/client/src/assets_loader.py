from typing import Dict
from utils import load_json

STRINGS_FILE_PATH: str = 'strings.json'


class AssetsLoader:
    """
    Class that handles loading assets for the game.
    """


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

        return assets