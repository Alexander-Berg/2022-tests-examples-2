import pytest


@pytest.mark.parametrize(
    ['passport_mock', 'status_code'],
    [pytest.param('client1', 200), pytest.param('unknown_client', 401)],
    indirect=['passport_mock'],
)
async def test_client_get_client_request_draft(
        passport_mock, status_code, taxi_corp_real_auth_client, mockserver,
):
    @mockserver.json_handler('/corp-requests/v1/client-request-draft')
    def _get(request):
        assert request.method == 'GET'
        return mockserver.make_response(json={'some': 'response'}, status=200)

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/{}/client-request-draft'.format(passport_mock),
    )
    assert response.status == status_code


@pytest.mark.parametrize(
    ['passport_mock', 'status_code'],
    [pytest.param('client1', 200), pytest.param('unknown_client', 401)],
    indirect=['passport_mock'],
)
async def test_client_put_client_request_draft(
        passport_mock, taxi_corp_real_auth_client, status_code, mockserver,
):
    @mockserver.json_handler('/corp-requests/v1/client-request-draft')
    def _put(request):
        assert request.method == 'PUT'
        return mockserver.make_response(json={}, status=200)

    response = await taxi_corp_real_auth_client.put(
        '/1.0/client/{}/client-request-draft'.format(passport_mock),
        json={'some': 'data'},
    )
    assert response.status == status_code


@pytest.mark.parametrize(
    ['passport_mock', 'status_code'],
    [pytest.param('client1', 200), pytest.param('unknown_client', 401)],
    indirect=['passport_mock'],
)
async def test_validate_client_request_draft(
        passport_mock, taxi_corp_real_auth_client, status_code, mockserver,
):
    @mockserver.json_handler('/corp-requests/v1/client-request-draft/validate')
    def _put(request):
        assert request.method == 'PUT'
        return mockserver.make_response(json={}, status=200)

    response = await taxi_corp_real_auth_client.put(
        f'/1.0/client/{passport_mock}/client-request-draft/validate',
    )
    assert response.status == status_code


@pytest.mark.parametrize(
    ['passport_mock', 'params', 'status_code'],
    [
        pytest.param(
            'client1', {'tax_system': 'USN', 'opf': 'INDIVIDUAL'}, 200,
        ),
        pytest.param('unknown_client', {}, 401),
    ],
    indirect=['passport_mock'],
)
async def test_commit_client_request_draft(
        passport_mock,
        status_code,
        params,
        taxi_corp_real_auth_client,
        mockserver,
):
    @mockserver.json_handler('/corp-requests/v1/client-request-draft/commit')
    def _commit(request):
        assert request.method == 'POST'
        return mockserver.make_response(json={}, status=200)

    response = await taxi_corp_real_auth_client.post(
        f'/1.0/client/{passport_mock}/client-request-draft/commit',
        params=params,
    )
    assert response.status == status_code


@pytest.mark.parametrize(
    ['passport_mock', 'params', 'status_code'],
    [pytest.param('client1', {'tax_system': 'USN', 'opf': 'INDIVIDUAL'}, 400)],
    indirect=['passport_mock'],
)
async def test_commit_client_request_draft_400(
        passport_mock,
        status_code,
        params,
        taxi_corp_real_auth_client,
        mockserver,
):
    @mockserver.json_handler('/corp-requests/v1/client-request-draft/commit')
    def _commit(request):
        return mockserver.make_response(json={'field': 'error'}, status=400)

    response = await taxi_corp_real_auth_client.post(
        f'/1.0/client/{passport_mock}/client-request-draft/commit',
        params=params,
    )
    assert response.status == status_code
    assert await response.json() == {'field': 'error'}
