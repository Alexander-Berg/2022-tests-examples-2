import pytest

from tests_access_control.helpers import admin_restrictions


SQL_FILES = ['add_systems.sql', 'add_roles.sql', 'add_restrictions.sql']


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_get_success(taxi_access_control, get_restriction_pg):
    handler_path = '/foo/bar'
    handler_method = 'POST'
    system_slug = 'system_main'
    role_slug = 'system_main_role_1'

    await admin_restrictions.get_restriction(
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
    assert result[0] == handler_path
    assert result[1] == handler_method
    assert result[2] == {}


@pytest.mark.pgsql('access_control', files=SQL_FILES)
@pytest.mark.parametrize(
    ['system_slug', 'role_slug', 'handler_path', 'handler_method'],
    [
        ('system_main', 'system_main_role_1', '/foo/bar', 'GET'),
        ('system_main', 'system_main_role_1', '/foo/bar/1', 'POST'),
        ('system_main', 'system_main_role_100', '/foo/bar', 'POST'),
        ('system_main_000', 'system_main_role_1', '/foo/bar', 'POST'),
    ],
)
async def test_get_not_found(
        taxi_access_control,
        get_restriction_pg,
        system_slug,
        role_slug,
        handler_path,
        handler_method,
):
    result = await get_restriction_pg(
        system_slug, role_slug, handler_path, handler_method,
    )
    assert not result

    await admin_restrictions.get_restriction(
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
