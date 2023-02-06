import pytest


@pytest.mark.parametrize(
    ['request_body', 'expected_code'],
    [
        pytest.param({'client_id': 'client_id_1'}, 200, id='success_path'),
        pytest.param(
            {'client_id': 'client_id_1', 'edo_operator': 'diadoc'},
            200,
            id='success_path',
        ),
        pytest.param(
            {'client_id': 'client_id_1', 'edo_operator': 'diadoc'},
            200,
            marks=pytest.mark.config(
                CORP_EDO_TESTING_CLIENTS_MAPPING={
                    'enabled': True,
                    'clients': {
                        'client_id_1': {'diadoc': {'inn': '', 'kpp': ''}},
                    },
                },
            ),
            id='client_in_mapping',
        ),
        pytest.param(
            {'client_id': 'client_id_1', 'edo_operator': 'diadoc'},
            400,
            marks=pytest.mark.config(
                CORP_MARKET_USE_EDO_FLOW=True,
                CORP_EDO_TESTING_CLIENTS_MAPPING={
                    'enabled': True,
                    'clients': {},
                },
            ),
            id='client_not_in_mapping',
        ),
        pytest.param(
            {'client_id': 'client_id_2'}, 409, id='contract_already_created',
        ),
    ],
)
async def test_market_offer_create(
        web_app_client,
        db,
        stq,
        mock_corp_clients,
        taxi_config,
        request_body,
        expected_code,
):
    response = await web_app_client.post(
        '/v1/market-offer/create', json=request_body,
    )

    assert response.status == expected_code

    if response.status == 200:
        assert stq.corp_create_market_offer.times_called == 1
        assert stq.corp_create_market_offer.next_call()['kwargs'] == {
            'client_id': request_body['client_id'],
        }

        if request_body.get('edo_operator'):
            assert stq.corp_send_edo_invite.times_called == 1
            assert stq.corp_send_edo_invite.next_call()['kwargs'] == {
                'client_id': request_body['client_id'],
                'operator': request_body['edo_operator'],
                'organization': 'market',
            }

        market_request = await db.corp_additional_client_requests.find_one(
            {'client_id': request_body['client_id']},
            projection={
                '_id': False,
                'task_id': False,
                'created': False,
                'updated': False,
            },
        )
        assert market_request == {
            'client_id': request_body['client_id'],
            'service': 'market',
        }
