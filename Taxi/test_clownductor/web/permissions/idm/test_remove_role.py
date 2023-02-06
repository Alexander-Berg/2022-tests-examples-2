import pytest

from clownductor.internal.utils import postgres


@pytest.mark.parametrize(
    'role_path, result_roles',
    [
        pytest.param(
            (
                '/project/taxi/project_role/services_roles/service/'
                'clownductor/service_role/deploy_approve_programmer/'
            ),
            [
                {
                    'id': 1,
                    'login': 'd1mbas',
                    'project_id': 1,
                    'role': 'deploy_approve_manager',
                    'is_super': False,
                },
            ],
            id='remove non existing role',
        ),
        pytest.param(
            '/project/taxi/project_role/deploy_approve_manager/',
            [],
            id='remove existing role',
        ),
        pytest.param(
            '/project/__supers__/deploy_approve_manager/',
            [
                {
                    'id': 1,
                    'login': 'd1mbas',
                    'project_id': 1,
                    'role': 'deploy_approve_manager',
                    'is_super': False,
                },
            ],
            id='remove not existing super role',
        ),
        pytest.param(
            '/project/__supers__/deploy_approve_programmer/',
            [
                {
                    'id': 1,
                    'login': 'd1mbas',
                    'project_id': 1,
                    'role': 'deploy_approve_manager',
                    'is_super': False,
                },
            ],
            id='remove existing super role',
            marks=[
                pytest.mark.pgsql(
                    'clownductor',
                    files=['pg_clownductor.sql', 'super_role.sql'],
                ),
            ],
        ),
        pytest.param(
            (
                '/project/taxi/project_role/services_roles/service/'
                'clownductor/service_role/strongbox_secrets_testing/'
            ),
            [
                {
                    'id': 1,
                    'login': 'd1mbas',
                    'project_id': 1,
                    'role': 'deploy_approve_manager',
                    'is_super': False,
                },
            ],
            id='remove non existing role for strongbox',
        ),
    ],
)
async def test_handler(web_app_client, web_context, role_path, result_roles):
    response = await web_app_client.post(
        '/permissions/v1/idm/remove-role/',
        headers={'X-IDM-Request-Id': 'abc'},
        data={'login': 'd1mbas', 'path': role_path},
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {'code': 0}

    roles = await web_context.service_manager.permissions.get_roles()
    assert [x.as_dict() for x in roles] == result_roles


@pytest.mark.parametrize(
    'role_path',
    [
        pytest.param(
            (
                '/project/taxi/project_role/services_roles/service/'
                'clownductor/service_role/deploy_approve_programmer/'
            ),
            id='remove existing role',
        ),
    ],
)
async def test_revoke_role_several_deleted_services(
        web_app_client, web_context, role_path,
):
    await web_app_client.post(
        '/permissions/v1/idm/add-role/',
        headers={'X-IDM-Request-Id': 'abc'},
        data={'login': 'd1mbas', 'path': role_path},
    )

    async with postgres.get_connection(web_context) as conn:
        await web_context.service_manager.services.set_deleted(
            service_id=1, conn=conn,
        )
        await conn.fetch(
            'insert into clownductor.services '
            '(id, name, project_id, artifact_name, cluster_type) '
            'values (3, \'clownductor\', 1, \'a\', \'nanny\')',
        )

    await web_app_client.post(
        '/permissions/v1/idm/add-role/',
        headers={'X-IDM-Request-Id': 'abc'},
        data={'login': 'd1mbas', 'path': role_path},
    )

    response = await web_app_client.post(
        '/permissions/v1/idm/remove-role/',
        headers={'X-IDM-Request-Id': 'abc'},
        data={'login': 'd1mbas', 'path': role_path},
    )

    assert response.status == 200
    roles = await web_context.service_manager.permissions.get_roles()
    assert [x.as_dict() for x in roles] == [
        {
            'id': 1,
            'login': 'd1mbas',
            'project_id': 1,
            'role': 'deploy_approve_manager',
            'is_super': False,
        },
    ]
