async def test_dataset(tap, dataset):
    with tap.plan(5, 'Тестируем dataset'):
        order = await dataset.order()
        tap.ok(order, 'Заказ создан')

        stock = await dataset.stock(order=order, valid='2011-01-03')
        tap.ok(stock, 'остаток создан')
        tap.ok(stock.product_id, 'продукт назначен')
        tap.ok(stock.count, 'количество')
        tap.eq(stock.valid.strftime('%F'), '2011-01-03', 'срок')


async def test_dataset_vars(tap, dataset):
    with tap.plan(3, 'Тестируем сохранение vars'):
        order = await dataset.order()
        tap.ok(order, 'Заказ создан')

        stock = await dataset.stock(order=order,
                                    valid='2011-01-03',
                                    vars={'hello': 'world'})
        tap.ok(stock, 'остаток создан')
        tap.eq(stock.vars, {'hello': 'world'}, 'vars')
