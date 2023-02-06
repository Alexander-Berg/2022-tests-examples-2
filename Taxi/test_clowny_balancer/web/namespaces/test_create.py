from typing import NamedTuple

import pytest


class Case(NamedTuple):
    extra_params: dict
    expected_response: dict
    expected: dict

    check_status: int = 200
    check_is_error: bool = False
    apply_status: int = 200
    apply_is_error: bool = False


@pytest.mark.parametrize(
    (
        'extra_params, expected_response, expected, '
        'check_status, check_is_error, apply_status, apply_is_error'
    ),
    [
        Case(
            {},
            {'job_id': 1},
            {
                'id': 3,
                'awacs_namespace': 'some',
                'env': 'stable',
                'is_shared': False,
                'is_external': False,
                'awacs_ready': False,
            },
        ),
        Case(
            {'is_external': True},
            {'job_id': 1},
            {
                'id': 3,
                'awacs_namespace': 'some',
                'env': 'stable',
                'is_shared': False,
                'is_external': True,
                'awacs_ready': False,
            },
        ),
        Case(
            {'awacs_namespace_name': 'existing'},
            {
                'code': 'REQUEST_ERROR',
                'message': (
                    'Namespace for awacs name "existing" is already exists'
                ),
            },
            {},
            check_status=400,
            check_is_error=True,
        ),
    ],
)
async def test_create(
        mockserver,
        load_json,
        mock_clownductor,
        mock_task_processor_start_job,
        taxi_clowny_balancer_web,
        web_context,
        extra_params,
        expected_response,
        expected,
        check_status,
        check_is_error,
        apply_status,
        apply_is_error,
):
    mock_task_processor_start_job()

    @mockserver.json_handler('/client-awacs/', prefix=True)
    def _handler(request):
        _data = request.json
        if _data['id'] == 'existing':
            return load_json('awacs/get_namespace.json')
        return mockserver.make_response(status=404)

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
        '/v1/namespaces/create/check/',
        json={
            'project_id': 1,
            'awacs_namespace_name': 'some',
            'env': 'stable',
            **extra_params,
        },
    )
    data = await response.json()
    assert response.status == check_status, data
    if check_is_error:
        return

    response = await taxi_clowny_balancer_web.post(
        '/v1/namespaces/create/apply/', json=data['data'],
    )
    data = await response.json()
    assert data == expected_response
    assert response.status == apply_status, data

    namespaces = await web_context.pg.primary.fetch(
        """
        SELECT id,
               awacs_namespace,
               env,
               is_shared,
               is_external,
               awacs_namespace,
               awacs_ready
        FROM balancers.namespaces
        ORDER BY id DESC
        """,
    )
    assert len(namespaces) == 3
    namespace = namespaces[0]

    assert dict(namespace) == expected
