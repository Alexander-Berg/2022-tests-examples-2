import pytest

SQL_FILES = [
    'add_systems.sql',
    'add_groups.sql',
    'add_roles.sql',
    'link_groups_roles.sql',
    'add_permissions.sql',
]


@pytest.mark.parametrize(
    ['system', 'permission'],
    [
        ('system_main', 'system_main_empty_permission_1'),
        ('system_main', 'system_main_empty_permission_2'),
    ],
)
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_delete_permission(
        permissions_delete_request,
        assert_response,
        system,
        permission,
        assert_link_deleted,
):
    response = await permissions_delete_request(
        system=system, permission=permission,
    )
    assert_response(
        response,
        200,
        {
            'permission': {
                'role_slugs': [],
                'slug': permission,
                'system_slug': system,
            },
        },
    )
    await assert_link_deleted(permission)


@pytest.mark.parametrize(
    ['system', 'permission'],
    [
        ('system_main', 'no_permission'),
        ('no_system', 'system_main_role_1_permission_1'),
        ('system_main', 'system_second_role_2_permission_1'),
    ],
)
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_delete_not_found(
        permissions_delete_request,
        assert_response,
        system,
        permission,
        assert_link_deleted,
):
    response = await permissions_delete_request(
        system=system, permission=permission,
    )
    assert_response(
        response,
        404,
        {
            'code': 'permission_not_found',
            'message': (
                f'Permission "{permission}" is not found in system "{system}"'
            ),
        },
    )
    await assert_link_deleted()
