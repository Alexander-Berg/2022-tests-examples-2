import json


import pytest

ROUTE = '/v1/billing/offer/create'
BILLING_ROOT = 'taxi.clients.billing_v2.BalanceClient.create_offer'
EXPECTED_DATA = {
    'operator_uid': '793360492',
    'client_id': 88394285,
    'partner_commission_sum': 0.1,
    'allowed_field': 'kirill',
}

RESPONSE = {'ID': '12321312', 'EXTERNAL_ID': '333333'}


@pytest.mark.servicetest
async def test_create_offer(web_app_client, create_collateral_mock):
    data = {
        'operator_uid': '793360492',
        'params': {
            'client_id': 88394285,
            'partner_commission_sum': 0.1,
            'allowed_field': 'kirill',
            'not_allowed_field': 'i_am',
            'empty_allowed_field': None,
        },
    }
    create_collateral_mock(EXPECTED_DATA, BILLING_ROOT, RESPONSE)
    response = await web_app_client.post(ROUTE, data=json.dumps(data))

    assert response.status == 200
    content = await response.json()
    assert content == {'ID': '12321312', 'EXTERNAL_ID': '333333'}
