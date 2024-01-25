import yaml


class ConfigLoader:
    global config_path
    config_path = "config/broker.yaml"

    @classmethod
    def load_config(cls):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        return config

    @classmethod
    def save_config(cls, config):
        with open(config_path, "w") as f:
            yaml.dump(config, f)
