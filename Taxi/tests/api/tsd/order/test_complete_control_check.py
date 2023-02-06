from aiohttp import web

from stall import log
from stall.client.onec import client as onec_client


async def test_happy_flow(tap, dataset, api, wait_order_status, ext_api, cfg):
    with tap.plan(9, 'хеппи флоу'):
        cfg.set('sync.1c.login', 'login')
        cfg.set('sync.1c.password', 'password')

        store = await dataset.store(type='dc')
        user = await dataset.user(store=store)
        cc = await dataset.order(
            type='control_check',
            status='processing',
            estatus='waiting',
            store=store,
            acks=[user.user_id],
            users=[user.user_id],
            vars={'target_store_id': '420abc1337'},
        )

        t = await api(user=user)
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
        t.json_is('code', 'OK')
        t.json_is('order_id', cc.order_id)

        stash = await dataset.Stash.load(
            f'{cc.order_id}_control_check_report', by='name',
        )
        tap.ok(stash, 'загрузили стэш')
        report = stash.value['report']
        tap.eq(len(report), 1, 'один продукт')
        tap.eq(
            report[0],
            {
                'product_id': '111',
                'count': 123,
                'shelf_barcode': 'YAY123',
            },
            'отчет о саджестах',
        )

        await cc.reload()
        await wait_order_status(cc, ('complete', 'begin'), user_done=user)

        async def handle_scan_data(req):
            rj = await req.json()
            log.error('работаем', res=rj['result'])
            return web.json_response(status=200)

        async with await ext_api(onec_client, handle_scan_data):
            await wait_order_status(cc, ('complete', 'done'), user_done=user)


async def test_bad_order(tap, dataset, api):
    with tap.plan(6, 'ордер кривой'):
        store = await dataset.store(type='dc')
        user = await dataset.user(store=store)
        not_cc = await dataset.order(
            status='processing',
            store=store,
            users=[user.user_id],
        )
        cc_bad = await dataset.order(
            status='processing',
            type='control_check',
            users=[user.user_id],
            store=store,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_complete_control_check',
            json={
                'order_id': not_cc.order_id,
                'report': [{
                    'product_id': '111',
                    'count': 123,
                    'shelf_barcode': 'YAY123',
                }],
            },
        )
        t.status_is(400)
        t.json_is('message', 'Wrong order type')

        await t.post_ok(
            'api_tsd_order_complete_control_check',
            json={
                'order_id': cc_bad.order_id,
                'report': [{
                    'product_id': '111',
                    'count': 123,
                    'shelf_barcode': 'YAY123',
                }],
            },
        )
        t.status_is(409)
        t.json_is('message', 'Wrong order status')


async def test_alrdy_complete(tap, dataset, api):
    with tap.plan(10, 'не дублируем действия при запусках'):
        store = await dataset.store(type='dc')
        user = await dataset.user(store=store)
        cc = await dataset.order(
            type='control_check',
            status='processing',
            estatus='waiting',
            store=store,
            acks=[user.user_id],
            users=[user.user_id],
            vars={'target_store_id': '420abc1337'},
        )

        t = await api(user=user)
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
        t.json_is('code', 'OK')
        t.json_is('order_id', cc.order_id)

        stash = await dataset.Stash.load(
            f'{cc.order_id}_control_check_report', by='name',
        )
        tap.ok(stash, 'загрузили стэш')

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
        t.json_is('code', 'OK')
        t.json_is('order_id', cc.order_id)

        old_stash_lsn = stash.lsn
        stash = await dataset.Stash.load(
            f'{cc.order_id}_control_check_report', by='name',
        )
        tap.eq(stash.lsn, old_stash_lsn, 'ничего не делали')


async def test_broken_order(tap, dataset, api):
    with tap.plan(12, 'не можем прикопать имя стеша в варсы'):
        store = await dataset.store(type='dc')
        user = await dataset.user(store=store)
        cc = await dataset.order(
            type='control_check',
            target='canceled',
            user_done=user.user_id,
            status='processing',
            estatus='waiting',
            store=store,
            acks=[user.user_id],
            users=[user.user_id],
            vars={'target_store_id': '420abc1337'},
        )

        t = await api(user=user)
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
        t.status_is(409)
        t.json_is('message', 'Closing order failed')

        cc.user_done = None
        await cc.save()
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
        t.status_is(409)
        t.json_is('message', 'Closing order failed')

        stash = await dataset.Stash.load(
            f'{cc.order_id}_control_check_report', by='name',
        )
        tap.ok(stash, 'загрузили стэш')

        cc.target = 'complete'
        await cc.save()

        await t.post_ok(
            'api_tsd_order_complete_control_check',
            json={
                'order_id': cc.order_id,
                'report': [{
                    'product_id': '112',
                    'count': 123,
                    'shelf_barcode': 'YAY123',
                }],
            },
        )
        t.status_is(200)
        stash_new = await dataset.Stash.load(
            f'{cc.order_id}_control_check_report', by='name',
        )
        tap.ok(stash_new, 'загрузили стэш')
        tap.eq(stash.stash_id, stash_new.stash_id, 'тот же стеш')
        tap.eq(stash.value, stash_new.value, 'велью не тронули')
