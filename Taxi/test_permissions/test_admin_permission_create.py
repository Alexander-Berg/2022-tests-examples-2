import pytest


@pytest.mark.pgsql(
    'access_control', files=['add_systems.sql', 'add_roles.sql'],
)
async def test_create_permissions_success(
        permissions_create_request,
        assert_response,
        assert_permission_role_links_pg,
):
    response = await permissions_create_request(
        'system_main', 'permission1', 'system_main_role_1',
    )
    assert_response(
        response,
        200,
        {
            'permission': {
                'slug': 'permission1',
                'role_slug': 'system_main_role_1',
                'role_slugs': ['system_main_role_1'],
                'system_slug': 'system_main',
            },
        },
    )
    await assert_permission_role_links_pg(
        [('system_main_role_1', 'permission1')],
    )


@pytest.mark.pgsql(
    'access_control', files=['add_systems.sql', 'add_roles.sql'],
)
async def test_create_permissions_empty(
        permissions_create_request,
        assert_response,
        assert_permission_role_links_pg,
):
    response = await permissions_create_request('system_main', 'permission1')
    assert_response(
        response,
        200,
        {
            'permission': {
                'slug': 'permission1',
                'role_slugs': [],
                'system_slug': 'system_main',
            },
        },
    )
    await assert_permission_role_links_pg([])


@pytest.mark.pgsql(
    'access_control',
    files=['add_systems.sql', 'add_roles.sql', 'permission1_role1.sql'],
)
async def test_create_permissions_conflict_same_permission(
        permissions_create_request,
        assert_response,
        assert_permission_role_links_pg,
):
    response = await permissions_create_request(
        'system_main', 'permission1', 'system_main_role_1',
    )
    assert_response(
        response,
        409,
        {'code': 'already_exists', 'message': 'Permission already exists'},
    )
    await assert_permission_role_links_pg(
        [('system_main_role_1', 'permission1')],
    )


@pytest.mark.pgsql('access_control', files=['add_systems.sql'])
async def test_create_permissions_role_not_found(
        permissions_create_request,
        assert_response,
        assert_permission_role_links_pg,
):
    response = await permissions_create_request(
        'system_main', 'permission1', 'system_main_role_1',
    )
    assert_response(
        response,
        404,
        {
            'code': 'role_not_found',
            'message': 'Role "system_main_role_1" not found',
        },
    )
    await assert_permission_role_links_pg([])


@pytest.mark.pgsql('access_control', files=['add_systems.sql'])
async def test_create_permissions_system_not_found(
        permissions_create_request,
        assert_response,
        assert_permission_role_links_pg,
):
    response = await permissions_create_request('system_not', 'permission1')
    assert_response(
        response,
        404,
        {
            'code': 'system_not_found',
            'message': 'System "system_not" not found',
        },
    )
    await assert_permission_role_links_pg([])
