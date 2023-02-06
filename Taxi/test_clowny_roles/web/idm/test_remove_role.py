import json

import pytest


def case(login: str, path: str, role: dict):
    return pytest.param(login, path, role)


@pytest.mark.parametrize('is_fired', [True, False])
@pytest.mark.parametrize('remove_existing_grand', [True, False])
@pytest.mark.parametrize(
    'login, path, role,',
    [
        case(
            'd1mbas',
            '/namespace/taxi/namespace_role/nanny_root/',
            {'namespace': 'taxi', 'namespace_role': 'nanny_root'},
        ),
        case(
            'd1mbas',
            (
                '/namespace/taxi/'
                'namespace_role/subsystem_nanny/'
                'namespace_subsystem_nanny/nanny_root/'
            ),
            {
                'namespace': 'taxi',
                'namespace_role': 'subsystem_nanny',
                'namespace_subsystem_nanny': 'nanny_root',
            },
        ),
        case(
            'd1mbas',
            (
                '/namespace/taxi/'
                'namespace_role/project_roles/'
                'project/prj-1/'
                'project_role/deploy_approve/'
            ),
            {
                'namespace': 'taxi',
                'namespace_role': 'project_roles',
                'project': 'prj-1',
                'project_role': 'deploy_approve',
            },
        ),
        case(
            'd1mbas',
            (
                '/namespace/taxi/'
                'namespace_role/project_roles/'
                'project/prj-1/'
                'project_role/service_roles/'
                'service/srv-1/'
                'service_role/deploy_approve/'
            ),
            {
                'namespace': 'taxi',
                'namespace_role': 'project_roles',
                'project': 'prj-1',
                'project_role': 'service_roles',
                'service': 'srv-1',
                'service_role': 'deploy_approve',
            },
        ),
    ],
)
async def test_handler(
        taxi_clowny_roles_web,
        add_subsystem,
        add_role,
        get_grands,
        is_fired,
        remove_existing_grand,
        login,
        path,
        role,
):
    nanny_id = await add_subsystem('nanny')
    await add_role('nanny_root', 'taxi', 'namespace', nanny_id)
    internal_id = await add_subsystem('internal')
    await add_role('deploy_approve', 'prj-1', 'project', internal_id)
    await add_role('deploy_approve', 'srv-1-slug', 'service', internal_id)

    request_data = {'login': login, 'path': path, 'role': json.dumps(role)}

    if remove_existing_grand:
        response = await taxi_clowny_roles_web.post(
            '/idm/v1/add-role/', data=request_data,
        )
        assert response.status == 200, await response.text()
        assert len(await get_grands()) == 1

    if is_fired:
        request_data['fired'] = 1

    response = await taxi_clowny_roles_web.post(
        '/idm/v1/remove-role/', data=request_data,
    )
    assert response.status == 200, await response.text()
    assert not await get_grands()
