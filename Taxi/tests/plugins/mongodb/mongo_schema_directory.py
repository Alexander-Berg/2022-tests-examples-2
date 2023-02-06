import os

import pytest


@pytest.fixture(scope='session')
def mongo_schema_directory():
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            os.path.pardir,
            'schemas',
            'mongo',
        ),
    )
