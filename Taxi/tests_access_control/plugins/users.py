import pytest


@pytest.fixture(name='group_users_retrieve_request')
async def _group_users_retrieve_request(request_post):
    async def _wrapper(body, system, group=None):
        params = {'system': system}
        if group:
            params['group'] = group
        return await request_post(
            url='/v1/admin/groups/users/retrieve/', body=body, params=params,
        )

    return _wrapper


@pytest.fixture(name='delete_bulk_users')
async def _delete_bulk_users(request_post):
    async def _wrapper(users):
        return await request_post(
            url='/v1/admin/users/bulk-delete/',
            body={'users': users},
            params=None,
        )

    return _wrapper


@pytest.fixture(name='detach_bulk_groups_users')
async def _detach_bulk_groups_users(request_post):
    async def _wrapper(system, users):
        return await request_post(
            url='/v1/admin/groups/users/bulk-detach/',
            body={'users': users},
            params={'system': system},
        )

    return _wrapper


@pytest.fixture(name='full_users_detach')
async def _full_users_detach(request_post):
    async def _wrapper(system, groups):
        return await request_post(
            url='/v1/admin/groups/users/full-detach/',
            body={'groups': groups},
            params={'system': system},
        )

    return _wrapper


@pytest.fixture(name='get_users_pg')
def _get_users_pg(pgsql):
    async def _wrapper():
        cursor = pgsql['access_control'].cursor()
        cursor.execute(
            """select provider, provider_user_id
            from access_control.users
            order by provider, provider_user_id""",
        )
        return list(cursor)

    return _wrapper


@pytest.fixture(name='assert_users_pg')
def _assert_users_pg(get_users_pg):
    async def _wrapper(expected_users):
        users = await get_users_pg()
        assert users == expected_users

    return _wrapper


@pytest.fixture(name='get_user_group_links_pg')
def _get_user_group_links_pg(pgsql):
    async def _wrapper():
        cursor = pgsql['access_control'].cursor()
        cursor.execute(
            """select group_id, user_id
            from access_control.m2m_groups_users
            order by id""",
        )
        return list(cursor)

    return _wrapper


@pytest.fixture(name='assert_user_group_links_pg')
def _assert_user_group_links_pg(get_user_group_links_pg):
    async def _wrapper(expected_links):
        links = await get_user_group_links_pg()
        assert links == expected_links

    return _wrapper
