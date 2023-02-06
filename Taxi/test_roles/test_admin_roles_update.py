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
    ['system', 'role', 'new_name'],
    [
        ('system_main', 'system_main_role_3', 'system main role'),
        ('system_main', 'system_main_role_2', 'system main role'),
        ('system_second', 'system_second_role_1', 'system second role'),
        ('system_second', 'system_second_role_1', 'system second role 1'),
    ],
)
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_update_role(
        roles_update_request, assert_response, system, role, new_name,
):
    response = await roles_update_request(
        system=system, role=role, new_name=new_name,
    )
    assert_response(
        response,
        200,
        {'role': {'name': new_name, 'slug': role, 'system_slug': system}},
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_update_empty(roles_update_request, assert_response):
    response = await roles_update_request(
        system='system_main', role='role', new_name=None,
    )
    assert_response(
        response,
        400,
        {'code': 'empty_body', 'message': 'There is nothing to update'},
    )


@pytest.mark.parametrize(
    ['system', 'role'],
    [
        ('system_main', 'no_role'),
        ('system_main', 'system_main_role_10'),
        ('system_second', 'system_main_role_1'),
    ],
)
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_update_role_not_found(
        roles_update_request, assert_response, system, role,
):
    response = await roles_update_request(
        system=system, role=role, new_name='system_main_role_3',
    )
    assert_response(
        response,
        404,
        {
            'code': 'role_not_found',
            'message': f'Role "{role}" is not found in system "{system}"',
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_update_name_exists(roles_update_request, assert_response):
    system = 'system_main'
    new_name = 'system main role 1'
    response = await roles_update_request(
        system=system, role='system_main_role_3', new_name=new_name,
    )
    assert_response(
        response,
        409,
        {
            'code': 'already_exists',
            'message': f'Role "{new_name}" already exists',
        },
    )
