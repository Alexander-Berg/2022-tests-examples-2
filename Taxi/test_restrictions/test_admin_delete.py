import pytest

from tests_access_control.helpers import admin_restrictions


SQL_FILES = ['add_systems.sql', 'add_roles.sql', 'add_restrictions.sql']


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_delete_success(taxi_access_control, get_restriction_pg):
    handler_path = '/foo/bar'
    handler_method = 'POST'
    system_slug = 'system_main'
    role_slug = 'system_main_role_1'

    restriction_in_db = await get_restriction_pg(
        system_slug, role_slug, handler_path, handler_method,
    )
    assert restriction_in_db

    await admin_restrictions.delete_restriction(
        taxi_access_control,
        system_slug=system_slug,
        role_slug=role_slug,
        handler_path=handler_path,
        handler_method=handler_method,
        expected_status_code=200,
        expected_response_json={
            'restriction': {
                'handler': {'path': handler_path, 'method': handler_method},
                'predicate': {},
            },
        },
    )

    result = await get_restriction_pg(
        system_slug, role_slug, handler_path, handler_method,
    )
    assert not result


@pytest.mark.pgsql('access_control', files=SQL_FILES)
@pytest.mark.parametrize(
    ['system_slug', 'role_slug', 'handler_path', 'handler_method'],
    [
        ('system_main', 'system_main_role_1', '/foo/bar', 'GET'),
        ('system_main', 'system_main_role_1', '/foo/bar/1', 'POST'),
        ('system_main', 'system_main_role_100', '/foo/bar', 'POST'),
        ('system_main_000', 'system_main_role_1', '/foo/bar', 'POST'),
        ('system_main', 'system_main_role_1', '/meow', 'POST'),
    ],
)
async def test_delete_restrictions_not_found(
        taxi_access_control,
        get_all_restrictions_pg,
        system_slug,
        role_slug,
        handler_path,
        handler_method,
):
    before_handle_call = await get_all_restrictions_pg()

    await admin_restrictions.delete_restriction(
        taxi_access_control,
        system_slug=system_slug,
        role_slug=role_slug,
        handler_path=handler_path,
        handler_method=handler_method,
        expected_status_code=404,
        expected_response_json={
            'code': 'restriction_not_found',
            'message': (
                f'Restriction is not found in role "{role_slug}"'
                f' in system "{system_slug}"'
            ),
        },
    )

    result = await get_all_restrictions_pg()
    assert before_handle_call == result
