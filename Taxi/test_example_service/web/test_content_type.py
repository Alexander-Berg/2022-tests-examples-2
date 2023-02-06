import json

from aiohttp import web
import pytest

from generated.clients import yet_another_service

from . import common


@pytest.mark.parametrize('charset', [None, 'utf-8', 'UTF-8'])
async def test_csv_doubler(web_app_client, charset):
    data = '1,2,3\n4,5,6\n'
    content_type = 'text/csv'
    if charset:
        content_type += f'; charset={charset}'
    resp = await web_app_client.post(
        '/test_content_type/csv_doubler',
        data=data,
        headers={'Content-Type': content_type},
    )
    assert resp.status == 200
    assert await resp.text() == data * 2
    assert resp.headers['Content-Type'] == 'text/csv; charset=utf-8'


async def test_csv_doubler_wrong_content_type(web_app_client):
    data = '1,2,3\n4,5,6\n'
    resp = await web_app_client.post(
        '/test_content_type/csv_doubler',
        data=data,
        headers={'Content-Type': 'text/html'},
    )
    assert resp.status == 400
    assert await resp.json() == common.make_request_error(
        'Invalid Content-Type: text/html; expected one of [\'text/csv\']',
    )


@pytest.mark.parametrize(
    'tst_request, expected_res',
    [pytest.param({'name': 'abacaba'}, {'name': 'abacaba'}, id='default')],
)
async def test_server_json_wrong_content_type(
        tst_request, expected_res, web_app_client,
):
    resp = await web_app_client.post(
        '/echo-json',
        data=json.dumps(tst_request),
        headers={'Content-Type': 'text/html'},
    )
    assert resp.status == 200
    assert await resp.json() == expected_res


async def test_server_invalid_json(web_app_client):
    resp = await web_app_client.post(
        '/echo-json', data='1/1/1', headers={'Content-Type': 'text/html'},
    )
    assert resp.status == 400
    assert await resp.json() == common.make_request_error(
        'Failed to decode json',
    )


async def test_client_json_wrong_content_type(
        web_context, mock_yet_another_service,
):
    @mock_yet_another_service('/get_some')
    async def handler(request):
        return web.Response(
            text=json.dumps({'name': 'abacaba'}),
            headers={'Content-Type': 'text/html'},
        )

    resp = await web_context.clients.yet_another_service.get_some()
    assert resp.status == 200
    assert resp.body.name == 'abacaba'

    assert handler.times_called == 1


async def test_client_invalid_json(web_context, mock_yet_another_service):
    @mock_yet_another_service('/get_some')
    async def handler(request):
        return web.Response(
            text='1/1/1', headers={'Content-Type': 'text/html'},
        )

    with pytest.raises(yet_another_service.ClientException) as exc_info:
        await web_context.clients.yet_another_service.get_some()
    resp = exc_info.value
    assert resp.status == 200
    assert str(resp) == (
        'yet-another-service invalid response: '
        'Failed to decode json, '
        'status: 200, body: b\'1/1/1\''
    )

    assert handler.times_called == 1
