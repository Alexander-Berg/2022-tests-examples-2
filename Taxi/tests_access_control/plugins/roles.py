import pytest


@pytest.fixture(name='roles_retrieve_request')
def _roles_retrieve_request(request_post):
    async def _wrapper(body, system):
        return await request_post(
            url='/v1/admin/roles/retrieve/',
            body=body,
            params={'system': system},
        )

    return _wrapper


@pytest.fixture(name='roles_get_request')
def _roles_get_request(request_get):
    async def _wrapper(system, role):
        return await request_get(
            url='/v1/admin/roles/', params={'system': system, 'role': role},
        )

    return _wrapper


@pytest.fixture(name='roles_create_request')
def _roles_create_request(request_post):
    async def _wrapper(system, role, name):
        return await request_post(
            url='/v1/admin/roles/create/',
            body={'slug': role, 'name': name},
            params={'system': system},
        )

    return _wrapper


@pytest.fixture(name='roles_update_request')
def _roles_update_request(request_post):
    async def _wrapper(system, role, new_name):
        body = {}
        if new_name:
            body['name'] = new_name
        return await request_post(
            url='/v1/admin/roles/update/',
            body=body,
            params={'system': system, 'role': role},
        )

    return _wrapper


@pytest.fixture(name='roles_delete_request')
def _roles_delete_request(request_post):
    async def _wrapper(system, role):
        return await request_post(
            url='/v1/admin/roles/delete/',
            body=None,
            params={'system': system, 'role': role},
        )

    return _wrapper
