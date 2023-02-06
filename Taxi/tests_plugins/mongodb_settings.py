import os

import pytest

from taxi_tests.utils import mongo_schema


@pytest.fixture(scope='session')
def mongodb_settings():
    path = os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        os.path.pardir,
        'schemas',
        'mongo',
    )
    return mongo_schema.MongoSchema(path)
