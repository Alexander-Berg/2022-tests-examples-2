from unittest import mock


async def make_post_request(client, relative_url, data=None, params=None):
    return await client.post(
        relative_url,
        json=data,
        params=params,
        headers={'X-Yandex-Login': 'superuser'},
    )


async def make_get_request(client, relative_url, params=None):
    return await client.get(
        relative_url, params=params, headers={'X-Yandex-Login': 'superuser'},
    )


async def post_ok_json_response(relative_url, data, client):
    response = await make_post_request(client, relative_url, data=data)
    assert response.status == 200, 'Response: {}'.format(await response.text())
    return await response.json()


def has_permissions(permissions):
    permissions = set(permissions)

    async def authorize_request_mock(
            request, mongodb, should_have_permissions,
    ):
        return set(should_have_permissions) & permissions

    return mock.patch(
        'taxi.util.permissions.authorize_request_db', authorize_request_mock,
    )
