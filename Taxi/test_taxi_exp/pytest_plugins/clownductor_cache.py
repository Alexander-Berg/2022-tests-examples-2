import pytest


@pytest.fixture(name='clown_namespaces')
def _clown_namespaces():
    return [
        {'id': 1, 'name': 'taxi'},
        {'id': 2, 'name': 'market'},
        {'id': 3, 'name': 'not_market'},
        {'id': 4, 'name': 'frozen'},
        {'id': 5, 'name': 'brand_new'},
    ]


@pytest.fixture(name='clown_projects')
def _clown_projects():
    return [
        {'id': 1, 'name': 'project', 'namespace_id': 2},
        {'id': 2, 'name': 'other_project', 'namespace_id': 3},
    ]


@pytest.fixture(name='clown_services')
def _clown_services():
    return [
        {'cluster_type': '', 'id': 123456, 'name': 'service', 'project_id': 1},
        {
            'cluster_type': '',
            'id': 12345,
            'name': 'other_service',
            'project_id': 2,
        },
        {
            'cluster_type': '',
            'id': 1,
            'name': 'service_to_test_search_1',
            'project_id': 1,
        },
        {
            'cluster_type': '',
            'id': 2,
            'name': 'service_to_test_search_2',
            'project_id': 1,
        },
        {
            'cluster_type': '',
            'id': 10,
            'name': 'service_to_test_search_10',
            'project_id': 1,
        },
        {'cluster_type': '', 'id': 123, 'name': 'service', 'project_id': 2},
    ]


@pytest.fixture(autouse=True)
def _clown_cache_mocks_autouse(clown_cache_mocks):
    return clown_cache_mocks
