# pylint: disable=unused-variable,too-many-locals,invalid-name,too-many-lines

from datetime import date, time, datetime, timezone, timedelta
from random import randint

import pytest

from libstall.util import tzone
from stall.model.courier_shift import (
    CourierShiftEvent,
    COURIER_SHIFT_STATUSES,
    COURIER_SHIFT_SOURCES,
    COURIER_SHIFT_PLACEMENT,
    ZONE_DELIVERY_TYPES
)


async def test_list(tap, api, dataset):
    with tap.plan(11, 'Список ограниченный складом пользователя'):
        store1 = await dataset.store()
        store2 = await dataset.store()
        user = await dataset.user(store=store1)

        courier_shift1 = await dataset.courier_shift(store=store1)
        courier_shift2 = await dataset.courier_shift(store=store2)

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list', json={})

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is(
                'courier_shifts.0.courier_shift_id',
                courier_shift1.courier_shift_id,
            )
            t.json_hasnt('courier_shifts.1')

            await t.post_ok(
                'api_admin_courier_shifts_list',
                json={
                    'cursor': t.res['json']['cursor'],
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_hasnt('courier_shifts.0')


async def test_cursor(tap, api, dataset, cfg, now):
    with tap.plan(20, 'Проверяем работу сортировки'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        count, chunk = 10, 2

        cfg.set('cursor.limit', chunk)
        _now = now(timezone.utc) - timedelta(days=count/2)

        for _ in range(count):
            await dataset.courier_shift(
                store=store,
                started_at=_now + timedelta(days=randint(0, count*2))
            )

        i = 0
        cursor = None
        prev = _now + timedelta(days=count*3), float('inf')
        with user.role as role:
            role.add_permit('out_of_store', True)
            role.add_permit('out_of_company', True)

            for req_i in range(count // chunk):
                tap.note(f'Запрос #{req_i}.')
                t = await api(user=user)
                await t.post_ok(
                    'api_admin_courier_shifts_list', json={
                        'store_id': store.store_id,
                        'cursor': cursor,
                    }
                )
                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_has('cursor')

                # Каждая следующая смена должна начинаться все раньше и раньше
                cursor = t.res['json']['cursor']
                for shift in t.res['json']['courier_shifts']:
                    cur = datetime.fromisoformat(shift['started_at']), \
                        shift['serial']

                    if cur > prev:
                        tap.failed(f'сортировка нарушена #{i}: {cur} > {prev}')

                    prev = cur
                    i += 1


async def test_list_only_self_store(tap, api, dataset):
    with tap.plan(6, 'Пользователь без пермита то видит только свой склад'):
        store1 = await dataset.store()
        store2 = await dataset.store()
        user = await dataset.user(store=store1)

        courier_shift1 = await dataset.courier_shift(store=store1)
        courier_shift2 = await dataset.courier_shift(store=store2)

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_list',
                json={'store_id': [store1.store_id, store2.store_id]},
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is(
                'courier_shifts.0.courier_shift_id',
                courier_shift1.courier_shift_id,
            )
            t.json_hasnt('courier_shifts.1')


async def test_list_only_stores_allow(tap, api, dataset):
    with tap.plan(6, 'Пользователь видит склады из разрешенного списка'):
        store1 = await dataset.store()
        store2 = await dataset.store()
        user = await dataset.user(
            store=store1,
            stores_allow=[store2.store_id],
        )

        courier_shift1 = await dataset.courier_shift(store=store1)
        courier_shift2 = await dataset.courier_shift(store=store2)

        with user.role as role:
            role.add_permit('out_of_store', True)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_list',
                json={},
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is(
                'courier_shifts.0.courier_shift_id',
                courier_shift2.courier_shift_id,
            )
            t.json_hasnt('courier_shifts.1')


async def test_list_only_stores_allow_with_filter(tap, api, dataset):
    with tap.plan(6, 'Пользователь видит склады из разрешенного списка'):
        store1 = await dataset.store()
        store2 = await dataset.store()
        store3 = await dataset.store()
        user = await dataset.user(
            store=store1,
            stores_allow=[store1.store_id, store2.store_id],
        )

        courier_shift1 = await dataset.courier_shift(store=store1)
        courier_shift2 = await dataset.courier_shift(store=store2)
        courier_shift3 = await dataset.courier_shift(store=store3)

        with user.role as role:
            role.add_permit('out_of_store', True)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_list',
                json={'store_id': [store2.store_id]},
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is(
                'courier_shifts.0.courier_shift_id',
                courier_shift2.courier_shift_id,
            )
            t.json_hasnt('courier_shifts.1')


@pytest.mark.parametrize('name', ['group_id'])
async def test_list_filter_id(tap, api, dataset, name, uuid):
    with tap.plan(5, f'Список с фильтром по "{name}'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        target_val = uuid()
        cs_targets = [
            await dataset.courier_shift(store=store, **{name: target_val})
            for _ in range(2)
        ]
        cs_ignored_unassigned = [
            await dataset.courier_shift(store=store)
            for _ in range(3)
        ]

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list', json={
                name: target_val,
            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')

            cs_response = t.res['json']['courier_shifts']
            tap.eq_ok(
                sorted([cs['courier_shift_id'] for cs in cs_response]),
                sorted([cs.courier_shift_id for cs in cs_targets]),
                'Все смены правильные, лишних нет'
            )


async def test_list_filter_import_id(tap, api, dataset):
    with tap.plan(5, 'Список с фильтром по "import_id"'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        schedule = await dataset.courier_shift_schedule(store=store)
        import_id = schedule.courier_shift_schedule_id
        cs_targets = [
            await dataset.courier_shift(store=store, import_id=import_id)
            for _ in range(2)
        ]
        cs_ignored_unassigned = [
            await dataset.courier_shift(store=store)
            for _ in range(3)
        ]

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list', json={
                'import_id': import_id,
            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')

            cs_response = t.res['json']['courier_shifts']
            tap.eq_ok(
                sorted([cs['courier_shift_id'] for cs in cs_response]),
                sorted([cs.courier_shift_id for cs in cs_targets]),
                'Все смены правильные, лишних нет'
            )


async def test_list_filter_courier_id(tap, api, dataset):
    with tap.plan(5, 'Список с фильтром по "courier_id"'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        courier = await dataset.courier(store=store)
        cs_targets = [
            await dataset.courier_shift(
                store=store,
                courier_id=courier.courier_id
            )
            for _ in range(2)
        ]
        cs_ignored_unassigned = [
            await dataset.courier_shift(store=store)
            for _ in range(3)
        ]

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list', json={
                'courier_id': courier.courier_id,
            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')

            cs_response = t.res['json']['courier_shifts']
            tap.eq_ok(
                sorted([cs['courier_shift_id'] for cs in cs_response]),
                sorted([cs.courier_shift_id for cs in cs_targets]),
                'Все смены правильные, лишних нет'
            )


async def test_list_filter_cluster_id(tap, api, dataset):
    with tap.plan(6, 'Список с фильтром по "cluster_id"'):
        cluster1 = await dataset.cluster()
        cluster2 = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster1)
        store2 = await dataset.store(cluster=cluster2)
        user = await dataset.user(store=store1)

        shift1 = await dataset.courier_shift(store=store1)
        shift2 = await dataset.courier_shift(store=store2)

        with user.role as role:
            role.add_permit('out_of_store', True)
            role.add_permit('out_of_company', True)

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list', json={
                'cluster_id': cluster1.cluster_id,
            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is(
                'courier_shifts.0.courier_shift_id',
                shift1.courier_shift_id
            )
            t.json_hasnt('courier_shifts.1')


async def test_list_date(tap, api, dataset):
    with tap.plan(8, 'Список с фильтром по дате'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 9, 0, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 12, 0, 0, 0, tzinfo=timezone.utc),
        )
        shift1 = await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 10, 0, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 15, 0, 0, 0, tzinfo=timezone.utc),
        )
        shift2 = await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 14, 0, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 16, 0, 0, 0, tzinfo=timezone.utc),
        )
        shift3 = await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 9, 21, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 17, 0, 0, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 15, 21, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 16, 0, 0, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 16, 0, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 17, 0, 0, 0, tzinfo=timezone.utc),
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list', json={
                'start_date_from': date(2020, 1, 10),
                'start_date_to': date(2020, 1, 15),
            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')

            shifts = t.res['json']['courier_shifts']
            tap.eq(len(shifts), 3, 'Найдено 3 смены')

            result = {shift['courier_shift_id']: shift for shift in shifts}
            tap.ok(result[shift1.courier_shift_id], 'Смена от 10 выведена')
            tap.ok(result[shift2.courier_shift_id], 'Смена от 14 выведена')
            tap.ok(result[shift3.courier_shift_id], 'Смена от 9 выведена')


async def test_list_time(tap, api, dataset):
    with tap.plan(7, 'Список с фильтром по времени'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 8, 9, 30, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 8, 11, 0, 0, tzinfo=timezone.utc),
        )
        shift1 = await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 9, 9, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 9, 17, 30, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 10, 9, 0, 1, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 11, 17, 30, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 10, 9, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 11, 17, 0, 0, tzinfo=timezone.utc),
        )
        shift2 = await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 10, 9, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 11, 17, 30, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 14, 4, 30, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 15, 9, 0, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 16, 17, 30, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 17, 23, 59, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 18, 12, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 18, 20, 30, 0, tzinfo=timezone.utc),
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list', json={
                'started_time_at': time(12).strftime('%H:%M'),
                'closes_time_at': time(20, 30).strftime('%H:%M'),
            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')

            shifts = t.res['json']['courier_shifts']
            tap.eq(len(shifts), 2, 'Найдено 2 смены')

            result = {shift['courier_shift_id']: shift for shift in shifts}
            tap.ok(result[shift1.courier_shift_id], 'Смена от 9 выведена')
            tap.ok(result[shift2.courier_shift_id], 'Смена от 10-11 выведена')


async def test_list_datetime(tap, api, dataset):
    with tap.plan(6, 'Список с фильтром по дате и времени'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 8, 10, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 8, 11, 0, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 9, 12, 30, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 9, 15, 0, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 9, 22, 30, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 10, 0, 0, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 10, 0, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 10, 6, 0, 0, tzinfo=timezone.utc),
        )
        shift = await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 14, 9, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 14, 12, 0, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 14, 12, 0, 1, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 15, 1, 0, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 16, 9, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 16, 13, 59, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 16, 12, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 16, 14, 0, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 20, 20, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 20, 22, 0, 0, tzinfo=timezone.utc),
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list', json={
                'start_date_from': date(2020, 1, 10),
                'start_date_to': date(2020, 1, 15),
                'started_time_at': time(12).strftime('%H:%M'),
                'closes_time_at': time(15).strftime('%H:%M'),
            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')

            shifts = t.res['json']['courier_shifts']
            tap.eq(len(shifts), 1, 'Найдена 1 смена')

            result = {shift['courier_shift_id']: shift for shift in shifts}
            tap.ok(result[shift.courier_shift_id], 'Смена от 15.01 15:00')


async def test_list_timezone(tap, api, dataset):
    with tap.plan(10, 'Список с фильтром с учётом временной зоны'):
        store = await dataset.store(tz='Asia/Omsk') # UTC+06:00
        user = await dataset.user(store=store)

        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 9, 12, 30, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 9, 15, 0, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 10, 5, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 10, 12, 0, 0, tzinfo=timezone.utc),
        )
        shift1 = await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 11, 12, 0, 0, tzinfo=tzone(6)),
            closes_at=datetime(2020, 1, 12, 20, 0, 0, tzinfo=tzone(6)),
        )
        shift2 = await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 12, 6, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 13, 14, 0, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 9, 6, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 9, 14, 0, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 9, 6, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 11, 14, 0, 0, tzinfo=timezone.utc),
        )
        shift3 = await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 15, 9, 0, 0, tzinfo=tzone(3)),
            closes_at=datetime(2020, 1, 15, 17, 0, 0, tzinfo=tzone(3)),
        )
        shift4 = await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 15, 17, 0, 0, tzinfo=tzone(11)),
            closes_at=datetime(2020, 1, 16, 1, 0, 0, tzinfo=tzone(11)),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 16, 1, 0, 1, tzinfo=tzone(11)),
            closes_at=datetime(2020, 1, 16, 1, 0, 2, tzinfo=tzone(11)),
        )
        shift5 = await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 9, 23, 0, 0, tzinfo=tzone(-7)),
            closes_at=datetime(2020, 1, 10, 7, 0, 0, tzinfo=tzone(-7)),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2020, 1, 16, 12, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2020, 1, 16, 22, 0, 0, tzinfo=timezone.utc),
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list', json={
                'start_date_from': date(2020, 1, 10),
                'start_date_to': date(2020, 1, 15),
                'started_time_at': time(12).strftime('%H:%M'),
                'closes_time_at': time(20).strftime('%H:%M'),
            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')

            shifts = t.res['json']['courier_shifts']
            tap.eq(len(shifts), 5, 'Найдено 5 смен')

            result = {shift['courier_shift_id']: shift for shift in shifts}
            tap.ok(result[shift1.courier_shift_id], 'Смена местное верхняя')
            tap.ok(result[shift2.courier_shift_id], 'Смена UTC внутри')
            tap.ok(result[shift3.courier_shift_id], 'Смена UTC+3 верхняя')
            tap.ok(result[shift4.courier_shift_id], 'Смена UTC+11 верхняя')
            tap.ok(result[shift5.courier_shift_id], 'Смена UTC-7 нижняя')


async def test_list_dst(tap, api, dataset):
    with tap.plan(7, 'Список с фильтром с учётом зимнего времени'):
        store = await dataset.store(tz='Europe/London') # UTC+01:00 / UTC
        user = await dataset.user(store=store)

        await dataset.courier_shift(
            store=store,
            started_at=datetime(2021, 10, 1, 10, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2021, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        shift1 = await dataset.courier_shift(
            store=store,
            started_at=datetime(2021, 10, 1, 11, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2021, 10, 1, 15, 0, 0, tzinfo=timezone.utc),
        )
        await dataset.courier_shift(
            store=store,
            started_at=datetime(2021, 12, 1, 11, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2021, 12, 2, 0, 0, 0, tzinfo=timezone.utc),
        )
        shift2 = await dataset.courier_shift(
            store=store,
            started_at=datetime(2021, 12, 1, 12, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2021, 12, 1, 0, 0, 1, tzinfo=timezone.utc),
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list', json={
                'started_time_at': time(12).strftime('%H:%M'),
            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')

            shifts = t.res['json']['courier_shifts']
            tap.eq(len(shifts), 2, 'Найдено 2 смены')

            result = {shift['courier_shift_id']: shift for shift in shifts}
            tap.ok(result[shift1.courier_shift_id], 'Смена от 01.10 11:30')
            tap.ok(result[shift2.courier_shift_id], 'Смена от 01.12 12:30')


async def test_list_store_id_all_stories(tap, api, dataset):
    with tap.plan(15, 'Список с фильтром по store_id, все компании'):
        company1 = await dataset.company()
        store1 = await dataset.store(company=company1)
        store2 = await dataset.store(company=company1)
        store3 = await dataset.store()
        user = await dataset.user(company_id=company1.company_id)

        courier_shifts_store1 = [
            await dataset.courier_shift(store=store1)
            for _ in range(2)
        ]
        courier_shifts_store2 = [
            await dataset.courier_shift(store=store2)
            for _ in range(3)
        ]
        courier_shifts_store3 = [
            await dataset.courier_shift(store=store3)
            for _ in range(3)
        ]

        with user.role as role:
            role.add_permit('out_of_store', True)
            role.add_permit('out_of_company', True)

            t = await api(user=user)

            cases = [
                (
                    store1.store_id,
                    courier_shifts_store1,
                    'Расписания для store1, своя компания',
                ),
                (
                    [store1.store_id, store2.store_id],
                    courier_shifts_store1 + courier_shifts_store2,
                    'Расписания для store1 и store2, своя компания',
                ),
                (
                    [store3.store_id],
                    courier_shifts_store3,
                    'Расписания для store3, чужая компания',
                ),
            ]

            for store_id, cs_target, msg in cases:
                await t.post_ok('api_admin_courier_shifts_list', json={
                    'store_id': store_id,
                })
                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_has('cursor')
                cs_response = t.res['json']['courier_shifts']
                tap.eq_ok(
                    sorted([cs['courier_shift_id'] for cs in cs_response]),
                    sorted([cs.courier_shift_id for cs in cs_target]),
                    msg
                )


async def test_list_store_id_own_company(tap, api, dataset):
    with tap.plan(10, 'Список с фильтром по store_id'):
        company1 = await dataset.company()
        company2 = await dataset.company()
        store1 = await dataset.store(company=company1)
        store2 = await dataset.store(company=company2)
        user = await dataset.user(company_id=company1.company_id, store_id=None)

        courier_shifts_store1 = [
            await dataset.courier_shift(store=store1)
            for _ in range(2)
        ]
        courier_shifts_store2 = [
            await dataset.courier_shift(store=store2)
            for _ in range(3)
        ]

        with user.role as role:
            role.add_permit('out_of_store', True)
            role.remove_permit('out_of_company')

            t = await api(user=user)

            cases = [
                (
                    store1.store_id,
                    courier_shifts_store1,
                    'Расписания для store1 из своей компании',
                ),
                (
                    [store1.store_id, store2.store_id],
                    courier_shifts_store1,
                    'Расписания для store1 + store2 чужой компании',
                ),
            ]

            for store_id, cs_target, msg in cases:
                await t.post_ok('api_admin_courier_shifts_list', json={
                    'store_id': store_id,
                })
                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_has('cursor')
                cs_response = t.res['json']['courier_shifts']
                tap.eq_ok(
                    sorted([cs['courier_shift_id'] for cs in cs_response]),
                    sorted([cs.courier_shift_id for cs in cs_target]),
                    msg
                )


@pytest.mark.parametrize(
    'param_name,param_values',
    [
        ['source', COURIER_SHIFT_SOURCES],
        ['delivery_type', ZONE_DELIVERY_TYPES],
        ['status', COURIER_SHIFT_STATUSES],
        ['placement', COURIER_SHIFT_PLACEMENT],
    ]
)
async def test_list_filter_one(tap, api, dataset, param_name, param_values):
    with tap.plan(6, f'Список с фильтром по "{param_name}"'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        start_at = datetime(2020, 1, 10, 0, 0, 0, tzinfo=timezone.utc)
        closes_at = datetime(2020, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        target, ignored = param_values[0], param_values[1:]

        cs_target = await dataset.courier_shift(
            store=store,
            started_at=start_at,
            closes_at=closes_at,
            **{param_name: target},
        )
        cs_ignored = [await dataset.courier_shift(
            store=store,
            started_at=start_at,
            closes_at=closes_at,
            **{param_name: param_value},
        ) for param_value in ignored]

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list', json={
                'store_id': store.store_id,
                'started_at': start_at,
                'closes_at': closes_at,
                param_name: target,
            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is(
                'courier_shifts.0.courier_shift_id',
                cs_target.courier_shift_id,
            )
            t.json_hasnt('courier_shifts.1')


@pytest.mark.parametrize(
    'param_name,param_values',
    [
        ['source', COURIER_SHIFT_SOURCES],
        ['delivery_type', ZONE_DELIVERY_TYPES],
        ['status', COURIER_SHIFT_STATUSES],
        ['placement', COURIER_SHIFT_PLACEMENT],
    ]
)
async def test_list_filter_array(tap, api, dataset, param_name, param_values):
    with tap.plan(5, f'Список с фильтром по нескольким "{param_name}"'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        start_at = datetime(2020, 1, 10, 0, 0, 0, tzinfo=timezone.utc)
        closes_at = datetime(2020, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        middle = len(param_values) // 2
        targets, ignored = param_values[:middle], param_values[middle:]

        cs_targets = [await dataset.courier_shift(
            store=store,
            started_at=start_at,
            closes_at=closes_at,
            **{param_name: value},
        ) for value in targets]

        cs_ignored = [await dataset.courier_shift(
            store=store,
            started_at=start_at,
            closes_at=closes_at,
            **{param_name: value},
        ) for value in ignored]

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list', json={
                'store_id': store.store_id,
                'started_at': start_at,
                'closes_at': closes_at,
                param_name: targets
            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')

            cs_response = t.res['json']['courier_shifts']

            tap.eq_ok(
                sorted([cs['courier_shift_id'] for cs in cs_response]),
                sorted([cs.courier_shift_id for cs in cs_targets]),
                'Все смены правильные, лишних нет'
            )


async def test_list_filter_tags(tap, dataset, api, uuid):
    with tap.plan(30, 'Фильтрация по тегам'):
        tags = [
            (await dataset.courier_shift_tag(title=f'tag-{uuid()}')).title
            for _ in range(4)
        ]

        store = await dataset.store()
        user = await dataset.user(store=store)

        start_at = datetime(2020, 1, 10, 0, 0, 0, tzinfo=timezone.utc)
        closes_at = datetime(2020, 1, 15, 0, 0, 0, tzinfo=timezone.utc)

        shift_1 = await dataset.courier_shift(
            store=store,
            started_at=start_at,
            closes_at=closes_at,
            tags=[tags[0], tags[1]],
        )
        shift_2 = await dataset.courier_shift(
            store=store,
            started_at=start_at,
            closes_at=closes_at,
            tags=[tags[1], tags[2]],
        )
        shift_3 = await dataset.courier_shift(
            store=store,
            started_at=start_at,
            closes_at=closes_at,
            tags=[tags[0], tags[1], tags[2]],
        )
        shift_4 = await dataset.courier_shift(
            store=store,
            started_at=start_at,
            closes_at=closes_at,
            tags=[tags[0]],
        )
        shift_5 = await dataset.courier_shift(
            store=store,
            started_at=start_at,
            closes_at=closes_at,
            tags=[tags[3]],
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)

            for idx, (tags_param, expected_shifts) in enumerate([
                ([tags[0]], [shift_1, shift_3, shift_4]),
                ([tags[1]], [shift_1, shift_2, shift_3]),
                ([tags[2]], [shift_2, shift_3]),
                ([tags[3]], [shift_5]),
                (
                    [tags[0], tags[1], tags[3]],
                    [shift_1, shift_2, shift_3, shift_4, shift_5]
                )
            ]):
                tap.note(f'test #{idx}')

                await t.post_ok('api_admin_courier_shifts_list', json={
                    'store_id': store.store_id,
                    'started_at': start_at,
                    'closes_at': closes_at,
                    'tags': tags_param,
                })

                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_has('cursor')

                response_shifts = t.res['json']['courier_shifts']
                tap.eq({it['courier_shift_id'] for it in response_shifts},
                       {it.courier_shift_id for it in expected_shifts},
                       'all expected shifts have been returned')
                tap.eq(len(response_shifts), len(expected_shifts),
                       'none extra shifts have been returned')


async def test_list_filter_courier_tags(tap, dataset, api):
    with tap.plan(8, 'Фильтрация по тегам курьера'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        tag_1 = (await dataset.courier_shift_tag(type='courier')).title
        tag_2 = (await dataset.courier_shift_tag(type='courier')).title
        tag_3 = (await dataset.courier_shift_tag(type='courier')).title

        target_shifts = [
            await dataset.courier_shift(store=store, courier_tags=[tag_1]),
            await dataset.courier_shift(store=store, courier_tags=[tag_2]),
            await dataset.courier_shift(
                store=store,
                courier_tags=[tag_1, tag_2]
            ),
        ]

        ignored_shifts = [
            await dataset.courier_shift(store=store, courier_tags=[tag_3]),
            await dataset.courier_shift(store=store, courier_tags=[]),
            await dataset.courier_shift(store=store, courier_tags=None),
        ]

        # Только с тегом_1 и тегом_2
        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_list', json={
            'store_id': store.store_id,
            'courier_tags': [tag_1, tag_2],
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        shifts = t.res['json']['courier_shifts']
        tap.eq_ok(
            sorted([cs['courier_shift_id'] for cs in shifts]),
            sorted([cs.courier_shift_id for cs in target_shifts]),
            'Все смены правильные, лишних нет'
        )

        # Все подряд, т.к. теги не заданы
        await t.post_ok('api_admin_courier_shifts_list', json={
            'store_id': store.store_id,
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        exp = [cs.courier_shift_id for cs in (*target_shifts, *ignored_shifts)]
        cs_response = t.res['json']['courier_shifts']
        tap.eq_ok(
            sorted([cs['courier_shift_id'] for cs in cs_response]),
            sorted(exp),
            'Все смены подряд',
        )


async def test_event_detail_time(tap, api, dataset, now, time2time):
    with tap.plan(10):
        now_ = now().replace(microsecond=0)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()
        shift = await dataset.courier_shift(
            store=store,
            shift_events=[
                CourierShiftEvent({
                    'type': 'stopped',
                    'courier_id': courier.courier_id,
                    'detail': {
                        'reason': 'no_geo',
                        'last_location_time': time2time(now_),
                        'checkin_time': time2time(now_),
                    },
                }),
            ],
        )

        t = await api(role='admin')
        await t.post_ok('api_admin_courier_shifts_list', json={
            'cluster_id': cluster.cluster_id,
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_is(
            'courier_shifts.0.courier_shift_id',
            shift.courier_shift_id,
            'courier_shift_id'
        )
        t.json_is(
            'courier_shifts.0.cluster_id',
            cluster.cluster_id,
            'cluster_id'
        )
        t.json_is(
            'courier_shifts.0.shift_events.0.detail.reason',
            'no_geo',
            'reason'
        )
        t.json_hasnt('courier_shifts.1')

        detail = t.res['json']['courier_shifts'][0]['shift_events'][0]['detail']
        tap.eq(time2time(detail['checkin_time']), now_, 'checkin_time')
        tap.eq(time2time(
            detail['last_location_time']),
            now_,
            'last_location_time'
        )
