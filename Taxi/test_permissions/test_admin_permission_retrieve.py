import pytest


SQL_FILES = [
    'add_systems.sql',
    'add_groups.sql',
    'add_roles.sql',
    'link_groups_roles.sql',
    'add_permissions.sql',
]


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve(permissions_retrieve_request, assert_response):
    system_slug = 'system_main'

    response = await permissions_retrieve_request({}, system=system_slug)
    assert_response(
        response,
        200,
        {
            'permissions': [
                {
                    'role_slugs': [],
                    'slug': 'system_main_empty_permission_1',
                    'system_slug': 'system_main',
                },
                {
                    'role_slugs': [],
                    'slug': 'system_main_empty_permission_2',
                    'system_slug': 'system_main',
                },
                {
                    'role_slug': 'system_main_role_1',
                    'role_slugs': ['system_main_role_1'],
                    'slug': 'system_main_role_1_permission_1',
                    'system_slug': 'system_main',
                },
                {
                    'role_slug': 'system_main_role_2',
                    'role_slugs': ['system_main_role_2'],
                    'slug': 'system_main_role_2_permission_1',
                    'system_slug': 'system_main',
                },
                {
                    'role_slug': 'system_main_role_3',
                    'role_slugs': ['system_main_role_3'],
                    'slug': 'system_main_role_3_permission_1',
                    'system_slug': 'system_main',
                },
                {
                    'role_slug': 'system_main_role_3',
                    'role_slugs': ['system_main_role_3'],
                    'slug': 'system_main_role_3_permission_2',
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
        permissions_retrieve_request, assert_response, system, role,
):
    body = {}
    if role:
        body['filters'] = {'role_slug': role}
    response = await permissions_retrieve_request(body, system=system)
    assert_response(response, 200, {'permissions': []})


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_cursor_result(
        permissions_retrieve_request, assert_response,
):
    system_slug = 'system_main'

    response = await permissions_retrieve_request(
        {'limit': 2}, system=system_slug,
    )
    assert_response(
        response,
        200,
        {
            'cursor': {'greater_than_slug': 'system_main_empty_permission_2'},
            'permissions': [
                {
                    'role_slugs': [],
                    'slug': 'system_main_empty_permission_1',
                    'system_slug': 'system_main',
                },
                {
                    'role_slugs': [],
                    'slug': 'system_main_empty_permission_2',
                    'system_slug': 'system_main',
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_using_cursor(
        permissions_retrieve_request, assert_response,
):
    system_slug = 'system_main'

    response = await permissions_retrieve_request(
        {
            'limit': 3,
            'cursor': {'greater_than_slug': 'system_main_role_2_permission_1'},
        },
        system=system_slug,
    )
    assert_response(
        response,
        200,
        {
            'permissions': [
                {
                    'role_slug': 'system_main_role_3',
                    'role_slugs': ['system_main_role_3'],
                    'slug': 'system_main_role_3_permission_1',
                    'system_slug': 'system_main',
                },
                {
                    'role_slug': 'system_main_role_3',
                    'role_slugs': ['system_main_role_3'],
                    'slug': 'system_main_role_3_permission_2',
                    'system_slug': 'system_main',
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_filter_role(
        permissions_retrieve_request, assert_response,
):
    system_slug = 'system_main'

    response = await permissions_retrieve_request(
        {'limit': 3, 'filters': {'role_slug': 'system_main_role_3'}},
        system=system_slug,
    )
    assert_response(
        response,
        200,
        {
            'permissions': [
                {
                    'role_slug': 'system_main_role_3',
                    'role_slugs': ['system_main_role_3'],
                    'slug': 'system_main_role_3_permission_1',
                    'system_slug': 'system_main',
                },
                {
                    'role_slug': 'system_main_role_3',
                    'role_slugs': ['system_main_role_3'],
                    'slug': 'system_main_role_3_permission_2',
                    'system_slug': 'system_main',
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_filter_empty(
        permissions_retrieve_request, assert_response,
):
    system_slug = 'system_main'

    response = await permissions_retrieve_request(
        {
            'limit': 1,
            'cursor': {'greater_than_slug': 'system_main_role_1_permission_1'},
            'filters': {},
        },
        system=system_slug,
    )
    assert_response(
        response,
        200,
        {
            'cursor': {'greater_than_slug': 'system_main_role_2_permission_1'},
            'permissions': [
                {
                    'role_slug': 'system_main_role_2',
                    'role_slugs': ['system_main_role_2'],
                    'slug': 'system_main_role_2_permission_1',
                    'system_slug': 'system_main',
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_filter_name_part(
        permissions_retrieve_request, assert_response,
):
    system_slug = 'system_main'

    response = await permissions_retrieve_request(
        {'limit': 1, 'filters': {'name_part': '1_permission_1'}},
        system=system_slug,
    )
    assert_response(
        response,
        200,
        {
            'cursor': {'greater_than_slug': 'system_main_role_1_permission_1'},
            'permissions': [
                {
                    'role_slug': 'system_main_role_1',
                    'role_slugs': ['system_main_role_1'],
                    'slug': 'system_main_role_1_permission_1',
                    'system_slug': 'system_main',
                },
            ],
        },
    )
