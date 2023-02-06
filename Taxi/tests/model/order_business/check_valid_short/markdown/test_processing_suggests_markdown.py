# pylint: disable=too-many-locals,unused-variable


async def test_waiting_suggests_markdown(
        tap,
        uuid,
        dataset,
        now,
        wait_order_status,
):
    with tap.plan(21, 'Генерация саджестов положить на полку уценки'):

        product1 = await dataset.product(valid=10, write_off_before=1)
        product2 = await dataset.product(valid=10, write_off_before=1)

        assortment = await dataset.assortment()
        await dataset.assortment_product(
            assortment=assortment, product=product1)
        await dataset.assortment_product(
            assortment=assortment, product=product2)

        store = await dataset.store(markdown_assortment=assortment)
        user  = await dataset.user(store=store)

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)

        trash  = await dataset.shelf(store=store, type='trash', order=3)
        mark   = await dataset.shelf(store=store, type='markdown', order=4)

        await dataset.stock(
            store=store,
            shelf=shelf1,
            product=product1,
            count=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            store=store,
            shelf=shelf1,
            product=product1,
            count=3,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            store=store,
            shelf=shelf2,
            product=product2,
            count=20,
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
        )
        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(
            order,
            ('processing', 'suggests_markdown'),
            user_done=user,
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['box2shelf'],
        )
        suggests = dict((s.product_id, s) for s in suggests)
        tap.eq(len(suggests), 2, 'Саджесты на полку уценки')

        with suggests[product1.product_id] as suggest:
            tap.eq(suggest.type, 'box2shelf', 'box2shelf')
            tap.eq(suggest.status, 'request', 'request')
            tap.eq(suggest.product_id, product1.product_id, 'product_id')
            tap.eq(suggest.shelf_id, mark.shelf_id, 'shelf_id')
            tap.eq(suggest.count, 10, 'count')

        with suggests[product2.product_id] as suggest:
            tap.eq(suggest.type, 'box2shelf', 'box2shelf')
            tap.eq(suggest.status, 'request', 'request')
            tap.eq(suggest.product_id, product2.product_id, 'product_id')
            tap.eq(suggest.shelf_id, mark.shelf_id, 'shelf_id')
            tap.eq(suggest.count, 20, 'count')
