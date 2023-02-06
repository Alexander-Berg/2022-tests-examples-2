# pylint: disable=unused-variable

import random


async def test_empty_snapshot(tap, api, dataset):
    with tap.plan(5, 'пустой снапшот'):
        order = await dataset.order()
        tap.ok(order, 'ордер создан')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_orders_snapshot',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('snapshot_items', [])


async def test_snapshot(tap, api, dataset):
    with tap.plan(15, 'непустой снапшот'):
        order = await dataset.order()
        tap.ok(order, 'ордер создан')

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

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_orders_snapshot',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                            'limit': 10,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_hasnt('snapshot_items.3.product.product_id')
        t.json_has('snapshot_items.9')
        t.json_hasnt('snapshot_items.10')
        t.json_has('snapshot_items.0.quants')
        t.json_has('cursor')

        cursor = t.res['json']['cursor']

        await t.post_ok('api_external_orders_snapshot',
                        json={
                            'order_id': order.order_id,
                            'cursor': cursor,
                            'limit': 10,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('snapshot_items.1')
        t.json_hasnt('snapshot_items.2')
        t.json_is('cursor', None)


async def test_snapshot_bigint(tap, api, dataset):
    with tap.plan(13, 'непустой снапшот с большими числами'):
        order = await dataset.order()
        tap.ok(order, 'ордер создан')

        for _ in range(12):
            product = await dataset.product()
            await dataset.InventoryRecord(
                {
                    'order_id': order.order_id,
                    'shelf_type': 'store',
                    'count': 2700000000,
                    'product_id': product.product_id,
                    'result_count': 7000000000,
                }
            ).save()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_orders_snapshot',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                            'limit': 10,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_hasnt('snapshot_items.3.product.product_id')
        t.json_has('snapshot_items.9')
        t.json_hasnt('snapshot_items.10')
        t.json_has('cursor')

        cursor = t.res['json']['cursor']

        await t.post_ok('api_external_orders_snapshot',
                        json={
                            'order_id': order.order_id,
                            'cursor': cursor,
                            'limit': 10,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('snapshot_items.1.count', 2700000000)
        t.json_is('snapshot_items.1.result_count', 7000000000)


async def test_list_company(tap, dataset, api):
    with tap.plan(6, 'Список по компании'):

        company1 = await dataset.company()
        company2 = await dataset.company()
        store1  = await dataset.store(company=company1)
        store2  = await dataset.store(company=company2)
        product = await dataset.product()

        order1 = await dataset.order(store=store1)
        order2 = await dataset.order(store=store1)

        ir1 = await dataset.inventory_snapshot(order=order1, product=product)
        ir2 = await dataset.inventory_snapshot(order=order2, product=product)

        t = await api(token=company1.token)

        await t.post_ok(
            'api_external_orders_snapshot',
            json={
                'order_id': order1.order_id,
                'cursor': None,
                'limit': 10,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('snapshot_items.0.order_id', order1.order_id)
        t.json_hasnt('snapshot_items.1')
        t.json_has('cursor')
