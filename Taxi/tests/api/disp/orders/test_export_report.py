from aiohttp import web

from stall.client.onec import client as onec_client
from stall import cfg


async def test_export_report_success(
    tap, api, ext_api, dataset, s3_stubber
):
    with tap.plan(6, 'тестируем флоу инв отчета из 1с'):
        user = await dataset.user(role='admin')

        cfg.set(
            'sync.1c.login',
            'login'
        )

        cfg.set(
            'sync.1c.password',
            'password'
        )

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            store_id=user.store_id,
            type='collect',
            required=[{'product_id': product.product_id, 'count': 12}],
        )
        tap.eq(order.store_id, user.store_id, 'ордер создан')

        bucket = '1c-ut'
        key = f'test/{order.order_id}.pdf'
        inv_path = onec_client.inv_path

        async def handler_1c(req):
            tap.eq(req.message.path,
                   f'{inv_path}/{order.order_id}/inv3',
                   'параметры приехали')

            return web.Response(
                status=200,
                content_type='text/plain',
                body=f'https://{bucket}.bucket.com/{key}'
            )

        s3_stubber.for_get_object_ok(
            bucket=bucket, key=key, data='testtesttest'.encode('utf-8')
        )
        s3_stubber.activate()

        async with await ext_api(onec_client, handler=handler_1c):
            t = await api(user=user,
                          spec=['doc/api/disp/orders.yaml',
                                'doc/api/support.yaml'])

            await t.post_ok(
                'api_disp_orders_export_report',
                json={'order_id': order.order_id,
                      'report_type': 'inv3'},
            )

            tap.eq_ok(t.res['status'], 200, 'response OK')
            tap.eq_ok(t.res['body'],
                      'testtesttest',
                      'Файл приехал')


async def test_export_report_1c_not_found(
    tap, api, ext_api, dataset, s3_stubber,
):
    with tap.plan(5, 'тестируем флоу инв отчета из 1с'
                     'когда файл не найден в 1с'):
        user = await dataset.user(role='admin')

        cfg.set('sync.1c.login', 'login')
        cfg.set('sync.1c.password', 'password')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            store_id=user.store_id,
            type='collect',
            required=[{'product_id': product.product_id, 'count': 12}],
        )
        tap.eq(order.store_id, user.store_id, 'ордер создан')

        bucket = '1c-ut'
        key = f'test/{order.order_id}.pdf'
        inv_path = onec_client.inv_path

        async def handler_1c(req):
            tap.eq(req.message.path,
                   f'{inv_path}/{order.order_id}/inv3',
                   'параметры приехали')

            return web.Response(
                status=404
            )

        s3_stubber.for_get_object_ok(
            bucket=bucket, key=key, data='testtesttest'.encode('utf-8')
        )
        s3_stubber.activate()

        async with await ext_api(onec_client, handler=handler_1c):
            t = await api(user=user,
                          spec=['doc/api/disp/orders.yaml',
                                'doc/api/support.yaml'])

            await t.post_ok(
                'api_disp_orders_export_report',
                json={'order_id': order.order_id,
                      'report_type': 'inv3'},
            )

            tap.eq_ok(t.res['status'], 424, 'Failed dependency')
