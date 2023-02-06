import pytest


@pytest.fixture(name='clown_namespaces')
def _clown_namespaces():
    return [{'id': 1, 'name': 'taxi'}, {'id': 2, 'name': 'market'}]


@pytest.fixture(autouse=True)
def _clown_cache_mocks_autouse(clown_cache_mocks):
    return clown_cache_mocks
