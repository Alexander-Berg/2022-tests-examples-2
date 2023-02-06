import pytest

# pylint: disable=too-many-locals,too-many-statements
@pytest.mark.parametrize('split', [True, False])
async def test_make_wave(tap, dataset, wait_order_status, uuid, split):
    with tap.plan(42):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        product2 = await dataset.product()
        tap.ok(product2, 'товар 2 создан')

        collect = await dataset.order(
            type='collect',
            store=store,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 227,
                },
                {
                    'product_id': product2.product_id,
                    'count': 123,
                }
            ]
        )
        await wait_order_status(collect, ('processing', 'waiting_stocks'))

        tap.eq(
            await collect.business.make_wave(split=split),
            0,
            'make_wave не создала ничего'
        )

        stock = await dataset.stock(store=store, product=product, count=100)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')
        tap.eq(stock.product_id, product.product_id, 'товар')
        tap.eq(stock.shelf_type, 'store', 'тип полки')
        tap.eq(stock.left, 100, 'количество')

        stock2 = await dataset.stock(
            store=store,
            product=product,
            count=22,
            shelf_id=stock.shelf_id,
            lot=uuid()
        )
        tap.eq(stock2.store_id, store.store_id, 'остаток создан')
        tap.eq(stock2.product_id, product.product_id, 'товар')
        tap.eq(stock2.shelf_type, 'store', 'тип полки')
        tap.eq(stock2.left, 22, 'количество')
        tap.ne(stock2.stock_id, stock.stock_id, 'другой сток')
        tap.eq(stock2.shelf_id, stock.shelf_id, 'на той же полке')

        tap.eq(
            await collect.business.make_wave(split=split),
            1,
            'make_wave создала один ордер'
        )
        tap.eq(
            await collect.business.make_wave(split=split),
            0,
            'make_wave не создала ничего (повтор)'
        )

        children = [
            await dataset.Order.load(oid)
            for oid in collect.vars('hand_move', [])
        ]

        tap.eq(len(children), 1, 'один дочерний ордер')
        with children[0] as o:
            tap.eq(o.parent, [collect.order_id], 'parent')
            tap.eq(o.store_id, store.store_id, 'store_id')
            tap.eq(o.type, 'hand_move', 'type')
            tap.eq(len(o.required), 1, 'required len')
            with o.required[0] as r:
                tap.eq(r.product_id, product.product_id, 'product_id')
                tap.eq(r.count, 100 + 22, 'count')
                tap.eq(r.src_shelf_id, stock.shelf_id, 'shelf_id')


        stock3 = await dataset.stock(
            product=product2,
            count=70,
            store=store,
            reserve=7
        )
        tap.eq(stock3.store_id, store.store_id, 'остаток создан')
        tap.eq(stock3.product_id, product2.product_id, 'товар')
        tap.eq(stock3.left, 70-7, 'доступно остатка')

        stock4 = await dataset.stock(
            product=product,
            count=17,
            store=store,
            reserve=5
        )
        tap.eq(stock4.store_id, store.store_id, 'остаток создан')
        tap.eq(stock4.product_id, product.product_id, 'товар')
        tap.eq(stock4.left, 17-5, 'доступно остатка')

        tap.eq(
            await collect.business.make_wave(split=split),
            1,
            'make_wave создала ещё ордер'
        )

        children = [
            await dataset.Order.load(oid)
            for oid in collect.vars('hand_move', [])
        ]
        tap.eq(len(children), 2, 'ещё один дочерний ордер')
        with children[1] as o:
            tap.eq(o.parent, [collect.order_id], 'parent')
            tap.eq(o.store_id, store.store_id, 'store_id')
            tap.eq(o.type, 'hand_move', 'type')
            tap.eq(len(o.required), 1, 'required len')
            with o.required[0] as r:
                tap.eq(r.product_id, product2.product_id, 'product_id')
                tap.eq(r.count, 70-7, 'count')
                tap.eq(r.src_shelf_id, stock3.shelf_id, 'src_shelf_id')
                tap.eq(r.dst_shelf_id, collect.vars('shelf'), 'dst_shelf_id')
