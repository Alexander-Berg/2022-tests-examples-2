import pytest

from tests_access_control.helpers import admin_restrictions


SQL_FILES = [
    'add_systems.sql',
    'add_roles.sql',
    'add_restrictions.sql',
    'add_many_restrictions.sql',
]


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve(taxi_access_control):
    system_slug = 'system_main'
    role_slug = 'system_main_role_1'

    await admin_restrictions.retrieve_restriction(
        taxi_access_control,
        system_slug=system_slug,
        role_slug=role_slug,
        body={},
        expected_status_code=200,
        expected_response_json={
            'restrictions': [
                {
                    'handler': {'method': 'POST', 'path': '/foo/bar'},
                    'predicate': {},
                },
            ],
        },
    )


@pytest.mark.parametrize(
    ['system_slug', 'role_slug'],
    [
        ('system_main', 'system_main_role_4'),
        ('no_system', 'system_main_role_4'),
        ('system_main', 'no_role'),
    ],
)
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_empty_retrieve(taxi_access_control, system_slug, role_slug):
    await admin_restrictions.retrieve_restriction(
        taxi_access_control,
        system_slug=system_slug,
        role_slug=role_slug,
        body={},
        expected_status_code=200,
        expected_response_json={'restrictions': []},
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_cursor_result(taxi_access_control):
    system_slug = 'system_second'
    role_slug = 'system_second_role_2'

    await admin_restrictions.retrieve_restriction(
        taxi_access_control,
        system_slug=system_slug,
        role_slug=role_slug,
        body={'limit': 2},
        expected_status_code=200,
        expected_response_json={
            'cursor': {
                'greater_than_handler': {'method': 'POST', 'path': '/test/1'},
            },
            'restrictions': [
                {
                    'handler': {'method': 'GET', 'path': '/test/1'},
                    'predicate': {'meow': 5},
                },
                {
                    'handler': {'method': 'POST', 'path': '/test/1'},
                    'predicate': {'meow': 4},
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_using_cursor(taxi_access_control):
    system_slug = 'system_second'
    role_slug = 'system_second_role_2'

    await admin_restrictions.retrieve_restriction(
        taxi_access_control,
        system_slug=system_slug,
        role_slug=role_slug,
        body={
            'limit': 2,
            'cursor': {
                'greater_than_handler': {'method': 'POST', 'path': '/test/1'},
            },
        },
        expected_status_code=200,
        expected_response_json={
            'restrictions': [
                {
                    'handler': {'method': 'PATCH', 'path': '/test/1'},
                    'predicate': {'meow': 6},
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_filter_part(taxi_access_control):
    system_slug = 'system_main'
    role_slug = 'system_main_role_2'

    await admin_restrictions.retrieve_restriction(
        taxi_access_control,
        system_slug=system_slug,
        role_slug=role_slug,
        body={'limit': 2, 'filters': {'handler_path_part': '/foo'}},
        expected_status_code=200,
        expected_response_json={
            'cursor': {
                'greater_than_handler': {'method': 'POST', 'path': '/foo/baz'},
            },
            'restrictions': [
                {
                    'handler': {'path': '/foo/bar', 'method': 'POST'},
                    'predicate': {},
                },
                {
                    'handler': {'path': '/foo/baz', 'method': 'POST'},
                    'predicate': {},
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_filter_method(taxi_access_control):
    system_slug = 'system_main'
    role_slug = 'system_main_role_2'

    await admin_restrictions.retrieve_restriction(
        taxi_access_control,
        system_slug=system_slug,
        role_slug=role_slug,
        body={'limit': 2, 'filters': {'handler_method': 'GET'}},
        expected_status_code=200,
        expected_response_json={
            'restrictions': [
                {
                    'handler': {'path': '/test/1', 'method': 'GET'},
                    'predicate': {'meow': 2},
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_filter_method_all(taxi_access_control):
    system_slug = 'system_main'
    role_slug = 'system_main_role_2'

    await admin_restrictions.retrieve_restriction(
        taxi_access_control,
        system_slug=system_slug,
        role_slug=role_slug,
        body={
            'limit': 2,
            'filters': {'handler_method': 'POST', 'handler_path_part': 'test'},
        },
        expected_status_code=200,
        expected_response_json={
            'restrictions': [
                {
                    'handler': {'path': '/test/1', 'method': 'POST'},
                    'predicate': {'meow': 1},
                },
            ],
        },
    )
