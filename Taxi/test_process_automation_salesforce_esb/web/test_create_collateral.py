import json

from freezegun import api
import pytest

ROUTE = '/v1/billing/collateral/create'
BILLING_ROOT = 'taxi.clients.billing_v2.BalanceClient.create_collateral'
EXPECTED_DATA = {
    'operator_id': '793360492',
    'log_extra': None,
    'collateral_type': 90,
    'contract_id': 2571995,
    'end_dt': api.FakeDatetime(2020, 11, 12, 0, 0),
    'allowed_field': 'kirill',
}

RESPONSE = {'COLLATERAL_NUM': '123'}


@pytest.mark.servicetest
async def test_create_collateral(web_app_client, create_collateral_mock):
    data = {
        'operator_uid': '793360492',
        'params': {
            'collateral_type': 90,
            'contract_id': 2571995,
            'end_dt': '2020-11-12',
            'allowed_field': 'kirill',
            'not_allowed_field': 'i_am',
            'empty_allowed_field': None,
        },
    }
    create_collateral_mock(EXPECTED_DATA, BILLING_ROOT, RESPONSE)
    response = await web_app_client.post(ROUTE, data=json.dumps(data))
    assert response.status == 200
    content = await response.json()
    assert content == {'collateral_num': '123'}
