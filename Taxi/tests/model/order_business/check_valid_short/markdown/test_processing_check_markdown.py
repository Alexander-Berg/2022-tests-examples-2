async def test_check_markdown(tap, uuid, now, dataset, wait_order_status):
    with tap.plan(3, 'Проверка наличия полок для уценки'):

        product1 = await dataset.product(
            valid=10, tags=['freezer'], write_off_before=1)
        product2 = await dataset.product(valid=10, write_off_before=1)

        assortment = await dataset.assortment()
        await dataset.assortment_product(
            assortment=assortment, product=product1)
        await dataset.assortment_product(
            assortment=assortment, product=product2)

        store = await dataset.store(markdown_assortment=assortment)
        user  = await dataset.user(store=store)

        shelf = await dataset.shelf(store=store, type='store', order=1)

        await dataset.shelf(store=store, type='trash', order=99)
        await dataset.shelf(store=store, type='markdown', order=3)
        await dataset.shelf(
            store=store, type='markdown', order=4, tags=['freezer'])

        await dataset.stock(
            store=store,
            shelf=shelf,
            product=product1,
            count=10,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            store=store,
            shelf=shelf,
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

        await wait_order_status(order, ('processing', 'check_markdown'))
        tap.ok(order.vars('write_off'), 'Есть остатки на уценку')

        await order.business.order_changed()

        tap.eq(len(order.problems), 0, 'Нет проблем')


async def test_check_markdown_tags(tap, uuid, now, dataset, wait_order_status):
    with tap.plan(7, 'Если нет подходящей полки уценки'):

        product1 = await dataset.product(
            valid=10, tags=['freezer'], write_off_before=1)

        assortment = await dataset.assortment()
        await dataset.assortment_product(
            assortment=assortment, product=product1)

        store = await dataset.store(markdown_assortment=assortment)
        user  = await dataset.user(store=store)

        shelf = await dataset.shelf(store=store, type='store', order=1)

        await dataset.shelf(store=store, type='trash', order=99)
        await dataset.shelf(store=store, type='markdown', order=3)

        await dataset.stock(
            store=store,
            shelf=shelf,
            product=product1,
            count=10,
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

        await wait_order_status(order, ('processing', 'check_markdown'))
        tap.ok(order.vars('write_off'), 'Есть остатки на уценку')

        await order.business.order_changed()
        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'begin', 'begin')

        tap.eq(len(order.problems), 1, 'Проблема')

        with order.problems[0] as problem:
            tap.eq(problem.type, 'shelf_not_found', 'Тип проблемы')
            tap.eq(problem.shelf_type, 'markdown', 'Тип полки')
