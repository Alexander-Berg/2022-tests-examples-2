import pytest


@pytest.fixture(name='clown_namespaces')
def _clown_namespaces():
    return [{'id': 1, 'name': 'ns1'}, {'id': 2, 'name': 'ns2'}]


@pytest.fixture(name='clown_projects')
def _clown_projects():
    return [{'id': 1, 'name': 'prj-1', 'namespace_id': 1}]


@pytest.fixture(name='clown_services')
def _clown_services():
    return [
        {
            'id': 1,
            'name': 'srv-1',
            'project_id': 1,
            'cluster_type': 'nanny',
            'abc_service': 'srv1',
        },
        {
            'id': 2,
            'name': 'srv-2',
            'project_id': 1,
            'cluster_type': 'mongo',
            'abc_service': 'srv2',
        },
        {
            'id': 3,
            'name': 'srv',
            'project_id': 1,
            'cluster_type': 'nanny',
            'abc_service': 'srv',
        },
        {
            'id': 4,
            'name': 'srv',
            'project_id': 1,
            'cluster_type': 'mongo',
            'abc_service': 'srv',
        },
        {
            'id': 5,
            'name': 'srv-5',
            'project_id': 1,
            'cluster_type': 'market_service',
            'abc_service': 'srv5',
        },
    ]


@pytest.fixture(name='data_fill', autouse=True)
async def _data_fill(add_subsystem, add_role, add_grand):
    nanny_id = await add_subsystem('nanny')
    nanny_root_name = ('nanny', 'няня')
    nanny_root_help = ('nanny help', 'няня помощь')
    await add_role(
        'nanny_root',
        'ns1',
        'namespace',
        nanny_id,
        nanny_root_name,
        nanny_root_help,
    )
    project_role_id = await add_role(
        'nanny_root',
        'prj-1',
        'project',
        nanny_id,
        nanny_root_name,
        nanny_root_help,
    )
    await add_grand('test-login-1', project_role_id)
    await add_grand('test-login-2', project_role_id)
    await add_grand('test-login-3', project_role_id)

    service_role_id = await add_role(
        'nanny_root',
        'srv',
        'service',
        nanny_id,
        nanny_root_name,
        nanny_root_help,
    )
    await add_grand('test-login-1', service_role_id)
    await add_grand('test-login-2', service_role_id)

    internal_id = await add_subsystem('internal')
    deploy_name = ('deploy approve', 'ок выкатки')
    deploy_help = ('Allows to approve release', 'Даёт право на аппрув релиза')
    deploy_role_id = await add_role(
        'deploy_approve',
        'srv1',
        'service',
        internal_id,
        deploy_name,
        deploy_help,
    )
    await add_grand('test-login-1', deploy_role_id)
    await add_grand('test-login-4', deploy_role_id)

    market_id = await add_subsystem('market')
    market_name = ('tsum view access', 'доступ на просмотр к цуму')
    market_help = (
        'grants view rights to tsum service',
        'предоставляет доступ на просмотр в цум',
    )
    market_role_id = await add_role(
        'market_view', 'srv5', 'service', market_id, market_name, market_help,
    )
    await add_grand('test-login-1', market_role_id)
    await add_grand('test-login-2', market_role_id)


async def test_handler(taxi_clowny_roles_web, get_grands):
    response = await taxi_clowny_roles_web.get(
        '/idm/v1/get-roles/', params={'limit': 5},
    )
    assert response.status == 200, await response.text()
    result = await response.json()
    assert result == {
        'code': 0,
        'next-url': '/idm/v1/get-roles/?limit=5&older_than=5',
        'roles': [
            {
                'fields': {},
                'login': 'test-login-2',
                'path': (
                    '/namespace/ns1/'
                    'namespace_role/project_roles/'
                    'project/prj-1/'
                    'project_role/service_roles/'
                    'service/srv-5/'
                    'service_role/subsystem_market/'
                    'service_subsystem_market/market_view/'
                ),
            },
            {
                'fields': {},
                'login': 'test-login-1',
                'path': (
                    '/namespace/ns1/'
                    'namespace_role/project_roles/'
                    'project/prj-1/'
                    'project_role/service_roles/'
                    'service/srv-5/'
                    'service_role/subsystem_market/'
                    'service_subsystem_market/market_view/'
                ),
            },
            {
                'fields': {},
                'login': 'test-login-4',
                'path': (
                    '/namespace/ns1/'
                    'namespace_role/project_roles/'
                    'project/prj-1/'
                    'project_role/service_roles/'
                    'service/srv-1/'
                    'service_role/subsystem_internal/'
                    'service_subsystem_internal/deploy_approve/'
                ),
            },
            {
                'fields': {},
                'login': 'test-login-1',
                'path': (
                    '/namespace/ns1/'
                    'namespace_role/project_roles/'
                    'project/prj-1/'
                    'project_role/service_roles/'
                    'service/srv-1/'
                    'service_role/subsystem_internal/'
                    'service_subsystem_internal/deploy_approve/'
                ),
            },
            {
                'fields': {},
                'login': 'test-login-2',
                'path': (
                    '/namespace/ns1/'
                    'namespace_role/project_roles/'
                    'project/prj-1/'
                    'project_role/service_roles/'
                    'service/srv/'
                    'service_role/subsystem_nanny/'
                    'service_subsystem_nanny/nanny_root/'
                ),
            },
        ],
    }

    response = await taxi_clowny_roles_web.get(result['next-url'])
    assert response.status == 200, await response.text()
    assert await response.json() == {
        'code': 0,
        'roles': [
            {
                'fields': {},
                'login': 'test-login-1',
                'path': (
                    '/namespace/ns1/'
                    'namespace_role/project_roles/'
                    'project/prj-1/'
                    'project_role/service_roles/'
                    'service/srv/'
                    'service_role/subsystem_nanny/'
                    'service_subsystem_nanny/nanny_root/'
                ),
            },
            {
                'fields': {},
                'login': 'test-login-3',
                'path': (
                    '/namespace/ns1/'
                    'namespace_role/project_roles/'
                    'project/prj-1/'
                    'project_role/subsystem_nanny/'
                    'project_subsystem_nanny/nanny_root/'
                ),
            },
            {
                'fields': {},
                'login': 'test-login-2',
                'path': (
                    '/namespace/ns1/'
                    'namespace_role/project_roles/'
                    'project/prj-1/'
                    'project_role/subsystem_nanny/'
                    'project_subsystem_nanny/nanny_root/'
                ),
            },
            {
                'fields': {},
                'login': 'test-login-1',
                'path': (
                    '/namespace/ns1/'
                    'namespace_role/project_roles/'
                    'project/prj-1/'
                    'project_role/subsystem_nanny/'
                    'project_subsystem_nanny/nanny_root/'
                ),
            },
        ],
    }
    assert len(await get_grands()) == 9
