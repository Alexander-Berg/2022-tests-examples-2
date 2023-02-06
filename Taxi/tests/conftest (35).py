import pathlib
import pytest
import sys


ROOT_PATH = pathlib.Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_PATH))


@pytest.fixture(scope='session')
def settings():
    class Settings:
        INITIAL_DATA_PATH = []

    settings = Settings()
    return settings
