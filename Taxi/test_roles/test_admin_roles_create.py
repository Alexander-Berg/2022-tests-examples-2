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
    ['system', 'role', 'name'],
    [
        ('system_main', 'role_10', 'role 10'),
        ('system_second', 'role_10', 'role 10'),
    ],
)
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_create_role_success(
        roles_create_request, assert_response, system, role, name,
):
    response = await roles_create_request(system=system, role=role, name=name)
    assert_response(
        response,
        200,
        {'role': {'name': name, 'slug': role, 'system_slug': system}},
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_create_role_conflict_same_name(
        roles_create_request, assert_response,
):
    response = await roles_create_request(
        system='system_main', role='role_1', name='system main role 1',
    )
    assert_response(
        response,
        409,
        {
            'code': 'already_exists',
            'message': 'Role "system main role 1" already exists',
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_create_role_conflict_same_slug(
        roles_create_request, assert_response,
):
    response = await roles_create_request(
        system='system_main', role='system_main_role_1', name='role 1',
    )
    assert_response(
        response,
        409,
        {
            'code': 'already_exists',
            'message': 'Role "system_main_role_1" already exists',
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_create_role_system_not_found(
        roles_create_request, assert_response,
):
    response = await roles_create_request(
        system='no_system', role='system_main_role_1', name='role 1',
    )
    assert_response(
        response,
        404,
        {
            'message': 'System "no_system" is not found',
            'code': 'system_not_found',
        },
    )
