import json

import pytest

BILLING_ROOT = 'taxi.clients.billing_v2.BalanceClient.create_person'
EXPECTED_DATA = (
    '793360492',
    {
        'account': '40817810660251203431',
        'allowed_field_person': 'GRUT',
        'bik': '040702615',
        'client_id': 88394285,
        'delivery-type': '4',
        'il-id': '',
        'type': 'ur',
    },
)
RESPONSE = 11048320


@pytest.mark.servicetest
async def test_create_persons(web_app_client, create_object_mock):
    data = {
        'operator_uid': '793360492',
        'params': {
            'client_id': 88394285,
            'type': 'ur',
            'account': '40817810660251203431',
            'bik': '040702615',
            'delivery-type': '4',
            'il-id': '',
            'allowed_field_person': 'GRUT',
            'not_allowed_field': 'i_am',
            'empty_allowed_field': None,
        },
    }

    create_object_mock(EXPECTED_DATA, BILLING_ROOT, RESPONSE)
    response = await web_app_client.post(
        '/v1/billing/person/create', data=json.dumps(data),
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'person_id': RESPONSE}
