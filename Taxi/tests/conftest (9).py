import os

import pytest

pytest_plugins = ['taxi.pytest_plugins.asyncio_connection']


@pytest.fixture(autouse=True)
def enable_databases(mongodb):
    pass


@pytest.fixture
def mongodb_collections():
    """Disable all collections by default."""
    return []


@pytest.fixture(scope='session')
def mongo_schema_extra_directories():
    return (os.path.join(os.path.dirname(__file__), 'schemas', 'mongo'),)
