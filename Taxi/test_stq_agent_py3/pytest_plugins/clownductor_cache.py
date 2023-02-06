import pytest


@pytest.fixture(name='clown_namespaces')
def _clown_namespaces(relative_load_json):
    return [{'id': 1, 'name': 'taxi'}, {'id': 2, 'name': 'market'}]


@pytest.fixture(name='clown_projects')
def _clown_projects(relative_load_json):
    return relative_load_json('projects.json')


@pytest.fixture(autouse=True)
def _clown_cache_mocks_autouse(clown_cache_mocks):
    return clown_cache_mocks
