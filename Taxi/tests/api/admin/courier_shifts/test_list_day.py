from datetime import timezone, timedelta

import pytest

from libstall.util import tzone


async def test_list_day_simple(tap, api, dataset, now):
    with tap.plan(6, 'Список смен по дате и по складу'):
        store = await dataset.store(tz='UTC')
        user = await dataset.user(store=store)

        _midnight = now(tzone(tz='UTC')).replace(hour=0, minute=0)

        # цель
        shift = await dataset.courier_shift(
            store=store,
            started_at=_midnight + timedelta(hours=2),
            closes_at=_midnight + timedelta(hours=4),
            tz='UTC',
        )
        # сегодня, но чужая
        await dataset.courier_shift(
            started_at=_midnight + timedelta(hours=2),
            closes_at=_midnight + timedelta(hours=4),
            tz='UTC',
        )

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_list_day',
                        json={
                            'local_date': _midnight.date(),
                            'store_id': shift.store_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('courier_shifts.0.courier_shift_id',
                  shift.courier_shift_id)
        t.json_hasnt('courier_shifts.1')


@pytest.mark.parametrize(
    'offset_start,offset_end', [
        (2, 8),     # начинается и заканчивается сегодня (с 02:00 до 08:00)
        (22, 26),   # начинается сегодня в 22:00, закончится завтра в 04:00
    ]
)
@pytest.mark.parametrize('tz', [
    'US/Hawaii',         # UTC-10
    'Europe/London',     # UTC+0
    'Asia/Vladivostok',  # UTC+10
])
async def test_list_day(tap, api, dataset, now, offset_start, offset_end, tz):
    with tap.plan(6, 'Список смен по складу пользователя'):
        store = await dataset.store(tz=tz)
        user = await dataset.user(store=store)

        _midnight = now(tzone(tz=tz)).replace(hour=0, minute=0)

        # цель
        shift = await dataset.courier_shift(
            store=store,
            started_at=_midnight + timedelta(hours=offset_start),
            closes_at=_midnight + timedelta(hours=offset_end),
            tz=tz,
        )

        # вчера, 3-часовая смена, начавшаяся вчера
        await dataset.courier_shift(
            store=store,
            started_at=_midnight - timedelta(hours=2),
            closes_at=_midnight + timedelta(hours=1),
            tz=tz,
        )
        # завтра, 1-часовая смена в начале дня
        await dataset.courier_shift(
            store=store,
            started_at=_midnight + timedelta(days=1, hours=1),
            closes_at=_midnight + timedelta(days=1, hours=2),
            tz=tz,
        )
        # сегодня, но чужая
        await dataset.courier_shift(
            started_at=_midnight + timedelta(hours=offset_start),
            closes_at=_midnight + timedelta(hours=offset_end),
            tz=tz,
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list_day',
                            json={
                                'local_date': _midnight.date(),
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is('courier_shifts.0.courier_shift_id',
                      shift.courier_shift_id)
            t.json_hasnt('courier_shifts.1')


async def test_list_day_own(tap, api, dataset, now):
    with tap.plan(6, 'Без параметра store_id - только свой склад'):
        store_1 = await dataset.store(tz='UTC')
        user = await dataset.user(store=store_1)

        _midnight = now(tz=timezone.utc).replace(hour=0, minute=0)
        shift = await dataset.courier_shift(
            store=store_1,
            started_at=_midnight + timedelta(hours=2),
            closes_at=_midnight + timedelta(hours=4),
            tz='UTC',
        )
        await dataset.courier_shift(
            started_at=_midnight + timedelta(hours=2),
            closes_at=_midnight + timedelta(hours=4),
            tz='UTC',
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_list_day',
                json={
                    'local_date': _midnight.date(),
                },
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is(
                'courier_shifts.0.courier_shift_id',
                shift.courier_shift_id,
            )
            t.json_hasnt('courier_shifts.1')


async def test_list_day_alien(tap, api, dataset, now):
    with tap.plan(6, 'Доступ к сменам чужой лавки'):
        store_1 = await dataset.store(tz='UTC')
        user = await dataset.user()

        _midnight = now(tz=timezone.utc).replace(hour=0, minute=0)
        shift = await dataset.courier_shift(
            store=store_1,
            started_at=_midnight + timedelta(hours=2),
            closes_at=_midnight + timedelta(hours=4),
            tz='UTC',
        )
        await dataset.courier_shift(
            started_at=_midnight + timedelta(hours=2),
            closes_at=_midnight + timedelta(hours=4),
            tz='UTC',
        )

        with user.role as role:
            role.add_permit('out_of_store', True)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_list_day',
                json={
                    'local_date': _midnight.date(),
                    'store_id': store_1.store_id,
                },
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is(
                'courier_shifts.0.courier_shift_id',
                shift.courier_shift_id,
            )
            t.json_hasnt('courier_shifts.1')


async def test_stores_allow_alien(tap, api, dataset, now):
    with tap.plan(6, 'Пользователь видит склады из разрешенного списка'):
        store_1 = await dataset.store(tz='UTC')
        store_2 = await dataset.store(tz='UTC')
        user = await dataset.user(store=store_2,
                                  stores_allow=[store_1.store_id])

        _midnight = now(tz=timezone.utc).replace(hour=0, minute=0)
        shift = await dataset.courier_shift(
            store=store_1,
            started_at=_midnight + timedelta(hours=2),
            closes_at=_midnight + timedelta(hours=4),
            tz='UTC',
        )
        await dataset.courier_shift(
            started_at=_midnight + timedelta(hours=2),
            closes_at=_midnight + timedelta(hours=4),
            tz='UTC',
        )

        with user.role as role:
            role.add_permit('out_of_store', True)

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list_day',
                            json={
                                'local_date': _midnight.date(),
                                'store_id': store_1.store_id,
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is('courier_shifts.0.courier_shift_id',
                      shift.courier_shift_id)
            t.json_hasnt('courier_shifts.1')


async def test_stores_allow_denied(tap, api, dataset, now):
    with tap.plan(3, 'Попытка доступ к лавке вне списка разрешенных'):
        store_1 = await dataset.store(tz='UTC')
        store_2 = await dataset.store(tz='UTC')
        user = await dataset.user(
            stores_allow=[store_1.store_id],
        )

        _midnight = now(tz=timezone.utc).replace(hour=0, minute=0)
        with user.role as role:
            role.add_permit('out_of_store', True)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_list_day',
                json={
                    'local_date': _midnight.date(),
                    'store_id': store_2.store_id,
                },
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')
