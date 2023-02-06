# pylint: disable=too-many-lines
from datetime import datetime, timezone, timedelta

import pytest

from libstall.util import now, uuid
from stall.model.courier_shift import CourierShift


async def test_store_permits_update(tap, api, dataset):
    with tap.plan(6, 'Обновление курьерской смены другого склада'):
        store = await dataset.store(tz='UTC')
        user = await dataset.user(store=store, role='admin')

        _now = now(tz=timezone.utc).replace(microsecond=0)
        external_id = uuid()
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=3)
        tags = ['one', 'two', 'three']

        # создаем смену
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'external_id': external_id,
                'delivery_type': 'rover',
                'started_at': started_at,
                'closes_at': closes_at,
                'tags': tags,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        # редактируем
        courier_shift_id = t.res['json']['courier_shift']['courier_shift_id']
        tags = ['one', 'two', 'NEW TAG']

        user2 = await dataset.user(role='admin')

        with user2.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user2)
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': courier_shift_id,
                    'delivery_type': 'car',
                    'status': 'closed',
                    'tags': tags,
                }
            )

            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


@pytest.mark.skip('пока забрали права Part Revert: LAVKADEV-2850')
@pytest.mark.parametrize('role', ['vice_store_admin', 'store_admin'])
async def test_permits_store_admins(tap, api, dataset, role):
    with tap.plan(18, f'Обновление смены директором склада - {role}'):
        store = await dataset.store(tz='UTC')
        user = await dataset.user(store=store, role=role)

        _now = now(tz=timezone.utc).replace(microsecond=0)
        external_id = uuid()
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=3)

        # создаем смену
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'external_id': external_id,
                'delivery_type': 'rover',
                'started_at': started_at,
                'closes_at': closes_at,
                'tags': ['one', 'two'],
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        courier_shift = t.res['json']['courier_shift']
        t_started_at = datetime.fromisoformat(courier_shift['started_at'])
        t_closes_at = datetime.fromisoformat(courier_shift['closes_at'])
        tap.eq(t_started_at, started_at, 'started_at')
        tap.eq(t_closes_at, closes_at, 'closes_at')
        tap.eq(courier_shift['tags'], ['one', 'two'], 'tags')
        tap.eq(courier_shift['status'], 'template', 'status')
        tap.eq(courier_shift['delivery_type'], 'rover', 'delivery_type')

        # редактируем доступные поля
        courier_shift_id = courier_shift['courier_shift_id']
        started_at += timedelta(minutes=3)
        closes_at += timedelta(minutes=3)

        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': courier_shift_id,
                'started_at': started_at,
                'closes_at': closes_at,
                'delivery_type': 'car',
                'status': 'closed',
                'tags': ['two', 'three'],
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        courier_shift = t.res['json']['courier_shift']
        t_started_at = datetime.fromisoformat(courier_shift['started_at'])
        t_closes_at = datetime.fromisoformat(courier_shift['closes_at'])
        tap.eq(t_started_at, started_at, 'started_at')
        tap.eq(t_closes_at, closes_at, 'closes_at')
        tap.eq(courier_shift['tags'], ['one', 'two'], 'tags')
        tap.eq(courier_shift['status'], 'template', 'status')
        tap.eq(courier_shift['delivery_type'], 'rover', 'delivery_type')

        t.json_is('courier_shift.delivery_type', 'rover', 'delivery_type')
        t.json_is('courier_shift.status', 'template', 'status')


async def test_permits_only_few_fields(tap, api, dataset):
    # pylint: disable=too-many-locals
    with tap.plan(10, 'Обновление только части полей смены'):
        cluster = await dataset.cluster()
        store_1 = await dataset.store(cluster=cluster, tz='UTC')
        store_2 = await dataset.store(cluster=cluster, tz='UTC')
        courier_1 = await dataset.courier(cluster=cluster, delivery_type='foot')
        courier_2 = await dataset.courier(cluster=cluster, delivery_type='car')

        _now = now(tz=timezone.utc).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=3)
        courier_shift = await dataset.courier_shift(
            cluster=cluster,
            store=store_1,
            status='waiting',
            delivery_type='foot',
            started_at=started_at,
            closes_at=closes_at,
            courier=courier_1,
            tags=[],
        )

        user = await dataset.user(store=store_1, role='admin')
        with user.role as role:
            # можно редактировать только 4 поля
            role.add_permit('save', {
                'courier_shift': [
                    'store_id',
                    'courier_id',
                    'delivery_type',
                    'closes_at',
                ]
            })
            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': courier_shift.courier_shift_id,

                    # изменится
                    'store_id': store_2.store_id,
                    'courier_id': courier_2.courier_id,
                    'delivery_type': 'car',
                    'closes_at': closes_at + timedelta(hours=1),

                    # игнорируется, т.к. нет прав
                    'started_at': started_at + timedelta(hours=1),
                    'tags': ['two', 'three'],
                    'status': 'cancelled',
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            with await courier_shift.reload() as shift:
                # изменилось
                tap.eq(shift.store_id, store_2.store_id, 'store_id')
                tap.eq(shift.courier_id, courier_2.courier_id, 'courier_id')
                tap.eq(shift.delivery_type, 'car', 'delivery_type')
                tap.eq(shift.closes_at,
                       closes_at + timedelta(hours=1),
                       'closes_at')

                # осталось без изменений
                tap.eq(shift.started_at, started_at, 'started_at')
                tap.eq(shift.tags, [], 'tags')
                tap.eq(shift.status, 'waiting', 'status')


@pytest.mark.parametrize(
    'cluster_params', [
        # отключен через конфиг
        {'courier_shift_setup': {'store_admin_create_shifts': False}},
        # отключен через настройки кластера
        {
            'disabled_role_permits': {
                'admin': ['courier_shifts_save']
            }
        }
    ]
)
async def test_store_shift_create_denied(tap, api, dataset, cluster_params):
    with tap.plan(3, 'Попытка создать смену, когда это запрещено'):
        cluster = await dataset.cluster(**cluster_params)
        store = await dataset.store(cluster=cluster, tz='UTC')
        user = await dataset.user(store=store)
        _now = now(tz=timezone.utc).replace(microsecond=0)

        with user.role as role:
            role.remove_permit('out_of_store')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'external_id': uuid(),
                    'delivery_type': 'rover',
                    'started_at': _now + timedelta(days=1),
                    'closes_at': _now + timedelta(days=1, hours=3),
                    'tags': [],
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_COURIER_SHIFT')


@pytest.mark.parametrize(
    'cluster_params', [
        # отключен через конфиг
        {'courier_shift_setup': {'store_shifts_save_enable': False}},
        # отключен через настройки кластера
        {
            'disabled_role_permits': {
                'admin': ['courier_shifts_save']
            }
        }
    ]
)
async def test_store_shift_save_denied(tap, api, dataset, cluster_params):
    with tap.plan(3, 'Попытка изменить смену, когда это запрещено'):
        cluster = await dataset.cluster(**cluster_params)
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, tz='UTC')
        _now = now(tz=timezone.utc).replace(microsecond=0)

        courier_shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=3),
            tags=[],
        )

        with user.role as role:
            role.remove_permit('out_of_store')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': courier_shift.courier_shift_id,
                    'delivery_type': 'rover',
                    'tags': [],
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_COURIER_SHIFT')


@pytest.mark.parametrize('limit', [
    0,  # создаем только сегодня;
    2,  # создаем сегодня, завтра и послезавтра
])
async def test_store_shift_create_limit(tap, api, dataset, limit):
    with tap.plan(12, f'Создание смены с лимитом ({limit}) по дате'):
        cluster = await dataset.cluster(courier_shift_setup={
            'store_admin_create_shifts': True,
            'store_shifts_create_day_limit': limit,
        })
        store = await dataset.store(cluster=cluster, tz='UTC')
        user = await dataset.user(store=store)
        _now = now(tz=timezone.utc).replace(microsecond=0)

        external_id = uuid()
        with user.role as role:
            role.remove_permit('out_of_store')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'external_id': external_id,
                    'delivery_type': 'rover',
                    'started_at': _now + timedelta(days=limit, hours=22),
                    'closes_at': _now + timedelta(days=limit + 1, hours=15),
                    'tags': [],
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('courier_shift.external_id', 'external_id')
            t.json_has('courier_shift.courier_shift_id', 'courier_shift_id')
            t.json_is('courier_shift.company_id', user.company_id, 'company_id')
            t.json_is('courier_shift.store_id', user.store_id, 'store_id')
            t.json_is('courier_shift.delivery_type', 'rover', 'delivery_type')
            t.json_is('courier_shift.status', 'request', 'статус')

            # далеко
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'external_id': uuid(),
                    'delivery_type': 'rover',
                    'started_at': _now + timedelta(days=limit + 1, hours=22),
                    'closes_at': _now + timedelta(days=limit + 2, hours=15),
                    'tags': [],
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_COURIER_SHIFT')


async def test_store_shift_create_nolimit(tap, api, dataset):
    with tap.plan(6, 'Создание смены на любую дату'):
        cluster = await dataset.cluster(courier_shift_setup={
            'store_admin_create_shifts': True,
            'store_shifts_create_day_limit': None,  # создание в любую дату
        })
        store = await dataset.store(cluster=cluster, tz='UTC')
        user = await dataset.user(store=store)
        _now = now(tz=timezone.utc).replace(microsecond=0)

        with user.role as role:
            role.remove_permit('out_of_store')

            # завтра
            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'external_id': uuid(),
                    'delivery_type': 'rover',
                    'started_at': _now + timedelta(days=1, hours=22),
                    'closes_at': _now + timedelta(days=2, hours=15),
                    'tags': [],
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            # через неделю
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'external_id': uuid(),
                    'delivery_type': 'foot',
                    'started_at': _now + timedelta(days=5, hours=22),
                    'closes_at': _now + timedelta(days=6, hours=15),
                    'tags': [],
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')


@pytest.mark.parametrize('limit', [
    0,  # редактируем только сегодня;
    2,  # редактируем сегодня, завтра и послезавтра
])
async def test_store_save_date_limit(tap, api, dataset, limit):
    with tap.plan(8, f'Редактирование смены с лимитом ({limit}) по дате'):
        cluster = await dataset.cluster(courier_shift_setup={
            'store_shifts_save_enable': True,
            'store_shifts_save_day_limit': limit,
        })
        store = await dataset.store(cluster=cluster, tz='UTC')
        user = await dataset.user(store=store)
        _now = now(tz=timezone.utc).replace(microsecond=0)

        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            started_at=_now + timedelta(days=limit, hours=22),
            closes_at=_now + timedelta(days=limit + 1, hours=15),
            delivery_type='foot',
            tags=[],
        )

        shift_2 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            started_at=_now + timedelta(days=limit + 1, hours=22),
            closes_at=_now + timedelta(days=limit + 2, hours=15),
            delivery_type='foot',
            tags=[],
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)

            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift_1.courier_shift_id,
                    'delivery_type': 'rover',
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift_2.courier_shift_id,
                    'delivery_type': 'rover',
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_COURIER_SHIFT')

        with await shift_1.reload() as shift:
            tap.eq(shift.delivery_type, 'rover', 'delivery_type')

        with await shift_2.reload() as shift:
            tap.eq(shift.delivery_type, 'foot', 'delivery_type')


async def test_store_save_no_date_limit(tap, api, dataset):
    with tap.plan(8, 'Редактирование смены на любую дату'):
        cluster = await dataset.cluster(courier_shift_setup={
            'store_shifts_save_enable': True,
            'store_shifts_save_day_limit': None,  # в любую дату
        })
        store = await dataset.store(cluster=cluster, tz='UTC')
        user = await dataset.user(store=store)
        _now = now(tz=timezone.utc).replace(microsecond=0)

        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            started_at=_now + timedelta(days=1, hours=22),
            closes_at=_now + timedelta(days=2, hours=15),
            delivery_type='foot',
            tags=[],
        )

        shift_2 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            started_at=_now + timedelta(days=5, hours=22),
            closes_at=_now + timedelta(days=6, hours=15),
            delivery_type='foot',
            tags=[],
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)

            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift_1.courier_shift_id,
                    'delivery_type': 'rover',
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift_2.courier_shift_id,
                    'delivery_type': 'rover',
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

        with await shift_1.reload() as shift:
            tap.eq(shift.delivery_type, 'rover', 'delivery_type')

        with await shift_2.reload() as shift:
            tap.eq(shift.delivery_type, 'rover', 'delivery_type')


async def test_store_create_percent_limit(tap, api, dataset):
    with tap.plan(14, 'Создание extra-смен не более Х% от плана'):
        day = now(tz=timezone.utc).replace(microsecond=0) + timedelta(hours=1)
        str_date = str(day.date())

        cluster = await dataset.cluster(courier_shift_setup={
            'store_shifts_save_enable': True,       # создание вкл.
            'store_admin_create_shifts': True,      # редактирование тоже вкл.
            'store_shifts_percent_limit': 5,        # 5% от плана в день
        })
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    str_date: {
                        'planned_sec': 100 * 3600,  # на этот день по плану
                        'extra_sec': 0,             # пока сверху создано 0ч.
                    }
                }
            },
            tz='UTC',
        )

        user = await dataset.user(store=store)
        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)

            # создаем 4ч-смену
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'external_id': uuid(),
                    'delivery_type': 'car',
                    'started_at': day,
                    'closes_at': day + timedelta(hours=4),      # 4 часа
                    'tags': [],
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            tap.eq(
                t.res['json']['courier_shift']['vars']['extra_sec'],
                4 * 3600,
                'extra_sec'
            )
            with await store.reload():
                tap.eq(
                    store.vars['courier_shift_counters'][str_date]['extra_sec'],
                    4 * 3600,
                    'добавилось 4ч., т.е. кпд 4%'
                )

            # пробуем создать >1ч-смену (неудача)
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'external_id': uuid(),
                    'delivery_type': 'car',
                    'started_at': day,
                    'closes_at': day + timedelta(hours=1, seconds=1),
                    'tags': [],
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_COURIER_SHIFT_DURATION_LIMIT')
            with await store.reload():
                tap.eq(
                    store.vars['courier_shift_counters'][str_date]['extra_sec'],
                    4 * 3600,
                    'все еще 4 часа'
                )

            # создаем 1ч-смену
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'external_id': uuid(),
                    'delivery_type': 'car',
                    'started_at': day,
                    'closes_at': day + timedelta(hours=1),      # 1 доп.час
                    'tags': [],
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            tap.eq(
                t.res['json']['courier_shift']['vars']['extra_sec'],
                1 * 3600,
                'extra_sec'
            )
            with await store.reload():
                tap.eq(
                    store.vars['courier_shift_counters'][str_date]['extra_sec'],
                    5 * 3600,
                    'добавилось, ровно 5 часов'
                )


async def test_store_save_extra_pct_limit(tap, api, dataset):
    with tap.plan(13, 'Редактирование extra-смены не более Х% от плана'):
        day = now(tz=timezone.utc).replace(microsecond=0) + timedelta(hours=1)
        str_date = str(day.date())

        cluster = await dataset.cluster(courier_shift_setup={
            'store_shifts_save_enable': True,       # создание вкл.
            'store_admin_create_shifts': True,      # редактирование тоже вкл.
            'store_shifts_percent_limit': 5,        # 5% от плана в день
        })
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    str_date: {
                        'planned_sec': 100 * 3600,  # на этот день по плану
                        'extra_sec': 4 * 3600,      # уже потрачено 4 часа
                    }
                }
            },
            tz='UTC',
        )

        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            started_at=day,
            closes_at=day + timedelta(hours=4),
            delivery_type='foot',
            placement='planned-extra',
            tags=[],
        )

        user = await dataset.user(store=store)
        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)

            # уменьшаем смену на 1 час
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift_1.courier_shift_id,
                    'closes_at': day + timedelta(hours=3),  # 3 часа вместо 4
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            with await shift_1.reload() as shift:
                tap.eq(shift.vars['extra_sec'], -1 * 3600, 'extra_sec')

            with await store.reload():
                tap.eq(
                    store.vars['courier_shift_counters'][str_date]['extra_sec'],
                    3 * 3600,
                    'минус 1ч., т.е. кпд 3%'
                )

            # пробуем увеличит на 2ч 1сек
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift_1.courier_shift_id,
                    'closes_at': day + timedelta(hours=5, seconds=1),
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_COURIER_SHIFT_DURATION_LIMIT')

            # увеличиваем ровно на 2ч
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift_1.courier_shift_id,
                    'closes_at': day + timedelta(hours=5),
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            with await shift_1.reload() as shift:
                tap.eq(shift.vars['extra_sec'], 1 * 3600, 'extra_sec')

            with await store.reload():
                tap.eq(
                    store.vars['courier_shift_counters'][str_date]['extra_sec'],
                    5 * 3600,
                    'максимум достигнут'
                )


async def test_store_save_extra_negative(tap, api, dataset):
    with tap.plan(9, 'Редактирование extra-смены не менее Х% от плана'):
        day = now(tz=timezone.utc).replace(microsecond=0) + timedelta(hours=1)
        str_date = str(day.date())

        cluster = await dataset.cluster(courier_shift_setup={
            'store_shifts_save_enable': True,       # создание вкл.
            'store_admin_create_shifts': True,      # редактирование тоже вкл.
            'store_shifts_percent_limit': 5,        # 5% от плана в день
        })
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    str_date: {
                        'planned_sec': 100 * 3600,  # на этот день по плану
                        'extra_sec': -4 * 3600,     # уже убрано 4 часа
                    }
                }
            },
            tz='UTC',
        )

        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            started_at=day,
            closes_at=day + timedelta(hours=4),
            delivery_type='foot',
            placement='planned-extra',
            tags=[],
        )

        user = await dataset.user(store=store)
        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)

            # уменьшаем смену на 2 часа
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift_1.courier_shift_id,
                    'closes_at': day + timedelta(hours=2),  # 2 часа вместо 4
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_COURIER_SHIFT_DURATION_LIMIT')

            # уменьшаем смену на 1 час
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift_1.courier_shift_id,
                    'closes_at': day + timedelta(hours=3),  # 3 часа вместо 4
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            with await shift_1.reload() as shift:
                tap.eq(shift.vars['extra_sec'], -3600, 'extra_sec')

            with await store.reload():
                _cache = store.vars['courier_shift_counters'][str_date]
                tap.eq(_cache['extra_sec'], -5 * 3600, 'кпд 5%')
                tap.eq(_cache['planned_sec'], 100 * 3600, 'план не изменен')


async def test_store_save_plan_pct_limit(tap, api, dataset):
    with tap.plan(15, 'Редактирование plan-смены не более Х% от плановых смен'):
        day = now(tz=timezone.utc).replace(microsecond=0) + timedelta(hours=1)
        str_date = str(day.date())

        cluster = await dataset.cluster(courier_shift_setup={
            'store_shifts_save_enable': True,       # создание вкл.
            'store_admin_create_shifts': True,      # редактирование тоже вкл.
            'store_shifts_percent_limit': 5,        # 5% от плана в день
        })
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    str_date: {
                        'planned_sec': 100 * 3600,  # на этот день по плану
                        'extra_sec': 4 * 3600,      # уже потрачено 4 часа
                    }
                }
            },
            tz='UTC',
        )

        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            started_at=day,
            closes_at=day + timedelta(hours=4),
            delivery_type='foot',
            placement='planned',
            tags=[],
        )

        user = await dataset.user(store=store)
        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)

            # уменьшаем смену на 1 час
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift_1.courier_shift_id,
                    'closes_at': day + timedelta(hours=3),  # 3 часа вместо 4
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            with await shift_1.reload() as shift:
                tap.eq(shift.vars['extra_sec'], -1 * 3600, 'extra_sec')

            with await store.reload():
                _cache = store.vars['courier_shift_counters'][str_date]
                tap.eq(_cache['extra_sec'], 3 * 3600, '-1ч, т.е. кпд 3/99')
                tap.eq(_cache['planned_sec'], 99 * 3600, 'тоже -1ч, т.е. 99ч')

            tap.note('Мы уменьшили кол-во плановых часов => лимит понизился')

            # пробуем увеличит на 2ч
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift_1.courier_shift_id,
                    'closes_at': day + timedelta(hours=5),
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_COURIER_SHIFT_DURATION_LIMIT')

            # увеличиваем на 1ч 57мин (столько осталось по КПД)
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift_1.courier_shift_id,
                    'closes_at': day + timedelta(hours=4, minutes=57),
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            tap.note('Мы увеличили кол-во плановых часов => лимит возрос')

            with await shift_1.reload() as shift:
                tap.eq(shift.vars['extra_sec'], 57 * 60, 'extra_sec 57мин')

            with await store.reload():
                _cache = store.vars['courier_shift_counters'][str_date]
                tap.eq(_cache['extra_sec'],
                       4 * 3600 + 57 * 60,
                       '4ч 57мин использовано')
                tap.eq(_cache['planned_sec'],       # КПД=4.9034175 %
                       100 * 3600 + 57 * 60,
                       'плановых часов 100ч 57мин')


async def test_store_cancel_plan_n_extra(tap, api, dataset):
    with tap.plan(14, 'Отменяем planned/extra смены директором'):
        day = now(tz=timezone.utc).replace(microsecond=0) + timedelta(hours=1)
        str_date = str(day.date())

        cluster = await dataset.cluster(courier_shift_setup={
            'store_shifts_save_enable': True,       # создание вкл.
            'store_shifts_percent_limit': 5,        # 5% от плана в день
        })
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    str_date: {
                        'planned_sec': 100 * 3600,  # на этот день по плану
                        'extra_sec': 4 * 3600,      # уже потрачено 4 часа
                    }
                }
            },
            tz='UTC',
        )
        shift_1 = await dataset.courier_shift(
            store=store,
            started_at=day,
            closes_at=day + timedelta(hours=4),
            placement='planned-extra',
        )
        shift_2 = await dataset.courier_shift(
            store=store,
            started_at=day,
            closes_at=day + timedelta(hours=4),
            placement='planned',
        )

        user = await dataset.user(store=store)
        with user.role as role:
            role.remove_permit('out_of_store')
            role.add_permit('courier_shifts_cancel', True)

            # отмена экстра смены
            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_save',
                            json={
                                'courier_shift_id': shift_1.courier_shift_id,
                                'status': 'cancelled',
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            with await shift_1.reload() as shift:
                tap.eq(shift.status, 'cancelled', 'смена отменена')
                tap.eq(shift.vars['extra_sec'], -4 * 3600, 'extra_sec')
            with await store.reload():
                _cache = store.vars['courier_shift_counters'][str_date]
                tap.eq(_cache['extra_sec'], 0, '-4ч, т.к. смена отменилась')
                tap.eq(_cache['planned_sec'], 100 * 3600, 'план не тронут')

            # отмена плановой смены
            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_save',
                            json={
                                'courier_shift_id': shift_2.courier_shift_id,
                                'status': 'cancelled',
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            with await shift_2.reload() as shift:
                tap.eq(shift.status, 'cancelled', 'смена отменена')
                tap.eq(shift.vars['extra_sec'], -4 * 3600, 'extra_sec')
            with await store.reload():
                _cache = store.vars['courier_shift_counters'][str_date]
                tap.eq(_cache['extra_sec'], -4 * 3600, 'еще -4ч')
                tap.eq(_cache['planned_sec'], 96 * 3600, 'план тоже -4ч')


@pytest.mark.parametrize(
    'placement,plan_delta', (
        ('planned', 5 * 60),    # изменение плановой влияет на план
        ('planned-extra', 0),   # изменение экстра смены - не влияет
    )
)
async def test_admin_save_plan_and_extra(
        tap, api, dataset, placement, plan_delta,
):
    with tap.plan(6, f'Правка {placement}-смены админом'):
        _now = now(timezone.utc) + timedelta(hours=1)
        str_date = str(_now.date())
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    str_date: {
                        'planned_sec': 2 * 3600,    # 2 часа
                        'extra_sec': 0,
                    }
                }
            },
            tz='UTC',
        )
        user = await dataset.user(store=store, role='admin')

        # 2 часовая плановая смена
        shift = await dataset.courier_shift(
            store=store,
            status='request',
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=3),
            placement=placement,
        )

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            'closes_at': shift.closes_at + timedelta(minutes=5),
                        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_hasnt('courier_shift.attr.extra_sec', 'extra_sec')

        with await store.reload():
            _cache = store.vars['courier_shift_counters'][str_date]
            tap.eq(_cache['planned_sec'],
                   2 * 3600 + plan_delta,
                   'изменение плана')
            tap.eq(_cache['extra_sec'], 0, '0 доп.')


@pytest.mark.parametrize(
    'planned_parent,plan_delta', (
        (True, 5 * 60),     # изменение плановой влияет на план
        (False, 0),         # изменение экстра смены - не влияет
    )
)
async def test_admin_save_replacement(
        tap, api, dataset, planned_parent, plan_delta,
):
    with tap.plan(6, 'Правка planned-смены админом'):
        _now = now(timezone.utc) + timedelta(hours=1)
        str_date = str(_now.date())
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    str_date: {
                        'planned_sec': 2 * 3600,    # 2 часа
                        'extra_sec': 0,
                    }
                }
            },
            tz='UTC',
        )
        user = await dataset.user(store=store, role='admin')

        # 2 часовая плановая смена
        shift = await dataset.courier_shift(
            store=store,
            status='request',
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=3),
            placement='replacement',
            attr={
                'planned_parent': planned_parent,
            }
        )

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            'closes_at': shift.closes_at + timedelta(minutes=5),
                        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_hasnt('courier_shift.attr.extra_sec', 'extra_sec')

        with await store.reload():
            _cache = store.vars['courier_shift_counters'][str_date]
            tap.eq(_cache['planned_sec'],
                   2 * 3600 + plan_delta,
                   'изменение плана')
            tap.eq(_cache['extra_sec'], 0, '0 доп.')


async def test_admin_cancel_plan_n_extra(tap, api, dataset):
    with tap.plan(14, 'Отменяем planned/extra смены админом'):
        day = now(tz=timezone.utc).replace(microsecond=0) + timedelta(hours=1)
        str_date = str(day.date())

        cluster = await dataset.cluster(courier_shift_setup={
            'store_shifts_save_enable': True,       # создание вкл.
            'store_shifts_percent_limit': 5,        # 5% от плана в день
        })
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    str_date: {
                        'planned_sec': 100 * 3600,  # на этот день по плану
                        'extra_sec': 4 * 3600,      # уже потрачено 4 часа
                    }
                }
            },
            tz='UTC',
        )
        shift_1 = await dataset.courier_shift(
            store=store,
            started_at=day,
            closes_at=day + timedelta(hours=4),
            placement='planned-extra',
        )
        shift_2 = await dataset.courier_shift(
            store=store,
            started_at=day,
            closes_at=day + timedelta(hours=4),
            placement='planned',
        )

        user = await dataset.user(store=store)
        with user.role as role:
            role.add_permit('courier_shifts_cancel', True)

            # отмена экстра смены
            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_save',
                            json={
                                'courier_shift_id': shift_1.courier_shift_id,
                                'status': 'cancelled',
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            with await shift_1.reload() as shift:
                tap.eq(shift.status, 'cancelled', 'смена отменена')
                tap.eq(shift.vars.get('extra_sec'), None, 'extra_sec не задан')
            with await store.reload():
                _cache = store.vars['courier_shift_counters'][str_date]
                tap.eq(_cache['extra_sec'], 4 * 3600, 'extra_sec без изменений')
                tap.eq(_cache['planned_sec'], 100 * 3600, 'план без изменений')

            # отмена плановой смены
            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_save',
                            json={
                                'courier_shift_id': shift_2.courier_shift_id,
                                'status': 'cancelled',
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            with await shift_2.reload() as shift:
                tap.eq(shift.status, 'cancelled', 'смена отменена')
                tap.eq(shift.vars.get('extra_sec'), None, 'extra_sec не задан')
            with await store.reload():
                _cache = store.vars['courier_shift_counters'][str_date]
                tap.eq(_cache['extra_sec'], 4 * 3600, 'extra_sec без изменений')
                tap.eq(_cache['planned_sec'], 96 * 3600, 'план тоже -4ч')


async def test_admin_plan_to_new_date(tap, api, dataset):
    with tap.plan(9, 'Перенос 4ч-план.-смены, растянутой на 1.5ч, на др.дату'):
        day = now(tz=timezone.utc).replace(microsecond=0) + timedelta(hours=1)
        next_day = day + timedelta(days=1)
        str_date1 = str(day.date())
        str_date2 = str(next_day.date())

        cluster = await dataset.cluster(courier_shift_setup={
            'store_shifts_save_enable': True,       # создание вкл.
            'store_admin_create_shifts': True,      # редактирование тоже вкл.
            'store_shifts_percent_limit': None,     # percent лимит не задан
        })
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    str_date1: {
                        'planned_sec': 4.5 * 3600,  # на этот день по плану
                        'extra_sec': 1800,          # уже потрачено
                    },
                    str_date2: {
                        'planned_sec': 4.5 * 3600,  # на этот день по плану
                        'extra_sec': 1800,          # уже потрачено
                    },
                }
            },
            tz='UTC',
        )

        shift_1 = await dataset.courier_shift(
            store=store,
            started_at=day,
            closes_at=day + timedelta(hours=4.5),
            placement='planned',
            vars={
                'extra_sec': 1800,
            }
        )

        user = await dataset.user(store=store)
        t = await api(user=user)

        # Перенос + увеличиваем на 1.5 часа
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift_1.courier_shift_id,
                'started_at': next_day,
                'closes_at': next_day + timedelta(hours=6),  # +1.5ч
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await shift_1.reload() as shift:
            tap.eq(shift.vars['extra_sec'], 1800, 'extra_sec без изменений')
            tap.eq(shift.duration, 6 * 3600, 'длительность увеличена на 1.5ч')

        with await store.reload():
            # старая дата
            _cache = store.vars['courier_shift_counters'][str_date1]
            tap.eq(_cache['extra_sec'], 0, 'extra_sec обнулился')
            tap.eq(_cache['planned_sec'], 0, 'planned_sec обнулился')

            # новая дата
            _cache = store.vars['courier_shift_counters'][str_date2]
            tap.eq(_cache['extra_sec'],
                   1800 + 1800,
                   'было 30мин, и прибавилось еще 30мин')
            tap.eq(_cache['planned_sec'],
                   4.5 * 3600 + 6 * 3600,
                   'planned_sec равен сумме длительности смен')


async def test_admin_extra_to_new_date(tap, api, dataset):
    with tap.plan(9, 'Перенос 4ч-extra-смены, растянутой на 1.5ч, на др.дату'):
        day = now(tz=timezone.utc).replace(microsecond=0) + timedelta(hours=1)
        next_day = day + timedelta(days=1)
        str_date1 = str(day.date())
        str_date2 = str(next_day.date())

        cluster = await dataset.cluster(courier_shift_setup={
            'store_shifts_save_enable': True,       # создание вкл.
            'store_admin_create_shifts': True,      # редактирование тоже вкл.
            'store_shifts_percent_limit': None,     # percent лимит не задан
        })
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    str_date1: {
                        'planned_sec': 8 * 3600,    # на этот день по плану
                        'extra_sec': 4.5 * 3600,    # уже потрачено
                    },
                    str_date2: {
                        'planned_sec': 4.5 * 3600,  # на этот день по плану
                        'extra_sec': 1800,          # уже потрачено
                    },
                }
            },
            tz='UTC',
        )

        shift_1 = await dataset.courier_shift(
            store=store,
            started_at=day,
            closes_at=day + timedelta(hours=4.5),
            placement='planned-extra',
            vars={
                'extra_sec': 4.5 * 3600,
            }
        )

        user = await dataset.user(store=store)
        t = await api(user=user)

        # Перенос + увеличиваем на 1.5 часа
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift_1.courier_shift_id,
                'started_at': next_day,
                'closes_at': next_day + timedelta(hours=6),  # +1.5ч
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await shift_1.reload() as shift:
            tap.eq(shift.vars['extra_sec'], 4.5 * 3600, 'extra_sec тот же')
            tap.eq(shift.duration, 6 * 3600, 'длительность увеличена на 1.5ч')

        with await store.reload():
            # старая дата
            _cache = store.vars['courier_shift_counters'][str_date1]
            tap.eq(_cache['extra_sec'], 0, 'extra_sec обнулился')
            tap.eq(_cache['planned_sec'], 8 * 3600, 'planned_sec тот же')

            # новая дата
            _cache = store.vars['courier_shift_counters'][str_date2]
            tap.eq(_cache['extra_sec'],
                   1800 + 4.5 * 3600,
                   'было 30мин, прибавилось еще 4.5ч')
            tap.eq(_cache['planned_sec'],
                   4.5 * 3600,
                   'planned_sec не меняется')


async def test_save_with_shifting(tap, api, dataset):
    with tap.plan(7, 'Смена сдвигается на 1 час, но не меняется'):
        day = now(tz=timezone.utc).replace(hour=0) + timedelta(days=1)
        str_date = str(day.date())

        cluster = await dataset.cluster(courier_shift_setup={
            'store_shifts_save_enable': True,       # создание вкл.
            'store_admin_create_shifts': True,      # редактирование тоже вкл.
            'store_shifts_percent_limit': 5,        # percent лимит 5%
        })
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    str_date: {
                        'planned_sec': 100,         # на этот день по плану
                        'extra_sec': 5 * 3600,      # все потрачено
                    },
                }
            },
            tz='UTC',
        )

        shift_1 = await dataset.courier_shift(
            store=store,
            started_at=day,
            closes_at=day + timedelta(hours=5),
            placement='planned',
            vars={
                'extra_sec': 1.5 * 3600,
            }
        )

        user = await dataset.user(store=store)
        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)

            # Сдвиг на 1 час
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift_1.courier_shift_id,
                    'started_at': shift_1.started_at + timedelta(hours=1),
                    'closes_at': shift_1.closes_at + timedelta(hours=1),
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            with await shift_1.reload() as shift:
                tap.eq(shift.duration, 5 * 3600, 'длительность без изменений')
                tap.eq(shift.vars['extra_sec'], 1.5 * 3600, 'без изменений')

            with await store.reload():
                _cache = store.vars['courier_shift_counters'][str_date]
                tap.eq(_cache['extra_sec'], 5 * 3600, 'extra_sec тот же')
                tap.eq(_cache['planned_sec'], 100, 'planned_sec не тронут')


async def test_store_save_to_new_date(tap, api, dataset):
    with tap.plan(9, 'Директор не может переносить смену на новую дату'):
        day = now(tz=timezone.utc).replace(microsecond=0) + timedelta(hours=1)
        next_day = day + timedelta(days=1)
        str_date1 = str(day.date())
        str_date2 = str(next_day.date())

        cluster = await dataset.cluster(courier_shift_setup={
            'store_shifts_save_enable': True,       # создание вкл.
            'store_admin_create_shifts': True,      # редактирование тоже вкл.
            'store_shifts_percent_limit': None,     # percent лимит не задан
        })
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    str_date1: {
                        'planned_sec': 100,         # на этот день по плану
                        'extra_sec': 3600,          # уже потрачено
                    },
                    str_date2: {
                        'planned_sec': 200,         # на этот день по плану
                        'extra_sec': 7200,          # уже потрачено
                    },
                }
            },
            tz='UTC',
        )

        shift_1 = await dataset.courier_shift(
            store=store,
            started_at=day,
            closes_at=day + timedelta(hours=2.5),
            placement='planned',
            vars={
                'extra_sec': 1.5 * 3600,
            }
        )

        user = await dataset.user(store=store)
        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)

            # Перенос + уменьшаем на 0.5 часа
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift_1.courier_shift_id,
                    'started_at': next_day,
                    'closes_at': next_day + timedelta(hours=1),  # -0.5ч
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_COURIER_SHIFT')

            with await shift_1.reload() as shift:
                tap.eq(shift.duration, 2.5 * 3600, 'длительность без изменений')
                tap.eq(shift.vars['extra_sec'], 1.5 * 3600, 'без изменений')

            with await store.reload():
                # старая дата
                _cache = store.vars['courier_shift_counters'][str_date1]
                tap.eq(_cache['extra_sec'], 3600, 'extra_sec тот же')
                tap.eq(_cache['planned_sec'], 100, 'planned_sec не тронут')

                # новая дата
                _cache = store.vars['courier_shift_counters'][str_date2]
                tap.eq(_cache['extra_sec'], 7200, 'extra_sec тот же')
                tap.eq(_cache['planned_sec'], 200, 'planned_sec не тронут')


async def test_admin_save_to_alien_store(tap, api, dataset):
    with tap.plan(9, 'Перенос 4ч-план.-смены, растянутой на 1.5ч, в др. лавку'):
        day = now(tz=timezone.utc).replace(microsecond=0) + timedelta(hours=1)
        str_date = str(day.date())

        cluster = await dataset.cluster(courier_shift_setup={
            'store_shifts_save_enable': True,       # создание вкл.
            'store_admin_create_shifts': True,      # редактирование тоже вкл.
            'store_shifts_percent_limit': None,     # percent лимит не задан
        })
        store_1 = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    str_date: {
                        'planned_sec': 4.5 * 3600,  # на этот день по плану
                        'extra_sec': 1800,          # уже потрачено
                    },
                },
            },
            tz='UTC',
        )
        store_2 = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    str_date: {
                        'planned_sec': 4.5 * 3600,  # на этот день по плану
                        'extra_sec': 1800,          # уже потрачено
                    },
                },
            },
            tz='UTC',
        )

        shift = await dataset.courier_shift(
            store=store_1,
            started_at=day,
            closes_at=day + timedelta(hours=4.5),
            placement='planned',
            vars={
                'extra_sec': 1800,  # указание, что смену увеличили на 30мин
            }
        )

        user = await dataset.user(store=store_1)
        t = await api(user=user)

        # Перенос в другую лавку
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'store_id': store_2.store_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await shift.reload() as shift:
            tap.eq(shift.store_id, store_2.store_id, 'store_id изменился')
            tap.eq(shift.vars['extra_sec'], 1800, 'extra_sec сохранен')

        with await store_1.reload() as store:
            _cache = store.vars['courier_shift_counters'][str_date]
            tap.eq(_cache['extra_sec'], 0, 'extra_sec обнулился')
            tap.eq(_cache['planned_sec'], 0, 'planned_sec обнулился')

        with await store_2.reload() as store:
            _cache = store.vars['courier_shift_counters'][str_date]
            tap.eq(_cache['extra_sec'], 1800 + 1800, 'extra_sec +1800')
            tap.eq(_cache['planned_sec'], 9 * 3600, 'planned_sec +4.5ч')


async def test_reissue_hell(tap, dataset, api):
    # pylint: disable=too-many-locals,import-outside-toplevel
    # pylint: disable=too-many-statements
    with tap.plan(21, 'Адские переиздания: отказ, правки, невыход, правки'):
        from scripts.cron.close_courier_shifts import close_courier_shifts
        from scripts.cron.sync_courier_shift_counters import (
            sync_courier_shift_counters,
        )

        _now = now(timezone.utc) + timedelta(hours=1)
        date = str(_now.date())

        cluster = await dataset.cluster(
            courier_shift_setup={
                'timeout_request': 3600,  # мин.размер 1ч
                'reissue_enable': True,
            },
        )
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    date: {
                        'planned_sec': 5 * 3600,
                        'extra_sec': 3600,
                    },
                },
            },
            tz='UTC',
        )
        courier = await dataset.courier(cluster=cluster)
        user = await dataset.user(store=store)

        # курьер уже отказался от модифицированной Директором плановой смены
        parent_0 = await dataset.courier_shift(
            status='released',
            placement='planned',
            started_at=_now,
            closes_at=_now + timedelta(hours=5),
            store=store,
            vars={
                'extra_sec': 3600,
            }
        )

        # переиздание отказа (ребенок не изменится и сохранит placement)
        await close_courier_shifts(cluster_id=cluster.cluster_id,
                                   now_=_now - timedelta(minutes=1))
        await parent_0.reload()
        event = parent_0.event_reissued()
        tap.ok(event, 'событие переиздания есть')
        child_1 = await CourierShift.load(event.detail['courier_shift_id'])
        tap.eq(child_1.status, 'request', 'свежая смена, 1го переиздания')

        # правки Админом (+1ч и новый курьер)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': child_1.courier_shift_id,
                'closes_at': child_1.closes_at + timedelta(hours=1),
                'courier_id': courier.courier_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        with await child_1.reload():
            tap.eq(child_1.vars['extra_sec'], 3600, 'доп.времени не появилось')
        with await store.reload():
            _cache = store.vars['courier_shift_counters'][date]
            tap.eq(_cache['extra_sec'], 3600, 'extra_sec без изменений')
            tap.eq(_cache['planned_sec'], 6 * 3600, 'planned_sec + 1 час')

        # переиздание пропуска (ребенок -1ч и станет replacement)
        await close_courier_shifts(cluster_id=cluster.cluster_id,
                                   now_=_now + timedelta(minutes=59))
        await child_1.reload()
        event = child_1.event_reissued()
        tap.ok(event, 'событие переиздания #2 есть')
        child_2 = await CourierShift.load(event.detail['courier_shift_id'])
        tap.eq(child_2.status, 'request', 'свежая смена, 2го переиздания')
        tap.eq(child_2.duration, 5 * 3600, 'снова стала на час короче')

        # пересчитываем счетчики
        await sync_courier_shift_counters(store_id=store.store_id)
        with await store.reload():
            _cache = store.vars['courier_shift_counters'][date]
            tap.eq(_cache['extra_sec'], 3600, 'extra_sec без изменений')
            tap.eq(_cache['planned_sec'], 6 * 3600, 'planned_sec + 1 час')

        # правки Директором (30мин)
        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': child_2.courier_shift_id,
                    'closes_at': child_2.closes_at - timedelta(hours=0.5),
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
        with await child_2.reload():
            tap.eq(child_2.vars['extra_sec'], 1800, 'доп.временя -30 мин')
        with await store.reload():
            _cache = store.vars['courier_shift_counters'][date]
            tap.eq(_cache['extra_sec'], 1800, 'extra_sec -30 мин')
            tap.eq(_cache['planned_sec'], 5.5 * 3600, 'planned_sec -30 мин')

        # пересчитываем счетчики
        await sync_courier_shift_counters(store_id=store.store_id)
        with await store.reload():
            _cache = store.vars['courier_shift_counters'][date]
            tap.eq(_cache['extra_sec'], 1800, 'extra_sec не сброшен')
            tap.eq(_cache['planned_sec'], 5.5 * 3600, 'planned_sec не сброшен')
