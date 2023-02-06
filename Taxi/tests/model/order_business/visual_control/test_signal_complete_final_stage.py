async def test_signal_close_suggest(tap, dataset, wait_order_status):
    with tap.plan(16, 'Тест complete_final_stage'):
        banana = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )
        apple = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )
        store = await dataset.store()

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'создали полку')

        await dataset.stock(product=banana, shelf=shelf, count=3)
        await dataset.stock(product=apple, shelf=shelf, count=5)

        trash = await dataset.shelf(type='trash', store=store)
        tap.eq(trash.store_id, store.store_id, 'создали полку списания')

        user = await dataset.user(store=store)
        user_diff = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='visual_control',
            status='processing',
            estatus='begin',
            acks=[user.user_id, user_diff.user_id],
            required=[
                {
                    'product_id': banana.product_id,
                    'shelf_id': shelf.shelf_id,
                },
                {
                    'product_id': apple.product_id,
                    'shelf_id': shelf.shelf_id,
                },
            ],
        )
        await wait_order_status(order, ('processing', 'waiting'))
        order.users = order.users + [user_diff.user_id]
        await order.save(store_job_event=False)
        suggests = await dataset.Suggest.list_by_order(
            order, types='shelf2box', status='request',
        )
        tap.eq(len(suggests), 2, 'саджесты на проверку')

        for s in suggests:
            await s.done(count=1)

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'visual_control', 'visual_control')

        tap.ok(
            await order.signal(
                {
                    'type': 'next_stage',
                },
                user=user_diff,
            ),
            'сигнал next_stage'
        )
        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'trash', 'trash')
        suggests = await dataset.Suggest.list_by_order(
            order, types='box2shelf', status='request',
        )
        tap.eq(len(suggests), 2, 'саджесты на перенос в треш')

        tap.ok(
            await order.signal(
                {
                    'type': 'complete_final_stage',
                },
                user=user_diff,
            ),
            'сигнал отправлен'
        )
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order, types='box2shelf', status='request',
        )
        tap.eq(len(suggests), 0, 'саджесты закрылись')

        suggests = await dataset.Suggest.list_by_order(
            order, types='box2shelf', status='done',
        )
        tap.ok(all(i.vars['closed'] == 'auto' for i in suggests),
               'проросло поле closed в vars')

        tap.ok(all(i.user_done == user_diff.user_id and
                   i.vars['logs'][0]['user'] == user_diff.user_id
                   for i in await
                   dataset.Suggest.list_by_order(order, types='box2shelf')),
               'юзеры проставленны')
