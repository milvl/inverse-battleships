# python .\client\src\main.py -c .\client\cfg\debug_cfg.json -l .\client\cfg\debug_loggers_cfg.json

import os
from init_setup import loggers, CFG_PATH, RESOURCES_DIR_PATH, EXIT_SUCCESS, EXIT_FAILURE, EXIT_INVALID_CFG, EXIT_INVALID_ASSETS_CFG, LOGGER_NAME
from typing import Dict
from pprint import pformat
from utils import load_json
from typedefs import IBGameConfig, IBAssets, IBGameUpdateResult
from pydantic import ValidationError
import pygame
from assets_loader import AssetsLoader
from game import IBGame

# logger = loggers.NullLogger()
# temp_logger = loggers.NullLogger()

def load_config(path: str) -> Dict:
    """
    Loads the configuration file from the given path.

    :param path: The path to the configuration file.
    :type path: str
    :return: The configuration file as a dictionary.
    :rtype: Dict
    """

    logger.debug(f'Loading configuration file from: {path}')
    loaded_data = load_json(path)
    logger.info(f'Loaded configuration file: {path}')
    logger.debug(f'Loaded configurations: \n{pformat(loaded_data, indent=4)}')
    return loaded_data


def main():
    # TODO DOC

    logger.info('Starting the client application...')

    # windows high dpi fix
    if os.name == 'nt':
        logger.info('Windows system detected')
        logger.info('Applying high DPI fix')
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
        logger.info('Successfully applied high DPI fix')
    elif os.name == 'posix':
        logger.info('Posix system detected')
    else:
        logger.critical('Unknown operating system detected, exiting...')
        exit(EXIT_FAILURE)

    # load the configuration file
    config: dict = load_config(CFG_PATH)
    try:
        logger.debug('Validating the default configuration data...')
        IBGameConfig.model_validate(config, strict=True)
        logger.info('Default configuration data is valid.')
    except ValidationError as e:
        print(f'Default config data has incorrect format: {e}')
        logger.critical(f'Config data has incorrect format: {e}')
        exit(EXIT_INVALID_CFG)

    # load the assets
    assets_loader: AssetsLoader = AssetsLoader(RESOURCES_DIR_PATH)
    assets: dict = assets_loader.load()
    try:
        logger.debug('Validating the assets data...')
        IBAssets.model_validate(assets, strict=True)
        logger.info('Assets data is valid')
    except ValidationError as e:
        print(f'Assets data has incorrect format: {e}')
        logger.critical(f'Assets data has incorrect format: {e}')
        exit(EXIT_INVALID_ASSETS_CFG)

    clock = pygame.time.Clock()
    tick_speed = config['tick_speed']

    logger.debug('Creating the game...')
    game = IBGame(config, assets)
    logger.info('Game instance created')

    window: pygame.display = pygame.display.set_mode((config['window_width'], config['window_height']), pygame.RESIZABLE, config['color_bit_depth'])
    logger.info('Window created')

    game.start(window)
    logger.info('Game started')
    pygame.display.flip()

    # MAIN LOOP
    while True:
        update_result: IBGameUpdateResult = game.update()
        if update_result.exit:
            break

        if update_result.update_areas:
            # complex update -> updates the entire screen
            if update_result.update_areas[0] == True:
                logger.debug('Complex update detected, updating the entire screen')
                pygame.display.flip()

            # updates only portions of the screen
            else:
                logger.debug(f'Partial update detected, updating areas: \n{pformat(update_result.update_areas, indent=4)}')
                pygame.display.update(update_result.update_areas)

        # add a delay to the game loop
        clock.tick(tick_speed)

    # end the game correctly
    if pygame.font.get_init():
        pygame.font.quit()
    if pygame.get_init():
        pygame.quit()

    logger.info('Program terminated')
    exit(EXIT_SUCCESS)


if __name__ == '__main__':
    logger = loggers.get_logger(LOGGER_NAME)
    temp_logger = loggers.get_temp_logger('temp')
    
    main()
