import pytest


@pytest.mark.parametrize('required_dict, expected_weight', [
    (
        {'product1': 1, 'product2': 3, 'product3': 2, 'item1': 1},
        2320
    ),
    (
        {'product1': 10, 'product3': 12},
        1230
    ),
])
async def test_weight(tap, dataset, required_dict, expected_weight):
    # pylint: disable=too-many-locals
    with tap.plan(7, 'Вес товара'):

        product1 = await dataset.product(
            vars={'imported': {'brutto_weight': 100, 'netto_weight': 123}})
        product2 = await dataset.product(
            vars={'imported': {'netto_weight': 321}})
        product3 = await dataset.product()
        item1 = await dataset.item(data={'weight': 1234})

        store = await dataset.store()

        stock1 = await dataset.stock(product=product1, store=store, count=10)
        tap.eq(stock1.count, 10, 'Остаток 1 положен')

        stock2 = await dataset.stock(product=product2, store=store, count=20)
        tap.eq(stock2.count, 20, 'Остаток 2 положен')

        stock3 = await dataset.stock(product=product3, store=store, count=30)
        tap.eq(stock3.count, 30, 'Остаток 3 положен')

        stock4 = await dataset.stock(item=item1, store=store, count=1)
        tap.eq(stock4.count, 1, 'Остаток 3 положен')

        required = []
        for var_name, count in required_dict.items():
            key = 'item_id' if var_name.startswith('item') else 'product_id'
            required.append({
                key: getattr(locals()[var_name], key),
                'count': count
            })

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='calculate_order_weight',
            required=required,
        )
        tap.ok(order, 'Заказ создан')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')

        tap.eq(
            order.vars('total_order_weight', 0),
            expected_weight,
            'Вес правильный'
        )
