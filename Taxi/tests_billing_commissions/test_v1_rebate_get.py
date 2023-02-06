import pytest


@pytest.mark.parametrize(
    'query, status, expected',
    [
        (
            {'rule_id': '2abf062a-b607-11ea-998e-07e60204cbcf'},
            200,
            {
                'rule': {
                    'fees': {'percent': '42'},
                    'id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                    'matcher': {
                        'starts_at': '2019-01-01T21:00:00+00:00',
                        'tariff': 'econom',
                        'zone': 'moscow',
                    },
                },
            },
        ),
        (
            {'rule_id': '2abf062a-b607-11ea-998e-07e60204cbce'},
            404,
            {'code': 'RULES_NOT_FOUND', 'message': 'Rule not found'},
        ),
    ],
)
@pytest.mark.now('2020-01-10T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_rebate_get.sql'],
)
async def test_select(taxi_billing_commissions, query, status, expected):
    response = await taxi_billing_commissions.get(
        'v1/rebate/get', params=query,
    )
    assert response.status_code == status
    assert expected == response.json()
