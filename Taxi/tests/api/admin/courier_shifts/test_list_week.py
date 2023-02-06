from datetime import timezone, timedelta

import pytest

from libstall.util import tzone


async def test_list_week_simple(tap, api, dataset, now):
    with tap.plan(8, 'Список смен по дате и по складу'):
        store = await dataset.store(tz='UTC')
        user = await dataset.user(store=store)

        _midnight = now(tzone(tz='UTC')).replace(hour=0, minute=0, second=0)
        _monday = _midnight + timedelta(days=14 - _midnight.weekday())

        # цель-1 (начало понедельника)
        shift_1 = await dataset.courier_shift(
            store=store,
            started_at=_monday + timedelta(minutes=1),
            closes_at=_monday + timedelta(hours=4),
            tz='UTC',
        )
        # цель-2 (среда)
        shift_2 = await dataset.courier_shift(
            store=store,
            started_at=_monday + timedelta(days=3),
            closes_at=_monday + timedelta(days=3, hours=4),
            tz='UTC',
        )
        # цель-3 (конец воскресенье)
        shift_3 = await dataset.courier_shift(
            store=store,
            started_at=_monday + timedelta(days=6, hours=23, minutes=50),
            closes_at=_monday + timedelta(days=7, hours=4),
            tz='UTC',
        )

        # среда, но чужая
        await dataset.courier_shift(
            started_at=_monday + timedelta(days=3),
            closes_at=_monday + timedelta(days=3, hours=4),
            tz='UTC',
        )
        # наша, но с другой недели
        await dataset.courier_shift(
            store=store,
            started_at=_monday - timedelta(days=7, hours=20),
            closes_at=_monday - timedelta(days=7, hours=10),
            tz='UTC',
        )

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_list_week',
                        json={
                            'local_date': _monday.date(),
                            'store_id': store.store_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('courier_shifts.0.courier_shift_id', shift_1.courier_shift_id)
        t.json_is('courier_shifts.1.courier_shift_id', shift_2.courier_shift_id)
        t.json_is('courier_shifts.2.courier_shift_id', shift_3.courier_shift_id)
        t.json_hasnt('courier_shifts.3')


@pytest.mark.parametrize(
    'offset_start,offset_end', [
        # начало понедельника
        (timedelta(hours=2), timedelta(hours=4)),
        # середина недели, среда
        (timedelta(days=3), timedelta(days=3, hours=4)),
        # конец воскресенья
        (timedelta(days=6, hours=22, minutes=50), timedelta(days=7, hours=4)),
    ]
)
@pytest.mark.parametrize('tz', [
    'US/Hawaii',         # UTC-10
    'Europe/London',     # UTC+0 (есть переход на летнее время)
    'Asia/Vladivostok',  # UTC+10
])
async def test_list_week(tap, api, dataset, now, offset_start, offset_end, tz):
    with tap.plan(6, 'Список смен по складу пользователя'):
        store = await dataset.store(tz=tz)
        user = await dataset.user(store=store)

        _midnight = now(tzone(tz=tz)).replace(hour=0, minute=0, second=0)
        _monday = _midnight + timedelta(days=14 - _midnight.weekday())

        # цель
        shift = await dataset.courier_shift(
            store=store,
            started_at=_monday + offset_start,
            closes_at=_monday + offset_end,
            tz=tz,
        )

        # смена с конца ВОСКРЕСЕНЬЯ ПРЕДЫДУЩЕЙ недели (относительно искомой)
        await dataset.courier_shift(
            store=store,
            started_at=_monday - timedelta(hours=2),
            closes_at=_monday - timedelta(minutes=10),
            tz=tz,
        )
        # смена с начала ПОНЕДЕЛЬНИКА СЛЕДУЮЩЕЙ недели (относительно искомой)
        await dataset.courier_shift(
            store=store,
            started_at=_monday + timedelta(days=7, minutes=10),
            closes_at=_monday + timedelta(days=7, minutes=120),
            tz=tz,
        )
        # та же дата, но лавка чужая
        await dataset.courier_shift(
            started_at=_monday + offset_start,
            closes_at=_monday + offset_end,
            tz=tz,
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list_week',
                            json={
                                'local_date': _monday.date(),
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is('courier_shifts.0.courier_shift_id',
                      shift.courier_shift_id)
            t.json_hasnt('courier_shifts.1')


@pytest.mark.parametrize(
    'offset_start,offset_end', [
        # начало первого дня недели (воскресенье или понедельник)
        (timedelta(hours=2), timedelta(hours=4)),
        # середина недели, среда
        (timedelta(days=3), timedelta(days=3, hours=4)),
        # конец последнего дня (суббота или воскресенье)
        (timedelta(days=6, hours=22, minutes=50), timedelta(days=7, hours=4)),
    ]
)
@pytest.mark.parametrize('week_from_sunday', [True, False])
async def test_week_from_sunday(
    tap, api, dataset, now, week_from_sunday, offset_start, offset_end,
):
    with tap.plan(6, f'За неделю, week_from_sunday={week_from_sunday}'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'week_from_sunday': week_from_sunday,
            },
            tz='Asia/Jerusalem',
        )
        store = await dataset.store(cluster=cluster, tz='Asia/Jerusalem')
        user = await dataset.user(store=store)

        _midnight = now(tzone(tz=store.tz)).replace(hour=0, minute=0, second=0)
        _week_start = _midnight + timedelta(
            days=14 - _midnight.weekday() - int(week_from_sunday)
        )

        # цель
        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            started_at=_week_start + offset_start,
            closes_at=_week_start + offset_end,
        )

        # смена с конца ПРЕДЫДУЩЕЙ недели (относительно искомой)
        await dataset.courier_shift(
            cluster=cluster,
            store=store,
            started_at=_week_start - timedelta(hours=2),
            closes_at=_week_start - timedelta(minutes=10),
        )
        # смена с начала СЛЕДУЮЩЕЙ недели (относительно искомой)
        await dataset.courier_shift(
            cluster=cluster,
            store=store,
            started_at=_week_start - timedelta(hours=6),
            closes_at=_week_start + timedelta(hours=1),
        )
        # та же дата, но лавка чужая
        await dataset.courier_shift(
            cluster=cluster,
            started_at=_week_start + offset_start,
            closes_at=_week_start + offset_end,
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list_week',
                            json={
                                'local_date': _week_start.date(),
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is('courier_shifts.0.courier_shift_id',
                      shift.courier_shift_id)
            t.json_hasnt('courier_shifts.1')


async def test_list_week_own(tap, api, dataset, now):
    with tap.plan(6, 'Без параметра store_id - только свой склад'):
        store_1 = await dataset.store(tz='UTC')
        user = await dataset.user(store=store_1)

        _midnight = now(tzone(tz='UTC')).replace(hour=0, minute=0, second=0)
        _monday = _midnight + timedelta(days=14 - _midnight.weekday())

        # цель (среда)
        shift = await dataset.courier_shift(
            store=store_1,
            started_at=_monday + timedelta(days=3),
            closes_at=_monday + timedelta(days=3, hours=4),
            tz='UTC',
        )
        # среда, но чужая
        await dataset.courier_shift(
            started_at=_monday + timedelta(days=3),
            closes_at=_monday + timedelta(days=3, hours=4),
            tz='UTC',
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_list_week',
                json={
                    'local_date': _monday.date(),
                },
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is('courier_shifts.0.courier_shift_id',
                      shift.courier_shift_id)
            t.json_hasnt('courier_shifts.1')


async def test_list_week_alien(tap, api, dataset, now):
    with tap.plan(6, 'Доступ к сменам чужой лавки'):
        store_1 = await dataset.store(tz='UTC')
        user = await dataset.user()

        _midnight = now(tzone(tz='UTC')).replace(hour=0, minute=0, second=0)
        _monday = _midnight + timedelta(days=14 - _midnight.weekday())

        # цель (среда)
        shift = await dataset.courier_shift(
            store=store_1,
            started_at=_monday + timedelta(days=3),
            closes_at=_monday + timedelta(days=3, hours=4),
            tz='UTC',
        )
        # среда, но чужая
        await dataset.courier_shift(
            started_at=_monday + timedelta(days=3),
            closes_at=_monday + timedelta(days=3, hours=4),
            tz='UTC',
        )

        with user.role as role:
            role.add_permit('out_of_store', True)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_list_week',
                json={
                    'local_date': _monday.date(),
                    'store_id': store_1.store_id,
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is('courier_shifts.0.courier_shift_id',
                      shift.courier_shift_id)
            t.json_hasnt('courier_shifts.1')


async def test_stores_allow_alien(tap, api, dataset, now):
    with tap.plan(6, 'Пользователь видит склады из разрешенного списка'):
        store_1 = await dataset.store(tz='UTC')
        store_2 = await dataset.store(tz='UTC')
        user = await dataset.user(store=store_2,
                                  stores_allow=[store_1.store_id])

        _midnight = now(tzone(tz='UTC')).replace(hour=0, minute=0, second=0)
        _monday = _midnight + timedelta(days=14 - _midnight.weekday())

        # цель (среда)
        shift = await dataset.courier_shift(
            store=store_1,
            started_at=_monday + timedelta(days=3),
            closes_at=_monday + timedelta(days=3, hours=4),
            tz='UTC',
        )
        # среда, но чужая
        await dataset.courier_shift(
            started_at=_monday + timedelta(days=3),
            closes_at=_monday + timedelta(days=3, hours=4),
            tz='UTC',
        )

        with user.role as role:
            role.add_permit('out_of_store', True)

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_list_week',
                            json={
                                'local_date': _monday.date(),
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

        with user.role as role:
            role.add_permit('out_of_store', True)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_list_week',
                json={
                    'local_date': now(tz=timezone.utc).date(),
                    'store_id': store_2.store_id,
                },
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')
