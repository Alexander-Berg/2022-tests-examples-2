from aiohttp import web


HEADERS = {
    'X-File-Name': 'filename',
    'X-Arg-Type': 'type',
    'Content-Type': 'application/x-www-form-urlencoded',
}

PARAMS = {'experiment': 'exp_name'}

BODY = 'body'


async def test_ok(web_app_client, mockserver):
    exp_resp = {'id': 'id', 'lines': 10, 'hash': 'hash'}

    @mockserver.handler('/taxi-exp/v1/files/')
    def _mock_exp(request):
        assert request.json == BODY
        return web.json_response(data=exp_resp, status=200)

    response = await web_app_client.post(
        f'/admin/promotions/experiments_files/',
        params=PARAMS,
        headers=HEADERS,
        json=BODY,
    )
    assert response.status == 200
    data = await response.json()
    assert data == exp_resp


async def test_exp_error(web_app_client, mockserver):
    @mockserver.handler('/taxi-exp/v1/files/')
    def _mock_exp(request):
        return web.HTTPInternalServerError()

    response = await web_app_client.post(
        f'/admin/promotions/experiments_files/',
        params=PARAMS,
        headers=HEADERS,
        json=BODY,
    )
    data = await response.json()
    assert response.status == 400
    assert data == {
        'code': 'taxi_exp_remote_error',
        'message': 'Ошибка сервиса экспериментов',
    }
