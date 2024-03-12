import logging.config
import os

import yaml

CONFIG_PATH = "config"
CONFIG_FILE = "logging.yaml"


def setup_logging(config_file=os.path.join(CONFIG_PATH, CONFIG_FILE)):
    with open(config_file, "r") as f:
        config = yaml.safe_load(f.read())
    log_dir = os.path.dirname(config["handlers"]["file"]["filename"])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.config.dictConfig(config)

    return logging.getLogger()
