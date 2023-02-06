import os
import pytest
import typing


@pytest.fixture(scope='session')
def settings():
    class Settings:
        INITIAL_DATA_PATH = []

    settings = Settings()
    return settings


@pytest.fixture(scope='function')
def get_pytest_signalq_config():
    def wrapped(
            cv: typing.Optional[str] = None,
            mode: typing.Optional[str] = None,
            config: typing.Optional[typing.Dict[str, typing.Any]] = None,
    ):
        import os
        from signalq_pyml import get_config

        if config is None:
            config = get_config(cv, mode)

        exist_checks = [
            os.path.exists(config['Drowsiness']['model_path']),
            os.path.exists(config['Drowsiness']['meta_path']),
            os.path.exists(config['Acceleration']['model_path']),
            os.path.exists(config['LocalTime']['timezone_array_path']),
        ]

        if not all(exist_checks):
            config.pop('Drowsiness')
            config.pop('LocalTime')
            config.pop('Acceleration')

        return config

    return wrapped


@pytest.fixture(scope='session')
def load_url():
    def wrapped(url: str, file: str):
        import requests
        with open(file, 'wb') as file:
            # get request
            response = requests.get(url)
            # write to file
            file.write(response.content)

    return wrapped


@pytest.fixture(scope='session')
def model_dir():
    current = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current, '..', 'models')


@pytest.fixture(scope='session')
def load_models(model_dir, load_url):
    url_file = os.path.join(model_dir, 'urls')
    with open(url_file, 'r') as uf:
        for line in uf.readlines():
            path, url = line.split(' ', 2)
            full_path = os.path.join(model_dir, path)
            os.makedirs(os.path.split(full_path)[0], exist_ok=True)
            load_url(url, full_path)
