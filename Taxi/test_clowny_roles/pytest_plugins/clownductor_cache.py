import pytest


@pytest.fixture(name='clown_namespaces')
def _clown_namespaces():
    return [{'id': 1, 'name': 'taxi'}, {'id': 2, 'name': 'market'}]


@pytest.fixture(name='clown_projects')
def _clown_projects():
    return [
        {
            'id': 1,
            'name': 'prj-1',
            'namespace_id': 1,
            'owners': {
                'groups': ['grp-1'],
                'logins': ['admin-1', 'admin-2', 'admin-3'],
            },
        },
        {
            'id': 2,
            'name': 'prj-2',
            'namespace_id': 1,
            'owners': {
                'groups': ['grp-2'],
                'logins': ['admin-4', 'admin-5', 'admin-6'],
            },
        },
        {
            'id': 3,
            'name': 'prj-3',
            'namespace_id': 1,
            'owners': {'groups': ['grp-3'], 'logins': ['admin-7', 'admin-8']},
        },
        {
            'id': 4,
            'name': 'prj-4',
            'namespace_id': 2,
            'owners': {'groups': ['grp-3'], 'logins': ['admin-7', 'admin-8']},
        },
    ]


@pytest.fixture(name='clown_services')
def _clown_services():
    return [
        {
            'id': 1,
            'name': 'srv-1',
            'project_id': 1,
            'cluster_type': 'nanny',
            'abc_service': 'srv-1-slug',
            'requester': 'login-1',
        },
        {
            'id': 2,
            'name': 'srv-2',
            'project_id': 1,
            'cluster_type': 'mongo',
            'abc_service': 'srv-2-slug',
            'requester': 'login-2',
        },
        {
            'id': 3,
            'name': 'srv-3',
            'project_id': 2,
            'cluster_type': 'nanny',
            'abc_service': 'srv-3-slug',
        },
        {
            'id': 4,
            'name': 'srv-4',
            'project_id': 2,
            'cluster_type': 'nanny',
            'abc_service': 'srv-4-slug',
        },
        {
            'id': 5,
            'name': 'srv-5',
            'project_id': 3,
            'cluster_type': 'nanny',
            'abc_service': 'srv-5-slug',
        },
        {
            'id': 6,
            'name': 'srv-6',
            'project_id': 4,
            'cluster_type': 'market_service',
            'abc_service': 'srv-6-slug',
        },
    ]


@pytest.fixture(name='clown_branches')
def _clown_branches():
    return []


@pytest.fixture(autouse=True)
def _clown_cache_mocks_autouse(clown_cache_mocks):
    return clown_cache_mocks
