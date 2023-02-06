# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from access_control_plugins import *  # noqa: F403 F401
import pytest

GET_QUERY = """
select
    r.handler_path, r.handler_method, r.restriction
from
    access_control.restrictions r
    join access_control.roles rl
        on r.role_id = rl.id
    join access_control.system s
        on rl.system_id = s.id
where
    s.name = '{}'
    and rl.slug = '{}'
    and r.handler_path = '{}'
    and r.handler_method = '{}'::access_control.http_method_t
"""
GET_ALL_QUERY = """
select
    r.handler_path, r.handler_method, r.restriction
from
    access_control.restrictions r
"""


@pytest.fixture(name='get_restriction_pg')
def _get_restriction_pg(pgsql):
    async def _wrapper(system_slug, role_slug, handler_path, handler_method):
        cursor = pgsql['access_control'].cursor()
        cursor.execute(
            GET_QUERY.format(
                system_slug, role_slug, handler_path, handler_method,
            ),
        )
        result = list(cursor)
        assert len(result) <= 1
        return result[0] if result else None

    return _wrapper


@pytest.fixture(name='get_all_restrictions_pg')
def _get_all_restrictions_pg(pgsql):
    async def _wrapper():
        cursor = pgsql['access_control'].cursor()
        cursor.execute(GET_ALL_QUERY)
        result = list(cursor)
        assert result
        return result

    return _wrapper
