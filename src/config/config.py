import threading
import time
from configparser import ConfigParser

# Config which polls for updates


def create_config(filename: str) -> ConfigParser:
    cfg_parser = ConfigParser()
    cfg_parser.read(filename)
    return cfg_parser
