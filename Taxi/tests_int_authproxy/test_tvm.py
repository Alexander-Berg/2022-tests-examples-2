import pytest

import utils


@pytest.mark.routing_rules(utils.AM_RULES_SIMPLE)
@pytest.mark.config(INT_AUTHPROXY_ROUTE_RULES=utils.RULES_SIMPLE)
async def test_no_ticket(request_post):
    response = await request_post()

    assert response.status_code == 401
    assert response.json()['code'] == '401'


@pytest.mark.routing_rules(utils.AM_RULES_SIMPLE)
@pytest.mark.config(
    INT_AUTHPROXY_ROUTE_RULES=utils.RULES_SIMPLE, TVM_ENABLED=False,
)
async def test_tvm_disabled(request_post, mock_remote):
    mock = mock_remote()
    response = await request_post()

    assert response.status_code == 200
    assert response.json() == {'sentinel': True}

    assert mock.has_calls
    mock_request = mock.next_call()['request']
    assert mock_request.headers['X-YaTaxi-External-Service-Name'] == 'unknown'


@pytest.mark.routing_rules(utils.AM_RULES_SIMPLE)
@pytest.mark.config(INT_AUTHPROXY_ROUTE_RULES=utils.RULES_SIMPLE)
async def test_happy_path(
        request_post, service_ticket, mock_remote, auth_headers,
):
    mock = mock_remote()
    response = await request_post(headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {'sentinel': True}

    assert mock.has_calls
    mock_request = mock.next_call()['request']
    assert mock_request.headers['X-YaTaxi-External-Service-Name'] == 'mock'


@pytest.mark.routing_rules(utils.AM_RULES_REWRITE)
@pytest.mark.config(INT_AUTHPROXY_ROUTE_RULES=utils.RULES_REWRITE)
async def test_strict_rewrite_no_query(
        request_post, service_ticket, mock_remote, auth_headers,
):
    mock = mock_remote('tost')

    response = await request_post('/test', headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {'sentinel': True}

    assert mock.has_calls


@pytest.mark.routing_rules(utils.AM_RULES_REWRITE)
@pytest.mark.config(INT_AUTHPROXY_ROUTE_RULES=utils.RULES_REWRITE)
async def test_strict_rewrite_query(
        request_post, service_ticket, mock_remote, auth_headers,
):
    mock = mock_remote('tost')

    response = await request_post(
        '/test', params={'a': 'b'}, headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == {'sentinel': True}

    assert mock.has_calls
    mock_args = mock.next_call()
    assert mock_args['request'].args == {'a': 'b'}


@pytest.mark.routing_rules(utils.AM_RULES_REWRITE)
@pytest.mark.config(INT_AUTHPROXY_ROUTE_RULES=utils.RULES_REWRITE)
async def test_strict_rewrite_suffix(
        request_post, service_ticket, mock_remote, auth_headers,
):
    response = await request_post('/test/123', headers=auth_headers)

    assert response.status_code == 401
    assert response.json()['code'] == 'BAD_URL'


@pytest.mark.routing_rules(utils.AM_RULES_SIMPLE)
@pytest.mark.config(INT_AUTHPROXY_ROUTE_RULES=utils.RULES_SIMPLE)
async def test_proxy_passport_headers(
        request_post, service_ticket, mock_remote, auth_headers,
):
    passport_headers = {
        'X-Yandex-Uid': 'some_uid',
        'X-Yataxi-Pass-Flags': 'portal',
    }
    mock = mock_remote()

    response = await request_post(headers={**auth_headers, **passport_headers})

    assert response.status_code == 200

    assert mock.has_calls
    mock_args = mock.next_call()
    for header, value in passport_headers.items():
        assert header in mock_args['request'].headers
        assert mock_args['request'].headers[header] == value
