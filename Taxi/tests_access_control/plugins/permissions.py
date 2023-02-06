import pytest


@pytest.fixture(name='permissions_retrieve_request')
async def _permissions_retrieve_request(request_post):
    async def _wrapper(body, system):
        return await request_post(
            url='/v1/admin/permissions/retrieve/',
            body=body,
            params={'system': system},
        )

    return _wrapper


@pytest.fixture(name='permissions_get_request')
async def _permissions_get_request(request_get):
    async def _wrapper(system, permission):
        return await request_get(
            url='/v1/admin/permissions/',
            params={'system': system, 'permission': permission},
        )

    return _wrapper


@pytest.fixture(name='permissions_create_request')
async def _permissions_create_request(request_post):
    async def _wrapper(system, permission, role_slug=None):
        body = {'slug': permission}
        if role_slug:
            body['role_slug'] = role_slug
        return await request_post(
            url='/v1/admin/permissions/create/',
            body=body,
            params={'system': system},
        )

    return _wrapper


@pytest.fixture(name='permissions_delete_request')
async def _permissions_delete_request(request_post):
    async def _wrapper(system, permission):
        return await request_post(
            url='/v1/admin/permissions/delete/',
            body=None,
            params={'system': system, 'permission': permission},
        )

    return _wrapper


@pytest.fixture(name='permissions_roles_attach_request')
async def _permissions_roles_attach_request(request_post):
    async def _wrapper(system, links):
        body_links = [
            {'permission_slug': permission_slug, 'role_slug': role_slug}
            for role_slug, permission_slug in links
        ]
        return await request_post(
            url='/v1/admin/permissions/roles/attach/',
            body={'links': body_links},
            params={'system': system},
        )

    return _wrapper


@pytest.fixture(name='permissions_roles_detach_request')
async def _permissions_roles_detach_request(request_post):
    async def _wrapper(system, links):
        body_links = [
            {'permission_slug': permission_slug, 'role_slug': role_slug}
            for role_slug, permission_slug in links
        ]
        return await request_post(
            url='/v1/admin/permissions/roles/detach/',
            body={'links': body_links},
            params={'system': system},
        )

    return _wrapper


@pytest.fixture(name='permission_role_links_pg')
def _permission_role_links_pg(pgsql):
    async def _wrapper():
        cursor = pgsql['access_control'].cursor()
        cursor.execute(
            """select r.slug, p.name
            from access_control.m2m_permissions_roles mpr
            left join access_control.roles r on mpr.role_id = r.id
            left join access_control.permissions p on mpr.permission_id = p.id
            order by r.slug, p.name, mpr.id""",
        )
        return list(cursor)

    return _wrapper


@pytest.fixture(name='assert_permission_role_links_pg')
def _assert_permission_role_links_pg(permission_role_links_pg):
    async def _wrapper(expected_links):
        links = await permission_role_links_pg()
        assert links == expected_links

    return _wrapper
