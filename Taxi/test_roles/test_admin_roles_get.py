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


@pytest.mark.parametrize(
    ['system', 'role'],
    [
        ('system_main', 'system_main_role_3'),
        ('system_main', 'system_main_role_2'),
        ('system_second', 'system_second_role_2'),
    ],
)
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_get_success(roles_get_request, assert_response, system, role):
    response = await roles_get_request(system=system, role=role)
    assert_response(
        response,
        200,
        {
            'role': {
                'name': role.replace('_', ' '),
                'slug': role,
                'system_slug': system,
            },
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
@pytest.mark.parametrize(
    ['system', 'role'],
    [
        ('no_system', 'system_second_role_2'),
        ('system_main', 'no_role'),
        ('system_second', 'system_main_role_3'),
        ('system_main', 'system_second_role_2'),
    ],
)
async def test_get_not_found(roles_get_request, assert_response, system, role):
    response = await roles_get_request(system=system, role=role)
    assert_response(
        response,
        404,
        {
            'code': 'role_not_found',
            'message': f'Role "{role}" is not found in system "{system}"',
        },
    )
