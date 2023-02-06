from datetime import timedelta
from aiohttp import web

import pytest

from stall.client.true_client import TrueClient, trueclient_dict


@pytest.mark.parametrize(
    'true_mark, expected_barcode, expected_serial',
    [
        (
            '0103041094787443215Qbag!\x1D93Zjqw\x1D3103000001',
            '3041094787443',
            '5Qbag!',
        ),
        (
            '010460780959133121e/Fw:xeo47NK2\x1D91F010\x1D92',
            '4607809591331',
            'e/Fw:xeo47NK2',
        ),
    ]
)
async def test_success(
        tap, api, dataset,
        true_mark, expected_barcode, expected_serial
):
    with tap.plan(6, 'Успешно распарсили код'):
        user = await dataset.user()
        order = await dataset.order(
            type='order',
            status='processing',
            estatus='begin',
            store_id=user.store_id,
            company_id=user.company_id,
        )
        t = await api(user=user)

        await t.post_ok(
            'api_tsd_check_true_mark',
            json={
                'true_mark': true_mark,
                'go_to_true_api': False,
                'order_id': order.order_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('barcode', expected_barcode)
        t.json_is('serial', expected_serial)
        t.json_is('true_mark_status', None)


async def test_failures_permit(tap, dataset, api):
    with tap.plan(6, 'Ошибки прав'):
        user = await dataset.user()
        user.role.remove_permit('tsd_check_true_mark')
        order = await dataset.order(
            type='order',
            status='processing',
            estatus='begin',
            store_id=user.store_id,
            company_id=user.company_id,
        )
        t = await api(user=user)
        true_mark = '0103041094787443215Qbag!\x1D93Zjqw\x1D3103000001'

        await t.post_ok(
            'api_tsd_check_true_mark',
            json={
                'true_mark': true_mark,
                'order_id': order.order_id,
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        user.role.add_permit('tsd_check_true_mark', True)

        await t.post_ok(
            'api_tsd_check_true_mark',
            json={
                'true_mark': true_mark,
                'go_to_true_api': False,
                'order_id': order.order_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_wrong_mark(tap, dataset, api, uuid):
    with tap.plan(3, 'Кривая марка'):
        user = await dataset.user()
        order = await dataset.order(
            type='order',
            status='processing',
            estatus='begin',
            store_id=user.store_id,
            company_id=user.company_id,
        )
        t = await api(user=user)

        await t.post_ok(
            'api_tsd_check_true_mark',
            json={
                'true_mark': uuid(),
                'order_id': order.order_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_INVALID_TRUE_MARK')


async def test_true_api_ok(tap, dataset, api, ext_api):
    with tap.plan(6, 'нормально ходим в тру апи'):
        company = await dataset.company()
        user = await dataset.user(company=company)
        order = await dataset.order(
            type='order',
            status='processing',
            estatus='begin',
            store_id=user.store_id,
            company_id=user.company_id,
        )
        await dataset.stash(
            name=f'true_mark_token_1c_{company.company_id}',
            value={'true_mark_token': 'lalala'},
        )
        true_client = TrueClient(company_id=company.company_id)
        trueclient_dict[company.company_id] = true_client

        async def handler(req):  # pylint: disable=unused-argument
            return web.json_response(
                status=200,
                data=[{'cisInfo': {'status': 'INTRODUCED'}}],
            )

        barcode = '03041094787443'
        serial = '5Qbag!'
        tail = '\x1D93Zjqw\x1D3103000001'

        t = await api(user=user)
        async with await ext_api(true_client, handler):
            await t.post_ok(
                'api_tsd_check_true_mark',
                json={
                    'true_mark': f'01{barcode}21{serial}{tail}',
                    'go_to_true_api': True,
                    'order_id': order.order_id,
                }
            )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('barcode', barcode[1:])
        t.json_is('serial', serial)
        t.json_is('true_mark_status', 'INTRODUCED')


async def test_true_api_fail(tap, dataset, api, ext_api, cfg, now):
    # pylint: disable=too-many-locals
    with tap.plan(16, 'ходим в тру апи и получаем говнишко'):
        cfg.set('true_client.go_to_true_api', 1)
        company = await dataset.company()
        store = await dataset.store(tz='Europe/Moscow')
        user = await dataset.user(
            company_id=company.company_id,
            store_id=store.store_id
        )
        cfg.set(
            'business.store.true_mark_start',
            (now() - timedelta(hours=72)).strftime('%Y-%m-%d %H:%M:%S')
        )
        order = await dataset.order(
            type='order',
            status='processing',
            estatus='begin',
            store_id=user.store_id,
            company_id=user.company_id,
        )

        await dataset.stash(
            name=f'true_mark_token_1c_{company.company_id}',
            value={'true_mark_token': 'lalala'},
        )
        true_client = TrueClient(company_id=company.company_id)
        trueclient_dict[company.company_id] = true_client
        response_status = 400
        response_data = [{'bad': 'response'}]

        async def handler(req):  # pylint: disable=unused-argument
            return web.json_response(
                status=response_status,
                data=response_data,
            )

        true_mark = '0103041094787443215Qbag!\x1D93Zjqw\x1D3103000001'
        t = await api(user=user)
        async with await ext_api(true_client, handler):
            await t.post_ok(
                'api_tsd_check_true_mark',
                json={
                    'true_mark': true_mark,
                    'order_id': order.order_id,
                }
            )

            t.status_is(424)
            t.json_is('code', 'ER_EXTERNAL_SERVICE')

            response_status = 200
            await t.post_ok(
                'api_tsd_check_true_mark',
                json={
                    'true_mark': true_mark,
                    'order_id': order.order_id,
                }
            )
            t.status_is(424)
            t.json_is('code', 'ER_TRUE_API_BROKEN')

            response_data = ['something bad']
            await t.post_ok(
                'api_tsd_check_true_mark',
                json={
                    'true_mark': true_mark,
                    'order_id': order.order_id,
                }
            )
            t.status_is(424)
            t.json_is('code', 'ER_TRUE_API_BROKEN')

            response_data = {'very bad': 'response'}
            await t.post_ok(
                'api_tsd_check_true_mark',
                json={
                    'true_mark': true_mark,
                    'order_id': order.order_id,
                }
            )
            t.status_is(424)
            t.json_is('code', 'ER_TRUE_API_BROKEN')

            response_data = [{'cisInfo': {'status': 'FAIL'}}]
            await t.post_ok(
                'api_tsd_check_true_mark',
                json={
                    'true_mark': true_mark,
                    'order_id': order.order_id,
                }
            )
            t.status_is(409)
            t.json_is('code', 'ER_BAD_TRUE_MARK')
            t.json_is('true_mark_status', 'FAIL')


async def test_true_api_supress_fail(tap, dataset, api, ext_api, cfg, now):
    # pylint: disable=too-many-locals
    with tap.plan(8, 'Игнорируем ошибку до всеобщего включения'):
        cfg.set('true_client.go_to_true_api', 1)
        company = await dataset.company()
        store = await dataset.store(tz='Europe/Moscow')
        user = await dataset.user(
            company_id=company.company_id,
            store_id=store.store_id
        )
        cfg.set(
            'business.store.true_mark_start',
            (now() + timedelta(hours=72)).strftime('%Y-%m-%d %H:%M:%S')
        )
        order = await dataset.order(
            type='order',
            status='processing',
            estatus='begin',
            store_id=user.store_id,
            company_id=user.company_id,
        )

        await dataset.stash(
            name=f'true_mark_token_1c_{company.company_id}',
            value={'true_mark_token': 'lalala'},
        )
        true_client = TrueClient(company_id=company.company_id)
        trueclient_dict[company.company_id] = true_client
        response_status = 400
        response_data = [{'bad': 'response'}]

        async def handler(req):  # pylint: disable=unused-argument
            return web.json_response(
                status=response_status,
                data=response_data,
            )

        true_mark = '0103041094787443215Qbag!\x1D93Zjqw\x1D3103000001'
        t = await api(user=user)
        async with await ext_api(true_client, handler):
            await t.post_ok(
                'api_tsd_check_true_mark',
                json={
                    'true_mark': true_mark,
                    'order_id': order.order_id,
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('true_mark_status', None)

            response_status = 200
            response_data = [{'cisInfo': {'status': 'FAIL'}}]
            await t.post_ok(
                'api_tsd_check_true_mark',
                json={
                    'true_mark': true_mark,
                    'order_id': order.order_id,
                }
            )
            t.status_is(409, diag=True)
            t.json_is('code', 'ER_BAD_TRUE_MARK')
            t.json_is('true_mark_status', 'FAIL')


async def test_refund(tap, dataset, api, ext_api, cfg):
    with tap.plan(3, 'Не ходим в true api при рефанде'):
        cfg.set('true_client.go_to_true_api', 1)
        user = await dataset.user()
        order = await dataset.order(
            type='refund',
            store_id=user.store_id,
            company_id=user.company_id,
            status='complete',
            estatus='done',
        )

        await dataset.stash(
            name=f'true_mark_token_1c_{user.company_id}',
            value={'true_mark_token': 'lalala'},
        )
        true_client = TrueClient(company_id=user.company_id)
        trueclient_dict[user.company_id] = true_client
        response_status = 400
        response_data = [{'bad': 'response'}]

        async def handler(req):  # pylint: disable=unused-argument
            tap.failed('Не должны ходить в API!')
            return web.json_response(
                status=response_status,
                data=response_data,
            )
        product = await dataset.product(true_mark=True)

        true_mark = await dataset.true_mark_value(product=product)
        t = await api(user=user)
        async with await ext_api(true_client, handler):
            await t.post_ok(
                'api_tsd_check_true_mark',
                json={
                    'true_mark': true_mark,
                    'order_id': order.order_id,
                }
            )
            t.status_is(200)
            t.json_is('code', 'OK')
