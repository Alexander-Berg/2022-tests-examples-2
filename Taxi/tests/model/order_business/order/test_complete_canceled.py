async def test_complete_canceled(tap, dataset, wait_order_status):
    with tap.plan(16, 'создание ордера отмены после отмены'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='admin', store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store, count=123)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')


        order = await dataset.order(
            store=store,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 32,
                }
            ],
            type='order',
            approved='2012-01-02',
            acks=[user.user_id],
            status='reserving',
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')
        tap.eq(order.type, 'order', 'тип')

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        tap.ok(await order.cancel(), 'отменён после завершения')

        await wait_order_status(order, ('canceled', 'done'), user_done=user)

        child_order = await order.load(order.vars('child_order_id'))
        tap.ok(child_order, 'дочерний ордер загружен')

        tap.eq(child_order.store_id, order.store_id, 'он на том же складе')
        tap.eq(child_order.fstatus, ('reserving', 'begin'), 'статус')
        tap.eq(child_order.parent, [order.order_id], 'parent')
        tap.ok(child_order.approved, 'он апрувлен')
        tap.eq(child_order.type, 'refund', 'тип')
        tap.eq(
            child_order.required[0].count,
            32,
            'Рефандим нужное количество'
        )


async def test_with_part_refund(tap, dataset, wait_order_status):
    with tap.plan(18, 'создание ордера отмены после отмены и part refund'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='admin', store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store, count=123)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        order = await dataset.order(
            store=store,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 32,
                }
            ],
            type='order',
            approved='2012-01-02',
            acks=[user.user_id],
            status='reserving',
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')
        tap.eq(order.type, 'order', 'тип')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        required = await order.business.refund_required()  # pylint: disable=protected-access
        tap.ok(required, 'Реквайред есть')
        required[0]['count'] = 10

        part_refund = await dataset.order(
            store=store,
            required=required,
            type='part_refund',
            parent=[order.order_id],
        )
        tap.ok(part_refund, 'Частичный возврат')

        tap.ok(await order.cancel(), 'отменён после завершения')

        await wait_order_status(order, ('canceled', 'done'), user_done=user)

        child_order = await order.load(order.vars('child_order_id'))
        tap.ok(child_order, 'дочерний ордер загружен')

        tap.eq(child_order.store_id, order.store_id, 'он на том же складе')
        tap.eq(child_order.fstatus, ('reserving', 'begin'), 'статус')
        tap.eq(child_order.parent, [order.order_id], 'parent')
        tap.ok(child_order.approved, 'он апрувлен')
        tap.eq(child_order.type, 'refund', 'тип')
        tap.eq(
            child_order.required[0].count,
            32-10,
            'Рефандим нужное количество'
        )


async def test_complete_canceled_empty(tap, dataset, wait_order_status):
    with tap.plan(10, 'Не создается ордер отмены для пустого'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='admin', store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь привязан')

        stock = await dataset.stock(store=store, count=123)
        tap.eq(stock.store_id, store.store_id, 'остаток на правильном складе')

        order = await dataset.order(
            store=store,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 0,
                }
            ],
            type='order',
            approved='2012-01-02',
            acks=[user.user_id],
            status='reserving',
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')
        tap.eq(order.type, 'order', 'тип')

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        tap.ok(await order.cancel(), 'отменён после завершения')
        await wait_order_status(order, ('canceled', 'done'), user_done=user)

        tap.ok(
            order.vars('child_order_id', None) is None,
            'Нет дочернего ордера'
        )
