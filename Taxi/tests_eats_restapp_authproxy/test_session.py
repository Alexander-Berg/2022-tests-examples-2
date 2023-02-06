import json


async def request_proxy(taxi_eats_authproxy, token, url):
    await taxi_eats_authproxy.invalidate_caches()

    headers = {}
    if token is not None:
        headers['X-Token'] = token
    extra = {'headers': headers}
    return await taxi_eats_authproxy.post(url, data=json.dumps({}), **extra)


async def test_auth_with_token(
        taxi_eats_restapp_authproxy,
        mockserver,
        mock_eats_restapp_authorizer,
        mock_return_partner_info_200,
):
    @mockserver.json_handler('auth')
    def _mock_backend(request):
        assert request.headers['X-YaEda-PartnerId'] == '41'
        return mockserver.make_response(status=200, json={'status': 'success'})

    response = await request_proxy(
        taxi_eats_restapp_authproxy, token='token', url='auth',
    )
    assert response.status_code == 200


async def test_auth_wrong_token(
        taxi_eats_restapp_authproxy, mockserver, mock_eats_restapp_authorizer,
):
    @mockserver.json_handler('auth')
    def _mock_backend(request):
        return mockserver.make_response(status=200, json={'status': 'success'})

    response = await request_proxy(
        taxi_eats_restapp_authproxy, token='wrong_token', url='auth',
    )
    assert response.status_code == 401


async def test_auth_without_token(
        taxi_eats_restapp_authproxy, mockserver, mock_eats_restapp_authorizer,
):
    @mockserver.json_handler('auth')
    def _mock_backend(request):
        return mockserver.make_response(status=200, json={'status': 'success'})

    response = await request_proxy(
        taxi_eats_restapp_authproxy, token=None, url='auth',
    )
    assert response.status_code == 401


async def test_noauth_without_token(
        taxi_eats_restapp_authproxy, mockserver, mock_eats_restapp_authorizer,
):
    @mockserver.json_handler('noauth')
    def _mock_backend(request):
        return mockserver.make_response(status=200, json={'status': 'success'})

    response = await request_proxy(
        taxi_eats_restapp_authproxy, token=None, url='noauth',
    )
    assert response.status_code == 200


async def test_error_authorizer(
        taxi_eats_restapp_authproxy, mockserver, mock_error_restapp_authorizer,
):
    @mockserver.json_handler('auth')
    def _mock_backend(request):
        return mockserver.make_response(status=200, json={'status': 'success'})

    response = await request_proxy(
        taxi_eats_restapp_authproxy, token='token', url='auth',
    )
    assert response.status_code == 500


async def test_without_trim_prefix(
        taxi_eats_restapp_authproxy, mockserver, mock_error_restapp_authorizer,
):
    @mockserver.json_handler('/4.0/restapp-front/some-path/noauth')
    def _mock_backend(request):
        return mockserver.make_response(status=200, json={'status': 'success'})

    response = await request_proxy(
        taxi_eats_restapp_authproxy,
        token=None,
        url='/4.0/restapp-front/some-path/noauth',
    )
    assert response.status_code == 200


async def test_proxy_401_should_still_authorize(
        taxi_eats_restapp_authproxy,
        mockserver,
        mock_eats_restapp_authorizer,
        mock_return_partner_info_200,
):
    @mockserver.json_handler('/4.0/restapp-front/test-proxy-401')
    def _mock_backend(request):
        assert request.headers.get('X-YaEda-PartnerId') == '41'
        return mockserver.make_response(status=200, json={'status': 'success'})

    response = await request_proxy(
        taxi_eats_restapp_authproxy,
        token='token',
        url='/4.0/restapp-front/test-proxy-401',
    )
    assert response.status_code == 200
