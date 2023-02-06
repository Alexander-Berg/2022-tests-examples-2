import pytest

RULE = {
    'acquiring_percent': '0.0200',
    'agent_percent': '0.0001',
    'begin': '2018-12-31T20:00:00',
    'billable_cancel_distance': 300,
    'branding_discounts': [],
    'callcenter_commission_percent': '0.0000',
    'cancel_percent': '0.0000',
    'end': '2030-01-01T00:00:00',
    'expired_cost': '800.0000',
    'expired_percent': '0.1100',
    'has_fixed_cancel_percent': False,
    'hiring': '0.0200',
    'hiring_age': 180,
    'hiring_commercial': '0.0400',
    'id': 'some_fixed_percent_commission_contract_id_in_future_end',
    'is_active': True,
    'is_deletable': False,
    'is_editable': True,
    'log_count': 0,
    'max_order_cost': '6000.0000',
    'min_order_cost': '0.0000',
    'park_cancel_max_td': 600,
    'park_cancel_min_td': 420,
    'payment_type': 'corp',
    'percent': '0.1100',
    'taximeter_payment': '1.0000',
    'type': 'fixed_percent',
    'unrealized_rate': '10.5000',
    'user_cancel_max_td': 600,
    'user_cancel_min_td': 120,
    'vat': '1.1800',
    'zone': 'moscow',
}


@pytest.mark.parametrize(
    'query, status, expected',
    [
        (
            {
                'rule_id': (
                    'some_fixed_percent_commission_contract_id_in_future_end'
                ),
            },
            200,
            {'rule': RULE},
        ),
        (
            {'rule_id': 'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f'},
            404,
            {'code': 'RULES_NOT_FOUND', 'message': ''},
        ),
        ({}, 400, {'code': '400', 'message': 'Missing rule_id in query'}),
    ],
)
@pytest.mark.now('2020-01-10T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions', files=['test_rules_v1_rules_base_get.sql'],
)
async def test_v1_rules_base_get(
        taxi_billing_commissions, query, status, expected,
):
    response = await taxi_billing_commissions.get(
        'v1/rules/base/get', params=query,
    )
    assert response.status_code == status
    assert expected == response.json()
