async def test_stages(tap, dataset, wait_order_status):
    with tap.plan(21, 'стадии списания'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            required=[
                {
                    'product_id': product.product_id,
                    'count': 27,
                    'valid': '2022-11-12',
                },
                {
                    'item_id': item.item_id,
                    'count': 1,
                },
            ],
            type='sale_stowage',
            status='reserving',
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')

        for s in suggests:
            if s.product_id != product.product_id:
                continue
            tap.ok(await s.done(count=1), 'закрыт саджест')

        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(order.vars('stage'), 'stowage', 'состояние')

        version = order.version

        tap.ok(await order.signal({'type': 'sale_stowage'}),
               'сигнал завершения раскладки отправлен')
        with tap.subtest(None, 'Ожидаем перехода в списание') as taps:
            while order.vars('stage') != 'trash':
                await wait_order_status(order,
                                        ('processing', 'waiting'),
                                        tap=taps)
        tap.ne(order.version, version, 'версия изменилась')

        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'саджест раскладки на trash')

        with suggests[0] as s:
            tap.eq(s.vars('stage'), 'trash', 'стадия')
            tap.eq(s.conditions.trash_reason, True, 'требуется ризон')
            tap.eq(s.conditions.max_count, True, 'максимум')
            tap.eq(s.conditions.error, False, 'нельзя закрывать в ошибку')
            tap.eq(s.product_id, product.product_id, 'саджест о товаре')
            tap.eq(s.count, 26, 'количество')
            shelf = await dataset.Shelf.load(s.shelf_id)
            tap.eq(shelf.type, 'trash', 'тип полки-списание')

        await wait_order_status(order, ('complete', 'done'), user_done=user)
