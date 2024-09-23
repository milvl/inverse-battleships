import os

__CURR_DIR_PATH: str = os.path.split(os.path.abspath(__file__))[0]
RESOURCES_DIR_PATH: str = os.path.abspath(f'{__CURR_DIR_PATH}/../res')
DEFAULT_CONFIG_PATH: str = os.path.abspath(f'{__CURR_DIR_PATH}/../cfg/default_config.json')
LOGGERS_CONFIG_PATH: str = os.path.abspath(f'{__CURR_DIR_PATH}/../cfg/loggers_config.json')

# logger names
MAIN_LOGGER_NAME = 'main_logger'
CONNECTION_INFO_LOGGER_NAME = 'connection_info_logger'

# EXIT CODES
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_INVALID_CFG = 2
EXIT_INVALID_ASSETS_CFG = 3