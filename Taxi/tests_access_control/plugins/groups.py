import pytest


@pytest.fixture(name='groups_update_request')
async def _groups_update_request(request_post):
    async def _wrapper(body, params):
        return await request_post(
            url='/v1/admin/groups/update', body=body, params=params,
        )

    return _wrapper


@pytest.fixture(name='groups_delete_request')
async def _groups_delete_request(request_post):
    async def _wrapper(system, group):
        return await request_post(
            url='/v1/admin/groups/delete',
            body={},
            params={'system': system, 'group': group},
        )

    return _wrapper
