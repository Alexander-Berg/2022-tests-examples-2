import pytest


@pytest.mark.pgsql('clownductor', files=['pg_clownductor.sql'])
@pytest.mark.parametrize(
    ['body', 'expected'],
    [
        (
            {'limit': 3, 'cursor': {'greater_than': 14}},
            {
                'responsibles': [
                    {
                        'id': 15,
                        'is_super': False,
                        'login': 'login1',
                        'project_id': 1,
                        'project_name': 'taxi',
                        'role': 'strongbox_secrets_testing',
                    },
                    {
                        'id': 16,
                        'is_super': False,
                        'login': 'login6',
                        'role': 'nanny_admin_prod',
                        'service_id': 7,
                        'service_name': 'clownductor',
                        'project_id': 3,
                        'project_name': 'lavka',
                    },
                    {
                        'id': 17,
                        'is_super': False,
                        'login': 'login6',
                        'role': 'strongbox_secrets_prod',
                        'service_id': 7,
                        'service_name': 'clownductor',
                        'project_id': 3,
                        'project_name': 'lavka',
                    },
                ],
            },
        ),
        (
            {'limit': 2},
            {
                'cursor': {'greater_than': 2},
                'responsibles': [
                    {
                        'id': 1,
                        'is_super': True,
                        'login': 'super',
                        'role': 'nanny_admin_prod',
                    },
                    {
                        'id': 2,
                        'is_super': True,
                        'login': 'super',
                        'role': 'strongbox_secrets_prod',
                    },
                ],
            },
        ),
    ],
)
async def test_roles_responsibles_view(web_app_client, body, expected):
    response = await web_app_client.post(
        '/permissions/v1/roles/responsibles/', json=body,
    )
    content = await response.json()
    assert response.status == 200, content
    assert content == expected


@pytest.mark.pgsql('clownductor', files=['pg_clownductor.sql'])
@pytest.mark.parametrize(
    ['body', 'expected_ids', 'cursor'],
    [
        ({'limit': 5}, [1, 2, 3, 4, 5], {'greater_than': 5}),
        (
            {'limit': 10, 'cursor': {'greater_than': 5}},
            [6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            {'greater_than': 15},
        ),
        ({'limit': 10, 'cursor': {'greater_than': 15}}, [16, 17], {}),
        (
            {'logins': ['super', 'login5', 'login2', 'not_found']},
            [1, 2, 3, 4, 5, 11, 12],
            {},
        ),
        (
            {
                'roles': [
                    'granded',
                    'strongbox_secrets_prod',
                    'deploy_approve_manager',
                    'not_found',
                ],
            },
            [2, 3, 4, 7, 8, 11, 13, 17],
            {},
        ),
        ({'scope': {'type': 'super'}}, [1, 2], {}),
        (
            {'scope': {'type': 'project', 'project_name': 'eda'}},
            [1, 2, 4, 5, 11, 12],
            {},
        ),
        (
            {'scope': {'type': 'project', 'project_name': 'not_found'}},
            [1, 2],
            {},
        ),
        (
            {
                'scope': {
                    'type': 'service',
                    'project_name': 'eda',
                    'service_name': 'clownductor',
                },
            },
            [1, 2, 4, 5, 12],
            {},
        ),
        (
            {
                'scope': {
                    'type': 'service',
                    'project_name': 'eda',
                    'service_name': 'not_found',
                },
            },
            [1, 2, 4, 5],
            {},
        ),
        (
            {
                'roles': ['nanny_admin_testing', 'not_found'],
                'logins': ['login5', 'login2'],
                'scope': {
                    'type': 'service',
                    'project_name': 'eda',
                    'service_name': 'clownductor',
                },
            },
            [5, 12],
            {},
        ),
    ],
)
async def test_roles_responsibles(web_app_client, body, expected_ids, cursor):
    response = await web_app_client.post(
        '/permissions/v1/roles/responsibles/', json=body,
    )
    content = await response.json()
    assert response.status == 200, content
    if cursor:
        assert content.pop('cursor') == cursor
    assert content.keys() == {'responsibles'}, content
    assert [item['id'] for item in content['responsibles']] == expected_ids
