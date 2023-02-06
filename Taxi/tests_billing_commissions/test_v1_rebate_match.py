import pytest


@pytest.mark.parametrize(
    'query, status, expected, logs_entries',
    [
        (  # rule with tariff
            {
                'zone': 'moscow',
                'reference_time': '2022-01-01T21:00:01+00:00',
                'tariff_class': 'econom',
            },
            200,
            {
                'agreement': {
                    'id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                    'base_rule_id': (
                        'some_fixed_percent_commission'
                        '_contract_id_in_future_end'
                    ),
                    'cancellation_settings': {
                        'park_billable_cancel_interval': ['420', '600'],
                        'pickup_location_radius': 300,
                        'user_billable_cancel_interval': ['120', '600'],
                    },
                    'cost_info': {
                        'kind': 'boundaries',
                        'max_cost': '6000',
                        'min_cost': '0',
                    },
                    'rate': {'kind': 'flat', 'rate': '42'},
                    'vat': '1.18',
                },
            },
            [],
        ),
        (  # all tariffs rule
            {
                'zone': 'moscow',
                'reference_time': '2022-01-01T21:00:01+00:00',
                'tariff_class': 'not_exists',
            },
            200,
            {
                'agreement': {
                    'id': '2abf062a-b607-11ea-998e-07e60204cbdf',
                    'base_rule_id': (
                        'some_fixed_percent_commission'
                        '_contract_id_in_future_end'
                    ),
                    'cancellation_settings': {
                        'park_billable_cancel_interval': ['420', '600'],
                        'pickup_location_radius': 300,
                        'user_billable_cancel_interval': ['120', '600'],
                    },
                    'cost_info': {
                        'kind': 'boundaries',
                        'max_cost': '6000',
                        'min_cost': '0',
                    },
                    'rate': {'kind': 'flat', 'rate': '24'},
                    'vat': '1.18',
                },
            },
            [],
        ),
        (  # no rebate rule
            {
                'zone': 'spb',
                'reference_time': '2022-01-01T21:00:01+00:00',
                'tariff_class': 'not_exists',
            },
            200,
            {
                'agreement': {
                    'base_rule_id': '6192318860c2da31f7c4e231',
                    'cancellation_settings': {
                        'park_billable_cancel_interval': ['420', '600'],
                        'pickup_location_radius': 300,
                        'user_billable_cancel_interval': ['120', '600'],
                    },
                    'cost_info': {
                        'kind': 'boundaries',
                        'max_cost': '6000',
                        'min_cost': '0',
                    },
                    'id': '29ac6065-8ebf-4374-99a6-f523492c3a2c',
                    'rate': {'kind': 'flat', 'rate': '0'},
                    'vat': '1.18',
                },
            },
            ['WARNING'],
        ),
    ],
)
@pytest.mark.now('2022-01-10T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_rebate_match.sql'],
)
async def test_match(
        taxi_billing_commissions,
        query,
        status,
        expected,
        logs_entries,
        taxi_config,
):
    async with taxi_billing_commissions.capture_logs() as logs:
        response = await taxi_billing_commissions.post(
            'v1/rebate/match', json=query,
        )
        assert response.status_code == status
        assert expected == response.json()
        for level in logs_entries:
            assert logs.select(level=level)
