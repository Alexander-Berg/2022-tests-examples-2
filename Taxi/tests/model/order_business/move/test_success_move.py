import pytest

from stall.model.stock import Stock


@pytest.mark.parametrize('shelf_status', ['active', 'disabled'])
async def test_success(tap, dataset, uuid, wait_order_status, shelf_status):
    with tap.plan(14, 'обычное перемещение'):
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

        shelf = await dataset.shelf(store_id=stock.store_id,
                                    status=shelf_status)
        tap.eq(shelf.store_id, stock.store_id, 'полка создана')

        user = await dataset.user()
        order = await dataset.order(
            type='move',
            status='reserving',
            estatus='begin',
            store_id=stock.store_id,
            user_id=user.user_id,
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

        await wait_order_status(order, ('complete', 'done'))

        stocks = [
            s for s in await Stock.list_by_product(
                product_id=stock.product_id,
                store_id=stock.store_id,
            ) if s.count
        ]
        tap.eq(len(stocks), 3, 'получилось три стока')

        count = sum(s.count for s in stocks if s.shelf_id == stock.shelf_id)
        reserve = sum(s.reserve for s in stocks
                      if s.shelf_id == stock.shelf_id)
        tap.eq(count, 1, 'осталось на старой полке')
        tap.eq(reserve, 0, 'нет зарезервированного')

        count = sum(s.count for s in stocks if s.shelf_id == shelf.shelf_id)
        reserve = sum(s.reserve for s in stocks
                      if s.shelf_id == shelf.shelf_id)
        tap.eq(count, sum([stock.count + stock2.count - 1]), 'На новой полке')
        tap.eq(reserve, 0, 'а резерва нет')
        await order.reload()
        tap.eq(order.user_done, user.user_id, 'user_done правильно выставлен')


# pylint: disable=too-many-locals
@pytest.mark.parametrize('src_shelf_type,dst_shelf_type,nomenclature_type',
                         [('store', 'store', 'product'),
                          ('office', 'office', 'consumable'),
                          ('store', 'repacking', 'product'),
                          ])
async def test_success_type(tap, dataset, uuid, wait_order_status,
                            src_shelf_type, dst_shelf_type, nomenclature_type):
    with tap.plan(14, 'обычное перемещение'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        src_shelf = await dataset.shelf(store_id=store.store_id,
                                        type=src_shelf_type)
        product = await dataset.product(vars={
            'imported': {
                'nomenclature_type': nomenclature_type,
            }
        })
        stock = await dataset.stock(
            shelf=src_shelf,
            product=product,
        )
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

        shelf = await dataset.shelf(store_id=stock.store_id,
                                    type=dst_shelf_type)
        tap.eq(shelf.store_id, stock.store_id, 'полка создана')

        order = await dataset.order(
            type='move',
            status='reserving',
            estatus='begin',
            store_id=stock.store_id,
            user_id=user.user_id,
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

        await wait_order_status(order, ('complete', 'done'))

        stocks = [
            s for s in await Stock.list_by_product(
                product_id=stock.product_id,
                store_id=stock.store_id,
                shelf_type=[dst_shelf_type, src_shelf_type],
            ) if s.count
        ]

        tap.eq(len(stocks), 3, 'получилось три стока')

        count = sum(s.count for s in stocks if s.shelf_id == stock.shelf_id)
        reserve = sum(s.reserve for s in stocks
                      if s.shelf_id == stock.shelf_id)
        tap.eq(count, 1, 'осталось на старой полке')
        tap.eq(reserve, 0, 'нет зарезервированного')

        count = sum(s.count for s in stocks if s.shelf_id == shelf.shelf_id)
        reserve = sum(s.reserve for s in stocks
                      if s.shelf_id == shelf.shelf_id)
        tap.eq(count, sum([stock.count + stock2.count - 1]), 'На новой полке')
        tap.eq(reserve, 0, 'а резерва нет')
        await order.reload()
        tap.eq(order.user_done, user.user_id, 'user_done правильно выставлен')


async def test_success_trash(tap, dataset, uuid, wait_order_status):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        src_shelf = await dataset.shelf(store_id=store.store_id,
                                        type='store')
        stock = await dataset.stock(
            shelf=src_shelf,
            valid='2020-01-01',
            lot=uuid(),
        )
        tap.ok(stock, 'остаток создан')
        shelf = await dataset.shelf(store_id=stock.store_id,
                                    type='trash')
        tap.eq(shelf.store_id, stock.store_id, 'полка создана')

        # Первое перемещение
        order = await dataset.order(
            type='move',
            status='reserving',
            estatus='begin',
            store_id=stock.store_id,
            user_id=user.user_id,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 3,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                    'reason_code': 'OPTIMIZE',
                }
            ]
        )
        tap.eq(order.store_id, stock.store_id, 'ордер создан')

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

        count = sum(s.count for s in stocks if s.shelf_id == stock.shelf_id)
        reserve = sum(s.reserve for s in stocks
                      if s.shelf_id == stock.shelf_id)
        tap.eq(count, 0, 'осталось на старой полке')
        tap.eq(reserve, 0, 'нет зарезервированного')

        count = sum(s.count for s in stocks if s.shelf_id == shelf.shelf_id)
        reserve = sum(s.reserve for s in stocks
                      if s.shelf_id == shelf.shelf_id)

        tap.eq(count, 3, 'На новой полке')
        tap.eq(reserve, 0, 'а резерва нет')
        await order.reload()
        tap.eq(order.user_done, user.user_id, 'user_done правильно выставлен')

        # Второе перемещение

        order = await dataset.order(
            type='move',
            status='reserving',
            estatus='begin',
            store_id=stock.store_id,
            user_id=user.user_id,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 5,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                    'reason_code': 'TRASH_DAMAGE',
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
        tap.eq(len(stocks[0].vars['reasons']), 2, 'добавлен reason')

        count = sum(s.count for s in stocks if s.shelf_id == shelf.shelf_id)
        reserve = sum(s.reserve for s in stocks
                      if s.shelf_id == shelf.shelf_id)

        tap.eq(count, 8, 'На новой полке')
        tap.eq(reserve, 0, 'а резерва нет')

        # Третье перемещение
        order = await dataset.order(
            type='move',
            status='reserving',
            estatus='begin',
            store_id=stock.store_id,
            user_id=user.user_id,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 6,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
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
        tap.eq(len(stocks[0].vars['reasons']), 3, 'добавлен reason')

        count = sum(s.count for s in stocks if s.shelf_id == shelf.shelf_id)
        reserve = sum(s.reserve for s in stocks
                      if s.shelf_id == shelf.shelf_id)

        tap.eq(count, 14, 'На новой полке')
        tap.eq(reserve, 0, 'а резерва нет')
