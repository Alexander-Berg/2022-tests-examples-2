async def test_update_requirements(tap, dataset, wait_order_status):
    with tap.plan(9, 'Обновление required после раскладки'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')


        order = await dataset.order(
            status='reserving',
            estatus='begin',
            type='stowage',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 127,
                    'maybe_count': True,
                    'valid': '2021-01-12',
                }
            ],
            store=store,
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'заказ создан')


        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.ok(await s.done(count=275), 'закрыт')


        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.eq(order.required[0].result_count, 275, 'итоговое количество')
