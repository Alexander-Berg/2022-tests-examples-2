from aiohttp import web

from stall.api.tsd.order.complete_control_check import process
from stall.client.onec import client as onec_client


async def test_happy_flow_full(
    tap, dataset, ext_api, cfg, wait_order_status,
):
    with tap.plan(3, 'проходим весь ордер'):
        cfg.set('sync.1c.login', 'login')
        cfg.set('sync.1c.password', 'password')

        store = await dataset.store(type='dc')
        user = await dataset.user(store=store)
        acc = await dataset.order(
            type='acceptance',
            required=[
                {
                    'product_id': '111',
                    'count': 1,
                },
                {
                    'product_id': '222',
                    'count': 2,
                }
            ],
        )

        cc = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='control_check',
            vars={
                'acceptance_ids': [acc.order_id],
                'target_store_id': acc.store_id,
            },
        )

        await wait_order_status(cc, ('processing', 'waiting'))
        await process(
            report=[{
                'product_id': '111',
                'count': 123,
                'shelf_barcode': 'YAY123',
            }],
            order=cc,
            cur_user=user,
        )
        await wait_order_status(cc, ('complete', 'begin'), user_done=user)

        async def handle_scan_data(req):
            rj = await req.json()
            assert 'dc_store_id' in rj, 'хых'
            assert 'store_id' in rj, 'хах'
            assert 'result' in rj, 'хех'
            return web.json_response(status=200)

        async with await ext_api(onec_client, handle_scan_data):
            await wait_order_status(cc, ('complete', 'done'), user_done=user)


async def test_1c_lag_but_happy(
    tap, dataset, ext_api, cfg, wait_order_status, uuid,
):
    with tap.plan(6, 'в конце 1с барахлит'):
        cfg.set('sync.1c.login', 'login')
        cfg.set('sync.1c.password', 'password')

        store = await dataset.store(type='dc')
        user = await dataset.user(store=store)
        acc = await dataset.order(
            type='acceptance',
            required=[
                {
                    'product_id': '111',
                    'count': 1,
                },
                {
                    'product_id': '222',
                    'count': 2,
                }
            ],
        )

        cc = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='control_check',
            vars={
                'acceptance_ids': [acc.order_id],
                'target_store_id': acc.store_id,
            },
        )

        await wait_order_status(cc, ('processing', 'waiting'))
        await process(
            report=[{
                'product_id': '111',
                'count': 123,
                'shelf_barcode': 'YAY123',
            }],
            order=cc,
            cur_user=user,
        )
        await wait_order_status(cc, ('complete', 'begin'), user_done=user)

        product_ex_id = uuid()

        async def sad_handle_scan_data(req):  # pylint: disable=unused-argument
            await dataset.product(external_id=product_ex_id)
            return web.json_response(status=420)

        async def happy_handle_scan_data(req):
            rj = await req.json()
            assert 'dc_store_id' in rj, 'хых'
            assert 'store_id' in rj, 'хах'
            assert 'result' in rj, 'хех'
            return web.json_response(status=200)

        async with await ext_api(onec_client, sad_handle_scan_data):
            await wait_order_status(
                cc, ('complete', 'send_report'), user_done=user,
            )
            await wait_order_status(
                cc, ('complete', 'send_report'), user_done=user,
            )

        pr = await dataset.Product.load(product_ex_id, by='external')
        tap.ok(pr, 'в 1с определенно сходили')

        async with await ext_api(onec_client, happy_handle_scan_data):
            await wait_order_status(
                cc, ('complete', 'done'), user_done=user,
            )


