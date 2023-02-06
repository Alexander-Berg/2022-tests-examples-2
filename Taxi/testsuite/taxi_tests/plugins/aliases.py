import pytest


# Backward compatibility fixtures
@pytest.fixture
def db(mongodb):
    return mongodb


@pytest.fixture
def load_fixture(mongodb_init):
    pass


@pytest.fixture
def config(taxi_config):
    return taxi_config
