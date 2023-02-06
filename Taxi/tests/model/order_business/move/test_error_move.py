from stall.model.stock import Stock


async def test_error(tap, dataset, uuid, wait_order_status):
    with tap.plan(13, 'обычное перемещение'):
        stock = await dataset.stock()
        tap.ok(stock, 'остаток создан')

        stock2 = await dataset.stock(
            store_id=stock.store_id,
            shelf_id=stock.shelf_id,
            product_id=stock.product_id,
            lot=uuid(),
        )
        tap.eq(stock2.product_id, stock.product_id, 'остаток 2 создан')
        tap.eq(stock2.shelf_id, stock.shelf_id, 'полка')
        tap.eq(stock2.store_id, stock.store_id, 'склад')
        tap.ne(stock2.stock_id, stock.stock_id, 'другой остаток')

        shelf = await dataset.shelf(store_id=stock.store_id)
        tap.eq(shelf.store_id, stock.store_id, 'полка создана')

        order = await dataset.order(
            type='move',
            status='reserving',
            estatus='begin',
            store_id=stock.store_id,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': sum([stock.count + stock2.count - 1]),
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                }
            ]
        )
        tap.eq(order.store_id, stock2.store_id, 'ордер создан')

        order2 = await dataset.order(store_id=stock.store_id)
        tap.eq(order2.store_id, order.store_id, 'второй ордер создан')

        tap.ok(await stock.do_reserve(order2, 1),
               'товар на одном стоке зарезервирован')


        await wait_order_status(order, ('failed', 'done'))

        stocks = [
            s for s in await Stock.list_by_product(
                product_id=stock.product_id,
                store_id=stock.store_id,
            ) if s.count
        ]

        tap.eq(len(stocks), 2, 'осталось два стока')

        count = sum(s.count for s in stocks if s.shelf_id == stock.shelf_id)
        reserve = sum(s.reserve for s in stocks
                      if s.shelf_id == stock.shelf_id)
        tap.eq(count, stock.count + stock2.count, 'осталось на старой полке')
        tap.eq(reserve, 1, 'один резерв')


async def test_error_zero_stock(tap, dataset, wait_order_status):
    with tap.plan(10, 'на полке ноль товара'):
        stock = await dataset.stock(count=1)
        tap.ok(stock, 'остаток создан')
        tap.eq(stock.count, 1, 'количество остатков')


        shelf = await dataset.shelf(store_id=stock.store_id)
        tap.eq(shelf.store_id, stock.store_id, 'полка создана')

        order = await dataset.order(
            type='move',
            status='reserving',
            estatus='begin',
            store_id=stock.store_id,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 5,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                }
            ]
        )

        await wait_order_status(order, ('failed', 'done'))
        tap.ok(await order.reload(), 'перегружен')
        tap.eq(len(order.problems), 1, 'одна проблема')
        with order.problems[0] as p:
            tap.eq(p.type, 'low', 'тип')
            tap.eq(p.shelf_id, stock.shelf_id, 'полка')
            tap.eq(p.count, 4, 'количество')
            tap.eq(p.product_id, stock.product_id, 'товар')


async def test_required_problems(tap, dataset, wait_order_status, uuid):
    with tap.plan(6, 'Проблемы с required'):
        store = await dataset.store(options={'exp_illidan': True})
        stock = await dataset.stock(store=store)
        tap.ok(stock, 'Остаток ')
        kitchen_shelf = await dataset.shelf(
            type='kitchen_components', store_id=stock.store_id)
        office_shelf = await dataset.shelf(
            type='office', store_id=stock.store_id)
        tap.ok(stock, 'Сток создан')
        order = await dataset.order(
            type='move',
            status='reserving',
            estatus='begin',
            store_id=stock.store_id,
            required=[
                # ok
                {
                    'product_id': stock.product_id,
                    'count': 32,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': kitchen_shelf.shelf_id,
                },

                # duplicate
                {
                    'product_id': stock.product_id,
                    'count': 30,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': kitchen_shelf.shelf_id,
                },

                # components -/-> store
                {
                    'product_id': stock.product_id,
                    'count': 30,
                    'src_shelf_id': kitchen_shelf.shelf_id,
                    'dst_shelf_id': stock.shelf_id,
                },

                # no movement
                {
                    'product_id': stock.product_id,
                    'count': 2,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': stock.shelf_id,
                },

                # unknown shelf
                {
                    'product_id': stock.product_id,
                    'count': 2,
                    'src_shelf_id': uuid(),
                    'dst_shelf_id': stock.shelf_id,
                },

                # product -/-> office
                {
                    'product_id': stock.product_id,
                    'count': 73,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': office_shelf.shelf_id,
                },

                # consumable -/-> store
                {
                    'product_id': stock.product_id,
                    'count': 73,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': office_shelf.shelf_id,
                },

            ]
        )
        tap.ok(order, 'Ордер создан')
        await wait_order_status(order, ('failed', 'done'))
        tap.eq(len(order.problems), 5, 'пять проблем')
        tap.eq(
            {p.type for p in order.problems},
            {
                'no_move_detected',
                'required_duplicate',
                'shelf_not_found',
                'non_component_shelf',
                'non_consumable_product_to_office',
            },
            'Все типы проблем'
        )
