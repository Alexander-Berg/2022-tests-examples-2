import pytest


@pytest.mark.parametrize(
    'uid, corp_managers_response, expected_response, expected_status',
    [
        (
            'client1_uid',
            {'client_id': 'client1', 'role': 'client', 'permissions': []},
            {'corp_client_id': 'client1'},
            200,
        ),
        (
            'department_secretary1_uid',
            {'code': '', 'message': ''},
            {'code': 'NOT_FOUND', 'message': 'Yandex UID not found'},
            404,
        ),
    ],
)
async def test_authproxy(
        web_app_client,
        mockserver,
        uid,
        corp_managers_response,
        expected_response,
        expected_status,
):
    @mockserver.json_handler('/corp-managers/v1/managers/access-data')
    async def _mock_access_data(request):
        return mockserver.make_response(
            json=corp_managers_response, status=expected_status,
        )

    response = await web_app_client.post(
        '/v1/authproxy/corp_client_id', json={'uid': uid},
    )

    data = await response.json()

    assert response.status == expected_status, data
    assert data == expected_response
