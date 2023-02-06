# pylint: disable=too-many-lines
import datetime
import tests.dataset as dt

from libstall.util import time2time

# pylint: disable=pointless-string-statement
'''
TEST PLAN:
- [x] Неверные параметры в запросе: нет периода, нет лавки
- [x] Дата начала периода больше даты окончания
- [x] Пустой ответ
- [x] Тест на пермиты
- [x] Курьерский CTE по одному курьеру. Курьер назначен, потом собрали заказ
- [x] Курьерский CTE по одному курьеру. Собрали заказ, потом назначен курьер
- [x] Курьерский CTE по одному курьеру. Нет события "Прибыл", берем "Доставлен"
- [x] Курьерский CTE по двум курьерам
- [x] Тест pickup_time сначала курьер назначен, потом собрали заказ
- [x] Тест pickup_time сначала собрали заказ, потом курьер назначен
- [x] Тест to_client_time
- [x] Если нет события "прибыл", то не считаем to_client_time
- [x] Тест drop_off_time
- [x] Если нет события "прибыл", то не считаем drop_off_time
- [x] Тест returning_time
- [x] returning_time при батчинге учитываем только последний заказ
- [x] returning_time. "Чекин" пришел раньше,
      чем последний заказ доставлен "Доставлен" - не считаем такие заказы
- [x] returning_time. Заказ отменен, а не доставлен
- [x] Доставленные заказы
- [x] Доставленные заказы без события "прибыл"
'''

async def test_list_invalid(api, dataset: dt, clickhouse_client):
    # pylint: disable=unused-argument
    store = await dataset.store()
    t = await api(role='admin')
    await t.post_ok(
        'api_report_data_courier_metrics_timings',
        json={
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2020, 5, 10),
            },
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')

    await t.post_ok(
        'api_report_data_courier_metrics_timings',
        json={
            'store_id': store.store_id,
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')


async def test_list_invalid_period(api, dataset: dt, clickhouse_client):
    # pylint: disable=unused-argument
    store = await dataset.store()
    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_courier_metrics_timings',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2010, 5, 1),
            },
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'ER_BAD_REQUEST')


async def test_list_access(api, tap, dataset: dt, clickhouse_client):
    # pylint: disable=unused-argument
    store = await dataset.store()
    other_store = await dataset.store()
    user = await dataset.user(store=store, role='executer')

    t = await api(user=user)
    request_body = {
        'store_id': store.store_id,
        'period': {
            'begin': datetime.date(2020, 5, 5),
            'end': datetime.date(2020, 5, 5),
        },
    }
    with tap.subtest(3, 'Ручка недоступна без пермита') as taps:
        t.tap = taps
        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json=request_body
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

    with user.role as role:
        role.add_permit('courier_analytics', True)

        with tap.subtest(3, 'Пермит есть - ручка доступна') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_courier_metrics_timings',
                json=request_body
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

        with tap.subtest(3, 'Ручка недоступна для другой лавки') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_courier_metrics_timings',
                json={
                    'store_id': other_store.store_id,
                    'period': {
                        'begin': datetime.date(2020, 5, 5),
                        'end': datetime.date(2020, 5, 5),
                    },
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


async def test_empty(tap, api, dataset: dt, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(4, 'Пустой ответ'):
        store = await dataset.store()

        t = await api(role='admin')

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': datetime.date(2020, 5, 6),
                    'end': datetime.date(2020, 5, 10),
                }
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('couriers', [])


async def test_courier_cte(tap, api, now, dataset: dt, tzone,
                           clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            7,
            'Курьерский CTE по одному курьеру. '
            'Курьер назначен, потом собрали заказ'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_matched(
            timestamp=today_at_12 + datetime.timedelta(minutes=2),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_wms_order_complete(
            timestamp=today_at_12 + datetime.timedelta(minutes=3),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_delivering_arrived(
            timestamp=today_at_12 + datetime.timedelta(minutes=13),
            order=order,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        tap.note(
            'grocery_delivering_arrived '
            '- max(wms_order_complete, grocery_order_matched)'
        )
        t.json_is('couriers.0.courier_id', courier.courier_id)
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.courier_cte.value', 10.0)


async def test_courier_cte_2(tap, api, now, dataset: dt, tzone,
                             clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            6,
            'Курьерский CTE по одному курьеру. '
            'Заказ собрали, потом курьер назначен'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_wms_order_complete(
            timestamp=today_at_12 + datetime.timedelta(minutes=3),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_order_matched(
            timestamp=today_at_12 + datetime.timedelta(minutes=5),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_delivering_arrived(
            timestamp=today_at_12 + datetime.timedelta(minutes=13),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=today_at_12 + datetime.timedelta(minutes=14),
            order=order,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        tap.note(
            'grocery_delivering_arrived '
            '- max(wms_order_complete, grocery_order_matched)'
        )
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.courier_cte.value', 8.0)


async def test_timings_two_couriers(tap, api, now, dataset: dt, tzone,
                                    clickhouse_client):
    # pylint: disable=unused-argument, too-many-locals
    with tap.plan(6, 'Полный CTE от подтвержден до статуса "Прибыл к клиенту"'):
        store = await dataset.store(tz='UTC')
        courier_1 = await dataset.courier(store=store)
        courier_2 = await dataset.courier(store=store)
        order_1 = await dataset.order(store=store)
        order_2 = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order_1,
            store=store,
            courier=courier_1,
        )

        await dataset.ch_wms_order_complete(
            timestamp=today_at_12 + datetime.timedelta(minutes=3),
            order=order_1,
            store=store,
        )

        await dataset.ch_grocery_order_matched(
            timestamp=today_at_12 + datetime.timedelta(minutes=4),
            order=order_1,
            store=store,
            courier=courier_1,
        )

        await dataset.ch_grocery_delivering_arrived(
            timestamp=today_at_12 + datetime.timedelta(minutes=12),
            order=order_1,
            store=store,
            courier=courier_1,
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order_2,
            store=store,
            courier=courier_2,
        )

        await dataset.ch_wms_order_complete(
            timestamp=today_at_12 + datetime.timedelta(minutes=3),
            order=order_2,
            store=store,
        )

        await dataset.ch_grocery_order_matched(
            timestamp=today_at_12 + datetime.timedelta(minutes=6),
            order=order_2,
            store=store,
            courier=courier_2,
        )

        await dataset.ch_grocery_delivering_arrived(
            timestamp=today_at_12 + datetime.timedelta(minutes=17),
            order=order_2,
            store=store,
            courier=courier_2,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        result_couriers = t.res['json']['couriers']
        tap.eq(len(result_couriers), 2, 'Данные по 2 курьерам')
        couriers = {it['courier_external_id']: it for it in result_couriers}
        tap.note(
            'grocery_delivering_arrived '
            '- max(wms_order_complete, grocery_order_matched)'
        )
        tap.eq(
            couriers[courier_1.external_id]['courier_cte']['value'],
            8.0,
            'Верный CTE у 1-го курьера'
        )
        tap.eq(
            couriers[courier_2.external_id]['courier_cte']['value'],
            11.0,
            'Верный CTE у 2-го курьера'
        )


async def test_courier_cte_miss_arrived(tap, api, now, dataset: dt, tzone,
                                        clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            6,
            'Курьерский CTE по одному курьеру. '
            'Нет события "Прибыл" берем "Доставлен"'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_wms_order_complete(
            timestamp=today_at_12 + datetime.timedelta(minutes=3),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_order_matched(
            timestamp=today_at_12 + datetime.timedelta(minutes=5),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=today_at_12 + datetime.timedelta(minutes=14),
            order=order,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        tap.note(
            'grocery_order_delivered '
            '- max(wms_order_complete, grocery_order_matched)'
        )
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.courier_cte.value', 9.0)


async def test_pickup_time_match_first(tap, api, now, dataset: dt, tzone,
                                       clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            6,
            'Время заобра заказа. Назначили курьера, потом собрали заказ'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_matched(
            timestamp=today_at_12 + datetime.timedelta(minutes=2),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_wms_order_complete(
            timestamp=today_at_12 + datetime.timedelta(minutes=3),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_order_pickup(
            timestamp=today_at_12 + datetime.timedelta(minutes=7),
            order=order,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        tap.note(
            'grocery_order_pickup '
            '- max(wms_order_complete, grocery_order_matched)'
        )
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.pickup_time.value', 4.0)


async def test_pickup_time_complete_first(tap, api, now, dataset: dt, tzone,
                                          clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            6,
            'Время заобра заказа. Назначили курьера, потом собрали заказ'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_wms_order_complete(
            timestamp=today_at_12 + datetime.timedelta(minutes=3),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_order_matched(
            timestamp=today_at_12 + datetime.timedelta(minutes=5),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_pickup(
            timestamp=today_at_12 + datetime.timedelta(minutes=7),
            order=order,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        tap.note(
            'grocery_order_pickup '
            '- max(wms_order_complete, grocery_order_matched)'
        )
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.pickup_time.value', 2.0)


async def test_to_client_time(tap, api, now, dataset: dt, tzone,
                              clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            6,
            'Время от забирания заказа до прибытия к клиенту'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_pickup(
            timestamp=today_at_12 + datetime.timedelta(minutes=7),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_delivering_arrived(
            timestamp=today_at_12 + datetime.timedelta(minutes=17),
            order=order,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        tap.note('grocery_delivering_arrived - grocery_order_pickup ')
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.to_client_time.value', 10.0)


async def test_to_client_miss_arrived(tap, api, now, dataset: dt, tzone,
                                      clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            6,
            'Если нет события "прибыл", то не считаем to_client_time'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_pickup(
            timestamp=today_at_12 + datetime.timedelta(minutes=7),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=today_at_12 + datetime.timedelta(minutes=17),
            order=order,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        tap.note('grocery_delivering_arrived - grocery_order_pickup ')
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.to_client_time.value', None)


async def test_drop_off_time(tap, api, now, dataset: dt, tzone,
                             clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            6,
            'Время передачи заказа'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_delivering_arrived(
            timestamp=today_at_12 + datetime.timedelta(minutes=17),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=today_at_12 + datetime.timedelta(minutes=20),
            order=order,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        tap.note('grocery_order_delivered - grocery_delivering_arrived')
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.drop_off_time.value', 3.0)


async def test_drop_off_time_miss_arrived(tap, api, now, dataset: dt, tzone,
                                          clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            6,
            'Если нет события "прибыл", то не считаем drop_off_time'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_pickup(
            timestamp=today_at_12 + datetime.timedelta(minutes=7),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=today_at_12 + datetime.timedelta(minutes=20),
            order=order,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        tap.note('grocery_order_delivered - grocery_delivering_arrived')
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.drop_off_time.value', None)


async def test_returning_time(tap, api, now, dataset: dt, tzone,
                              clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            6,
            'Время возвращения на лавку'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=today_at_12 + datetime.timedelta(minutes=20),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_return_depot(
            timestamp=today_at_12 + datetime.timedelta(minutes=25),
            order=order,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        tap.note('grocery_return_depot - grocery_order_delivered')
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.returning_time.value', 5.0)


async def test_returning_time_batch(tap, api, now, dataset: dt, tzone,
                                    clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            6,
            'Время возвращения на лавку. '
            'При батчинге учитываем последний заказ'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order_1 = await dataset.order(store=store)
        order_2 = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_return_depot(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order_1,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=1),
            order=order_2,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=today_at_12 + datetime.timedelta(minutes=15),
            order=order_1,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=today_at_12 + datetime.timedelta(minutes=20),
            order=order_2,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_return_depot(
            timestamp=today_at_12 + datetime.timedelta(minutes=26),
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        tap.note('grocery_return_depot - grocery_order_delivered')
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.returning_time.value', 6.0)


async def test_returning_wrong_order(tap, api, now, dataset: dt, tzone,
                                     clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            6,
            'Время возвращения на лавку. Батчинг. '
            'Если чекин пришел раньше, чем доставлен, то не считаем заказ'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order_1 = await dataset.order(store=store)
        order_2 = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_return_depot(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order_1,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=1),
            order=order_2,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=today_at_12 + datetime.timedelta(minutes=15),
            order=order_1,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_return_depot(
            timestamp=today_at_12 + datetime.timedelta(minutes=20),
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=today_at_12 + datetime.timedelta(minutes=20, seconds=30),
            order=order_2,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        tap.note('grocery_return_depot - grocery_order_delivered')
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.returning_time.value', None)


async def test_returning_time_canceled(tap, api, now, dataset: dt, tzone,
                                       clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            6,
            'Время возвращения на лавку. Заказ отменен'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_delivering_arrived(
            timestamp=today_at_12 + datetime.timedelta(minutes=17),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_closed(
            timestamp=today_at_12 + datetime.timedelta(minutes=20),
            order=order,
            store=store,
            is_canceled=1,
        )

        await dataset.ch_grocery_return_depot(
            timestamp=today_at_12 + datetime.timedelta(minutes=25),
            order=order,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        tap.note('grocery_return_depot - grocery_order_closed')
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.returning_time.value', 5.0)


async def test_returning_canceled_2(tap, api, now, dataset: dt, tzone,
                                    clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            6,
            'Время возвращения на лавку. '
            'Заказ отменен, но курьер не прибыл к клиенту'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_closed(
            timestamp=today_at_12 + datetime.timedelta(minutes=20),
            order=order,
            store=store,
            is_canceled=1,
        )

        await dataset.ch_grocery_return_depot(
            timestamp=today_at_12 + datetime.timedelta(minutes=25),
            order=order,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        tap.note('grocery_return_depot - grocery_order_closed')
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.returning_time.value', None)


async def test_delivered_orders(tap, api, now, dataset: dt, tzone,
                                clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            7,
            'Доставленные заказы.'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_delivering_arrived(
            timestamp=today_at_12 + datetime.timedelta(minutes=13),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=today_at_12 + datetime.timedelta(minutes=14),
            order=order,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.delivered_orders.value', 1)
        t.json_is('couriers.0.miss_arrived_orders.value', 0)


async def test_miss_arrived_orders(tap, api, now, dataset: dt, tzone,
                                   clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            7,
            'Доставленные заказы без события "прибыл"'
    ):
        store = await dataset.store(tz='UTC')
        courier = await dataset.courier(store=store)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            courier=courier,
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=today_at_12 + datetime.timedelta(minutes=14),
            order=order,
            store=store,
            courier=courier,
        )

        await t.post_ok(
            'api_report_data_courier_metrics_timings',
            json={
                'store_id': store.store_id,
                'period': {
                    'begin': today,
                    'end': today,
                }
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq_ok(len(t.res['json']['couriers']), 1, 'Данные по 1 курьеру')
        t.json_is('couriers.0.courier_external_id', courier.external_id)
        t.json_is('couriers.0.delivered_orders.value', 1)
        t.json_is('couriers.0.miss_arrived_orders.value', 1)
