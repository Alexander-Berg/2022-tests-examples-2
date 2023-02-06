import pytest


@pytest.fixture(name='make_request')
def _make_request(taxi_access_control):
    async def _wrapper(url, method, body=None, params=None):
        handler = getattr(taxi_access_control, method.lower())
        response = await handler(
            url,
            params=params,
            json=body,
            headers={'X-Yandex-Login': 'userx', 'X-Yandex-Uid': '100'},
        )
        return response

    return _wrapper


@pytest.fixture(name='request_get')
async def _request_get(make_request):
    async def _wrapper(url, params):
        return await make_request(url, 'GET', params=params)

    return _wrapper


@pytest.fixture(name='request_post')
async def _request_post(make_request):
    async def _wrapper(url, body, params=None):
        return await make_request(url, 'POST', body=body, params=params)

    return _wrapper


@pytest.fixture(name='request_put')
async def _request_put(make_request):
    async def _wrapper(url, body, params=None):
        return await make_request(url, 'PUT', body=body, params=params)

    return _wrapper


@pytest.fixture(name='assert_status_code')
def _assert_status_code():
    def _wrapper(response, expected_status_code):
        response_body = response.json()
        assert response.status_code == expected_status_code, (
            response.status_code,
            expected_status_code,
            response_body,
        )
        return response_body

    return _wrapper


@pytest.fixture(name='response_body_format')
def _response_body_format():
    def _wrapper(response_body, expected_status_code):
        assert expected_status_code
        return response_body

    return _wrapper


@pytest.fixture(name='assert_response')
def _assert_response(assert_status_code, response_body_format):
    def _wrapper(response, expected_status_code, expected_body):
        response_body = assert_status_code(response, expected_status_code)
        response_body = response_body_format(
            response_body, expected_status_code,
        )
        assert expected_body == response_body, (expected_body, response_body)
        if response.status_code >= 400:
            assert 'code' in expected_body
            assert (
                response.headers['X-YaTaxi-Error-Code']
                == expected_body['code']
            )
        return response_body

    return _wrapper
