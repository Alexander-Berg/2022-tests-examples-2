from typing import List
from typing import Optional

import pytest


CLOWNDUCTOR = {
    'cluster_type': 'nanny',
    'id': 1,
    'name': 'clownductor',
    'project_id': 1,
    'project_name': 'taxi-devops',
}

BRE = {
    'cluster_type': 'market_service',
    'id': 2,
    'name': 'bre',
    'project_id': 2,
    'project_name': 'market',
}

UTILS = {
    'cluster_type': 'market_service',
    'id': 3,
    'name': 'utils',
    'project_id': 2,
    'project_name': 'market',
}


@pytest.fixture(autouse=True)
def clownductor_services_mock(mockserver):
    @mockserver.json_handler('/clownductor/v1/services/search/')
    async def _handler(request):
        filter_name = request.query['name']
        namespace = request.query['namespace']
        projects = []
        if namespace == 'taxi':
            projects = [
                {
                    'project_id': 1,
                    'project_name': 'taxi-devops',
                    'services': [
                        item
                        for item in (CLOWNDUCTOR,)
                        if filter_name in item['name']
                    ],
                },
            ]
        if namespace == 'market':
            projects = [
                {
                    'project_id': 2,
                    'project_name': 'market',
                    'services': [
                        item
                        for item in (BRE, UTILS)
                        if filter_name in item['name']
                    ],
                },
            ]
        return {'projects': projects}


@pytest.fixture(name='services_suggest_handler')
def _services_suggest(taxi_clownductor_web):
    async def _wrapper(namespace: str, name: Optional[str] = None):
        filters = {'namespace': namespace}
        if name:
            filters['name'] = name
        response = await taxi_clownductor_web.post(
            '/v1/services/suggest/', json={'filters': filters},
        )
        assert response.status == 200
        return await response.json()

    return _wrapper


@pytest.fixture(name='run_and_compare')
def _run_and_compare(services_suggest_handler):
    async def _wrapper(
            expected_services: List[dict],
            namespace: str,
            name: Optional[str] = None,
    ):
        result = await services_suggest_handler(namespace, name)
        assert result == {'services': expected_services}

    return _wrapper


@pytest.mark.parametrize(
    ['namespace', 'expected'],
    [
        pytest.param('taxi', [CLOWNDUCTOR], id='taxi'),
        pytest.param('market', [BRE, UTILS], id='market'),
    ],
)
async def test_services_suggest(run_and_compare, namespace, expected):
    await run_and_compare(expected, namespace)


@pytest.mark.parametrize(
    ['name', 'expected'],
    [
        pytest.param('til', [UTILS], id='partial_one_services'),
        pytest.param('nononon', [], id='no_services'),
    ],
)
async def test_filter_name(run_and_compare, name, expected):
    await run_and_compare(expected, 'market', name)
