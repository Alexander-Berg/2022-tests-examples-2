import decimal
import typing

import pytest

from taxi_billing_audit import models


@pytest.mark.parametrize(
    'left, right, expected',
    [
        (
            models.AuditSummaryStore(
                name='l',
                source=[
                    models.AuditSummary(
                        currency='RUB',
                        amount=decimal.Decimal('12.0001'),
                        count=1,
                    ),
                ],
            ),
            models.AuditSummaryStore(
                name='r',
                source=[
                    models.AuditSummary(
                        currency='RUB',
                        amount=decimal.Decimal('.0001'),
                        count=1,
                    ),
                ],
            ),
            [
                {
                    'l': models.AuditSummary(
                        currency='RUB',
                        amount=decimal.Decimal('12.0001'),
                        count=1,
                    ).asdict(),
                    'r': models.AuditSummary(
                        currency='RUB',
                        amount=decimal.Decimal('.0001'),
                        count=1,
                    ).asdict(),
                },
            ],
        ),
        (
            models.AuditSummaryStore(
                name='l',
                source=[
                    models.AuditSummary(
                        currency='RUB',
                        amount=decimal.Decimal('12.0001'),
                        count=1,
                    ),
                    models.AuditSummary(
                        currency='EUR',
                        amount=decimal.Decimal('12.0001'),
                        count=1,
                    ),
                ],
            ),
            models.AuditSummaryStore(
                name='r',
                source=[
                    models.AuditSummary(
                        currency='RUB',
                        amount=decimal.Decimal('.0001'),
                        count=1,
                    ),
                ],
            ),
            [
                {
                    'l': models.AuditSummary(
                        currency='EUR',
                        amount=decimal.Decimal('12.0001'),
                        count=1,
                    ).asdict(),
                    'r': {},
                },
                {
                    'l': models.AuditSummary(
                        currency='RUB',
                        amount=decimal.Decimal('12.0001'),
                        count=1,
                    ).asdict(),
                    'r': models.AuditSummary(
                        currency='RUB',
                        amount=decimal.Decimal('.0001'),
                        count=1,
                    ).asdict(),
                },
            ],
        ),
    ],
)
def test_find_diff(
        left: models.AuditSummaryStore,
        right: models.AuditSummaryStore,
        expected: models.AuditSummaryStore,
):
    assert expected == left.diff(right)


@pytest.mark.parametrize(
    'source, expected',
    [
        (
            models.AuditSummaryStore(
                name='tst',
                source=[
                    models.AuditSummary(
                        currency='EUR',
                        amount=decimal.Decimal('12.0001'),
                        count=1,
                    ),
                    models.AuditSummary(
                        currency='RUB', amount=decimal.Decimal('12'), count=0,
                    ),
                ],
            ),
            True,
        ),
        (models.AuditSummaryStore(name='tst'), False),
    ],
)
def test_bool_property(source: models.AuditSummaryStore, expected: bool):
    assert bool(source) == expected


@pytest.mark.parametrize(
    'source_values, expected',
    [
        (
            [
                models.AuditSummary(
                    count=1, amount=decimal.Decimal('0.0003'), currency='RUB',
                ),
                models.AuditSummary(
                    count=1, amount=decimal.Decimal('0.0003'), currency='RUB',
                ),
                models.AuditSummary(
                    count=1, amount=decimal.Decimal('1.0004'), currency='RUB',
                ),
                models.AuditSummary(
                    count=1, amount=decimal.Decimal('42'), currency='EUR',
                ),
            ],
            models.AuditSummaryStore(
                name='tst',
                source=[
                    models.AuditSummary(
                        count=3,
                        amount=decimal.Decimal('1.001'),
                        currency='RUB',
                    ),
                    models.AuditSummary(
                        count=1, amount=decimal.Decimal('42'), currency='EUR',
                    ),
                ],
            ),
        ),
    ],
)
def test_add_functionality(
        source_values: typing.List[models.AuditSummary],
        expected: models.AuditSummaryStore,
):
    test_model = models.AuditSummaryStore(name='add_test')
    for item in source_values:
        test_model.add(item)
    assert test_model == expected
