# TODO add doc

import argparse
from const import *
args_parser = argparse.ArgumentParser(description='Client application for the game "Inverse Battleships"')
args_parser.add_argument('-l', '--loggers_config', type=str, help='Path to the loggers configuration file')
args_parser.add_argument('-c', '--config', type=str, help='Path to the configuration file')
args_parser.add_argument('-n', '--name', type=str, help='Name of the main logger from the loggers configuration file')
args = args_parser.parse_args()

LOGGERS_CFG_PATH = args.loggers_config if args.loggers_config else LOGGERS_CONFIG_PATH
CFG_PATH = args.config if args.config else DEFAULT_CONFIG_PATH
LOGGER_NAME = args.name if args.name else MAIN_LOGGER_NAME

from utils import loggers
from time import sleep
loggers.set_path_to_config_file(LOGGERS_CFG_PATH)
while not loggers.is_ready():
    sleep(0.1)