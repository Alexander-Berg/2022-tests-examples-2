import pytest


SQL_FILES = [
    'add_systems.sql',
    'add_groups.sql',
    'add_roles.sql',
    'link_groups_roles.sql',
    'add_permissions.sql',
]


@pytest.mark.parametrize(
    ['system', 'permission', 'expected_role'],
    [
        (
            'system_main',
            'system_main_role_3_permission_1',
            'system_main_role_3',
        ),
        (
            'system_main',
            'system_main_role_3_permission_1',
            'system_main_role_3',
        ),
        (
            'system_second',
            'system_second_role_2_permission_1',
            'system_second_role_2',
        ),
    ],
)
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_get_success(
        permissions_get_request,
        assert_response,
        system,
        permission,
        expected_role,
):
    response = await permissions_get_request(
        system=system, permission=permission,
    )
    assert_response(
        response,
        200,
        {
            'permission': {
                'role_slug': expected_role,
                'role_slugs': [expected_role],
                'slug': permission,
                'system_slug': system,
            },
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_get_success_empty(permissions_get_request, assert_response):
    system = 'system_main'
    permission = 'system_main_empty_permission_2'
    response = await permissions_get_request(
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


@pytest.mark.pgsql('access_control', files=SQL_FILES)
@pytest.mark.parametrize(
    ['system', 'permission'],
    [
        ('no_system', 'system_second_role_2_permission_1'),
        ('system_main', 'no_role'),
        ('system_second', 'system_main_role_3_permission_1'),
        ('system_main', 'system_second_role_2_permission_1'),
    ],
)
async def test_get_not_found(
        permissions_get_request, assert_response, system, permission,
):
    response = await permissions_get_request(
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
