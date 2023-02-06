import csv
import itertools

import pytest


@pytest.mark.parametrize(
    'query',
    (
        {'date': '2022-01-01T00:00:00+03:00', 'zones': ['moscow']},
        {'date': '2022-01-01T00:00:00+03:00', 'countries': ['rus']},
    ),
)
@pytest.mark.pgsql(
    'billing_commissions',
    files=['test_rules_v1_rules_base_export_to_csv.sql'],
)
async def test_v1_base_export_to_csv(taxi_billing_commissions, load, query):
    response = await taxi_billing_commissions.post(
        '/v1/rules/base/export_to_csv/', query,
    )
    assert response.status == 200
    assert response.headers['Content-Disposition'] == 'commissions.csv'
    actual = csv.DictReader(response.content.decode().strip().split('\n'))
    expected = csv.DictReader(load('commissions.csv').strip().split('\n'))
    for row, expected_row in itertools.zip_longest(actual, expected):
        assert row == expected_row
