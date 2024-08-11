from typing import Dict
import os
from utils import load_json
from typedefs import PongGameConfig, PongGameAssets, PongGameUpdateResult
import pygame
from assets_loader import AssetsLoader
from game import PongGame

CURR_DIR_PATH: str = os.path.split(os.path.abspath(__file__))[0]
RESOURCES_DIR_PATH: str = f'{CURR_DIR_PATH}/../res'
DEFAULT_CONFIG_PATH: str = f'{CURR_DIR_PATH}/../cfg/default_config.json'


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
    # TODO DOC

    # load the configuration file
    config: dict = load_config(DEFAULT_CONFIG_PATH)
    try:
        PongGameConfig(**config)
    except Exception as e:
        print(f'Config data has incorrect format: {e}')
        return

    # load the assets
    assets_loader: AssetsLoader = AssetsLoader(RESOURCES_DIR_PATH)
    assets: dict = assets_loader.load()
    try:
        PongGameAssets(**assets)
    except Exception as e:
        print(f'Assets data has incorrect format: {e}')
        return
    import pprint; pprint.pprint(assets)

    clock = pygame.time.Clock()
    tick_speed = config['tick_speed']
    game = PongGame(config, assets, display_debug_info=True)

    game.start()
    pygame.display.update()
    while True:
        update_result: PongGameUpdateResult = game.update()
        if update_result.exit:
            break

        if update_result.update:
            pygame.display.update()
        clock.tick(tick_speed)


if __name__ == '__main__':
    main()
