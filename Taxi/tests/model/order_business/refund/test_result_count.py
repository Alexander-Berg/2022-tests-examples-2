async def test_result_count(tap, dataset, wait_order_status, now):
    with tap.plan(28, 'Заполнение result_count в refund'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'карточка экземпляра')

        stock = await dataset.stock(store=store, count=128)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        item_stock = await dataset.stock(item=item, store=store, count=1)
        tap.eq(item_stock.store_id, store.store_id, 'остаток создан')
        tap.eq(item_stock.count, 1, 'значение остатка')
        tap.eq(item_stock.product_id, item.item_id, 'product_id')

        order = await dataset.order(
            type='order',
            store=store,
            acks=[user.user_id],
            required=[
                {'product_id': stock.product_id, 'count': 35},
                {'item_id': item_stock.product_id},
            ],
            approved=now(),
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('complete', 'done'), user_done=user)
        tap.ok(await order.cancel(), 'отменён')
        await wait_order_status(order, ('canceled', 'done'))
        tap.ok(order.vars('child_order_id', None), 'дочерний ордер есть')


        order = await dataset.Order.load(order.vars['child_order_id'])
        tap.ok(order, 'refund загружен')
        await wait_order_status(order, ('request', 'waiting'))
        tap.ok(await order.ack(user), 'ack')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'пара саджестов')
        for s in suggests:
            if s.product_id == stock.product_id:
                tap.eq(s.count, 35, 'количество')
                tap.ok(await s.done(count=27, valid='2018-02-01'),
                       'Саджест товара закрыт')
                continue
            if s.product_id == item_stock.product_id:
                tap.eq(s.count, 1, 'количество')
                tap.ok(await s.done(count=1), 'Саджест экземпляра закрыт')
                continue

        while order.vars('stage') == 'store':
            await wait_order_status(order, ('processing', 'waiting'))

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.eq(len(order.required), 2, 'две записи required')

        rp = next(
            (r for r in order.required if r.product_id == stock.product_id),
            None
        )
        tap.ok(rp, 'required товара найден')
        tap.eq(rp.result_count, 27, 'result_count проставлен')

        ri = next(
            (r for r in order.required if r.item_id == item.item_id),
            None
        )
        tap.ok(ri, 'required экземпляра найден')
        tap.eq(ri.result_count, 1, 'result_count проставлен')


async def test_result_count_multi(tap, dataset, wait_order_status, now, uuid):
    with tap.plan(22, 'Заполнение result_count при дублях в required'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'карточка экземпляра')

        stock = await dataset.stock(store=store, count=128, lot=uuid())
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        stock2 = await dataset.stock(
            store=store,
            count=12,
            lot=uuid(),
            product_id=stock.product_id
        )
        tap.eq(stock2.product_id, stock.product_id, 'второй остаток')

        item_stock = await dataset.stock(item=item, store=store, count=1)
        tap.eq(item_stock.store_id, store.store_id, 'остаток создан')
        tap.eq(item_stock.count, 1, 'значение остатка')
        tap.eq(item_stock.product_id, item.item_id, 'product_id')

        order = await dataset.order(
            type='order',
            store=store,
            acks=[user.user_id],
            required=[
                {'product_id': stock.product_id, 'count': 135},
                {'item_id': item_stock.product_id},
            ],
            approved=now(),
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('complete', 'done'), user_done=user)
        tap.ok(await order.cancel(), 'отменён')
        await wait_order_status(order, ('canceled', 'done'))
        tap.ok(order.vars('child_order_id', None), 'дочерний ордер есть')


        order = await dataset.Order.load(order.vars['child_order_id'])
        tap.ok(order, 'refund загружен')
        await wait_order_status(order, ('request', 'waiting'))
        tap.ok(await order.ack(user), 'ack')
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.eq(len(order.required), 3, 'три записи required')

        rp = [
            r for r in order.required if r.product_id == stock.product_id
        ]
        tap.eq(len(rp), 2, 'две записи о товаре')
        tap.eq(sum(r.result_count for r in rp), 135, 'result_count проставлен')

        ri = next(
            (r for r in order.required if r.item_id == item.item_id),
            None
        )
        tap.ok(ri, 'required экземпляра найден')
        tap.eq(ri.result_count, 1, 'result_count проставлен')
