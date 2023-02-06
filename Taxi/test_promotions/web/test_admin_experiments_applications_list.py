from aiohttp import web


async def test_ok(web_app_client, mockserver):
    exp_resp = {'applications': [{'name': 'name1'}]}

    @mockserver.handler('/taxi-exp/v1/experiments/filters/applications/list/')
    def _mock_exp(request):
        return web.json_response(data=exp_resp, status=200)

    response = await web_app_client.get(
        f'/admin/promotions/experiments_applications/list/',
    )
    assert response.status == 200
    data = await response.json()
    assert data == exp_resp


async def test_exp_error(web_app_client, mockserver):
    @mockserver.handler('/taxi-exp/v1/experiments/filters/applications/list/')
    def _mock_exp(request):
        return web.HTTPInternalServerError()

    response = await web_app_client.get(
        f'/admin/promotions/experiments_applications/list/',
    )
    data = await response.json()
    assert response.status == 400
    assert data == {
        'code': 'taxi_exp_remote_error',
        'message': 'Ошибка сервиса экспериментов',
    }
