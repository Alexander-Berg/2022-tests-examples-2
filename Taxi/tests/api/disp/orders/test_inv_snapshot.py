import random

from libstall.money import Money

async def test_empty_snapshot(tap, api, dataset):
    with tap.plan(6, 'пустой снапшот'):
        user = await dataset.user()
        tap.ok(user.store_id, 'пользователь создан')

        order = await dataset.order(store_id=user.store_id)
        tap.eq(order.store_id, user.store_id, 'ордер создан')

        t = await api(user=user)
        await t.post_ok('api_disp_orders_inventory_snapshot',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('snapshot', [])


async def test_snapshot(tap, api, dataset):
    with tap.plan(16, 'непустой снапшот'):
        user = await dataset.user()
        tap.ok(user.store_id, 'пользователь создан')

        order = await dataset.order(store_id=user.store_id)
        tap.eq(order.store_id, user.store_id, 'ордер создан')

        for _ in range(12):
            product = await dataset.product()
            await dataset.InventoryRecord(
                {
                    'order_id': order.order_id,
                    'shelf_type': 'store',
                    'count': random.randrange(100, 200),
                    'product_id': product.product_id,
                    'result_count': random.randrange(300, 500),
                    'price': Money(69.00),
                }
            ).save()

        t = await api(user=user)
        await t.post_ok('api_disp_orders_inventory_snapshot',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                            'limit': 10,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_hasnt('snapshot.3.product.product_id')
        t.json_has('snapshot.9')
        t.json_hasnt('snapshot.10')
        t.json_has('cursor')

        cursor = t.res['json']['cursor']

        await t.post_ok('api_disp_orders_inventory_snapshot',
                        json={
                            'order_id': order.order_id,
                            'cursor': cursor,
                            'limit': 10,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('snapshot.1')
        t.json_hasnt('snapshot.2')
        t.json_is('cursor', None)
        t.json_is('snapshot.1.price', '69.00')


async def test_snapshot_full(tap, api, dataset):
    with tap.plan(16, 'непустой снапшот'):
        user = await dataset.user()
        tap.ok(user.store_id, 'пользователь создан')

        order = await dataset.order(store_id=user.store_id)
        tap.eq(order.store_id, user.store_id, 'ордер создан')

        for _ in range(12):
            product = await dataset.product()
            await dataset.InventoryRecord(
                {
                    'order_id': order.order_id,
                    'shelf_type': 'store',
                    'count': random.randrange(100, 200),
                    'product_id': product.product_id,
                    'result_count': random.randrange(300, 500),
                }
            ).save()

        t = await api(user=user)
        await t.post_ok('api_disp_orders_inventory_snapshot',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                            'limit': 10,
                            'full': True,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('snapshot.9')
        t.json_has('snapshot.3.product.product_id')
        t.json_has('snapshot.3.product.quants')
        t.json_hasnt('snapshot.10')
        t.json_has('cursor')

        cursor = t.res['json']['cursor']

        await t.post_ok('api_disp_orders_inventory_snapshot',
                        json={
                            'order_id': order.order_id,
                            'cursor': cursor,
                            'limit': 10,
                            'full': True,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('snapshot.1')
        t.json_hasnt('snapshot.2')
        t.json_is('cursor', None)
