import logging.config
import yaml
import os

CONFIG_PATH = "config"
CONFIG_FILE = "logging.yaml"


def setup_logging(config_file=os.path.join(CONFIG_PATH, CONFIG_FILE)):
    with open(config_file, "r") as f:
        config = yaml.safe_load(f.read())

    logging.config.dictConfig(config)

    return logging.getLogger()
