async def test_update_reserve(tap, dataset, now, wait_order_status):
    with tap.plan(12, 'Сигнал резервирования'):

        product = await dataset.product()

        store = await dataset.store()
        user = await dataset.user(store=store)

        stock = await dataset.stock(store=store, product=product, count=10)

        other = await dataset.order(store=store)
        tap.ok(await stock.do_reserve(other, 3), 'Часть товара зарезервирована')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            approved=now(),
            type='order',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 10,
                }
            ],
            vars = {'editable': True}
        )
        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(len(order.problems), 1, 'Проблема есть')
        with order.problems[0] as problem:
            tap.eq(problem.count, 3, 'Не хватает 3 шт')

        with await order.signal({'type': 'update_reserve'}) as s:
            tap.ok(s, 'сигнал отправлен')
            await wait_order_status(order, ('processing', 'waiting'))
            tap.eq(len(order.problems), 1, 'Проблема еще не решена')

        tap.ok(await stock.do_reserve(other, 0), 'Резерв освобожден')

        with await order.signal({'type': 'update_reserve'}) as s:
            tap.ok(s, 'сигнал отправлен')
            await wait_order_status(order, ('processing', 'waiting'))
            tap.eq(len(order.problems), 0, 'Проблем нет')

        await wait_order_status(order, ('complete', 'begin'), user_done=user)
