import pytest
from stall.model.true_mark import TrueMark


@pytest.mark.parametrize('order_vars,eda_status,expected', [
    (
        {
            'true_mark_in_order': True
        },
        'PICKUP',
        False
    ),
    (
        {
            'true_mark_in_order': True,
            'need_sell_true_mark': False
        },
        'DELIVERED',
        False
    ),
    (
        {},
        'DELIVERED',
        False
    ),
    (
        {
            'true_mark_in_order': True,
            'true_mark_status': 'sold',
        },
        'DELIVERED',
        False
    ),
    (
        {
            'true_mark_in_order': True,
            'true_mark_status': 'in_order',
        },
        'DELIVERED',
        True
    ),
    (
        {
            'true_mark_in_order': True,
        },
        'UNKNOWN',
        True
    ),
])
async def test_need_sell(tap, dataset, order_vars, eda_status, expected):
    with tap.plan(2, 'Когда нужна джоба для марок'):
        order = await dataset.order(
            type='order',
            vars=order_vars,
        )
        order.eda_status = eda_status

        result = await TrueMark.order_need_sell_marks_job(order)

        tap.eq(result, expected, 'Ожидаемый результат')
        tap.eq(
            order.vars('need_sell_true_mark', False),
            expected,
            'Флаг в заказе'
        )
