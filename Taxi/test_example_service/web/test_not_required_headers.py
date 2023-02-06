from aiohttp import web
import pytest

import generated.clients.yet_another_service as yas

from . import common


@pytest.mark.parametrize(
    'req_params,status,header_a,header_b,resp_body',
    [
        ({'send-a': 'true'}, 200, 'a', None, None),
        ({'send-a': 'true', 'send-b': 'true'}, 200, 'a', 'b', None),
        (
            {'send-b': 'true'},
            500,
            None,
            None,
            common.make_response_error('Header X-A is missing'),
        ),
    ],
)
async def test_server_get(
        web_app_client, req_params, status, header_a, header_b, resp_body,
):
    response = await web_app_client.get('/required-headers', params=req_params)
    assert response.status == status
    if status != 200:
        assert await response.json() == resp_body
        return
    if header_a:
        assert response.headers['X-A'] == header_a
    else:
        assert 'X-A' not in response.headers

    if header_b:
        assert response.headers['X-B'] == header_b
    else:
        assert 'X-B' not in response.headers


@pytest.mark.parametrize(
    'send_a,send_b,error,error_args,header_a,header_b',
    [
        (True, True, None, None, 'a', 'b'),
        (True, False, None, None, 'a', None),
        (
            False,
            False,
            yas.RequiredHeadersGetInvalidResponse,
            None,
            None,
            None,
        ),
    ],
)
async def test_client_get(
        web_context,
        mock_yet_another_service,
        send_a,
        send_b,
        error,
        error_args,
        header_a,
        header_b,
):
    client = web_context.clients.yet_another_service

    @mock_yet_another_service('/required-headers')
    async def handler(request):
        headers = {}
        if request.query.get('send-a') == 'true':
            headers['X-A'] = 'a'
        if request.query.get('send-b') == 'true':
            headers['X-B'] = 'b'
        return web.Response(headers=headers)

    if error:
        with pytest.raises(error) as exc_info:
            await client.required_headers_get(send_a=send_a, send_b=send_b)
        assert exc_info.value.args == (200, b'')
    else:
        resp = await client.required_headers_get(send_a=send_a, send_b=send_b)
        assert resp.status == 200
        assert resp.headers.x_a == header_a
        assert resp.headers.x_b == header_b

    assert handler.times_called == 1
