import pytest

import pymlaas.protocol.app
import pymlaas.settings

pytest_plugins = [
    'taxi_tests.plugins.common',
    'taxi_tests.plugins.mockserver'
]


@pytest.fixture(scope='session')
def settings():
    class Settings:
        MOCKSERVER_OPTS = {
            'hostname': pymlaas.settings.MOCKSERVER_HOST,
            'port': pymlaas.settings.MOCKSERVER_PORT
        }
        INITIAL_DATA_PATH = []
    settings = Settings()
    return settings


@pytest.fixture(scope='session')
def taxi_pyml():
    pyml_app = pymlaas.protocol.app.app
    pyml_app.config['TESTING'] = True
    return pyml_app.test_client()
