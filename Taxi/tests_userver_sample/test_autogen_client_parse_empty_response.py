import pytest


@pytest.mark.parametrize(
    'ret_code, ret_throw', [(200, False), (403, False), (403, True)],
)
async def test_swagger_2_0(
        taxi_userver_sample, mockserver, ret_code, ret_throw,
):
    url = 'autogen/client-parse-empty-response/swagger-2-0'

    @mockserver.handler(f'/userver-sample/{url}')
    def _handler(request):
        return mockserver.make_response()

    params = {'ret-code': ret_code, 'ret-throw': ret_throw}
    response = await taxi_userver_sample.get(url, params=params)
    assert response.status_code == ret_code
    assert response.json() == {}
    assert _handler.times_called == 1


@pytest.mark.parametrize(
    'ret_code, ret_throw', [(200, False), (403, False), (403, True)],
)
async def test_openapi_3_0(
        taxi_userver_sample, mockserver, ret_code, ret_throw,
):
    url = 'autogen/client-parse-empty-response/openapi-3-0'

    @mockserver.handler(f'/userver-sample/{url}')
    def _handler(request):
        return mockserver.make_response()

    params = {'ret-code': ret_code, 'ret-throw': ret_throw}
    response = await taxi_userver_sample.get(url, params=params)
    assert response.status_code == ret_code
    assert response.text == ''
    assert _handler.times_called == 1
