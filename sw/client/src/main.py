from typing import Dict
import os
from utils import load_json
from assets_loader import AssetsLoader
import pygame

CURR_FILE_PATH: str = __file__
RESOURCES_DIR_PATH: str = f'{os.path.split(CURR_FILE_PATH)[0]}/../res'
DEFAULT_CONFIG_PATH: str = f'{RESOURCES_DIR_PATH}/cfg/default_config.json'

print(f'CURR_FILE_PATH: {CURR_FILE_PATH}')
print(f'DEFAULT_CONFIG_PATH: {DEFAULT_CONFIG_PATH}')


def load_config(path: str) -> Dict:
    """
    Loads the configuration file from the given path.

    :param path: The path to the configuration file.
    :type path: str
    :return: The configuration file as a dictionary.
    :rtype: Dict
    """

    return load_json(path)

def main():
    # load the configuration file
    config: dict = load_config(DEFAULT_CONFIG_PATH)

    # load the assets
    assets_loader: AssetsLoader = AssetsLoader(RESOURCES_DIR_PATH)
    assets: dict = assets_loader.load()
    
    window: pygame.display = pygame.display.set_mode((config['window_width'], config['window_height']))
    pygame.display.set_caption(assets.strings.window_title)
    input('Press Enter to exit...')


if __name__ == '__main__':
    main()
