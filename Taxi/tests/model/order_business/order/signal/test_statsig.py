async def test_statsig(tap, dataset, now, wait_order_status):
    with tap.plan(11, 'Тесты на сигнал stat'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        await dataset.stock(store=store, product=product, count=10)

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='order',
            approved=now(),
            required=[
                {
                    'product_id': product.product_id,
                    'count': 5,
                }
            ],
            attr={'hello': 'world'}
        )

        tap.eq(order.store_id, store.store_id, 'заказ создан')
        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(
            await order.signal(
                {
                    'type': 'stat',
                    'data': {'truck_temperature': 28}
                }
            ),
            'сигнал отправлен'
        )

        tap.ok(
            await order.signal(
                {
                    'type': 'stat',
                    'data': {'truck_temperature': 23},
                }
            ),
            'сигнал отправлен'
        )

        tap.ok(
            await order.signal(
                {
                    'type': 'stat',
                    'data': {'gift_for_customer': 'Yes'},
                }
            ),
            'сигнал отправлен'
        )

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.eq(order.attr['stat'],
               {'truck_temperature': 23, 'gift_for_customer': 'Yes'},
               'stat сохранён')

        tap.eq(order.attr['hello'], 'world', 'старый attr не менялся')
