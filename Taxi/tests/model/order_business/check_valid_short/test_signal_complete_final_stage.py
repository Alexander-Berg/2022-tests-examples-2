async def test_close_suggest_store(tap,
                                   uuid,
                                   now,
                                   dataset,
                                   wait_order_status):
    with tap.plan(12, 'Генерация и закрытие саджестов'
                      ' по сигналу для store2markdown'):

        product = await dataset.product(valid=10, write_off_before=1)
        assortment = await dataset.assortment()
        await dataset.assortment_product(assortment=assortment, product=product)

        store = await dataset.store(markdown_assortment=assortment)
        user  = await dataset.user(store=store)

        shelf  = await dataset.shelf(store=store, type='store', order=1)
        await dataset.shelf(store=store, type='trash', order=3)
        await dataset.shelf(store=store, type='markdown', order=4)

        await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=3,
            valid='2020-01-01',
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            accepted=now(),
            acks=[user.user_id],
            vars={'mode': 'store2markdown'},
        )

        await wait_order_status(
            order,
            ('processing', 'reserve_online'),
            user_done=user,
        )
        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )
        await order.reload()
        tap.eq(order.vars['stage'],
               'control',
               'проставлена стадия control')
        tap.eq(order.vars['suggests_write_off'],
               False,
               'саджесты на списание не сгенерированы')

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )

        await order.reload()
        tap.eq(order.vars['stage'], 'trash', 'проставлена стадия')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )

        suggests = await dataset.Suggest.list_by_order(
            order, types='box2shelf', status='request',
        )

        suggests = dict((s.product_id, s) for s in suggests)
        tap.eq(len(suggests), 1, 'Саджесты на полку уценки')

        tap.ok(
            await order.signal(
                {
                    'type': 'complete_final_stage',
                }
            ),
            'сигнал отправлен'
        )
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order, types='box2shelf', status='request',
        )
        tap.eq(len(suggests), 0, 'саджесты закрылись')
