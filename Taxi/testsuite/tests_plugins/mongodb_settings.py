import pytest


@pytest.fixture(scope='session')
def mongo_schema_directory(get_source_path):
    return get_source_path('../schemas/schemas/mongo').resolve()


@pytest.fixture
def mongodb_collections():
    # Empty collections list by default.
    return ()
