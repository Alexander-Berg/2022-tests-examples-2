import pytest


ALL_PROJECTS = [
    {'id': 1, 'name': 'taxi-devops'},
    {'id': 2, 'name': 'taxi-infra'},
]
ALL_SERVICES = [
    {
        'id': 1,
        'project_id': 1,
        'cluster_type': 'nanny',
        'name': 'test_service',
    },
    {
        'id': 2,
        'project_id': 1,
        'cluster_type': 'postgresql',
        'name': 'test_service',
    },
    {'id': 3, 'project_id': 2, 'cluster_type': 'nanny', 'name': 'some'},
]
ALL_BRANCHES = [
    {
        'id': 123,
        'service_id': 1,
        'env': 'stable',
        'direct_link': 'test_service_stable',
        'name': 'stable',
    },
]


@pytest.fixture(autouse=True)
def clownductor_mock(mock_clownductor_internal):
    @mock_clownductor_internal('/v1/projects/')
    def _projects(_):
        return ALL_PROJECTS

    @mock_clownductor_internal('/v1/services/')
    def _services(request):
        service_name = request.query['name']
        cluster_type = request.query.get('cluster_type')
        project_names = {
            project['id']: project['name'] for project in ALL_PROJECTS
        }
        return [
            {**x, 'project_name': project_names[x['project_id']]}
            for x in ALL_SERVICES
            if x['name'] == service_name
            and (
                x['cluster_type'] == cluster_type
                if cluster_type is not None
                else True
            )
        ]

    @mock_clownductor_internal('/v1/branches/')
    def _branches(request):
        service_id = int(request.query['service_id'])
        return [x for x in ALL_BRANCHES if x['service_id'] == service_id]

    @mock_clownductor_internal('/v2/branches/')
    def _v2_branches(request):
        _body = request.json
        _newer_than = _body.get('cursor', {}).get('newer_than')
        _results = ALL_BRANCHES[:]
        if _newer_than:
            _results = [x for x in _results if x['id'] > _newer_than]
        _results = _results[: int(_body['limit'])]
        response = {'branches': _results}
        if _results:
            response['cursor'] = {'newer_than': max(x['id'] for x in _results)}
        return response
