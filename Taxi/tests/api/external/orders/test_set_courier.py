import pytest

from libstall.model.coerces import date_time
from libstall.util import time2iso


async def test_set_courier(tap, api, dataset, uuid):
    with tap.plan(13, 'Тесты ручки set_courier'):
        order = await dataset.order()
        tap.ok(order, 'ордер создан')
        tap.ok(not order.courier, 'курьера в заказе нет')

        t = await api(role='token:web.external.tokens.0')
        courier_external_id = uuid()
        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,

                'courier_external_id': courier_external_id,
                'courier_name': 'Василий Иванович',
                'courier_arrival_time': '2017-01-01T23:34:42+04:00',
                'courier_phone': '+79261234567',
                'related_orders': [order.external_id],
                'dispatch_delivery_type': 'yandex_taxi',
            }
        )
        t.status_is(200, diag=True)
        tap.ok(await order.reload(), 'ордер перегружен')
        tap.ok(order.courier, 'курьер в ордере появился')
        tap.eq(order.dispatch_delivery_type, 'yandex_taxi', 'Тип диспатча')

        with order.courier as c:
            tap.eq(c.name, 'Василий Иванович', 'имя')
            tap.eq(c.external_id, courier_external_id, 'external_id')
            tap.eq(time2iso(c.arrival_time),
                   '2017-01-01T23:34:42+04:00',
                   'время прибытия')
            tap.ok(c.related_orders, 'связанные ордера')

            for order_id in c.related_orders:
                tap.ok(await dataset.Order.load(order_id), 'Ордер есть')
            tap.eq(c.type, 'human', 'Тип курьера дефолтный')


async def test_set_courier_no_related(tap, api, dataset, uuid):
    with tap.plan(12, 'Тесты ручки set_courier'):
        order = await dataset.order()
        tap.ok(order, 'ордер создан')
        tap.ok(not order.courier, 'курьера в заказе нет')
        version = order.version

        t = await api(role='token:web.external.tokens.0')
        courier_external_id = uuid()
        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,

                'courier_external_id': courier_external_id,
                'courier_name': 'Василий Иванович',
                'courier_arrival_time': '2017-01-01T23:34:42+04:00',
                'related_orders': [uuid()],
                'courier_type': 'rover',
            }
        )
        t.status_is(200, diag=True)
        tap.ok(await order.reload(), 'ордер перегружен')
        tap.ok(order.courier, 'курьер в ордере появился')
        tap.ok(order.version > version, 'Версия изменилась')

        with order.courier as c:
            tap.eq(c.name, 'Василий Иванович', 'имя')
            tap.eq(c.external_id, courier_external_id, 'external_id')
            tap.eq(time2iso(c.arrival_time),
                   '2017-01-01T23:34:42+04:00',
                   'время прибытия')
            tap.eq(
                c.related_orders,
                [order.order_id],
                'связанные ордера не нашлись'
            )
            tap.eq(c.type, 'rover', 'Тип курьера робот')


@pytest.mark.parametrize(
    'delivery_promise',
    [
        'skip',
        '2017-01-02T23:34:42+04:00',
        None,
    ]
)
async def test_set_courier_promise(tap, api, dataset, uuid, delivery_promise):
    with tap.plan(10, 'Тест управления delivery_promise'):
        order = await dataset.order(
            delivery_promise='2010-01-01T21:12:13+04:00'
        )
        tap.ok(order, 'ордер создан')
        tap.ok(not order.courier, 'курьера в заказе нет')
        tap.ok(order.delivery_promise, 'delivery_promise заполнен')
        orig_promise = order.delivery_promise

        t = await api(role='token:web.external.tokens.0')
        courier_external_id = uuid()

        dp = {}
        if delivery_promise != 'skip':
            dp['courier_delivery_promise'] = delivery_promise

        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,

                'courier_external_id': courier_external_id,
                'courier_name': 'Василий Иванович',
                'courier_arrival_time': '2017-01-01T23:34:42+04:00',
                'courier_phone': '+79261234567',
                'courier_vin': 'JH2PC35051M200020',
                'taxi_driver_uuid': '141a33b0-6c31-461f-b65c-e292f6617fa6',
                'related_orders': [order.external_id],

                **dp,
            }
        )
        t.status_is(200, diag=True)
        tap.ok(await order.reload(), 'ордер перегружен')
        tap.ok(order.courier, 'курьер в ордере появился')
        tap.eq(order.courier.vin, 'JH2PC35051M200020', 'vin прописался')
        tap.eq(order.courier.taxi_driver_uuid,
               '141a33b0-6c31-461f-b65c-e292f6617fa6',
               'taxi_driver_uuid прописался')

        if delivery_promise == 'skip':
            tap.eq(order.delivery_promise, orig_promise, 'промис не менялся')
        else:
            tap.eq(
                order.delivery_promise,
                date_time(delivery_promise),
                'новый промис'
            )


async def test_set_courier_taxi_uuid(tap, dataset, api, uuid):
    with tap.plan(10, 'Ставим курьера по одному taxi_uuid'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier_external_id = uuid()
        courier = await dataset.courier(
            cluster=cluster,
            external_id=courier_external_id,
        )
        order = await dataset.order(store=store)
        tap.ok(not order.courier, 'курьера в заказе нет')
        t = await api(role='token:web.external.tokens.0')

        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,

                'courier_name': 'Василий Иванович',
                'courier_arrival_time': '2017-01-01T23:34:42+04:00',
                'courier_phone': '+79261234567',
                'related_orders': [order.external_id],
                'dispatch_delivery_type': 'yandex_taxi',
                'taxi_driver_uuid': courier_external_id,
            }
        )
        t.status_is(200, diag=True)
        tap.ok(await order.reload(), 'ордер перегружен')
        tap.ok(order.courier, 'курьер в ордере появился')
        tap.eq(order.courier.name, 'Василий Иванович', 'имя')
        tap.eq(
            order.courier.taxi_driver_uuid,
            courier_external_id,
            'external id курьера'
        )

        tap.eq(
            order.courier_id,
            courier.courier_id,
            'Нашли подходящего курьера'
        )

        users = await dataset.user(store=store)
        t = await api(spec=('doc/api/disp/orders.yaml',), user=users)

        await t.post_ok(
            'api_disp_orders_load',
            json={
                'order_id': order.order_id,
            }
        )
        t.status_is(200, diag=True)


async def test_type(tap, api, dataset, uuid):
    with tap.plan(10, 'Тестируем что если тип не пришёл, он форсится в human'):
        order = await dataset.order()
        tap.ok(order, 'ордер создан')
        tap.ok(not order.courier, 'курьера в заказе нет')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,

                'courier_external_id': uuid(),
                'courier_name': 'Бендер',
                'courier_arrival_time': '2017-01-01T23:34:42+04:00',
                'courier_phone': '+79261234567',
                'related_orders': [order.external_id],
                'courier_type': 'rover',
            }
        )
        t.status_is(200, diag=True)
        with await order.reload() as o:
            tap.eq(o.courier.name, 'Бендер', 'name')
            tap.eq(o.courier.type, 'rover', 'type')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,

                'courier_external_id': uuid(),
                'courier_name': 'Василий Иванович',
                'courier_arrival_time': '2017-01-01T23:34:42+04:00',
                'courier_phone': '+79261234568',
                'related_orders': [order.external_id],
            }
        )
        t.status_is(200, diag=True)
        with await order.reload() as o:
            tap.eq(o.courier.name, 'Василий Иванович', 'name')
            tap.eq(o.courier.type, 'human', 'type')


@pytest.mark.parametrize('empty_fields, extra_params', [
    (['courier_name'], {}),

    # courier_external_id is None
    (
            ['taxi_driver_uuid'],
            {'courier_external_id': None}),
    (
            ['courier_arrival_time', 'taxi_driver_uuid'],
            {'courier_external_id': None}
    ),

    # courier_external_id is omitted
    (['courier_external_id', 'taxi_driver_uuid'], {}),
    (['courier_external_id', 'courier_arrival_time', 'taxi_driver_uuid'], {}),
])
async def test_unset_courier(tap, api, dataset, empty_fields, extra_params):
    with tap.plan(10, 'тесты сброса курьера'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        order = await dataset.order(
            store=store,
            courier={'external_id': courier.courier_id},
            courier_id=courier.courier_id,
            courier_shift_id=shift.courier_shift_id,
        )
        tap.ok(order, 'ордер создан')
        tap.ok(order.courier, 'курьер в заказе есть')
        tap.ok(order.courier_id, 'курьер в заказе есть')
        tap.ok(order.courier_shift_id, 'смена в заказе есть')

        t = await api(role='token:web.external.tokens.0')

        courier_data = {
            'courier_external_id': courier.courier_id,
            'taxi_driver_uuid': courier.external_id,
            'courier_name': 'Василий Иванович',
            'courier_arrival_time': '2017-01-01T23:34:42+04:00',
            'courier_phone': '+79261234567',
        }
        request_body = {
            'store_id': order.store_id,
            'external_id': order.external_id,
            'related_orders': [order.external_id],
            **courier_data,
        }
        request_body.update(extra_params)
        for empty_field in empty_fields:
            del request_body[empty_field]

        await t.post_ok(
            'api_external_orders_set_courier',
            json=request_body,
        )
        t.status_is(200, diag=True)
        tap.ok(await order.reload(), 'ордер перегружен')
        tap.ok(not order.courier, 'курьера сброшен')
        tap.eq(order.courier_id, None, 'курьер сброшен')
        tap.eq(order.courier_shift_id, None, 'смена сброшена')


@pytest.mark.parametrize('maybe_rover', [True, False])
async def test_unset_maybe_rover(tap, api, dataset, uuid, maybe_rover):
    with tap:
        order = await dataset.order(attr={'maybe_rover': maybe_rover})
        tap.ok(order, 'ордер создан')
        tap.ok(not order.courier, 'курьера в заказе нет')
        tap.eq(order.attr['maybe_rover'], maybe_rover, 'maybe_rover set')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,

                'courier_external_id': uuid(),
                'courier_name': 'Бендер',
                'courier_arrival_time': '2017-01-01T23:34:42+04:00',
                'courier_phone': '+79261234567',
                'related_orders': [order.external_id],
                'courier_type': 'rover',
            }
        )
        t.status_is(200, diag=True)

        await order.reload()
        tap.ok('maybe_rover' not in order.attr, 'maybe_rover unset')


async def test_courier_shift_by_eda(tap, api, dataset, uuid):
    with tap.plan(5, 'Детектим курьера и смену по courier_external_id'):
        eda_id = uuid()

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            vars={'external_ids': {'eats': eda_id}}
        )
        order = await dataset.order(store=store)
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,

                'courier_external_id': eda_id,
                'courier_name': 'Василий Иванович',
                'courier_arrival_time': '2017-01-01T23:34:42+04:00',
                'courier_phone': '+79261234567',
                'related_orders': [order.external_id],
            }
        )
        t.status_is(200, diag=True)

        with await order.reload():
            tap.ok(order.courier, 'курьер в ордере появился')
            tap.eq(order.courier_id, courier.courier_id, 'courier_id')
            tap.eq(
                order.courier_shift_id,
                shift.courier_shift_id,
                'courier_shift_id'
            )


async def test_courier_shift_by_taxi(tap, api, dataset, uuid):
    with tap.plan(5, 'Детектим курьера и смену по taxi_driver_uuid'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        order = await dataset.order(store=store)
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,

                'courier_external_id': uuid(),
                'courier_name': 'Василий Иванович',
                'courier_arrival_time': '2017-01-01T23:34:42+04:00',
                'courier_phone': '+79261234567',
                'related_orders': [order.external_id],
                'taxi_driver_uuid': courier.external_id,
            }
        )
        t.status_is(200, diag=True)

        with await order.reload():
            tap.ok(order.courier, 'курьер в ордере появился')
            tap.eq(order.courier_id, courier.courier_id, 'courier_id')
            tap.eq(
                order.courier_shift_id,
                shift.courier_shift_id,
                'courier_shift_id'
            )


async def test_dispatch_delivery_type(tap, api, dataset, uuid):
    with tap.plan(14, 'Обновление типа диспатча'):
        order = await dataset.order()
        tap.ok(order, 'ордер создан')
        tap.ok(not order.courier, 'курьера в заказе нет')

        t = await api(role='token:web.external.tokens.0')
        courier_external_id = uuid()
        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,

                'courier_external_id': courier_external_id,
                'courier_name': 'Василий Иванович',
                'courier_arrival_time': '2017-01-01T23:34:42+04:00',
                'courier_phone': '+79261234567',
                'related_orders': [order.external_id],
                'dispatch_delivery_type': 'yandex_taxi',
            }
        )
        t.status_is(200, diag=True)
        with await order.reload():
            tap.ok(order.courier, 'курьер в ордере появился')
            tap.eq(order.dispatch_delivery_type, 'yandex_taxi', 'Тип диспатча')

        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,

                'courier_external_id': courier_external_id,
                'courier_name': 'Василий Иванович',
                'courier_arrival_time': '2017-01-01T23:34:42+04:00',
                'courier_phone': '+79261234567',
                'related_orders': [order.external_id],
            }
        )
        t.status_is(200, diag=True)
        with await order.reload():
            tap.ok(order.courier, 'курьер в ордере появился')
            tap.eq(order.dispatch_delivery_type,
                   'yandex_taxi', 'Не сбрасывается')

        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,

                'courier_external_id': courier_external_id,
                'courier_name': 'Василий Иванович',
                'courier_arrival_time': '2017-01-01T23:34:42+04:00',
                'courier_phone': '+79261234567',
                'related_orders': [order.external_id],
                'dispatch_delivery_type': 'courier',
            }
        )
        t.status_is(200, diag=True)
        with await order.reload():
            tap.ok(order.courier, 'курьер в ордере появился')
            tap.eq(order.dispatch_delivery_type,
                   'courier', 'Но меняется')


async def test_log_set_courier(tap, api, dataset, uuid):
    with tap.plan(16, 'Проверим что назначенный курьер записывается в лог'):
        eda_id = uuid()

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            vars={'external_ids': {'eats': eda_id}}
        )
        order = await dataset.order(
            store=store,
            vars={
                'manual_dispatch_last_time': '2017-01-01T23:34:42+04:00',
                'manual_dispatch_last_target': 'any_courier',
            }
        )
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        tap.note("Установим курьера")
        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,

                'courier_external_id': eda_id,
                'courier_name': 'Василий Иванович',
                'courier_arrival_time': '2017-01-01T23:34:42+04:00',
                'courier_phone': '+79261234567',
                'related_orders': [order.external_id],
            }
        )
        t.status_is(200, diag=True)

        order_log_cursor = await dataset.OrderLog.list_by_order(order)
        tap.ok(len(order_log_cursor.list), 'Лог по ордеру не пустой')
        with order_log_cursor.list[-1] as order_log:
            tap.eq_ok(order_log.source, 'set_courier',
                      'Запись о выставлении курьера')
            tap.eq_ok(order_log.vars.get('courier_id'),
                      courier.courier_id, 'Идентификатор курьера записан')
            tap.eq_ok(order_log.vars.get('courier_shift_id'),
                      shift.courier_shift_id, 'Смена курьера записана')
            tap.ne_ok(order_log.vars.get('manual_dispatch_last_time'),
                      None, 'Время попало в лог')
            tap.ne_ok(order_log.vars.get('manual_dispatch_last_target'),
                      None, 'Правильный target')

        tap.note("Сбросим курьера")
        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'courier_external_id': eda_id,
                'courier_arrival_time': '2017-01-01T23:34:42+04:00',
                'courier_phone': '+79261234567',
                'related_orders': [order.external_id],
            }
        )
        t.status_is(200, diag=True)

        order_log_cursor = await dataset.OrderLog.list_by_order(order)
        tap.ok(len(order_log_cursor.list), 'Лог по ордеру не пустой')
        with order_log_cursor.list[-1] as order_log:
            tap.eq_ok(order_log.source, 'set_courier',
                      'Запись о выставлении курьера')
            tap.eq_ok(order_log.vars.get('courier_id'),
                      None, 'курьер сброшен')
            tap.eq_ok(order_log.vars.get('courier_shift_id'),
                      None, 'Смена курьера сброшена')

        tap.note('Проверим, что лог заказа соответсвует спецификации')
        user = await dataset.user(store=store, role='admin')
        t = await api(spec='doc/api/disp/orders.yaml', user=user)
        await t.post_ok('api_disp_orders_log',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                        })
        t.status_is(200, diag=True)


async def test_without_arrival_time(tap, api, dataset, uuid):
    with tap.plan(8, 'Тесты ручки set_courier без courier_arrival_time'):
        order = await dataset.order()
        tap.ok(order, 'ордер создан')
        tap.ok(not order.courier, 'курьера в заказе нет')

        t = await api(role='token:web.external.tokens.0')
        courier_external_id = uuid()
        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,

                'courier_external_id': courier_external_id,
                'courier_name': 'Василий Иванович',
                'courier_phone': '+79261234567',
                'related_orders': [order.external_id],
                'dispatch_delivery_type': 'yandex_taxi',
            }
        )

        t.status_is(400, diag=True)
        t.content_type_like(r'^application/json')
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Bad request')
        t.json_is('details',
                  {'message': 'Courier requires courier_arrival_time'})

