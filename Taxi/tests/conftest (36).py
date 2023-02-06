import pytest


@pytest.fixture(scope='session')
def settings():
    class Settings:
        INITIAL_DATA_PATH = []

    settings = Settings()
    return settings
