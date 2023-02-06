import datetime

import pytest


@pytest.mark.parametrize(
    [
        'client_id',
        'request_update_doc',
        'corp_clients_response',
        'expected_response',
    ],
    [
        pytest.param(
            'client_id_1',
            None,
            {},
            {'status': 'EMPTY'},
            id='not-found-market-request',
        ),
        pytest.param(
            'market_client_id',
            {
                'last_error': {
                    'datetime': datetime.datetime.utcnow(),
                    'error': 'error.customer_linking_error',
                    'error_reason': '',
                },
            },
            {},
            {
                'message': 'Ошибка при создании плательщика в биллинге',
                'status': 'ERROR',
                'code': 'error.customer_linking_error',
            },
            id='failed-market-request',
        ),
        pytest.param(
            'market_client_id',
            None,
            {'contracts': []},
            {'status': 'PENDING'},
            id='pending-market-request',
        ),
        pytest.param(
            'market_client_id',
            None,
            {
                'contracts': [
                    {
                        'contract_id': 15384971,
                        'external_id': '3553886/21',
                        'billing_client_id': '1354933928',
                        'billing_person_id': '19104248',
                        'payment_type': 'prepaid',
                        'is_offer': True,
                        'currency': 'RUB',
                        'services': ['market'],
                        'is_active': True,
                    },
                ],
            },
            {'status': 'SUCCESS'},
            id='success-market-request',
        ),
    ],
)
@pytest.mark.translations(
    corp={
        'error.customer_linking_error': {
            'ru': 'Ошибка при создании плательщика в биллинге',
        },
    },
)
async def test_market_offer_create(
        web_app_client,
        db,
        mock_corp_clients,
        client_id,
        request_update_doc,
        corp_clients_response,
        expected_response,
):
    mock_corp_clients.data.get_contracts_response = corp_clients_response

    if request_update_doc:
        await db.corp_client_requests.update_one(
            {'client_id': client_id}, {'$set': request_update_doc},
        )

    response = await web_app_client.post(
        '/v1/market-client/status', params={'client_id': client_id},
    )

    response_body = await response.json()
    assert response.status == 200, response_body
    assert response_body == expected_response
