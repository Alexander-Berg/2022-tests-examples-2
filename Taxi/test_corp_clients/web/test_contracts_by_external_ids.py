import pytest

EXPECTED_JSON_DEFAULT = [
    {
        'contract_id': 101,
        'external_id': '101/12',
        'billing_client_id': '100001',
        'billing_person_id': '100001',
        'payment_type': 'prepaid',
        'is_offer': True,
        'currency': 'RUB',
        'services': ['taxi', 'cargo', 'eats2'],
        'is_active': True,
        'is_sent': True,
        'is_faxed': True,
        'is_signed': True,
        'offer_accepted': False,
        'offer_accepted_common': True,
        'edo_accepted': True,
        'balances': {
            'balance': '150',
            'receipt_sum': '250',
            'total_charge': '100',
            'apx_sum': '0',
            'discount_bonus_sum': '0',
        },
        'settings': {
            'is_active': True,
            'is_auto_activate': True,
            'prepaid_deactivate_threshold': '123.34',
            'prepaid_deactivate_threshold_type': 'standard',
            'low_balance_notification_enabled': True,
            'low_balance_threshold': '100',
        },
        'created': '2020-11-01T13:00:00+03:00',
    },
    {
        'contract_id': 102,
        'external_id': '102/12',
        'billing_client_id': '100001',
        'billing_person_id': '100001',
        'payment_type': 'prepaid',
        'is_offer': True,
        'currency': 'RUB',
        'services': ['taxi'],
        'is_active': False,
        'is_sent': False,
        'is_faxed': False,
        'is_signed': False,
        'offer_accepted': False,
        'offer_accepted_common': False,
        'finish_dt': '2020-11-02T13:00:00+03:00',
        'balances': {
            'balance': '200',
            'receipt_sum': '250',
            'total_charge': '50',
            'discount_bonus_sum': '0',
        },
        'settings': {
            'is_active': False,
            'is_auto_activate': True,
            'prepaid_deactivate_threshold': '123.34',
            'prepaid_deactivate_threshold_type': 'standard',
            'contract_limit': {'limit': '123.45', 'threshold': '456.789'},
            'low_balance_notification_enabled': False,
            'low_balance_threshold': '0',
        },
        'created': '2020-11-01T14:00:00+03:00',
    },
]


@pytest.mark.parametrize(
    ['json', 'expected_json'],
    [
        pytest.param(
            {'contract_external_ids': ['101/12', '102/12']},
            EXPECTED_JSON_DEFAULT,
        ),
        pytest.param(
            {'contract_external_ids': ['101/12', '102/12'], 'is_active': True},
            [EXPECTED_JSON_DEFAULT[0]],
        ),
    ],
)
async def test_contracts(web_app_client, json, expected_json):

    response = await web_app_client.post(
        '/v1/contracts/by-external-ids', json=json,
    )
    assert response.status == 200
    response_json = await response.json()
    assert expected_json == response_json['contracts']
