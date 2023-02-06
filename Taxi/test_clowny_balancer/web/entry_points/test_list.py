import pytest

from testsuite.utils import matching

_EP_1 = {
    'awacs_namespace': 'ns1',
    'can_share_namespace': False,
    'created_at': matching.any_string,
    'env': 'stable',
    'fqdn': 'fqdn.net',
    'id': 1,
    'is_external': False,
    'namespace_id': 1,
    'protocol': 'http',
    'updated_at': matching.any_string,
    'upstream_ids': [1, 2],
}
_EP_2 = {
    'awacs_namespace': 'ns2',
    'can_share_namespace': False,
    'created_at': matching.any_string,
    'env': 'testing',
    'fqdn': 'fqdn.test.net',
    'id': 2,
    'is_external': False,
    'namespace_id': 2,
    'protocol': 'http',
    'updated_at': matching.any_string,
    'upstream_ids': [3],
}


@pytest.mark.parametrize(
    'params, json_data, result',
    [
        ({'limit': 1}, {}, {'entry_points': [_EP_1], 'max_id': 1}),
        ({'limit': 100500}, {}, {'entry_points': [_EP_1, _EP_2], 'max_id': 2}),
        (
            {'limit': 100500},
            {'namespace_id': 2},
            {'entry_points': [_EP_2], 'max_id': 2},
        ),
        (
            {'limit': 1, 'greater_than_id': 1},
            {'namespace_id': 1},
            {'entry_points': []},
        ),
        (
            {'limit': 100500},
            {'service_id': 1},
            {'entry_points': [_EP_1, _EP_2], 'max_id': 2},
        ),
        (
            {'limit': 100500},
            {'branch_ids': [1, 2, 3]},
            {'entry_points': [_EP_1, _EP_2], 'max_id': 2},
        ),
        ({'limit': 100500}, {'project_id': 10}, {'entry_points': []}),
        (
            {'limit': 100500},
            {'project_id': 1},
            {'entry_points': [_EP_1, _EP_2], 'max_id': 2},
        ),
        (
            {'limit': 100500},
            {'project': 'taxi'},
            {'entry_points': [_EP_1, _EP_2], 'max_id': 2},
        ),
        ({'limit': 100500}, {'project': 'taxi-some'}, {'entry_points': []}),
        (
            {'limit': 100500},
            {'fqdn': 'fqdn'},
            {'entry_points': [_EP_1, _EP_2], 'max_id': 2},
        ),
        (
            {'limit': 100500},
            {'fqdn': 'fqdn.n'},
            {'entry_points': [_EP_1], 'max_id': 1},
        ),
        ({'limit': 100500}, {'fqdn': 'fqdn.some'}, {'entry_points': []}),
    ],
)
async def test_list(
        mock_clownductor, taxi_clowny_balancer_web, params, json_data, result,
):
    @mock_clownductor('/v1/branches/')
    def _branches_handler(request):
        return [
            {
                'id': 1,
                'env': 'stable',
                'name': 'stable',
                'direct_link': '',
                'service_id': 0,
            },
            {
                'id': 2,
                'env': 'prestable',
                'name': 'prestable',
                'direct_link': '',
                'service_id': 0,
            },
            {
                'id': 3,
                'env': 'testing',
                'name': 'testing',
                'direct_link': '',
                'service_id': 0,
            },
        ]

    @mock_clownductor('/api/projects')
    def _projects_handler(request):
        _projects = [
            {'id': 1, 'name': 'taxi', 'namespace_id': 1},
            {'id': 10, 'name': 'taxi-some', 'namespace_id': 1},
        ]
        return [x for x in _projects if request.query['name'] == x['name']]

    response = await taxi_clowny_balancer_web.post(
        '/v1/entry-points/list/', params=params, json=json_data,
    )
    data = await response.json()
    assert response.status == 200, data
    assert data == result
