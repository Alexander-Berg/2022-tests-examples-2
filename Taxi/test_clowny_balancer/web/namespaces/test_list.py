import pytest


@pytest.mark.parametrize(
    'params, json_data, result',
    [
        ({'limit': 0}, {}, {'namespaces': []}),
        (
            {'limit': 1},
            {},
            {
                'namespaces': [
                    {
                        'id': 1,
                        'project_id': 1,
                        'awacs_namespace': 'aaa.net',
                        'env': 'stable',
                        'abc_quota': 'some',
                        'is_shared': False,
                        'is_external': False,
                        'created_at': '2020-06-05T15:00:00+03:00',
                        'updated_at': '2020-06-05T15:10:00+03:00',
                    },
                ],
                'max_id': 1,
            },
        ),
        ({'limit': 100, 'greater_than_id': 100}, {}, {'namespaces': []}),
        ({'limit': 100}, {'project_id': 2}, {'namespaces': []}),
        (
            {'limit': 100},
            {'project_id': 1},
            {
                'namespaces': [
                    {
                        'id': 1,
                        'project_id': 1,
                        'awacs_namespace': 'aaa.net',
                        'env': 'stable',
                        'abc_quota': 'some',
                        'is_shared': False,
                        'is_external': False,
                        'created_at': '2020-06-05T15:00:00+03:00',
                        'updated_at': '2020-06-05T15:10:00+03:00',
                    },
                ],
                'max_id': 1,
            },
        ),
        (
            {'limit': 100},
            {'project': 'taxi'},
            {
                'namespaces': [
                    {
                        'id': 1,
                        'project_id': 1,
                        'awacs_namespace': 'aaa.net',
                        'env': 'stable',
                        'abc_quota': 'some',
                        'is_shared': False,
                        'is_external': False,
                        'created_at': '2020-06-05T15:00:00+03:00',
                        'updated_at': '2020-06-05T15:10:00+03:00',
                    },
                ],
                'max_id': 1,
            },
        ),
        ({'limit': 100}, {'is_external': True}, {'namespaces': []}),
        (
            {'limit': 100},
            {'is_external': False},
            {
                'namespaces': [
                    {
                        'id': 1,
                        'project_id': 1,
                        'awacs_namespace': 'aaa.net',
                        'env': 'stable',
                        'abc_quota': 'some',
                        'is_shared': False,
                        'is_external': False,
                        'created_at': '2020-06-05T15:00:00+03:00',
                        'updated_at': '2020-06-05T15:10:00+03:00',
                    },
                ],
                'max_id': 1,
            },
        ),
        ({'limit': 100}, {'name': 'none-existing'}, {'namespaces': []}),
        (
            {'limit': 100},
            {'name': 'aa'},
            {
                'namespaces': [
                    {
                        'id': 1,
                        'project_id': 1,
                        'awacs_namespace': 'aaa.net',
                        'env': 'stable',
                        'abc_quota': 'some',
                        'is_shared': False,
                        'is_external': False,
                        'created_at': '2020-06-05T15:00:00+03:00',
                        'updated_at': '2020-06-05T15:10:00+03:00',
                    },
                ],
                'max_id': 1,
            },
        ),
    ],
)
async def test_list(
        mock_clownductor, taxi_clowny_balancer_web, params, json_data, result,
):
    @mock_clownductor('/api/projects')
    def _projects_handler(request):
        return [
            {
                'name': 'taxi',
                'yp_quota_abc': 'taxi_yp_quota',
                'datacenters': ['SAS', 'VLA', 'MAN'],
                'id': 1,
                'namespace_id': 1,
            },
        ]

    response = await taxi_clowny_balancer_web.post(
        '/v1/namespaces/list/', params=params, json=json_data,
    )
    data = await response.json()
    assert response.status == 200, data
    assert data == result
