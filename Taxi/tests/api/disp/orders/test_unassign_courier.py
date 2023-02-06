from datetime import timedelta
from aiohttp import web
import pytest
from dateutil.relativedelta import relativedelta

from libstall.util import tzone
from stall.api.disp.orders.unassign_courier import gd_client


# pylint: disable=unused-argument
@pytest.mark.parametrize(
    'extra_payload',
    [
        {'disable_batching': True},
        {'taxi_only': False},
    ]
)
async def test_happy_flow(
        tap, dataset, api, uuid, ext_api, tvm_ticket, extra_payload,
):
    # pylint: disable=too-many-locals
    with tap.plan(19, 'успешное снятие курьера с заказа'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            options={'exp_jack_sparrow_2': True},
        )
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)
        order = await dataset.order(
            store=store,
            type='order',
            courier={'external_id': courier.external_id},
        )
        tap.eq(order.vars, {}, 'Пустые vars')

        async def gd_handler(request):
            r = await request.json()
            tap.eq(
                r['order_id'], order.external_id, 'посылаем корректный айди',
            )

            return web.json_response(
                status=200,
                data={'description': 'ok'},
            )

        async with await ext_api(gd_client, handler=gd_handler):
            t = await api(user=user)

            payload = {'order_id': order.order_id}

            if extra_payload:
                payload = {**payload, **extra_payload}

            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json=payload,
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('order')
        tap.ok(await order.reload(), 'Перезабрали ордер')
        tap.eq(
            order.vars.get('manual_dispatch_last_target'),
            'any_courier',
            'Выставили правильный таргет'
        )
        tap.ok(
            order.vars.get('manual_dispatch_last_time'),
            'Выставили время диспатча'
        )

        order_log_cursor = await dataset.OrderLog.list_by_order(order)
        tap.ok(len(order_log_cursor.list), 'Лог заказ не пустой')
        with order_log_cursor.list[-1] as order_log:
            tap.eq_ok(order_log.source, 'grocery_dispatch', 'Запрос отправлен')
            tap.eq_ok(order_log.user_id, user.user_id,
                      'Пользователь сохранен')
            tap.eq_ok(order_log.vars.get('action'), 'unassign',
                      'Запрос на открепление курьера')
            tap.eq_ok(order_log.vars.get('code'), 'OK',
                      'Запрос успешно отправлен')
            tap.eq_ok(order_log.vars.get('courier_id'), None,
                      'Курьер не назначен')
            tap.eq_ok(order_log.vars.get('store_id'), order.store_id,
                      'Лавка сохранена')
            tap.ok(order_log.vars.get('request'), 'Тело запроса залоггировано')

        tap.note('Проверим, что лог заказа соответсвует спецификации')
        await t.post_ok('api_disp_orders_log',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                        })
        t.status_is(200, diag=True)


async def test_reassign(tap, dataset, api, uuid, ext_api, tvm_ticket):
    with tap.plan(14, 'успешное переназначение курьера'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            options={'exp_jack_sparrow_2': True},
        )
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)
        order = await dataset.order(
            store=store,
            type='order',
            courier={'external_id': courier.external_id},
        )

        async def gd_handler(request):
            r = await request.json()
            tap.eq(r['order_id'], order.external_id, 'order_id')
            tap.eq(
                r['options']['performer_id'],
                courier.external_id, 'performer_id',
            )

            return web.json_response(
                status=200,
                data={'description': 'ok'},
            )

        async with await ext_api(gd_client, handler=gd_handler):
            t = await api(user=user)

            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={
                    'order_id': order.order_id,
                    'courier_id': courier.courier_id
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('order')

        tap.ok(await order.reload(), 'Перезабрали ордер')
        tap.eq(
            order.vars.get('manual_dispatch_last_target'),
            courier.courier_id,
            'Выставили правильный таргет'
        )
        tap.ok(
            order.vars.get('manual_dispatch_last_time'),
            'Выставили время диспатча'
        )

        order_log_cursor = await dataset.OrderLog.list_by_order(order)
        tap.ok(len(order_log_cursor.list), 'Лог заказ не пустой')
        with order_log_cursor.list[-1] as order_log:
            tap.eq_ok(order_log.source, 'grocery_dispatch', 'Запрос отправлен')
            tap.eq_ok(order_log.vars.get('action'), 'assign',
                      'Запрос на открепление курьера')
            tap.eq_ok(order_log.vars.get('code'), 'OK',
                      'Запрос успешно отправлен')
            tap.ok(order_log.vars.get('request'), 'Тело запроса залоггировано')


async def test_reassign_with_batching(
        tap, dataset, api, uuid, ext_api, tvm_ticket):
    # pylint: disable=too-many-locals
    with tap.plan(15, 'успешное переназначение курьера с батчем'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            options={'exp_jack_sparrow_2': True},
        )
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)
        order = await dataset.order(
            store=store,
            type='order',
            courier={'external_id': courier.external_id},
        )
        batch_to_order = await dataset.order(
            store=store,
            type='order',
            courier_id=courier.courier_id,
            eda_status='READY_FOR_DELIVERY',
        )

        async def gd_handler(request):
            r = await request.json()
            tap.eq(r['order_id'], order.external_id, 'order_id')
            tap.eq(
                r['options']['performer_id'],
                courier.external_id,
                'performer_id',
            )
            tap.eq(
                r['options']['batch_to_order_id'],
                batch_to_order.external_id,
                'batch',
            )

            return web.json_response(
                status=200,
                data={'description': 'ok'},
            )

        async with await ext_api(gd_client, handler=gd_handler):
            t = await api(user=user)

            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={
                    'order_id': order.order_id,
                    'courier_id': courier.courier_id,
                    'batch_to_order_id': batch_to_order.order_id,
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('order')

        order_log_cursor = await dataset.OrderLog.list_by_order(order)
        tap.ok(len(order_log_cursor.list), 'Лог заказ не пустой')
        with order_log_cursor.list[-1] as order_log:
            tap.eq_ok(order_log.source, 'grocery_dispatch', 'Запрос отправлен')
            tap.eq_ok(order_log.vars['action'], 'assign',
                      'Запрос на открепление курьера')
            tap.eq_ok(order_log.vars['code'], 'OK',
                      'Запрос успешно отправлен')
            tap.eq_ok(order_log.vars['courier_id'], courier.courier_id,
                      'Конкретный курьер назначен')
            tap.eq_ok(order_log.vars['store_id'], order.store_id,
                      'Лавка сохранена')
            tap.ok(order_log.vars['request'], 'Тело запроса залоггировано')
            tap.eq_ok(order_log.vars['request']['batch_to_order_id'],
                      batch_to_order.order_id, 'Заказ для датчинга сохранён')


# pylint: disable=too-many-arguments,too-many-locals
@pytest.mark.parametrize('eda_status, payload,  expected_code, code', [
    (
        'ORDER_TAKEN',
        {},
        400,
        'ER_ORDER_NOT_FOUND',
    ),
    (
        'READY_FOR_DELIVERY',
        {'batch_to_order_id': 'random_staff_here'},
        403,
        'ER_ACCESS',
    )
])
async def test_fail_with_batching(
        tap, dataset, api, uuid, ext_api, tvm_ticket,
        eda_status, payload, expected_code, code
):
    with tap.plan(3, 'неудача переназначение курьера с батчем'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            options={'exp_jack_sparrow_2': True},
        )
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)
        order = await dataset.order(
            store=store,
            type='order',
            courier={'external_id': courier.external_id},
        )
        batch_to_order = await dataset.order(
            store=store,
            type='order',
            courier_id=courier.courier_id,
            eda_status=eda_status,
        )

        async def gd_handler(request):
            r = await request.json()
            tap.eq(
                r['options']['order_id'],
                order.external_id,
                'order_id',
            )
            tap.eq(
                r['options']['performer_id'],
                courier.external_id,
                'performer_id',
            )

            return web.json_response(
                status=200,
                data={'description': 'ok'},
            )

        async with await ext_api(gd_client, handler=gd_handler):
            t = await api(user=user)
            body = {
                'order_id': order.order_id,
                'courier_id': courier.courier_id,
                'batch_to_order_id': batch_to_order.order_id,
            }
            body.update(payload)

            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json=body,
            )
            t.status_is(expected_code, diag=True)
            t.json_is('code', code)


async def test_reassign_fail(tap, dataset, api, uuid, ext_api, tvm_ticket):
    with tap.plan(3, 'курьер не подходит для назначения'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            options={'exp_jack_sparrow_2': True},
        )
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster, status='disabled')
        order = await dataset.order(
            store=store,
            type='order',
            courier={'external_id': courier.external_id},
        )

        async def gd_handler(request):
            r = await request.json()
            tap.eq(
                r['options']['order_id'],
                order.external_id,
                'order_id',
            )
            tap.eq(
                r['options']['performer_id'],
                courier.external_id,
                'performer_id',
            )

            return web.json_response(
                status=200,
                data={'description': 'ok'},
            )

        async with await ext_api(gd_client, handler=gd_handler):
            t = await api(user=user)

            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={
                    'order_id': order.order_id,
                    'courier_id': courier.courier_id
                },
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_COURIER_NOT_FOUND')


async def test_err_grocery_dispatch(
        tap, dataset, api, now, uuid, ext_api, tvm_ticket,
):
    with tap.plan(18, 'имитация ошибок со стороны grocery-dispatch'):
        store = await dataset.store(
            options={'exp_jack_sparrow_2': True},
        )
        user = await dataset.user(store=store, role='admin')
        order = await dataset.order(
            store=store,
            type='order',
            courier={'external_id': uuid()},
        )

        requests = []

        async def gd_handler(request):
            requests.append(request)

            if len(requests) == 1:
                return web.json_response(status=404)

            return web.json_response(
                status=409,
                data={'dispatch_error_type': 'found_something_wrong'}
            )

        async with await ext_api(gd_client, handler=gd_handler):
            t = await api(user=user)

            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={'order_id': order.order_id},
            )
            t.status_is(424, diag=True)
            t.json_is('code', 'ER_EXTERNAL_SERVICE')
            t.json_is(
                'message', 'grocery-dispatch service does not support order',
            )

            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={'order_id': order.order_id},
            )
            t.status_is(424, diag=True)
            t.json_is('code', 'ER_EXTERNAL_SERVICE')
            t.json_is(
                'message',
                'grocery-dispatch service failed to reassign courier',
            )

        tap.ok(await order.reload(), 'Перезабрали ордер')
        tap.not_in_ok(
            'manual_dispatch_last_target',
            order.vars,
            'таргет диспатча не проставили'
        )
        tap.not_in_ok(
            'manual_dispatch_last_time',
            order.vars,
            'время диспатча не проставили'
        )

        order_log_cursor = await dataset.OrderLog.list_by_order(order)
        tap.ok(len(order_log_cursor.list), 'Лог заказ не пустой')
        with order_log_cursor.list[-1] as order_log:
            tap.eq_ok(order_log.source, 'grocery_dispatch', 'Запрос отправлен')
            tap.eq_ok(order_log.vars.get('action'), 'unassign',
                      'Запрос на открепление курьера')
            tap.eq_ok(order_log.vars.get('code'), 'FAIL',
                      'Ошибка при отправке запроса')
            tap.ok(order_log.vars.get('request'), 'Тело запроса залоггировано')
            gd_response = order_log.vars.get('gd_response', {})
            tap.eq(gd_response.get('status'), 409, 'Код ответа GD')
            tap.eq(
                gd_response.get('error_type'),
                'found_something_wrong',
                'Тип ошибки GD'
            )


async def test_already_taxi(tap, dataset, api, uuid):
    with tap.plan(3, 'уже назначено на такси'):
        store = await dataset.store(
            options={'exp_jack_sparrow_2': True},
        )
        user = await dataset.user(store=store, role='admin')
        order = await dataset.order(
            store=store,
            type='order',
            dispatch_delivery_type='yandex_taxi',
            courier={
                'external_id': uuid(),
            },
        )

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_unassign_courier',
            json={'order_id': order.order_id, 'taxi_only': True},
        )
        t.status_is(429, diag=True)
        t.json_is('code', 'ER_ALREADY_PROCESSING')


@pytest.mark.parametrize(
    'exp_mc_hammer, expected_http, expected_code',
    [
        (True, 403, 'ER_ACCESS'),
        (False, 200, 'OK'),
    ]
)
async def test_taxi_hummer(
        tap, dataset, api, ext_api,
        exp_mc_hammer, expected_http, expected_code):
    with tap.plan(3, 'Работа экспа mc_hammer'):
        store = await dataset.store(
            options={'exp_mc_hammer': exp_mc_hammer},
        )
        user = await dataset.user(store=store, role='admin')
        order = await dataset.order(
            store=store,
            type='order',
        )
        t = await api(user=user)

        async def gd_handler(request):
            return web.json_response(
                status=200,
                data={'description': 'ok'},
            )

        async with await ext_api(gd_client, handler=gd_handler):
            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={'order_id': order.order_id, 'taxi_only': True},
            )
        t.status_is(expected_http, diag=True)
        t.json_is('code', expected_code)


@pytest.mark.parametrize(
    'begin_shift,end_shift,expected_http,expected_code',
    [
        (-2, +2, 403, 'ER_ACCESS'),
        (-6, -2, 200, 'OK'),
    ]
)
async def test_taxi_hummer_schedule(
        tap, dataset, api, ext_api, now,
        begin_shift, end_shift, expected_http, expected_code
):
    with tap.plan(3, 'Работа расписания mc hummer'):
        tz = 'Europe/Moscow'
        timezone = tzone(tz)
        current_time = now(tz=timezone)
        begin_time = current_time + timedelta(hours=begin_shift)
        end_time = current_time + timedelta(hours=end_shift)
        store = await dataset.store(
            tz=tz,
            options={'exp_mc_hammer': False},
            options_setup={
                'exp_mc_hammer_timetable': [{
                    'type': 'everyday',
                    'begin': begin_time.strftime('%H:%M'),
                    'end': end_time.strftime('%H:%M'),
                }],
            }
        )
        user = await dataset.user(store=store, role='admin')
        order = await dataset.order(
            store=store,
            type='order',
        )
        t = await api(user=user)

        async def gd_handler(request):
            return web.json_response(
                status=200,
                data={'description': 'ok'},
            )

        async with await ext_api(gd_client, handler=gd_handler):
            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={'order_id': order.order_id, 'taxi_only': True},
            )
        t.status_is(expected_http, diag=True)
        t.json_is('code', expected_code)


async def test_not_json(tap, dataset, api, ext_api):
    with tap.plan(4, 'не разваливаемся если не json'):
        store = await dataset.store(options={'exp_jack_sparrow_2': True})
        user = await dataset.user(store=store, role='admin')
        order = await dataset.order(
            store=store,
            type='order',
        )
        t = await api(user=user)

        async def gd_handler(request):
            return web.Response(
                status=404,
                content_type='text/html',
            )

        async with await ext_api(gd_client, handler=gd_handler):
            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={'order_id': order.order_id},
            )
        t.status_is(424, diag=True)
        t.json_is('code', 'ER_EXTERNAL_SERVICE')
        t.json_is('message', 'grocery-dispatch service does not support order')


# pylint: disable=too-many-statements
@pytest.mark.parametrize('gender', ['male', 'female'])
async def test_order_max_weight(
        tap, dataset, api, ext_api, now,
        gender,
):
    with tap.plan(27, 'проверка ограничения по весу заказов'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                f'order_max_weight_{gender}_g': 10_000,
            },
            courier_shift_underage_setup={
                f'order_max_weight_{gender}_g': 3_000,
            },
        )
        store = await dataset.store(
            cluster=cluster,
            options={'exp_jack_sparrow_2': True},
        )
        user = await dataset.user(store=store, role='admin')

        young_courier = await dataset.courier(
            cluster=cluster,
            gender=gender,
            birthday=now() - relativedelta(years=16),
        )
        adult_courier = await dataset.courier(
            cluster=cluster,
            gender=gender,
            birthday=now() - relativedelta(years=23),
        )

        very_heavy_order = await dataset.order(
            store=store,
            type='order',
            vars={
                'total_order_weight': 20_000,
            }
        )
        heavy_order = await dataset.order(
            store=store,
            type='order',
            vars={
                'total_order_weight': 5_000,
            }
        )
        light_order = await dataset.order(
            store=store,
            type='order',
            vars={
                'total_order_weight': 1_000,
            }
        )
        light_order_2 = await dataset.order(
            store=store,
            type='order',
            vars={
                'total_order_weight': 1_000,
            }
        )

        existing_young_order = await dataset.order(
            store=store,
            courier_id=young_courier.courier_id,
            type='order',
            vars={
                'total_order_weight': 2_000,
            }
        )

        async def gd_handler(request):
            return web.json_response(
                status=200,
                data={'description': 'ok'},
            )

        async with await ext_api(gd_client, handler=gd_handler):
            t = await api(user=user)

            tap.note('very_heavy_order – young_courier')
            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={
                    'order_id': very_heavy_order.order_id,
                    'courier_id': young_courier.courier_id,
                },
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_ORDER_MAX_WEIGHT_EXCEEDED')

            tap.note('heavy_order – young_courier')
            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={
                    'order_id': heavy_order.order_id,
                    'courier_id': young_courier.courier_id,
                },
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_ORDER_MAX_WEIGHT_EXCEEDED')

            tap.note('light_order – young_courier')
            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={
                    'order_id': light_order.order_id,
                    'batch_to_order_id': existing_young_order.order_id,
                    'courier_id': young_courier.courier_id,
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            # позволяем назначить курьера
            # даже если в сумме превышаем лимит по весу
            # сумма по батчу считается на стороне диспатча
            tap.note('light_order_2 – young_courier')
            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={
                    'order_id': light_order_2.order_id,
                    'batch_to_order_id': existing_young_order.order_id,
                    'courier_id': young_courier.courier_id,
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            tap.note('very_heavy_order – adult_courier')
            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={
                    'order_id': very_heavy_order.order_id,
                    'courier_id': adult_courier.courier_id,
                },
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_ORDER_MAX_WEIGHT_EXCEEDED')

            tap.note('heavy_order – adult_courier')
            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={
                    'order_id': heavy_order.order_id,
                    'courier_id': adult_courier.courier_id,
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            # доехало назначение курьера на заказ
            light_order.courier_id = young_courier.courier_id
            await light_order.save()

            # если заказы в батче уже известны
            # проверка происходит на нашей стороне
            tap.note('light_order+light_order_2 – young_courier')
            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={
                    'order_id': light_order_2.order_id,
                    'batch_to_order_id': existing_young_order.order_id,
                    'courier_id': young_courier.courier_id,
                },
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_ORDER_MAX_WEIGHT_EXCEEDED')

            # заказ уже есть в батче, ограничение не смотрим
            tap.note('repeat light_order – young_courier')
            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={
                    'order_id': light_order.order_id,
                    'batch_to_order_id': existing_young_order.order_id,
                    'courier_id': young_courier.courier_id,
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            # переназначить заказ, однако, можно
            tap.note('light_order_2 – young_courier')
            await t.post_ok(
                'api_disp_orders_unassign_courier',
                json={
                    'order_id': light_order_2.order_id,
                    'courier_id': young_courier.courier_id,
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
