import pytest
from stall.model.order_required import OrderRequired


@pytest.mark.parametrize('params', [
    {'count': 20, 'result_count': 0},
    {'weight': 12, 'result_weight': 0}
])
async def test_required(tap, dataset, params):
    with tap:
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            required = [
                {
                    'product_id': product.product_id,
                    **params
                }
            ]
        )

        tap.eq(len(order.required), 1, 'один элемент в required')
        tap.isa_ok(order.required[0], OrderRequired, 'Элементы в required')

        tap.eq(order.required[0].product_id, product.product_id, 'product_id')
        tap.eq(order.type, 'order', 'тип ордера')
        for attr in params:
            tap.eq(
                getattr(order.required[0], attr),
                params[attr],
                f'Правильный параметр {attr}'
            )




