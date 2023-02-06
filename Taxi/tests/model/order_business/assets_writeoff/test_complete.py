async def test_complete(tap, dataset, wait_order_status):
    with tap.plan(18, 'Частично уже зарезервировано'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()

        stock1 = await dataset.stock(product=product1, store=store, count=10)
        tap.eq(stock1.count, 10, 'Остаток 1 положен')
        tap.eq(stock1.reserve, 0, 'Резерва 1 нет')

        stock2 = await dataset.stock(product=product2, store=store, count=20)
        tap.eq(stock2.count, 20, 'Остаток 2 положен')
        tap.eq(stock2.reserve, 0, 'Резерва 2 нет')

        stock3 = await dataset.stock(product=product3, store=store, count=30)
        tap.eq(stock3.count, 30, 'Остаток 3 положен')
        tap.eq(stock3.reserve, 0, 'Резерва 3 нет')

        task = await dataset.repair_task(store=store)
        order = await dataset.order(
            store=store,
            type='assets_writeoff',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 1
                },
                {
                    'product_id': product3.product_id,
                    'count': 3
                },
                {
                    'product_id': product2.product_id,
                    'count': 2
                },
            ],
            vars={
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
            },
        )
        tap.eq(order.target, 'complete', 'target: complete')

        await wait_order_status(order, ('complete', 'done'))

        await order.business.order_changed()

        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.ok(await stock1.reload(), 'Остаток 1 получен')
        tap.eq(stock1.count, 9, 'Остаток 1 есть (9)')
        tap.eq(stock1.reserve, 0, 'Зарезервировано 0')

        tap.ok(await stock2.reload(), 'Остаток 2 получен')
        tap.eq(stock2.count, 18, 'Остаток 2 есть (18)')
        tap.eq(stock2.reserve, 0, 'Зарезервировано 0')

        tap.ok(await stock3.reload(), 'Остаток 3 получен')
        tap.eq(stock3.count, 27, 'Остаток 3 есть (27)')
        tap.eq(stock3.reserve, 0, 'Зарезервировано 0')
