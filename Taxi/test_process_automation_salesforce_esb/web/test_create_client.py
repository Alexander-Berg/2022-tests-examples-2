import json

import pytest

ROUTE = '/v1/billing/client/create'

BILLING_ROOT = 'taxi.clients.billing_v2.BalanceClient.create_client'
EXPECTED_DATA = (
    '793360492',
    {
        'EMAIL': 'evgenius@yandex-team.ru',
        'allowed_field_client': 'NO_SUPERMAN',
    },
)
RESPONSE = '11048320'


@pytest.mark.servicetest
async def test_create_client(web_app_client, create_object_mock):
    data = {
        'operator_uid': '793360492',
        'params': {
            'CLIENT_ID': None,
            'EMAIL': 'evgenius@yandex-team.ru',
            'allowed_field_client': 'NO_SUPERMAN',
            'not_allowed_field': 'i_am',
            'empty_allowed_field': None,
        },
    }

    create_object_mock(EXPECTED_DATA, BILLING_ROOT, RESPONSE)
    response = await web_app_client.post(ROUTE, data=json.dumps(data))

    assert response.status == 200
    content = await response.json()
    assert content == {'client_id': RESPONSE}
