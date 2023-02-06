import asyncio
import pytest
from stall.model.event_cache import EventCache


@pytest.mark.parametrize('request_params, expected_params', [
    # меняем только статус, ETA не меняется
    (
        {
            'eda_status': 'ARRIVED_TO_CUSTOMER',
        },
        {
            'eda_status': 'ARRIVED_TO_CUSTOMER',
            'delivery_eta': '2020-10-22T12:00:00+00:00',
        }
    ),

    # меняем оба параметра
    (
        {
            'eda_status': 'READY_FOR_DELIVERY',
            'delivery_eta': '2007-10-22T12:00:00+03:00'
        },
        {
            'eda_status': 'READY_FOR_DELIVERY',
            'delivery_eta': '2007-10-22T12:00:00+03:00'
        }
    ),

    # обнуляем ETA
    (
        {
            'eda_status': 'READY_FOR_DELIVERY',
            'delivery_eta': None
        },
        {
            'delivery_eta': None
        }
    )
])
async def test_set_eda_status(
        tap, api, dataset, request_params, expected_params):
    with tap:
        order = await dataset.order(attr={
            'delivery_eta': '2020-10-22T12:00:00+00:00'
        })
        tap.ok(order, 'ордер создан')
        tap.ok(
            not order.eda_status_updated,
            'время обновления статуса пусто'
        )

        events = (await dataset.OrderEvent.list(
            by='full',
            conditions=[
                ('order_id', order.order_id)
            ],
            db={'shard': order.shardno}
        )).list
        tap.eq(len(events), 1, 'new order_event')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_orders_set_eda_status',
                        json={
                            'external_id': order.external_id,
                            'store_id': order.store_id,
                            **request_params
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order_id', order.order_id)
        t.json_is('external_id', order.external_id)
        t.json_is('store_id', order.store_id)

        for key, value in expected_params.items():
            t.json_is(key, value)

        tap.ok(await order.reload(), 'перегружен')
        if 'eda_status' in expected_params:
            tap.eq(
                order.eda_status,
                expected_params['eda_status'],
                'статус сохранён'
            )
            tap.ok(
                order.eda_status_updated,
                'время обновления статуса сохранёно'
            )
        if 'delivery_eta' in expected_params:
            tap.eq(
                order.attr['delivery_eta'],
                expected_params['delivery_eta'],
                'ETA доставки установлено верно'
            )

        events = (await dataset.OrderEvent.list(
            by='full',
            conditions=[
                ('order_id', order.order_id),
            ],
            db={'shard': order.shardno}
        )).list
        tap.eq(len(events), 2, 'new order_event')


async def test_dispatch_delivery_type(tap, api, dataset):
    with tap.plan(11, 'Обновление типа диспатча'):
        order = await dataset.order()
        tap.ok(order, 'ордер создан')
        tap.ok(not order.courier, 'курьера в заказе нет')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_set_eda_status',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'eda_status': 'READY_FOR_DELIVERY',
                'dispatch_delivery_type': 'yandex_taxi',
            }
        )
        t.status_is(200, diag=True)
        with await order.reload():
            tap.eq(order.dispatch_delivery_type, 'yandex_taxi', 'Тип диспатча')

        await t.post_ok(
            'api_external_orders_set_eda_status',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'eda_status': 'READY_FOR_DELIVERY',
            }
        )
        t.status_is(200, diag=True)
        with await order.reload():
            tap.eq(order.dispatch_delivery_type,
                   'yandex_taxi', 'Не сбрасывается')

        await t.post_ok(
            'api_external_orders_set_eda_status',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'eda_status': 'READY_FOR_DELIVERY',
                'dispatch_delivery_type': 'courier',
            }
        )
        t.status_is(200, diag=True)
        with await order.reload():
            tap.eq(order.dispatch_delivery_type,
                   'courier', 'Но меняется')


async def test_log_eda_status(tap, api, dataset):
    with tap.plan(12, 'Проверим, что смена статуса из еды логгируется'):
        store = await dataset.store()
        order = await dataset.order(
            store=store,
            vars={
                'manual_dispatch_last_time': '2017-01-01T23:34:42+04:00',
                'manual_dispatch_last_target': 'any_courier',
            }
        )
        tap.ok(order, 'ордер создан')
        order_log_cursor = await dataset.OrderLog.list_by_order(order)
        tap.eq_ok(len(order_log_cursor.list), 1, 'В логе одна запись')

        t = await api(role='token:web.external.tokens.0')
        request_params = {
            'store_id': order.store_id,
            'external_id': order.external_id,
            'eda_status': 'READY_FOR_DELIVERY',
            'dispatch_delivery_type': 'yandex_taxi',
        }
        await t.post_ok(
            'api_external_orders_set_eda_status',
            json=request_params
        )
        t.status_is(200, diag=True)
        t.json_is('order_id', order.order_id)

        tap.ok(await order.reload(), 'перегружен')
        order_log_cursor = await dataset.OrderLog.list_by_order(order)
        tap.eq_ok(len(order_log_cursor.list), 2,
                  'В лог добавилась запись об обновлении')
        with order_log_cursor.list[-1] as order_log:
            tap.eq_ok(order_log.source, 'set_eda_status', 'Источник из еды')
            tap.eq_ok(
                order_log.eda_status,
                'READY_FOR_DELIVERY',
                'Статус из еды попал в лог'
            )
            tap.eq_ok(
                order_log.vars,
                {
                    'request': request_params,
                    'manual_dispatch_last_time': '2017-01-01T23:34:42+04:00',
                    'manual_dispatch_last_target': 'any_courier',
                },
                'Параметры запроса изменения статуса залоггированы'
            )

        tap.note('Проверим, что лог заказа соответсвует спецификации')
        user = await dataset.user(store=store, role='admin')
        t = await api(spec='doc/api/disp/orders.yaml', user=user)
        await t.post_ok('api_disp_orders_log',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                        })
        t.status_is(200, diag=True)


async def test_last_order_time(tap, api, dataset):
    with tap.plan(15, 'Обновление времени последнего заказа в курьере'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        order = await dataset.order(
            store=store,
            type='order',
            status='complete',
            estatus='done',
            courier_id=courier.courier_id,
        )

        cursor = await EventCache.list(
            by='look',
            conditions=(
                ('type', 'lp'),
                ('pk', courier.courier_id),
            ),
            db={'shard': courier.shardno},
            direction='DESC',
        )
        existed_events = len(cursor.list)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_set_eda_status',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'eda_status': 'DELIVERED',
            }
        )
        t.status_is(200, diag=True)

        with await order.reload() as order:
            tap.ok(order.eda_status_updated, 'Время проставлено')

        await order.business.order_changed()
        cursor = await EventCache.list(
            by='look',
            conditions=(
                ('type', 'lp'),
                ('pk', courier.courier_id),
            ),
            db={'shard': courier.shardno},
            direction='DESC',
        )
        tap.eq_ok(len(cursor.list), existed_events + 1,
                  'Новый контейнер событий')
        with cursor.list[0] as wrapper:
            tap.eq_ok(len(wrapper.events), 1, '1 событие в контейнере')
            event = wrapper.events[0]
            tap.eq_ok(event['key'], ['courier', 'store', store.store_id],
                      'key')
            tap.eq_ok(event['data']['courier_id'], courier.courier_id,
                      'data.courier_id')
            tap.eq_ok(event['data']['store_id'], store.store_id,
                      'data.store_id')
        with await courier.reload() as courier:
            tap.eq(
                courier.last_order_time,
                order.eda_status_updated,
                'Время выполнения заказа сохранено'
            )

        await order.business.order_changed()

        await asyncio.sleep(1)

        old_eda_updated = order.eda_status_updated
        tap.note('Проверим идемпотентность')

        await t.post_ok(
            'api_external_orders_set_eda_status',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'eda_status': 'DELIVERED',
            }
        )
        t.status_is(200, diag=True)
        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали ордер')
        tap.ok(await courier.reload(), 'Перезабрали курьера')

        tap.eq(
            order.eda_status_updated,
            old_eda_updated,
            'Едовое время не изменилось в заказе, курьера не обновили'
        )
        tap.eq(
            courier.last_order_time,
            old_eda_updated,
            'Время в курьере не поменялось'
        )


@pytest.mark.parametrize('eda_status, expected', [
    ('CANCELLED', False),
    ('ARRIVED_TO_CUSTOMER', False),
    ('DELIVERED', True),
])
async def test_true_mark_sell(tap, dataset, api, eda_status, expected):
    with tap.plan(5, 'ЧЗ заказ получает флаг'):
        store = await dataset.store()
        order = await dataset.order(
            store=store,
            status='complete',
            estatus='done',
            eda_status='ARRIVED_TO_CUSTOMER',
            dispatch_delivery_type='courier',
            vars={
                'true_mark_in_order': True
            }
        )
        t = await api(role='token:web.external.tokens.0')
        request_params = {
            'store_id': order.store_id,
            'external_id': order.external_id,
            'eda_status': eda_status,
        }
        await t.post_ok(
            'api_external_orders_set_eda_status',
            json=request_params
        )
        t.status_is(200, diag=True)
        t.json_is('order_id', order.order_id)

        tap.ok(await order.reload(), 'перегружен')
        tap.eq(
            order.vars('need_sell_true_mark', False),
            expected,
            'Марки нужно продать'
        )


async def test_full_true_mark_path(tap, dataset, api, wait_order_status, now):
    with tap.plan(15, 'Полный цикл ЧЗ заказа'):
        store = await dataset.store(options={'exp_albert_hofmann': True})
        user = await dataset.user(store=store)
        marked_product = await dataset.product(true_mark=True)
        await dataset.stock(product=marked_product, store=store, count=10)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': marked_product.product_id,
                    'count': 1
                },
            ],
            vars={'editable': True},
        )
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status=['request']
        )
        tap.eq(len(suggests), 1, 'Один саджест')

        suggest = suggests[0]
        mark_value = await dataset.true_mark_value(product=marked_product)
        tap.ok(
            await suggest.done(
                user=user, count=suggest.count, true_mark=mark_value),
            'Закрыли успешно марочный саджест'
        )
        tap.ok(
            await order.done(user=user, target='complete'),
            'Успешно завершили документ',
        )

        await wait_order_status(order, ('complete', 'done'))
        await wait_order_status(order, ('complete', 'done'))
        in_order_mark = await dataset.TrueMark.load(mark_value, by='value')
        tap.ok(in_order_mark, 'Получили марку')
        tap.eq(
            in_order_mark.order_id,
            order.order_id,
            'Марка в нужном заказе'
        )
        tap.eq(
            in_order_mark.status,
            'in_order',
            'Марка пока не продана'
        )

        t = await api(role='token:web.external.tokens.0')
        request_params = {
            'store_id': order.store_id,
            'external_id': order.external_id,
            'eda_status': 'DELIVERED',
        }
        await t.post_ok(
            'api_external_orders_set_eda_status',
            json=request_params
        )
        t.status_is(200, diag=True)
        t.json_is('order_id', order.order_id)
        await wait_order_status(order, ('complete', 'done'))
        tap.ok(await in_order_mark.reload(), 'Перезабрали марку')
        tap.eq(in_order_mark.status, 'sold', 'Продана марка')
