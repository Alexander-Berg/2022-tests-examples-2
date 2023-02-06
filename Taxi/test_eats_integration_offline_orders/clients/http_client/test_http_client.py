# pylint: disable=redefined-outer-name
import aiohttp
import pytest

from eats_integration_offline_orders.clients import http_client


@pytest.fixture
def test_path():
    return '/test'


@pytest.fixture
def test_url(mockserver, test_path):
    path = test_path[1:]  # cut left /
    return f'{mockserver.base_url}{path}'


@pytest.fixture
def http_handler(mockserver, test_path):
    def _wrapper(*resp_args, **resp_kwargs):
        @mockserver.handler(test_path)
        def _test(*args, **kwargs):
            return mockserver.make_response(*resp_args, **resp_kwargs)

        return _test

    return _wrapper


@pytest.fixture
def http_request(mockserver, web_context, test_url):
    async def _wrapper(**kwargs):
        return await http_client.HttpClient(web_context).request(
            'GET', test_url, **kwargs,
        )

    return _wrapper


@pytest.mark.parametrize('status', [200, 300, 400, 500])
async def test_http_client(http_handler, http_request, status):
    http_handler(status=status)
    resp = await http_request()
    assert resp.status == status


@pytest.mark.parametrize('status', [400, 500])
async def test_http_client_raise_for_status_raise(
        http_handler, http_request, status,
):
    http_handler(status=status)
    with pytest.raises(aiohttp.ClientResponseError) as exc:
        await http_request(raise_for_status=True)
    assert exc.value.status == status


@pytest.mark.parametrize('status', [200, 300])
async def test_http_client_raise_for_status_dont_raise(
        http_handler, http_request, status,
):
    http_handler(status=status)
    response = await http_request(raise_for_status=True)
    assert response.status == status


async def test_http_client_retries(http_handler, http_request):
    handler = http_handler(status=500)
    response = await http_request(retries=3)
    assert handler.times_called == 3
    assert response.status == 500


async def test_http_client_doesnt_retry_400(http_handler, http_request):
    handler = http_handler(status=400)
    response = await http_request(retries=3)
    assert handler.times_called == 1
    assert response.status == 400


async def test_http_client_retries_with_raise_for_status(
        http_handler, http_request,
):
    handler = http_handler(status=500)
    with pytest.raises(aiohttp.ClientResponseError) as exc:
        await http_request(retries=3, raise_for_status=True)
    assert handler.times_called == 3
    assert exc.value.status == 500


async def test_http_client_doesnt_retry_400_with_raise_for_status(
        http_handler, http_request,
):
    handler = http_handler(status=400)
    with pytest.raises(aiohttp.ClientResponseError) as exc:
        await http_request(retries=3, raise_for_status=True)
    assert handler.times_called == 1
    assert exc.value.status == 400


async def test_http_client_with_auth(
        web_context, mockserver, test_path, test_url,
):
    class CertainClient(http_client.HttpClientWithAuth):
        async def auth(self):
            return 'token_value'

    _try = 1

    @mockserver.handler(test_path)
    def _mockserver(request):
        nonlocal _try

        if _try == 1:
            assert 'Authorization' in request.headers
            _try = 2
            return mockserver.make_response(status=401)

        if _try == 2:
            assert 'Authorization' in request.headers
            assert request.headers['Authorization'] == 'token_value'
            return mockserver.make_response(status=200)

        return None

    await CertainClient(web_context).request('GET', test_url, with_auth=True)

    assert _mockserver.times_called == 2
