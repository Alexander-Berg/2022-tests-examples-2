import pytest


@pytest.mark.parametrize('method', ['GET', 'POST'])
@pytest.mark.parametrize('url', ['/fns-se/intro', '/fns-se/v2/agreement'])
@pytest.mark.parametrize(
    'token,expect_code', [('', 400), ('bad_token', 401), ('good_token', 200)],
)
async def test_fns_se(
        taxi_selfreg, mockserver, method, url, token, expect_code,
):

    request_body = {'foo': 'bar'} if method == 'POST' else None
    expect_response = {'bar': 'baz'}

    @mockserver.json_handler(f'/selfemployed-api/self-employment{url}')
    def _selfemployed(request):
        assert request.query['selfreg_id'] == '5a7581722016667706734a33'
        assert request.method == method
        if method == 'POST':
            assert request.json == request_body
        else:
            assert not request.get_data()
        return expect_response

    response = await taxi_selfreg.request(
        method, f'/selfreg{url}', params={'token': token}, json=request_body,
    )

    assert response.status == expect_code
    if expect_code == 200:
        response_body = await response.json()
        assert response_body == expect_response


@pytest.mark.parametrize('method', ['GET', 'POST'])
@pytest.mark.parametrize('url', ['/fns-se/intro', '/fns-se/v2/agreement'])
@pytest.mark.parametrize('error_code', [400, 401, 409, 500])
async def test_fns_se_proxy_errors(
        taxi_selfreg, mockserver, method, url, error_code,
):
    @mockserver.json_handler(f'/selfemployed-api/self-employment{url}')
    def _selfemployed(request):
        return mockserver.make_response(json={}, status=error_code)

    response = await taxi_selfreg.request(
        method,
        f'/selfreg{url}',
        params={'token': 'good_token'},
        json={} if method == 'POST' else None,
    )

    assert response.status == error_code
