import pytest

from taxi_schemas import utils


@pytest.fixture(scope='session')
def mongodb_settings():
    return utils.MongoSchema()
