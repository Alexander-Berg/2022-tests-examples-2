from aiohttp import web
import pytest


def _get_client_method(web_app_client, method):
    if method == 'GET':
        return web_app_client.get
    if method == 'POST':
        return web_app_client.post
    return web_app_client.put


async def _make_response(web_app_client, method):
    client_method = _get_client_method(web_app_client, method)
    params = {'name': 'exp_name'}
    if method == 'PUT':
        params.update({'last_modified_at': '10000'})
    return await client_method(
        f'/admin/promotions/experiments/',
        params=params,
        json=None if method == 'GET' else {'data': 'data'},
    )


@pytest.mark.parametrize('method', ['GET', 'POST', 'PUT'])
async def test_ok(web_app_client, mockserver, method):
    @mockserver.handler('/taxi-exp/v1/experiments/')
    def _mock_exp(request):
        if method != 'GET':
            assert request.json == {'data': 'data'}
        data = {'content': 'content'} if method == 'GET' else {}
        return web.json_response(data=data, status=200)

    response = await _make_response(web_app_client, method)
    data = await response.json()
    assert response.status == 200
    if method == 'GET':
        assert data['content'] == 'content'


@pytest.mark.parametrize('method', ['GET', 'POST', 'PUT'])
async def test_exp_error(web_app_client, mockserver, method):
    expected_exp_status = 404 if method == 'GET' else 409

    @mockserver.handler('/taxi-exp/v1/experiments/')
    def _mock_exp(request):
        return web.json_response(
            data={
                'code': 'error_code',
                'message': 'error message',
                'details': 'error details',
            },
            status=expected_exp_status,
        )

    response = await _make_response(web_app_client, method)
    data = await response.json()
    assert response.status == 400
    assert data == {
        'code': 'taxi_exp_request_error',
        'message': 'Ошибка в запросе в сервис экспериментов',
        'details': {
            'reason': (
                'Request to taxi_exp failed: (response_code='
                + str(expected_exp_status)
                + '): '
                '{"code": "error_code", "message": "error message", '
                '"details": "error details"}'
            ),
        },
    }
