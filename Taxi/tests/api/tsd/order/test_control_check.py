from aiohttp import web

from stall import log
from stall.client.onec import client as onec_client


async def test_happy_flow(
    tap, dataset, ext_api, api, uuid, cfg, wait_order_status,
):
    # pylint: disable=too-many-locals
    with tap.plan(22, 'хеппи флоу, успешно создаем ордер'):
        cfg.set('sync.1c.login', 'login')
        cfg.set('sync.1c.password', 'password')

        store = await dataset.store(type='dc')
        user = await dataset.user(store=store)
        acc = await dataset.order(
            type='acceptance',
            required=[
                {'product_id': '111', 'count': 12},
                {'product_id': '222', 'count': 3},
            ]
        )
        pallet_barcode = uuid()
        target_store_id = acc.store_id
        acc_id = acc.order_id
        external_id = uuid()

        async def handle_info_pallets(req):  # pylint: disable=unused-argument
            return web.json_response(
                status=200,
                data={
                    'stores': [{
                        'store_id': target_store_id,
                        'pallets': [{
                            'barcode': pallet_barcode,
                            'type': ['zhopka_v_holode'],
                            'acceptance_id': [acc_id],
                        }],
                    }],
                }
            )

        t = await api(user=user)
        async with await ext_api(onec_client, handle_info_pallets):
            await t.post_ok(
                'api_tsd_order_control_check',
                json={
                    'order_id': external_id,
                    'shelf_barcode': pallet_barcode,
                }
            )
        t.status_is(200)
        t.json_is('code', 'OK')
        t.json_is('message', 'Order created')
        t.json_is('order.type', 'control_check')
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.vars.target_store_id', target_store_id)
        t.json_is('order.vars.acceptance_ids', [acc_id])

        cc = await dataset.Order.load(
            (store.store_id, external_id), by='external',
        )
        tap.eq(cc.external_id, external_id, 'внешний айди')
        tap.eq(cc.store_id, store.store_id, 'лавка')
        tap.eq(cc.company_id, store.company_id, 'компания')
        tap.eq(cc.type, 'control_check', 'тип')
        tap.eq(cc.source, 'tsd', 'с тсдшки прилетело')
        tap.eq(cc.vars['target_store_id'], target_store_id, 'целевая лавка')
        tap.eq(cc.vars['has_refrigerator'], False, 'не нужна морозилка')
        tap.eq(cc.vars['shelves_to_check'], [pallet_barcode], 'полки')
        tap.eq(cc.vars['acceptance_ids'], [acc_id], 'айдишники приемок')

        await wait_order_status(cc, ('processing', 'waiting'))
        await t.post_ok(
            'api_tsd_order_complete_control_check',
            json={
                'order_id': cc.order_id,
                'report': [{
                    'product_id': '111',
                    'count': 123,
                    'shelf_barcode': 'YAY123',
                }],
            },
        )
        t.status_is(200)

        await cc.reload()
        await wait_order_status(cc, ('complete', 'begin'), user_done=user)

        async def handle_scan_data(req):
            rj = await req.json()
            log.error('работаем', res=rj['result'])
            return web.json_response(status=200)

        async with await ext_api(onec_client, handle_scan_data):
            await wait_order_status(cc, ('complete', 'done'), user_done=user)


async def test_bad_store(tap, dataset, api, uuid):
    with tap.plan(6, 'лавка кривая'):
        store1 = await dataset.store()
        store2 = await dataset.store(type='dc', estatus='inventory')
        user1 = await dataset.user(store=store1)
        user2 = await dataset.user(store=store2)

        t = await api(user=user1)
        await t.post_ok(
            'api_tsd_order_control_check',
            json={
                'order_id': uuid(),
                'shelf_barcode': uuid(),
            }
        )
        t.status_is(400)
        t.json_is('message', 'Wrong store type')

        t = await api(user=user2)
        await t.post_ok(
            'api_tsd_order_control_check',
            json={
                'order_id': uuid(),
                'shelf_barcode': uuid(),
            }
        )
        t.status_is(423)
        t.json_is('message', 'Can not do it in current store mode')


async def test_onec_dead(tap, dataset, api, uuid, ext_api, cfg):
    with tap.plan(4, '1с типа вскрылся'):
        cfg.set('sync.1c.login', 'login')
        cfg.set('sync.1c.password', 'password')

        store = await dataset.store(type='dc')
        user = await dataset.user(store=store)

        async def handle_info_pallets(req):  # pylint: disable=unused-argument
            return web.json_response(status=420)

        t = await api(user=user)
        async with await ext_api(onec_client, handle_info_pallets):
            await t.post_ok(
                'api_tsd_order_control_check',
                json={
                    'order_id': uuid(),
                    'shelf_barcode': uuid(),
                }
            )
        t.status_is(424)
        t.json_is('code', 'ER_EXTERNAL_SERVICE')
        t.json_is('message', 'ERP hasnt answered')


async def test_many_stores(tap, dataset, api, uuid, ext_api, cfg):
    with tap.plan(4, 'много конечных лавок'):
        cfg.set('sync.1c.login', 'login')
        cfg.set('sync.1c.password', 'password')

        store = await dataset.store(type='dc')
        user = await dataset.user(store=store)

        async def handle_info_pallets(req):  # pylint: disable=unused-argument
            return web.json_response(
                status=200,
                data={
                    'stores': [
                        {
                            'store_id': uuid(),
                            'pallets': [{
                                'barcode': uuid(),
                                'type': ['zhopka_v_holode'],
                                'acceptance_id': [uuid()],
                            }]
                        }
                        for _ in range(2)
                    ],
                },
            )

        t = await api(user=user)
        async with await ext_api(onec_client, handle_info_pallets):
            await t.post_ok(
                'api_tsd_order_control_check',
                json={
                    'order_id': uuid(),
                    'shelf_barcode': uuid(),
                }
            )
        t.status_is(409)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Too many stores in result')


async def test_no_shelves(tap, dataset, api, uuid, ext_api, cfg):
    with tap.plan(4, 'много конечных лавок'):
        cfg.set('sync.1c.login', 'login')
        cfg.set('sync.1c.password', 'password')

        store = await dataset.store(type='dc')
        user = await dataset.user(store=store)

        async def handle_info_pallets(req):  # pylint: disable=unused-argument
            return web.json_response(status=200, data={'stores': []})

        t = await api(user=user)
        async with await ext_api(onec_client, handle_info_pallets):
            await t.post_ok(
                'api_tsd_order_control_check',
                json={
                    'order_id': uuid(),
                    'shelf_barcode': uuid(),
                }
            )
        t.status_is(409)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'ERP data doesnt contain original pallet')


async def test_test_mode(
    tap, dataset, api, uuid, wait_order_status,
):
    with tap.plan(22, 'хеппи флоу, но создаем в тестовом режиме без 1с'):
        store = await dataset.store(type='dc')
        user = await dataset.user(store=store)
        acc = await dataset.order(
            type='acceptance',
            required=[
                {'product_id': '111', 'count': 3},
                {'product_id': '222', 'count': 6},
            ]
        )
        pallet_barcode = uuid()
        target_store_id = acc.store_id
        acc_id = acc.order_id
        external_id = uuid()

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_control_check',
            json={
                'order_id': external_id,
                'shelf_barcode': pallet_barcode,
                'test': {
                    'stores': [{
                        'store_id': target_store_id,
                        'pallets': [{
                            'barcode': pallet_barcode,
                            'type': ['zhopka_v_holode'],
                            'acceptance_id': [acc_id],
                        }],
                    }],
                }
            }
        )
        t.status_is(200)
        t.json_is('code', 'OK')
        t.json_is('message', 'Order created')
        t.json_is('order.type', 'control_check')
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.vars.target_store_id', target_store_id)
        t.json_is('order.vars.acceptance_ids', [acc_id])
        t.json_is('order.vars.test', True)

        cc = await dataset.Order.load(
            (store.store_id, external_id), by='external',
        )
        tap.eq(cc.external_id, external_id, 'внешний айди')
        tap.eq(cc.store_id, store.store_id, 'лавка')
        tap.eq(cc.company_id, store.company_id, 'компания')
        tap.eq(cc.type, 'control_check', 'тип')
        tap.eq(cc.source, 'tsd', 'с тсдшки прилетело')
        tap.eq(cc.vars['target_store_id'], target_store_id, 'целевая лавка')
        tap.eq(cc.vars['has_refrigerator'], False, 'не нужна морозилка')
        tap.eq(cc.vars['shelves_to_check'], [pallet_barcode], 'полки')
        tap.eq(cc.vars['acceptance_ids'], [acc_id], 'айдишники приемок')

        await wait_order_status(cc, ('processing', 'waiting'))
        await t.post_ok(
            'api_tsd_order_complete_control_check',
            json={
                'order_id': cc.order_id,
                'report': [{
                    'product_id': '111',
                    'count': 123,
                    'shelf_barcode': 'YAY123',
                }],
            },
        )
        t.status_is(200)

        await cc.reload()
        await wait_order_status(cc, ('complete', 'done'), user_done=user)
