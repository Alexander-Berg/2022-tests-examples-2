import pytest


async def test_no_ticket(make_request, mock_remote):
    mock = mock_remote()
    response = await make_request()

    assert response.status_code == 401
    assert response.json()['code'] == '401'
    assert not mock.has_calls


async def test_no_consumer(
        make_request, service_ticket, mock_remote, request_headers,
):
    mock = mock_remote()
    response = await make_request(headers=request_headers(consumer=None))

    assert response.status_code == 401
    assert response.json()['code'] == '401'
    assert not mock.has_calls


async def test_bad_consumer(
        make_request, service_ticket, mock_remote, request_headers,
):
    mock = mock_remote()
    response = await make_request(
        headers=request_headers(consumer='bad-consumer'),
    )

    assert response.status_code == 401
    assert response.json()['code'] == '401'
    assert not mock.has_calls


@pytest.mark.config(
    PRO_GATEWAY_ALLOWED_CONSUMERS={'another-service': ['consumer']},
)
async def test_bad_service(
        make_request, service_ticket, mock_remote, request_headers,
):
    mock = mock_remote()
    response = await make_request(headers=request_headers())

    assert response.status_code == 401
    assert response.json()['code'] == '401'
    assert not mock.has_calls


async def test_happy_path(
        make_request, service_ticket, mock_remote, request_headers,
):
    mock = mock_remote()
    additional_headers = {
        'X-Custom-Header': 'custom',
        'Cookie': 'session',
        'X-Ya-User-Ticket': 'userticket',
    }
    request_body = {'id': 'abc123'}
    params = {'a': 'one', 'b': 'two'}
    response = await make_request(
        request_body=request_body,
        params=params,
        headers=request_headers(additional_headers=additional_headers),
    )

    assert response.status_code == 200
    assert response.json() == {'sentinel': True}
    assert mock.has_calls
    mock_request = mock.next_call()['request']
    assert mock_request.headers['X-Platform-Consumer'] == 'consumer'
    assert mock_request.headers['X-Custom-Header'] == 'custom'
    assert mock_request.headers['X-Ya-User-Ticket'] == 'userticket'
    assert mock_request.cookies == {}
    assert dict(mock_request.query.items()) == params


@pytest.mark.parametrize(
    'method', ['get', 'post', 'put', 'delete', 'patch', 'options'],
)
async def test_methods(
        make_request, service_ticket, mock_remote, request_headers, method,
):
    mock = mock_remote(response_body={})
    response = await make_request(headers=request_headers(), method=method)

    assert response.status_code == 200
    assert mock.has_calls
    mock_request = mock.next_call()['request']
    assert mock_request.method.lower() == method


@pytest.mark.parametrize('code', [201, 301, 401, 501])
async def test_status(
        make_request, service_ticket, mock_remote, request_headers, code,
):
    mock = mock_remote(response_code=code)
    response = await make_request(headers=request_headers())

    assert response.status_code == code
    assert mock.has_calls
