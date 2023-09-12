from schema import Schema
import logging
from configparser import ConfigParser

logger = logging.getLogger(__name__)


class Config:
    _filename: str
    _schema: Schema
    _config: dict

    def __init__(self, filename: str, schema: Schema):
        self._filename = filename
        self._schema = schema
        self.load()

    def load(self):
        parser = ConfigParser()
        parser.read(self._filename)
        config_dict = {
            section: dict(parser.items(section)) for section in parser.sections()
        }
        self._config = self._schema.validate(config_dict)
        logger.debug(f"Loaded config file: {self._filename}")
        return self._config

    def __getitem__(self, key):
        return self._config[key]


def load_config(filename: str) -> ConfigParser:
    cfg_parser = ConfigParser()
    cfg_parser.read(filename)
    return cfg_parser
