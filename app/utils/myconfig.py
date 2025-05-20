import yaml
import os
import sys
from utils.mylogging import setup_logging

logger = setup_logging()


class ConfigLoader:
    def __init__(self):
        self.init_config()

    def init_config():
        global config_path
        config_path = "config/broker.yaml"
        dirs = ["data/logs", "data/data", "data/config"]
        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)
        if not os.path.exists(config_path):
            logger.info("no config file found")
            sys.exit(0)

    @classmethod
    def load_config(cls):
        ConfigLoader.init_config()
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        return config

    @classmethod
    def save_config(cls, config):
        with open(config_path, "w") as f:
            yaml.dump(config, f)
