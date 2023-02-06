import pytest

import operation_calculations.geosubventions.multidraft.report as report


@pytest.mark.parametrize(
    'budget, expected',
    [
        [1, '1'],
        [10, '10'],
        [100, '100'],
        [1000, '1000'],
        [10000, '10 000 (10K)'],
        [100000, '100 000 (0.1M)'],
        [1000000, '1 000 000 (1M)'],
        [10000000, '10 000 000 (10M)'],
        [100000000, '100 000 000 (0.1B)'],
        [1000000000, '1 000 000 000 (1B)'],
        [100000.433, '100 000.43 (0.1M)'],
        [100000.000, '100 000 (0.1M)'],
        [1000000.9999, '1 000 001 (1M)'],
        [1.435, '1.44'],
        [10.0, '10'],
        [100.9999, '101'],
        [1001000, '1 001 000 (1M)'],
        [1500000, '1 500 000 (1.5M)'],
        [1400000, '1 400 000 (1.4M)'],
        [1399999, '1 399 999 (1.4M)'],
        [11000000, '11 000 000 (11M)'],
        [11399900, '11 399 900 (11.4M)'],
        [72911100, '72 911 100 (72.9M)'],
    ],
)
def test_format_budget(budget, expected):
    foramtted_value = report.format_budget_value(budget)
    assert foramtted_value == expected
