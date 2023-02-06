import configparser


def load_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    if not config.has_section('default'):
        raise Exception('No [default] section in config.')
    return config
