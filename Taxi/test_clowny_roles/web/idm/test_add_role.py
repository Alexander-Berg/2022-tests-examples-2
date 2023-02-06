import json
from typing import List
from typing import Optional

import pytest


def case(
        login: str,
        path: str,
        role: dict,
        *,
        new_roles: Optional[List[dict]] = None,
        response_data: Optional[dict] = None,
        response_status: int = 200,
):
    return (
        login,
        path,
        role,
        new_roles or [],
        response_data or {'code': 0},
        response_status,
    )


@pytest.mark.parametrize(
    'login, path, role, new_roles, response_data, response_status',
    [
        case(
            'd1mbas',
            '/namespace/taxi/namespace_role/deploy_approve/',
            {'namespace': 'taxi', 'namespace_role': 'deploy_approve'},
            new_roles=[{'login': 'd1mbas', 'role_id': 5}],
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
            new_roles=[{'login': 'd1mbas', 'role_id': 6}],
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
            new_roles=[{'login': 'd1mbas', 'role_id': 7}],
        ),
        case(
            'd1mbas',
            '/namespace/non-exists/namespace_role/deploy_approve/',
            {'namespace': 'non-exists', 'namespace_role': 'deploy_approve'},
            response_data={
                'code': 404,
                'fatal': 'unknown namespace non-exists',
            },
            response_status=404,
        ),
        case(
            'd1mbas',
            '/namespace/taxi/namespace_role/non_existing/',
            {'namespace': 'taxi', 'namespace_role': 'non_existing'},
            response_data={
                'code': 404,
                'fatal': (
                    'unknown role /namespace/taxi/namespace_role/non_existing/'
                ),
            },
            response_status=404,
        ),
        case(
            'd1mbas',
            (
                '/namespace/taxidevopsclownyroles/'
                'standalone_subsystem_taxidevopsclownyroles/subsystem_nanny/'
                'standalone_subsystem_nanny/queue_change_approve/'
            ),
            {
                'namespace': 'taxidevopsclownyroles',
                'standalone_subsystem_taxidevopsclownyroles': (
                    'subsystem_nanny'
                ),
                'standalone_subsystem_nanny': 'queue_change_approve',
            },
            new_roles=[{'login': 'd1mbas', 'role_id': 8}],
        ),
    ],
)
async def test_handler(
        taxi_clowny_roles_web,
        add_abc_scope,
        add_subsystem,
        add_role,
        add_grand,
        get_grands,
        login,
        path,
        role,
        new_roles,
        response_data,
        response_status,
):
    nanny_id = await add_subsystem('nanny')
    await add_role('nanny_root', 'taxi', 'namespace', nanny_id)
    await add_role('nanny_root', 'ns2', 'namespace', nanny_id)
    await add_role('nanny_root', 'prj-1', 'project', nanny_id)
    await add_role('nanny_root', 'srv-1-slug', 'service', nanny_id)

    internal_id = await add_subsystem('internal')
    await add_role('deploy_approve', 'taxi', 'namespace', internal_id)
    await add_role('deploy_approve', 'prj-1', 'project', internal_id)
    await add_role('deploy_approve', 'srv-1-slug', 'service', internal_id)

    abc_id = await add_abc_scope('taxidevopsclownyroles')
    await add_role('queue_change_approve', abc_id, 'standalone', nanny_id)

    await add_grand('d1mbas', 1)
    old_grands = await get_grands()

    response = await taxi_clowny_roles_web.post(
        '/idm/v1/add-role/',
        data={'login': login, 'path': path, 'role': json.dumps(role)},
    )
    assert response.status == response_status, await response.text()
    assert (await response.json()) == response_data

    new_grands = await get_grands()
    assert sorted(new_grands - old_grands) == new_roles
