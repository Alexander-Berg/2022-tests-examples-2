import pytest


@pytest.mark.parametrize(
    'role_path, new_roles',
    [
        (
            (
                '/project/taxi/project_role/services_roles/service/'
                'clownductor/service_role/deploy_approve_programmer/'
            ),
            [
                {
                    'id': 2,
                    'login': 'd1mbas',
                    'service_id': 1,
                    'role': 'deploy_approve_programmer',
                    'is_super': False,
                },
            ],
        ),
        (
            (
                '/project/taxi/project_role/services_roles/service/'
                'clownductor/service_role/deploy_approve_manager/'
            ),
            [
                {
                    'id': 2,
                    'login': 'd1mbas',
                    'service_id': 1,
                    'role': 'deploy_approve_manager',
                    'is_super': False,
                },
            ],
        ),
        ('/project/taxi/project_role/deploy_approve_manager/', []),
        (
            '/project/__supers__/deploy_approve_manager',
            [
                {
                    'id': 2,
                    'login': 'd1mbas',
                    'role': 'deploy_approve_manager',
                    'is_super': True,
                },
            ],
        ),
        (
            (
                '/project/taxi/project_role/services_roles/service/'
                'clownductor/service_role/strongbox_secrets_testing/'
            ),
            [
                {
                    'id': 2,
                    'login': 'd1mbas',
                    'service_id': 1,
                    'role': 'strongbox_secrets_testing',
                    'is_super': False,
                },
            ],
        ),
    ],
)
async def test_handler(web_app_client, web_context, role_path, new_roles):
    response = await web_app_client.post(
        '/permissions/v1/idm/add-role/',
        headers={'X-IDM-Request-Id': 'abc'},
        data={'login': 'd1mbas', 'path': role_path},
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {'code': 0}
    roles = await web_context.service_manager.permissions.get_roles()
    assert [x.as_dict() for x in roles] == [
        {
            'id': 1,
            'login': 'd1mbas',
            'project_id': 1,
            'role': 'deploy_approve_manager',
            'is_super': False,
        },
        *new_roles,
    ]
