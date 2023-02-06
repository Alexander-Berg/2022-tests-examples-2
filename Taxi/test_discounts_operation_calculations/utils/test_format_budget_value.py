import pytest

from discounts_operation_calculations.internals import description


@pytest.mark.parametrize(
    ('budget', 'precision', 'expected'),
    [
        (100.0, 0, '100'),
        (100.0, 3, '100'),
        (100.03, 0, '100'),
        (100.03, 1, '100'),
        (100.03, 2, '100.03'),
        (1000, 0, '1000'),
        (10000, 0, '10 000 (10K)'),
        (10000, 2, '10 000 (10K)'),
        (10000.1, 0, '10 000 (10K)'),
        (10000.03, 2, '10 000.03 (10K)'),
        (252522.3333, 0, '252 522 (0.3M)'),
        (7211267, 0, '7 211 267 (7.2M)'),
        (97253322.232, 0, '97 253 322 (97.3M)'),
    ],
)
def test_format_budget_value(budget, precision, expected):
    assert description.format_budget_value(budget, precision) == expected
