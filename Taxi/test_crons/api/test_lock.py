import datetime

import pytest


NOW = datetime.datetime(2019, 4, 1, 1, 00, 00)


async def test_aquire(web_app_client):
    response = await web_app_client.post(
        '/v1/task/test/lock/aquire/',
        json={
            'owner': '123',
            'key': 'test',
            'now': '2019-04-01T00:00:00.0Z',
            'till': '2019-04-01T02:00:00.0Z',
        },
    )
    assert response.status == 200


@pytest.mark.now(NOW.isoformat())
async def test_aquire_twice(web_app_client):
    response = await web_app_client.post(
        '/v1/task/test/lock/aquire/',
        json={
            'owner': '123',
            'key': 'test',
            'now': '2019-04-01T00:00:00.0Z',
            'till': '2019-04-01T02:00:00.0Z',
        },
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v1/task/test/lock/aquire/',
        json={
            'owner': '123',
            'key': 'test',
            'now': '2019-04-01T00:00:00.0Z',
            'till': '2019-04-01T02:00:00.0Z',
        },
    )
    assert response.status == 200


async def test_prolong(web_app_client):
    response = await web_app_client.post(
        '/v1/task/test/lock/prolong/',
        json={'owner': '123', 'key': 'test', 'till': '2019-04-01T03:00:00.0Z'},
    )
    assert response.status == 404

    await web_app_client.post(
        '/v1/task/test/lock/aquire/',
        json={
            'owner': '123',
            'key': 'test',
            'now': '2019-04-01T00:00:00.0Z',
            'till': '2019-04-01T02:00:00.0Z',
        },
    )

    response = await web_app_client.post(
        '/v1/task/test/lock/prolong/',
        json={'owner': '123', 'key': 'test', 'till': '2019-04-01T03:00:00.0Z'},
    )
    assert response.status == 200


async def test_release(web_app_client):
    response = await web_app_client.post(
        '/v1/task/test/lock/release/', json={'owner': '123', 'key': 'test'},
    )
    assert response.status == 404

    await web_app_client.post(
        '/v1/task/test/lock/aquire/',
        json={
            'owner': '123',
            'key': 'test',
            'now': '2019-04-01T00:00:00.0Z',
            'till': '2019-04-01T02:00:00.0Z',
        },
    )

    response = await web_app_client.post(
        '/v1/task/test/lock/release/', json={'owner': '123', 'key': 'test'},
    )
    assert response.status == 200


@pytest.mark.now(NOW.isoformat())
async def test_is_acquired(web_app_client):
    response = await web_app_client.post(
        '/v1/task/test/lock/aquire/',
        json={
            'owner': '123',
            'key': 'test',
            'now': '2019-04-01T00:00:00.0Z',
            'till': '2019-04-01T02:00:00.0Z',
        },
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/locks/v2/is-acquired/', json={'key': 'test'},
    )
    assert response.status == 200
    assert (await response.json()) == {'is_acquired': True}
