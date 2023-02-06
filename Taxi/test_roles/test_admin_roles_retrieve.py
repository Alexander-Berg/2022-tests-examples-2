import pytest


SQL_FILES = [
    'add_systems.sql',
    'add_groups.sql',
    'add_roles.sql',
    'link_groups_roles.sql',
    'add_permissions.sql',
]


@pytest.fixture(name='response_body_format')
def _response_body_format():
    def _wrapper(response_body, expected_status_code):
        if expected_status_code == 200:
            roles = response_body['roles']
            for role in roles:
                assert role.pop('created_at')
                assert role.pop('updated_at')
        return response_body

    return _wrapper


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve(roles_retrieve_request, assert_response):
    system_slug = 'system_main'

    response = await roles_retrieve_request({}, system=system_slug)
    assert_response(
        response,
        200,
        {
            'roles': [
                {
                    'name': 'system main role 1',
                    'slug': 'system_main_role_1',
                    'system_slug': 'system_main',
                },
                {
                    'name': 'system main role 2',
                    'slug': 'system_main_role_2',
                    'system_slug': 'system_main',
                },
                {
                    'name': 'system main role 3',
                    'slug': 'system_main_role_3',
                    'system_slug': 'system_main',
                },
            ],
        },
    )


@pytest.mark.parametrize(
    ['system', 'role'],
    [
        ('system_main', 'system_second_role_1'),
        ('no_system', 'system_main_role_3'),
        ('system_main', 'no_role'),
        ('no_system', None),
    ],
)
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_empty_retrieve(
        roles_retrieve_request, assert_response, system, role,
):
    body = {}
    if role:
        body['filters'] = {'role_part': role}
    response = await roles_retrieve_request(body, system=system)
    assert_response(response, 200, {'roles': []})


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_cursor_result(roles_retrieve_request, assert_response):
    system_slug = 'system_main'

    response = await roles_retrieve_request({'limit': 2}, system=system_slug)
    assert_response(
        response,
        200,
        {
            'cursor': {'greater_than_slug': 'system_main_role_2'},
            'roles': [
                {
                    'name': 'system main role 1',
                    'slug': 'system_main_role_1',
                    'system_slug': 'system_main',
                },
                {
                    'name': 'system main role 2',
                    'slug': 'system_main_role_2',
                    'system_slug': 'system_main',
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_using_cursor(roles_retrieve_request, assert_response):
    system_slug = 'system_main'

    response = await roles_retrieve_request(
        {'limit': 3, 'cursor': {'greater_than_slug': 'system_main_role_2'}},
        system=system_slug,
    )
    assert_response(
        response,
        200,
        {
            'roles': [
                {
                    'name': 'system main role 3',
                    'slug': 'system_main_role_3',
                    'system_slug': 'system_main',
                },
            ],
        },
    )


@pytest.mark.parametrize(
    ['system', 'body', 'expected'],
    [
        (
            'system_main',
            {'limit': 3, 'filters': {'role_part': 'role_3'}},
            {
                'roles': [
                    {
                        'name': 'system main role 3',
                        'slug': 'system_main_role_3',
                        'system_slug': 'system_main',
                    },
                ],
            },
        ),
        (
            'system_main',
            {'limit': 3, 'filters': {'group_name': 'system_main_group_3'}},
            {
                'roles': [
                    {
                        'name': 'system main role 1',
                        'slug': 'system_main_role_1',
                        'system_slug': 'system_main',
                    },
                    {
                        'name': 'system main role 2',
                        'slug': 'system_main_role_2',
                        'system_slug': 'system_main',
                    },
                ],
            },
        ),
        (
            'system_main',
            {
                'limit': 3,
                'filters': {
                    'group_name': 'system_main_group_3',
                    'role_part': 'role_2',
                },
            },
            {
                'roles': [
                    {
                        'name': 'system main role 2',
                        'slug': 'system_main_role_2',
                        'system_slug': 'system_main',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_filter_role(
        roles_retrieve_request, assert_response, system, body, expected,
):
    response = await roles_retrieve_request(body, system=system)
    assert_response(response, 200, expected)


@pytest.mark.parametrize(
    ['system', 'body', 'expected'],
    [
        (
            'system_main',
            {'filters': {'permission': 'system_main_role_3_permission_1'}},
            {
                'roles': [
                    {
                        'name': 'system main role 3',
                        'slug': 'system_main_role_3',
                        'system_slug': 'system_main',
                    },
                ],
            },
        ),
        (
            'system_second',
            {'filters': {'permission': 'system_second_role_1_2_permission_1'}},
            {
                'roles': [
                    {
                        'name': 'system second role 1',
                        'slug': 'system_second_role_1',
                        'system_slug': 'system_second',
                    },
                    {
                        'name': 'system second role 2',
                        'slug': 'system_second_role_2',
                        'system_slug': 'system_second',
                    },
                ],
            },
        ),
        (
            'system_main',
            {'filters': {'permission': 'system_main_empty_permission_1'}},
            {'roles': []},
        ),
    ],
)
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_filter_permission(
        roles_retrieve_request, assert_response, system, body, expected,
):
    response = await roles_retrieve_request(body, system=system)
    assert_response(response, 200, expected)


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_filter_empty(roles_retrieve_request, assert_response):
    system_slug = 'system_main'

    response = await roles_retrieve_request(
        {
            'limit': 1,
            'cursor': {'greater_than_slug': 'system_main_role_1'},
            'filters': {},
        },
        system=system_slug,
    )
    assert_response(
        response,
        200,
        {
            'cursor': {'greater_than_slug': 'system_main_role_2'},
            'roles': [
                {
                    'name': 'system main role 2',
                    'slug': 'system_main_role_2',
                    'system_slug': 'system_main',
                },
            ],
        },
    )
