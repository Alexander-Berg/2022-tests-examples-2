# pylint: disable=too-many-locals, too-many-statements
async def test_close_suggest_trash(tap, uuid, now, dataset, wait_order_status):
    with tap.plan(16, 'Генерация и закрытие саджестов'
                      ' по сигналу для markdown2trash'):
        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10, write_off_before=1)

        assortment = await dataset.assortment()
        await dataset.assortment_product(
            assortment=assortment, product=product2)

        store = await dataset.store(markdown_assortment=assortment)
        user = await dataset.user(store=store)
        user_diff = await dataset.user(store=store)

        shelf = await dataset.shelf(store=store, type='store', order=1)
        await dataset.shelf(store=store, type='trash', order=3)
        mark = await dataset.shelf(store=store, type='markdown', order=4)

        await dataset.stock(
            store=store,
            shelf=shelf,
            product=product1,
            count=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            store=store,
            shelf=mark,
            product=product2,
            count=3,
            valid='2020-01-01',
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            type='check_valid_short',
            status='reserving',
            estatus='begin',
            accepted=now(),
            acks=[user.user_id],
            users=[user.user_id],
            vars={'mode': 'markdown2trash'},
        )
        await wait_order_status(
            order, ('processing', 'reserve_online'), user_done=user,
        )
        order.users = order.users + [user_diff.user_id]
        await order.save(store_job_event=False)
        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user_diff,
        )
        await order.reload()
        tap.eq(order.vars['stage'],
               'control',
               'проставлена стадия control')
        tap.eq(order.vars['suggests_write_off'],
               False,
               'саджесты на списание не сгенерированы')

        tap.ok(
            await order.signal(
                {
                    'type': 'next_stage'
                },
                user=user_diff,
            ),
            'сигнал next_stage'
        )

        await wait_order_status(
            order, ('processing', 'waiting'),
        )

        await order.reload()
        tap.eq(order.vars['stage'], 'trash', 'проставлена стадия')

        await wait_order_status(
            order, ('processing', 'waiting'),
        )
        await order.reload()
        tap.eq(order.vars['suggests_write_off'], True, 'саджесты сгенерированы')

        suggests = await dataset.Suggest.list_by_order(
            order, types=['box2shelf'],
        )
        suggests = dict((s.product_id, s) for s in suggests)
        tap.eq(len(suggests), 2, 'Саджесты на полку уценки')

        await wait_order_status(order, ('processing', 'waiting'))

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

        tap.ok(
            all(
                i.user_done == user_diff.user_id and
                i.vars['logs'][0]['user'] == user_diff.user_id
                for i in await dataset.Suggest.list_by_order(
                    order, types='box2shelf'
                )
            ),
            'юзеры проставленны'
        )
