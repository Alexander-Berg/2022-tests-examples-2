import pytest


def _env_params():
    return {'domain': 'yandex.net', 'juggler_folder': 'folder'}


def env_params(project_prefix):
    return {
        'general': {'project_prefix': project_prefix, 'docker_image_tpl': ''},
        'stable': _env_params(),
        'testing': _env_params(),
        'unstable': _env_params(),
    }


ALL_PROJECTS = [
    {
        'id': 150,
        'name': 'taxi-infra',
        'env_params': env_params('taxi'),
        'namespace_id': 1,
    },
    {
        'id': 2,
        'name': 'taxi',
        'env_params': env_params('taxi'),
        'namespace_id': 2,
    },
    {
        'id': 3,
        'name': 'eda',
        'env_params': env_params('eda'),
        'namespace_id': 3,
    },
]
ALL_SERVICES = [
    {
        'id': 1,
        'project_id': 150,
        'cluster_type': 'nanny',
        'name': 'clownductor',
    },
    {
        'id': 2,
        'project_id': 150,
        'cluster_type': 'postgresql',
        'name': 'clownductor',
    },
    {'id': 3, 'project_id': 2, 'cluster_type': 'nanny', 'name': 'some'},
    {'id': 4, 'project_id': 150, 'cluster_type': 'nanny', 'name': 'some'},
    {
        'id': 5,
        'project_id': 150,
        'cluster_type': 'nanny',
        'name': 'clowny-balancer',
    },
    {
        'id': 100500,
        'project_id': 150,
        'cluster_type': 'nanny',
        'name': 'service-to-direct-commit',
    },
    {'id': 139, 'project_id': 150, 'cluster_type': 'nanny', 'name': 'hejmdal'},
    {
        'id': 123,
        'project_id': 150,
        'cluster_type': 'nanny',
        'name': 'test_service',
    },
    {
        'id': 666,
        'project_id': 150,
        'cluster_type': 'nanny',
        'name': 'service_without_stable',
    },
    {
        'id': 13,
        'project_id': 150,
        'cluster_type': 'nanny',
        'name': 'clowny-alert-manager',
    },
]
ALL_BRANCHES = [
    {
        'id': 1,
        'service_id': 1,
        'env': 'stable',
        'direct_link': 'taxi_clownductor_stable',
        'name': 'stable',
    },
    {
        'id': 10,
        'service_id': 1,
        'env': 'prestable',
        'direct_link': 'taxi_clownductor_pre_stable',
        'name': 'prestable',
    },
    {
        'id': 2,
        'env': 'stable',
        'service_id': 2,
        'direct_link': 'some_host',
        'name': 'stable',
    },
    {
        'id': 222,
        'env': 'stable',
        'service_id': 2,
        'direct_link': 'child_1',
        'name': 'stable',
    },
    {
        'id': 3,
        'service_id': 5,
        'direct_link': 'taxi-clowny-balancer_stable',
        'env': 'stable',
        'name': 'stable',
    },
    {
        'id': 100500,
        'service_id': 100500,
        'direct_link': 'branch_to_direct_commit',
        'env': 'stable',
        'name': 'branch_to_direct_commit',
    },
    {
        'id': 16,
        'service_id': 139,
        'direct_link': 'taxi_hejmdal_testing',
        'env': 'testing',
        'name': 'taxi_hejmdal_testing',
    },
    {
        'id': 17,
        'service_id': 139,
        'direct_link': 'taxi_hejmdal_testing2',
        'env': 'testing',
        'name': 'taxi_hejmdal_testing2',
    },
    {
        'id': 18,
        'service_id': 139,
        'direct_link': 'taxi_hejmdal_stable',
        'env': 'stable',
        'name': 'taxi_hejmdal_stable',
    },
    {
        'id': 19,
        'service_id': 139,
        'direct_link': 'taxi_hejmdal_pre_stable',
        'env': 'prestable',
        'name': 'taxi_hejmdal_pre_stable',
    },
    {
        'id': 1234,
        'service_id': 123,
        'direct_link': 'test_service_stable',
        'env': 'stable',
        'name': 'test_service_stable',
    },
    {
        'id': 666,
        'service_id': 666,
        'direct_link': 'service_without_stable_testing',
        'env': 'testing',
        'name': 'service_without_stable_testing',
    },
    {
        'id': 13,
        'service_id': 13,
        'direct_link': 'clowny-alert-manager_stable',
        'env': 'stable',
        'name': 'clowny-alert-manager_stable',
    },
    {
        'id': 1337,
        'service_id': 1337,
        'direct_link': 'test_service_irresponsible_stable',
        'env': 'stable',
        'name': 'test_service_irresponsible_stable',
    },
    {
        'id': 1338,
        'service_id': 1338,
        'direct_link': 'test_service_days_only_stable',
        'env': 'stable',
        'name': 'test_service_days_only_stable',
    },
]
ALL_HOSTS = [
    {'branch_id': 222, 'name': 'child_1-stable-sas', 'datacenter': 'sas'},
    {'branch_id': 222, 'name': 'child_1-stable-vla', 'datacenter': 'vla'},
    {'branch_id': 222, 'name': 'child_1-stable-man', 'datacenter': 'man'},
]


@pytest.fixture(autouse=True)
def clownductor_mock(mock_clownductor):
    @mock_clownductor('/v1/projects/')
    def _projects(_):
        return ALL_PROJECTS

    @mock_clownductor('/v1/services/')
    def _services(request):
        project_id = int(request.query['project_id'])
        return [x for x in ALL_SERVICES if x['project_id'] == project_id]

    @mock_clownductor('/v1/branches/')
    def _branches(request):
        service_id = int(request.query['service_id'])
        return [x for x in ALL_BRANCHES if x['service_id'] == service_id]

    @mock_clownductor('/v1/hosts/')
    def _hosts(request):
        branch_id = int(request.query['branch_id'])
        return [x for x in ALL_HOSTS if x['branch_id'] == branch_id]

    @mock_clownductor('/v2/branches/')
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
