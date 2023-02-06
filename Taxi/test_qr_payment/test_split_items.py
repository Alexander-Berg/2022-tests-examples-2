import decimal
from typing import List

import pytest

from qr_payment import components as qr_lib


@pytest.mark.parametrize(
    ['items', 'points', 'expected_items'],
    [
        pytest.param(
            [
                decimal.Decimal('10'),
                decimal.Decimal('0'),
                decimal.Decimal('20'),
                decimal.Decimal('0.5'),
                decimal.Decimal('30'),
                decimal.Decimal('1.3'),
            ],
            decimal.Decimal('1000'),
            [
                (decimal.Decimal('1'), decimal.Decimal('9')),
                (decimal.Decimal('0'), decimal.Decimal('0')),
                (decimal.Decimal('1'), decimal.Decimal('19')),
                (decimal.Decimal('0.5'), decimal.Decimal('0')),
                (decimal.Decimal('1'), decimal.Decimal('29')),
                (decimal.Decimal('0.3'), decimal.Decimal('1')),
            ],
            id='Points more than total price',
        ),
        pytest.param(
            [
                decimal.Decimal('10'),
                decimal.Decimal('20.5'),
                decimal.Decimal('50'),
            ],
            decimal.Decimal('18'),
            [
                (decimal.Decimal('1'), decimal.Decimal('9')),
                (decimal.Decimal('11.5'), decimal.Decimal('9')),
                (decimal.Decimal('50'), decimal.Decimal('0')),
            ],
            id='Points less than total price',
        ),
        pytest.param(
            [decimal.Decimal('10'), decimal.Decimal('50.1')],
            decimal.Decimal('0'),
            [
                (decimal.Decimal('10'), decimal.Decimal('0')),
                (decimal.Decimal('50.1'), decimal.Decimal('0')),
            ],
            id='0 points',
        ),
    ],
)
async def test_split_items(library_context, items, points, expected_items):
    result = library_context.qr_payment_lib.split_for_money_and_points(
        items_prices=[price for price in items], points=points,
    )
    excpected_result: List[qr_lib.SplittedItem] = [
        qr_lib.SplittedItem(money=value[0], points=value[1])
        for value in expected_items
    ]
    assert excpected_result == result
