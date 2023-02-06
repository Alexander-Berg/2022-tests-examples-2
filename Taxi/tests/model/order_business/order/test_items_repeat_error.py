async def test_repeat_error(tap, dataset, wait_order_status, now):
    with tap.plan(27, 'Проблемы резервирования экземпляра'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр')

        stock = await dataset.stock(
            store=store,
            item=item,
            count=1,
        )
        tap.eq(stock.store_id, store.store_id, 'остаток создан')
        tap.eq(stock.product_id, item.item_id, 'остаток про экземпляр')
        tap.eq(stock.count, 1, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='order',
            required=[{'item_id': item.item_id}],
            vars={'editable': True},
            approved=now(),
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(order.problems, [], 'нет проблем')
        tap.ok(await stock.reload(), 'остаток перегружен')
        tap.eq(stock.reserve, 1, 'зарезервирован экземпляр')


        order2 = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='order',
            required=[{'item_id': item.item_id}],
            vars={'editable': True},
            approved=now(),
        )
        tap.eq(order2.store_id, store.store_id, 'Ещё ордер создан')
        tap.ne(order2.order_id, order.order_id, 'это другой ордер')

        await wait_order_status(order2, ('processing', 'waiting'))
        tap.eq(len(order2.problems), 1, 'проблемы есть')

        suggests = await dataset.Suggest.list_by_order(order2)
        tap.eq([s for s in suggests if s.product_id == item.item_id],
               [],
               'нет саджеста про экземпляр')

        with order2.problems[0] as p:
            tap.eq(p.item_id, item.item_id, 'проблема о экземпляре')
            tap.eq(p.type, 'low', 'тип проблемы')


        tap.ok(await order.cancel(), 'ордер1 отменён')
        await wait_order_status(order, ('canceled', 'done'))
        tap.ok(await stock.reload(), 'остаток перегружен')
        tap.eq(stock.reserve, 0, 'нет резерва')

        order2.vars['required'] = order2.required
        tap.ok(await order2.save(), 'пересохранён')

        await wait_order_status(order2, ('processing', 'waiting'))
        tap.eq(len(order2.problems), 0, 'проблемы отрезолвились')

        suggests = await dataset.Suggest.list_by_order(order2)
        tap.ok([s for s in suggests if s.product_id == item.item_id],
               'есть саджест про экземпляр')
