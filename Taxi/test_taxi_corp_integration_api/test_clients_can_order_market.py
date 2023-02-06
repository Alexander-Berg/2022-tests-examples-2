import pytest

from test_taxi_corp_integration_api import utils


@pytest.mark.parametrize(
    ['request_data', 'response_data'],
    [
        pytest.param(
            {'client_ids': ['client_market']},
            [
                {
                    'can_order': True,
                    'client_id': 'client_market',
                    'order_disable_reason': '',
                    'zone_available': True,
                    'zone_disable_reason': '',
                },
            ],
        ),
        pytest.param(
            {'client_ids': ['client_market_2']},
            [
                {
                    'can_order': False,
                    'client_id': 'client_market_2',
                    'order_disable_reason': (
                        'Ваш корпоративный счет больше недоступен'
                    ),
                    'zone_available': True,
                    'zone_disable_reason': '',
                },
            ],
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_clients_can_order_market(
        web_app_client, mockserver, request_data, response_data,
):
    response = await web_app_client.post(
        '/v1/clients/can_order/market', json=request_data,
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {'statuses': response_data}
