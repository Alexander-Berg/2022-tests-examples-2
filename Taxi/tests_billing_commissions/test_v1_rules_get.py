import pytest


@pytest.mark.parametrize(
    'query, status, expected',
    [
        (
            {'rule_id': '2abf062a-b607-11ea-998e-07e60204cbcf'},
            200,
            {
                'rule': {
                    'fees': [
                        {'fee': '42.0001', 'subscription_level': 'level'},
                    ],
                    'id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                    'kind': 'software_subscription',
                    'matcher': {
                        'ends_at': '2120-01-01T21:00:00+00:00',
                        'starts_at': '2019-01-01T21:00:00+00:00',
                        'tariff': 'econom',
                        'zone': 'moscow',
                    },
                },
            },
        ),
        (
            {'rule_id': 'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f'},
            200,
            {
                'rule': {
                    'fees': [
                        {'fee': '42.0002', 'subscription_level': 'level'},
                    ],
                    'id': 'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f',
                    'kind': 'software_subscription',
                    'matcher': {
                        'ends_at': '2030-01-01T21:00:00+00:00',
                        'starts_at': '2024-01-01T21:00:00+00:00',
                        'tariff': 'econom',
                        'zone': 'spb',
                    },
                },
            },
        ),
        (
            {'rule_id': 'f3a0403d-3f30-4a43-8e30-71d77ebcaa1f'},
            404,
            {'code': 'RULES_NOT_FOUND', 'message': ''},
        ),
        ({}, 400, {'code': '400', 'message': 'Missing rule_id in query'}),
        (
            {'rule_id': 'f3a0603d-3f30-4a43-8e30-71d77ebcaa3f'},
            200,
            {
                'rule': {
                    'fees': {'percent': '0.13'},
                    'id': 'f3a0603d-3f30-4a43-8e30-71d77ebcaa3f',
                    'kind': 'hiring_kind',
                    'matcher': {
                        'ends_at': '2030-01-01T21:00:00+00:00',
                        'hiring_type': 'commercial_returned',
                        'starts_at': '2024-01-01T21:00:00+00:00',
                        'tariff': 'econom',
                        'zone': 'ekb',
                    },
                    'settings': {'hiring_age': 180},
                },
            },
        ),
        (
            {'rule_id': 'f3a1603d-3f30-4a43-8e30-71d77ebcaa3f'},
            200,
            {
                'rule': {
                    'fees': {'fee': '0.13'},
                    'id': 'f3a1603d-3f30-4a43-8e30-71d77ebcaa3f',
                    'kind': 'fine_kind',
                    'matcher': {
                        'ends_at': '2030-01-01T21:00:00+00:00',
                        'fine_code': 'fine!!!',
                        'starts_at': '2024-01-01T21:00:00+00:00',
                        'tariff': 'econom',
                        'zone': 'ekb',
                    },
                },
            },
        ),
    ],
)
@pytest.mark.now('2020-01-10T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_rules_get.sql'],
)
async def test_select(
        taxi_billing_commissions,
        load_json,
        query,
        status,
        expected,
        billing_commissions_postgres_db,
):
    response = await taxi_billing_commissions.get('v1/rules/get', params=query)
    assert response.status_code == status
    assert expected == response.json()
