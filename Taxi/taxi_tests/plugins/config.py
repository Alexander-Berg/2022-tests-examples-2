import pytest


class BaseError(Exception):
    """Base class for exceptions of this module"""


class ConfigNotFoundError(BaseError):
    """Config parameter was not found and no default was provided"""


class TaxiConfig:
    """Simple config backend."""

    def __init__(self):
        self._values = {}

    def set_values(self, values):
        self._values.update(values)

    def get_values(self):
        return self._values.copy()

    def set(self, **values):
        self.set_values(values)

    def get(self, key, default=None):
        if key not in self._values:
            if default is not None:
                return default
            raise ConfigNotFoundError(
                'param "%s" is not found in config' % (key,))
        return self._values[key]


@pytest.fixture
def taxi_config(request, search_path, load_json, config_service_defaults):
    config = TaxiConfig()
    all_values = config_service_defaults.copy()
    for path in reversed(list(search_path('config.json'))):
        values = load_json(path)
        all_values.update(values)
    marker = request.node.get_marker('config')
    if marker:
        all_values.update(marker.kwargs)
    config.set_values(all_values)
    return config


@pytest.fixture(scope='session')
def config_service_defaults():
    """
    Fixture that returns default values for config. You have to override
    it in your local conftest.py or fixture:

    @pytest.fixture(scope='session')
    def config_service_defaults():
        with open('defaults.json') as fp:
            return json.load(fp)
    """
    raise RuntimeError(
        'In order to use fixture %s you have to override %s fixture' % (
            'mock_configs_service',
            config_service_defaults.__name__,
        ),
    )
