# pylint: disable=too-many-statements,too-many-locals
async def test_inventory(tap, dataset, wait_order_status):
    with tap.plan(16, 'отчет в слепой инвентаризации'):
        product = await dataset.product(quants=31)
        store = await dataset.full_store(estatus='inventory')
        await dataset.assortment_contractor_product(
            store=store,
            product=product,
            price=69.69
        )
        user = await dataset.user(store=store)
        stock = await dataset.stock(store=store, count=4, quants=11)
        stock2 = await dataset.stock(
            store=store,
            shelf_id=stock.shelf_id,
            count=3,
            quants=11,
        )

        order = await dataset.order(
            type='inventory_check_more',
            store=store,
            required=[{'shelf_id': stock.shelf_id}],
            status='reserving',
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест на полку')

        with suggests[0] as suggest:

            tap.eq(suggest.shelf_id, stock.shelf_id, 'полка')
            tap.ok(
                await suggest.done(
                    product_id=product.product_id,
                    count=8
                ),
                'саджест закрыт'
            )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order, status='request')
        tap.eq(len(suggests), 1, 'ещё один саджест на полку')
        suggest = suggests[0]

        tap.eq(suggest.type, 'check_more', 'тип')
        tap.eq(suggest.shelf_id, stock.shelf_id, 'полка')
        tap.ok(
            await suggest.done(
                product_id=stock2.product_id,
                count=5
            ),
            'второй саджест закрыт'
        )
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order, status='request')
        tap.eq(len(suggests), 1, 'ещё один саджест на полку')
        suggest = suggests[0]
        tap.ok(
            await suggest.done(status='error'),
            'работу с саджестами завершаем'
        )

        await wait_order_status(
            order,
            ('complete', 'wait_child_done'),
            user_done=user
        )
        tap.eq(
            order.vars('report', None),
            {
                stock.shelf_id:
                    {
                        stock.product_id: {
                            'count': 4,
                            'quants': 11,
                        },
                        stock2.product_id: {
                            'count': 3,
                            'result_count': 5,
                            'quants': 11,
                        },
                        product.product_id: {
                            'result_count': 8,
                            'price': '69.69',
                            'quants': 1,
                        },
                    }
            },
            'Отчет нужного вида'
        )


async def test_kitchen(tap, dataset, wait_order_status):
    with tap.plan(13, 'кухня в слепой инвентаризации'):
        product = await dataset.product()
        store = await dataset.full_store(estatus='inventory')
        shelf1 = await dataset.shelf(store=store, type='kitchen_components')
        shelf2 = await dataset.shelf(store=store, type='kitchen_components')
        await dataset.assortment_contractor_product(
            store=store,
            product=product,
            price=69.69
        )
        user = await dataset.user(store=store)
        await dataset.stock(
            store=store,
            shelf_id=shelf2.shelf_id,
            product_id=product.product_id,
            count=4,
            quants=1
        )
        product.quants = 31
        tap.ok(await product.save(), 'Кванты обновили')

        order = await dataset.order(
            type='inventory_check_more',
            store=store,
            required=[
                {'shelf_id': shelf2.shelf_id},
                {'shelf_id': shelf1.shelf_id},
            ],
            status='reserving',
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'два саджеста')

        for suggest in suggests:
            tap.ok(
                await suggest.done(
                    product_id=product.product_id,
                    count=8
                ),
                'саджест закрыт'
            )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order, status='request')
        tap.eq(len(suggests), 2, 'ещё два саджеста')
        for suggest in suggests:
            tap.ok(
                await suggest.done(status='error'),
                'работу с саджестами завершаем'
            )
        await wait_order_status(
            order,
            ('complete', 'wait_child_done'),
            user_done=user
        )
        tap.eq(
            order.vars('report', None),
            {
                shelf1.shelf_id: {
                    product.product_id: {
                        'result_count': 8,
                        'quants': 31,
                        'price': '69.69',
                    }
                },
                shelf2.shelf_id: {
                    product.product_id: {
                        'count': 4,
                        'result_count': 8,
                        'quants': 1,
                        'price': '69.69',
                    }
                },
            },
            'Отчет нужного вида'
        )
