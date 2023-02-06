import pytest


@pytest.mark.parametrize(
    ['passport_mock', 'expected_code', 'expected_response'],
    [
        pytest.param(
            'client1',
            200,
            {},
            marks=pytest.mark.config(
                CORP_EDO_TESTING_CLIENTS_MAPPING={
                    'clients': {'client1': {'diadoc': {'inn': '', 'kpp': ''}}},
                    'enabled': True,
                },
            ),
        ),
        pytest.param(
            'client1',
            400,
            {
                'code': 'CLIENT_NOT_IN_MAPPING',
                'errors': [
                    {
                        'code': 'CLIENT_NOT_IN_MAPPING',
                        'text': (
                            'add client to '
                            'CORP_EDO_TESTING_CLIENTS_MAPPING config'
                        ),
                    },
                ],
                'message': (
                    'add client to CORP_EDO_TESTING_CLIENTS_MAPPING config'
                ),
            },
            marks=pytest.mark.config(
                CORP_EDO_TESTING_CLIENTS_MAPPING={
                    'clients': {},
                    'enabled': True,
                },
            ),
        ),
    ],
    indirect=['passport_mock'],
)
async def test_send_edo_invites(
        patch,
        taxi_corp_real_auth_client,
        mockserver,
        passport_mock,
        expected_code,
        expected_response,
):
    @patch('taxi.stq.client.put')
    async def _put_stq_task(*args, **kwargs):
        pass

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/edo-invites/send',
        json={'organization': 'market', 'operator': 'diadoc'},
    )
    response_json = await response.json()
    assert response.status == expected_code, response_json
    assert response_json == expected_response

    if response.status == 200:
        stq_calls = _put_stq_task.calls
        assert len(stq_calls) == 1
        assert stq_calls[0]['kwargs']['kwargs'] == {
            'client_id': 'client1',
            'operator': 'diadoc',
            'organization': 'market',
        }


@pytest.mark.parametrize(
    ['passport_mock'], [pytest.param('client1')], indirect=['passport_mock'],
)
async def test_find_edo_invites(
        taxi_corp_real_auth_client, passport_mock, mockserver,
):
    @mockserver.json_handler('/corp-edo/v1/invitations')
    def _find_invites(request):
        return mockserver.make_response(json={'invitations': []}, status=200)

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/edo-invites/find',
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {'invitations': []}


@pytest.mark.parametrize(
    ['passport_mock'], [pytest.param('client1')], indirect=['passport_mock'],
)
async def test_resend_edo_invite(
        taxi_corp_real_auth_client, passport_mock, mockserver,
):
    @mockserver.json_handler('/corp-edo/v1/invitations/reinvite')
    def _resend_invites(request):
        return mockserver.make_response(json={}, status=200)

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/edo-invites/resend',
        json={'organization': 'market', 'operator': 'diadoc'},
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}
