from aiohttp import web
import pytest

from . import common


@pytest.fixture(name='client')
def yas_fixture(web_context):
    return web_context.clients.yet_another_service


@pytest.mark.parametrize(
    'query, response_json, header',
    [
        (
            {'is-nuclear': 'False'},
            {'is-nuclear': False, 'is-wild': False},
            'false',
        ),
        (
            {'is-nuclear': 'True'},
            {'is-nuclear': True, 'is-wild': False},
            'false',
        ),
        (
            {'is-nuclear': 'True', 'is-wild': 'True'},
            {'is-nuclear': True, 'is-wild': True},
            'true',
        ),
        ({}, {'is-wild': False}, 'false'),
    ],
)
async def test_server_happy_path(web_app_client, query, response_json, header):
    response = await web_app_client.post('/blow-up-the-world', params=query)
    assert response.status == 200
    assert await response.json() == response_json
    assert response.headers['AmI'] == header


async def test_server_error(web_app_client):
    response = await web_app_client.post(
        '/blow-up-the-world', params={'is-nuclear': '1'},
    )
    assert response.status == 400
    assert await response.json() == common.make_request_error(
        'Invalid value for is-nuclear: \'1\' is not instance of bool',
    )


async def test_client_happy_path(client, mock_yet_another_service):
    @mock_yet_another_service('/blow-up-the-world')
    async def handler(request):
        assert request.query.get('im-nuclear') == 'false'
        assert request.query.get('im-wild') is None
        assert request.query.get('im-breaking-up-inside') == 'true'
        assert request.headers['heart-of-broken-glass'] == 'false'
        assert request.headers['defiled'] == 'true'
        return web.Response(
            headers={'DeepInside': 'false', 'AbandonedChild': 'True'},
        )

    response = await client.blow_up_the_world_post(
        im_nuclear=False,
        im_breaking_up_inside=True,
        heart_of_broken_glass=False,
        defiled=True,
    )

    assert response.status == 200
    assert response.headers.deep_inside is False
    assert response.headers.abandoned_child is True
    assert handler.times_called == 1


async def test_server_array(web_app_client):
    response = await web_app_client.get(
        '/array-headers', headers={'input': 'true,True,False,false'},
    )
    assert response.status == 200
    assert (
        response.headers['output'].split(',') == ['true'] * 3 + ['false'] * 3
    )


async def test_client_array(client, mock_yet_another_service):
    @mock_yet_another_service('/array-headers')
    async def handler(request):
        assert request.headers['input'] == 'true,false'
        return web.Response(headers={'output': 'false,True'})

    response = await client.array_headers_get(input=[True, False])

    assert response.status == 200
    assert response.headers.output == [False, True]

    assert handler.times_called == 1
