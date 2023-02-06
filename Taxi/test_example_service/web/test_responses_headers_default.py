from aiohttp import web
import pytest


@pytest.mark.parametrize(
    'params, primitive, array',
    [
        ({}, '789', '1,2,3'),
        ({'primitive': '100'}, '100', '1,2,3'),
        ({'array': '9,8,7'}, '789', '7,8,9'),
    ],
)
async def test_server(web_app_client, params, primitive, array):
    response = await web_app_client.get(
        '/openapi/response-headers-with-default', params=params,
    )
    assert response.status == 200
    assert response.headers['X-Primitive'] == primitive
    assert response.headers['X-Array'] == array


@pytest.mark.parametrize(
    'headers, primitive, array',
    [
        ({}, 789, [1, 2, 3]),
        ({'x-primitive': '100'}, 100, [1, 2, 3]),
        ({'x-array': '7,8,9'}, 789, [7, 8, 9]),
    ],
)
async def test_client(
        web_context, mock_yet_another_service, headers, primitive, array,
):
    client = web_context.clients.yet_another_service

    @mock_yet_another_service('/openapi/response-headers-with-default')
    async def handler(request):
        return web.Response(headers=headers)

    response = await client.openapi_response_headers_with_default_get()

    assert response.status == 200
    assert response.headers.x_primitive == primitive
    assert response.headers.x_array == array
    assert handler.times_called == 1
