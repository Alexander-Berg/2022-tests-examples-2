import pytest


@pytest.mark.parametrize(
    'url',
    [
        'inplace/swagger-2-0',
        'strong-typedef/swagger-2-0',
        'def-strong-typedef/swagger-2-0',
    ],
)
async def test_swagger_2_0(taxi_userver_sample, mockserver, url):
    @mockserver.json_handler(f'/userver-sample/autogen/client-default/{url}')
    def _handler(request):
        assert 'param-header' not in request.headers
        assert 'param-query' not in request.args
        assert 'param-a' not in request.json
        return {}

    response = await taxi_userver_sample.post(f'autogen/client-default/{url}')
    assert response.status_code == 200
    assert response.json() == {
        'param-header': 41,
        'param-query': 42,
        'param-body-a': 43,
    }
    assert _handler.times_called == 1
