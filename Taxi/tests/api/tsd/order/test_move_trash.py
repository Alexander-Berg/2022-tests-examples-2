from stall.model.stock import Stock


async def test_no_permit(tap, dataset, api, uuid):
    with tap.plan(6, 'Проверка пермитов'):
        store = await dataset.store()
        user = await dataset.user(role='barcode_executer', store=store)

        trash = await dataset.shelf(store_id=store.store_id,
                                    type='trash')
        shelf = await dataset.shelf(store_id=user.store_id,
                                    type='store')

        stock_trash = await dataset.stock(
            store_id=user.store_id,
            reserve=10,
            count=20,
            shelf_id=trash.shelf_id,
        )
        tap.eq(stock_trash.store_id, user.store_id, 'ещё остаток там же')
        tap.eq(stock_trash.shelf_id, trash.shelf_id, 'та же полка')

        t = await api(user=user)
        external_id = uuid()

        request = {
            'product_id': stock_trash.product_id,
            'count': stock_trash.count,
            'src_shelf_id': trash.shelf_id,
            'dst_shelf_id': shelf.shelf_id,
        }
        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': external_id,
                            'move': [request]
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Cannot move from trash without permit')


async def test_no_needed(tap, dataset, api, uuid):
    with tap.plan(4, 'Нет важных параметров'):
        store = await dataset.store()
        user = await dataset.user(role='store_admin', store=store)

        trash = await dataset.shelf(store_id=store.store_id,
                                    type='trash')
        shelf = await dataset.shelf(store_id=user.store_id,
                                    type='store')

        stock_trash = await dataset.stock(
            store_id=user.store_id,
            count=20,
            shelf_id=trash.shelf_id,
        )

        t = await api(user=user)
        external_id = uuid()

        request = {
            'product_id': stock_trash.product_id,
            'count': stock_trash.count,
            'src_shelf_id': trash.shelf_id,
            'dst_shelf_id': shelf.shelf_id,
        }
        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': external_id,
                            'move': [request]
                        })
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('details.errors.0.code', 'ER_WRONG_REQUIRED')
        t.json_is('details.errors.0.message',
                  'Moving from trash required stock_id and stock reason')


async def test_no_stock(tap, dataset, api, uuid):
    with tap.plan(4, 'Хотим больше чем могем взять'):
        store = await dataset.store()
        user = await dataset.user(role='store_admin', store=store)

        trash = await dataset.shelf(store_id=store.store_id,
                                    type='trash')
        shelf = await dataset.shelf(store_id=user.store_id,
                                    type='store')

        stock_trash = await dataset.stock(
            store_id=user.store_id,
            count=20,
            shelf_id=trash.shelf_id,
        )

        t = await api(user=user)
        external_id = uuid()

        request = {
            'product_id': stock_trash.product_id,
            'count': stock_trash.count*2,
            'stock_id': stock_trash.stock_id,
            'reason': {'code': 'TRASH_TTL'},
            'src_shelf_id': trash.shelf_id,
            'dst_shelf_id': shelf.shelf_id,
            'move_order_id': uuid()
        }
        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': external_id,
                            'move': [request]
                        })
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('details.errors.0.code', 'ER_CONFLICT')
        t.json_is('details.errors.0.message',
                  'No such stocklog or stock')


# pylint: disable=too-many-locals
async def test_more_than_can(tap, dataset, api, uuid, wait_order_status):
    with tap.plan(7, 'Пытаемся взять больше чем положенно'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='store_admin')
        src_shelf = await dataset.shelf(store_id=store.store_id,
                                        type='store')
        stock = await dataset.stock(
            shelf=src_shelf,
            valid='2020-01-01',
            lot=uuid(),
        )
        trash = await dataset.shelf(store_id=stock.store_id,
                                    type='trash')

        order = await dataset.order(
            type='move',
            status='reserving',
            estatus='begin',
            store_id=stock.store_id,
            user_id=user.user_id,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 10,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': trash.shelf_id,
                    'reason_code': 'OPTIMIZE',
                }
            ]
        )

        await wait_order_status(order, ('complete', 'done'))

        stocks = [
            s for s in await Stock.list_by_product(
                product_id=stock.product_id,
                store_id=stock.store_id,
                shelf_type='trash',
            ) if s.count
        ]

        tap.eq(len(stocks), 1, 'получился 1 сток')
        tap.eq(len(stocks[0].vars['reasons']), 1, 'добавлен reason')

        trash_stock = stocks[0]
        t = await api(user=user)
        external_id = uuid()

        request = {
            'product_id': trash_stock.product_id,
            'count': trash_stock.count * 2,
            'stock_id': trash_stock.stock_id,
            'reason': {'code': 'TRASH_TTL'},
            'src_shelf_id': trash.shelf_id,
            'dst_shelf_id': src_shelf.shelf_id,
            'move_order_id': order.order_id
        }
        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': external_id,
                            'move': [request]
                        })

        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('details.errors.0.code', 'ER_COUNT_OR_RESERVE')
        t.json_is('details.errors.0.message',
                  'Too many product to get from trash')


async def test_trash(tap, dataset, api, uuid):
    with tap.plan(4, 'Проверка, что с треша делаем одним документом'):
        store = await dataset.store()
        user = await dataset.user(role='store_admin', store=store)
        trash = await dataset.shelf(store_id=store.store_id,
                                    type='trash')
        shelf = await dataset.shelf(store_id=user.store_id,
                                     type='store')
        shelf_dest = await dataset.shelf(store_id=user.store_id,
                                    type='store')

        stock = await dataset.stock(
            store_id=user.store_id,
            reserve=10,
            count=20,
            shelf_id=shelf.shelf_id,
        )

        stock_trash = await dataset.stock(
            store_id=user.store_id,
            reserve=10,
            count=20,
            shelf_id=trash.shelf_id,
        )

        t = await api(user=user)
        external_id = uuid()

        request1 = {
            'product_id': stock_trash.product_id,
            'count': stock_trash.count,
            'src_shelf_id': trash.shelf_id,
            'dst_shelf_id': shelf_dest.shelf_id,
        }

        request2 = {
            'product_id': stock.product_id,
            'count': stock.count,
            'src_shelf_id': shelf.shelf_id,
            'dst_shelf_id': shelf_dest.shelf_id,
        }

        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': external_id,
                            'move': [request1, request2]
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Cannot move to different shelves if any trash')
