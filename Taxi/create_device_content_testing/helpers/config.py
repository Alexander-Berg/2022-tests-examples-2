# pylint: skip-file
# flake8: noqa
import json
import pathlib


def _config_dir():
    return pathlib.Path(__file__).parent.parent / 'config'


def _names_dir():
    return pathlib.Path(__file__).parent.parent / 'helpers/names'


def _keys_dir():
    return pathlib.Path(__file__).parent.parent / 'helpers/keys'


def read_dynamic_config():
    config_path = _config_dir() / 'dynamic.json'
    with open(config_path) as dynamic_config:
        return json.loads(dynamic_config.read())


def read_secret_config():
    secret_config_path = _config_dir() / 'secret.json'
    with open(secret_config_path) as static_config:
        return json.loads(static_config.read())


def read_static_config():
    static_config_path = _config_dir() / 'static.json'
    with open(static_config_path) as static_config:
        return json.loads(static_config.read())


def read_names_surnames():
    names_path = _names_dir() / 'names.txt'
    surnames_path = _names_dir() / 'surnames.txt'
    with open(names_path) as names_file:
        names = names_file.read()
    with open(surnames_path) as surnames_file:
        surnames = surnames_file.read()
    return names, surnames


def read_private_key():
    private_key_path = _keys_dir() / 'private_key.pem'
    with open(private_key_path, 'rb') as private_key_file:
        return private_key_file.read()


def read_public_key():
    public_key_path = _keys_dir() / 'public_key.pem'
    with open(public_key_path, 'rb') as public_key_file:
        return public_key_file.read()
