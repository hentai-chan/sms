#!/usr/bin/env python3

import json
import logging
import os
import platform
import sys
from itertools import chain
from json.decoder import JSONDecodeError
from pathlib import Path
from types import FrameType
from typing import Dict, Union

from . import config
from .__init__ import package_name
from .config import BLUE, BRIGHT, CYAN, DIM, GREEN, MAGENTA, NORMAL, RED, RESET_ALL, YELLOW

#region logging and resource access

def get_config_dir() -> Path:
    """
    Return a platform-specific root directory for user configuration settings.
    """
    return {
        'Windows': Path(os.path.expandvars('%LOCALAPPDATA%')),
        'Darwin': Path.home().joinpath('Library').joinpath('Application Support'),
        'Linux': Path.home().joinpath('.config')
    }[platform.system()].joinpath(package_name)

def get_resource_path(filename: Union[str, Path]) -> Path:
    """
    Return a platform-specific log file path.
    """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    resource = config_dir.joinpath(filename)
    resource.touch(exist_ok=True)
    return resource

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(lineno)d::%(name)s::%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = logging.FileHandler(get_resource_path(config.LOGFILE))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def read_json_file(filename: Union[str, Path]) -> Dict:
    """
    Read `filename` and, if this file is empty, return an empty dictionary in its place.
    """
    with open(get_resource_path(filename), mode='r', encoding='utf-8') as file_handler:
        try:
            return json.load(file_handler)
        except JSONDecodeError:
            return dict()

def write_json_file(filename: Union[str, Path], params: dict) -> None:
    """
    Save the data in `params` as a JSON file by creating an union of pre-existing data (if any).
    """
    config = read_json_file(filename)
    with open(get_resource_path(filename), mode='w', encoding='utf-8') as file_handler:
        json.dump({**config, **params}, file_handler, indent=4)
        file_handler.write('\n')

def reset_file(filename: Union[str, Path]) -> None:
    open(get_resource_path(filename), mode='w', encoding='utf-8').close()

#endregion logging and resource access

#region development utilities

def add_col(value: str, color: str) -> str:
    return BRIGHT + color + str(value) + RESET_ALL

def det_col(value: str) -> str:
    return add_col(value, {
        'int': CYAN,
        'float': CYAN,
        'bool': MAGENTA,
        'str': GREEN,
        'bytes': YELLOW
    }.get(value.__class__.__name__, GREEN))

def print_dict(data: dict, level: int=0, start: bool=True, end: bool=False) -> None:
    """
    Print a pretty nested dictionary in color. This is some of the worst code I
    have ever written. There must be a better way to implement this.
    """
    indent = lambda i: '    ' * i
    last_item = lambda item: item == list(data.values())[-1]

    print(indent(level) + '{')

    start = False

    for key, value in data.items():
        print(indent(level + 1) + add_col(key, BLUE) + ': ', end='')

        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            print('[')
            for _ in value:
                print_dict(_, level + 2, start, end=(_ == value[-1]))
                start = True
            print(indent(level + 1) + ']' + ('' if last_item(value) else ','))
        elif isinstance(value, list) or isinstance(value, tuple):
            delim = "()" if isinstance(value, tuple) else "[]"
            if len(value):
                print(delim[0] + '\n' + indent(level + 2), end='')
                print(('\n' + indent(level + 2)).join([det_col(_) + ('' if _ == value[-1] else ',') for _ in value]), end='')
                print('\n' + indent(level + 1) + delim[1] + ('' if last_item(value) else ','))
            else:
                print(delim + '\n' + '}')
        else:
            print(det_col(value) + ('\n' + indent(level) + ('}' if start or end else '},') if last_item(value) else ','))

    if start and isinstance(list(data.values())[-1], list):
        print('}')

def print_on_success(message: str, verbose: bool=True) -> None:
    """
    Print a formatted success message if verbose is enabled.
    """
    if verbose:
        print(BRIGHT + GREEN + "[  OK  ]".ljust(12, ' ') + RESET_ALL + message)

def print_on_warning(message: str, verbose: bool=True) -> None:
    """
    Print a formatted warning message if verbose is enabled.
    """
    if verbose:
        print(BRIGHT + YELLOW + "[ WARNING ]".ljust(12, ' ') + RESET_ALL + message)

def print_on_error(message: str, verbose: bool=True) -> None:
    """
    Print a formatted error message if verbose is enabled.
    """
    if verbose:
        print(BRIGHT + RED + "[ ERROR ]".ljust(12, ' ') + RESET_ALL + message, file=sys.stderr)

def clear():
    """
    Reset terminal screen.
    """
    os.system('cls' if platform.system() == 'Windows' else 'clear')

#endregion development utilities
