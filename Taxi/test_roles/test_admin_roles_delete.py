import pytest

SQL_FILES = [
    'add_systems.sql',
    'add_groups.sql',
    'add_roles.sql',
    'link_groups_roles.sql',
]


@pytest.fixture(name='response_body_format')
def _response_body_format():
    def _wrapper(response_body, expected_status_code):
        if expected_status_code == 200:
            role = response_body['role']
            assert role.pop('created_at')
            assert role.pop('updated_at')
        return response_body

    return _wrapper


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_delete_role(roles_delete_request, assert_response):
    response = await roles_delete_request(
        system='system_main', role='system_main_role_3',
    )
    assert_response(
        response,
        200,
        {
            'role': {
                'name': 'system main role 3',
                'slug': 'system_main_role_3',
                'system_slug': 'system_main',
            },
        },
    )


@pytest.mark.parametrize(
    ['system', 'role'],
    [
        ('system_main', 'no_role'),
        ('no_system', 'system_main_role_1'),
        ('system_main', 'system_second_role_2'),
    ],
)
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_delete_not_found(
        roles_delete_request, assert_response, system, role,
):
    response = await roles_delete_request(system=system, role=role)
    assert_response(
        response,
        404,
        {
            'code': 'role_not_found',
            'message': f'Role "{role}" is not found in system "{system}"',
        },
    )


@pytest.mark.parametrize(
    ['system', 'role'],
    [
        ('system_main', 'system_main_role_1'),
        ('system_main', 'system_main_role_2'),
        ('system_second', 'system_second_role_2'),
    ],
)
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_delete_used_role(
        roles_delete_request, assert_response, system, role,
):
    response = await roles_delete_request(system=system, role=role)
    assert_response(
        response,
        409,
        {
            'code': 'used_role',
            'message': (
                f'Role "{role}" can not be deleted! '
                f'You should detach the role from all groups.'
            ),
        },
    )
