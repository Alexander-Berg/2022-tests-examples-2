# pylint: disable=too-many-locals,invalid-name,too-many-lines

from datetime import datetime, timezone, timedelta, time

import pytest
import pytz

from libstall.util import now, uuid
from stall.model.courier_shift import CourierShiftEvent


async def test_save_create(tap, api, dataset):
    with tap.plan(18, 'Создание курьерской смены'):
        company = await dataset.company()
        store = await dataset.store(company=company, status='active')
        user = await dataset.user(store=store, role='admin')

        external_id = uuid()
        _now = now(tz=timezone.utc).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=3)
        tags = ['one', 'two', 'three']
        attr = {'public': True}

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'external_id': external_id,
                            'delivery_type': 'rover',
                            # 'status': 'processing',         # игнорируется
                            'started_at': started_at,
                            'closes_at': closes_at,
                            'tags': tags,
                            'source': 'batch',              # игнорируется
                            'attr': attr,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('courier_shift.courier_shift_id', 'courier_shift_id')

        t.json_is('courier_shift.external_id', external_id, 'external_id')
        t.json_is('courier_shift.company_id', user.company_id, 'company_id')
        t.json_is('courier_shift.store_id', user.store_id, 'store_id')
        t.json_is('courier_shift.delivery_type', 'rover', 'delivery_type')
        t.json_is('courier_shift.status', 'request', 'status (старт.значение)')
        t.json_is(
            'courier_shift.placement',
            'planned-extra',
            'Вручную созданная смена всегда planned-extra'
        )
        t.json_is('courier_shift.attr.public', True, 'public attr')

        json_courier_shift = t.res['json']['courier_shift']
        t_started_at = datetime.fromisoformat(json_courier_shift['started_at'])
        t_closes_at = datetime.fromisoformat(json_courier_shift['closes_at'])
        tap.eq(t_started_at, started_at, 'started_at')
        tap.eq(t_closes_at, closes_at, 'closes_at')

        t.json_is('courier_shift.tags', tags, 'tags')
        t.json_is('courier_shift.source', 'manual', 'для админ. ручки manual')
        t.json_is('courier_shift.user_id', user.user_id, 'user_id')
        t.json_hasnt('courier_shift.attr.extra_sec', 'extra_sec')

        with await store.reload() as s:
            tap.eq(s.vars.get('courier_shift_counters'), None, 'счетчика нет')


async def test_save_create_alien_store(tap, api, dataset):
    with tap.plan(16, 'Создание смены в чужой лавке/компании'):
        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store1, role='admin')

        external_id = uuid()
        _now = now(tz=timezone.utc).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=3)
        tags = ['one', 'two', 'three']

        t = await api(user=user)
        with user.role as role:
            json = {
                'external_id': external_id,
                'store_id': store2.store_id,
                'delivery_type': 'rover',
                'started_at': started_at,
                'closes_at': closes_at,
                'tags': tags,
            }

            role.remove_permit('out_of_company')
            role.remove_permit('out_of_store')
            await t.post_ok('api_admin_courier_shifts_save', json=json)
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

            role.add_permit('out_of_store', True)
            await t.post_ok('api_admin_courier_shifts_save', json=json)
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

            role.add_permit('out_of_company', True)
            await t.post_ok('api_admin_courier_shifts_save', json=json)
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            t.json_has('courier_shift.courier_shift_id', 'courier_shift_id')

            t.json_is('courier_shift.external_id', external_id, 'external_id')
            t.json_is('courier_shift.company_id',
                      store2.company_id,
                      'company_id')
            t.json_is('courier_shift.store_id', store2.store_id, 'store_id')
            t.json_is('courier_shift.user_id', user.user_id, 'user_id')

        with await store1.reload() as s:
            tap.eq(s.vars.get('courier_shift_counters'), None, 'счетчика нет')

        with await store2.reload() as s:
            tap.eq(s.vars.get('courier_shift_counters'), None, 'счетчика нет')


async def test_create_inactive_store(tap, api, dataset):
    with tap.plan(3, 'Создание смены в неактивной лавке'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster, status='repair')

        t = await api(role='admin')
        await t.post_ok('api_admin_courier_shifts_save', json={
            'external_id': uuid(),
            'store_id': store.store_id,
            'delivery_type': 'rover',
            'started_at': now() + timedelta(hours=1),
            'closes_at': now() + timedelta(hours=1),
        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_STORE_IS_INACTIVE')


async def test_save_create_with_courier(tap, api, dataset):
    with tap.plan(8, 'Создание курьерской смены сразу с курьером'):
        _now = now(tz=timezone.utc).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=3)
        tags = ['one', 'two', 'three']

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster, tags=tags + ['x', 'y'])
        user = await dataset.user(store=store, role='admin')

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'external_id': uuid(),
                            'delivery_type': 'foot',
                            'courier_id': courier.courier_id,
                            'started_at': started_at,
                            'closes_at': closes_at,
                            'tags': tags,
                            'guarantee': '123.00',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('courier_shift.courier_shift_id')
        t.json_is('courier_shift.courier_id', courier.courier_id)
        t.json_is('courier_shift.status', 'waiting')
        t.json_is('courier_shift.shift_events.0.type', 'waiting')
        t.json_hasnt(
            'courier_shift.shift_events.1',
            'Событий changes нет для новой смены'
        )


@pytest.mark.parametrize(
    'fixed_param', (
        {'tags': ['three', 'four']},
        {'delivery_type': 'car'},
    )
)
async def test_save_create_courier_err(tap, api, dataset, fixed_param):
    _now = now(tz=timezone.utc).replace(microsecond=0)
    started_at = _now + timedelta(hours=1)
    closes_at = _now + timedelta(hours=3)
    tags = ['one', 'two']
    delivery_type = 'foot'

    with tap.plan(3, 'Создание курьерской смены с неподходящим курьером'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(
            cluster=cluster,
            delivery_type=delivery_type,
            tags=tags
        )

        shift_params = {
            'courier_id': courier.courier_id,
            'tags': tags,
            'delivery_type': delivery_type,
        }
        shift_params.update(fixed_param)

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'external_id': uuid(),
                            'started_at': started_at,
                            'closes_at': closes_at,
                            **shift_params
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')


async def test_courier_blocked(tap, api, dataset):
    with tap.plan(3, 'Курьер заблокирован'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(
            cluster=cluster,
            blocks=[
                {'source': 'wms', 'reason': 'ill'},
            ],
        )

        _now = now(tz=timezone.utc).replace(microsecond=0)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'external_id': uuid(),
                'started_at': _now + timedelta(hours=1),
                'closes_at': _now + timedelta(hours=3),
                'courier_id': courier.courier_id,
                'delivery_type': courier.delivery_type,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_COURIER_BLOCKED')


async def test_save_create_cluster_err(tap, api, dataset):
    _now = now(tz=timezone.utc).replace(microsecond=0)
    started_at = _now + timedelta(hours=1)
    closes_at = _now + timedelta(hours=3)
    tags = ['one', 'two']
    delivery_type = 'foot'

    with tap.plan(9, 'Создание смены с курьером и лавкой из разных кластеров'):
        cluster1 = await dataset.cluster()
        cluster2 = await dataset.cluster()
        store = await dataset.store(cluster=cluster1)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(
            cluster=cluster2,
            delivery_type=delivery_type,
            tags=tags
        )

        t = await api(user=user)

        # разные кластера
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'external_id': uuid(),
                            'started_at': started_at,
                            'closes_at': closes_at,
                            'courier_id': courier.courier_id,
                            'tags': tags,
                            'delivery_type': delivery_type,
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')

        # одинаковые
        courier = await dataset.courier(
            cluster=cluster1,
            delivery_type=delivery_type,
            tags=tags
        )
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'external_id': uuid(),
                            'started_at': started_at,
                            'closes_at': closes_at,
                            'courier_id': courier.courier_id,
                            'tags': tags,
                            'delivery_type': delivery_type,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('courier_shift.store_id', user.store_id, 'store_id')
        t.json_is('courier_shift.courier_id', courier.courier_id, 'courier_id')
        t.json_is('courier_shift.cluster_id', cluster1.cluster_id, 'cluster_id')


async def test_save_update(tap, api, dataset):
    with tap.plan(11, 'Обновление курьерской смены'):
        company = await dataset.company()
        cluster = await dataset.cluster()
        store = await dataset.store(company=company, cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        _now = now(tz=timezone.utc).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=3)
        tags = ['one', 'two', 'three']

        # создаем смену
        shift = await dataset.courier_shift(
            store=store,
            status='request',
            started_at=started_at,
            closes_at=closes_at,
            tags=tags,
            delivery_type='rover',
        )
        tap.is_ok(shift.attr.get('public', False), False,
                  'public option default')

        # редактируем
        store2 = await dataset.store(company=company, cluster=cluster)
        started_at += timedelta(minutes=3)
        closes_at += timedelta(minutes=3)
        tags = ['one', 'two', 'NEW TAG']
        attr = {'public': True}

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            'store_id': store2.store_id,
                            'delivery_type': 'car',
                            'status': 'closed',
                            'started_at': started_at,
                            'closes_at': closes_at,
                            'tags': tags,
                            'source': 'batch',              # игнорируется
                            'attr': attr,
                        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('courier_shift.delivery_type', 'car', 'delivery_type')
        t.json_is('courier_shift.status', 'closed', 'status')
        t.json_is('courier_shift.attr.public', True, 'public attr')

        json_courier_shift = t.res['json']['courier_shift']
        t_started_at = datetime.fromisoformat(json_courier_shift['started_at'])
        t_closes_at = datetime.fromisoformat(json_courier_shift['closes_at'])
        tap.eq(t_started_at, started_at, 'started_at')
        tap.eq(t_closes_at, closes_at, 'closes_at')

        t.json_is('courier_shift.tags', tags, 'tags')
        t.json_is('courier_shift.source', 'manual', 'source (не изменилось)')


async def test_save_create_update(tap, api, dataset, time2iso_utc, time2time):
    with tap.plan(16, 'Создание и обновление курьерской смены'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster, status='active')
        user = await dataset.user(store=store, role='admin')

        _now = now(tz=timezone.utc).replace(microsecond=0)
        started_at = _now + timedelta(hours=3)
        closes_at = _now + timedelta(hours=6)
        showtime = _now + timedelta(hours=1)

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save', json={
            'external_id': uuid(),
            'delivery_type': 'rover',
            'started_at': started_at,
            'closes_at': closes_at,
            'tags': ['one', 'two', 'three'],
            'attr': {'public': True},
            'schedule': [
                {"tags": ['best'], "time": time2iso_utc(showtime)},
            ],
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('courier_shift.courier_shift_id', 'courier_shift_id')
        shift = t.res['json']['courier_shift']

        tap.eq(len(shift['schedule']), 1, 'Публикации сохранены')
        schedule = shift['schedule'][0]
        tap.eq(schedule['tags'], ['best'], 'теги сохранены')
        tap.eq(time2time(schedule['time']), showtime, 'время показа')

        # редактируем
        store2 = await dataset.store(cluster=cluster, status='active')
        started_at += timedelta(hours=1)
        closes_at += timedelta(hours=1)
        showtime2 = showtime + timedelta(hours=1)

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save', json={
            'courier_shift_id': shift['courier_shift_id'],
            'store_id': store2.store_id,
            'started_at': started_at,
            'closes_at': closes_at,
            'schedule': [
                {"tags": ['best'], "time": time2iso_utc(showtime)},
                {"tags": ['bad'], "time": time2iso_utc(showtime2)},
            ],
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        shift = t.res['json']['courier_shift']
        tap.eq(shift['store_id'], store2.store_id, 'store_id')
        tap.eq(time2time(shift['started_at']), started_at, 'started_at')
        tap.eq(time2time(shift['closes_at']), closes_at, 'closes_at')

        tap.eq(len(shift['schedule']), 2, 'Публикации сохранены')
        schedule = shift['schedule'][1]
        tap.eq(schedule['tags'], ['bad'], 'теги сохранены')
        tap.eq(time2time(schedule['time']), showtime2, 'время показа')


async def test_save_update_alien_store(tap, api, dataset):
    with tap.plan(12, 'Редактирование смены с чужой лавкой/компанией'):
        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store1, role='admin')

        _now = now(tz=timezone.utc).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=3)

        # создаем смену
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            store=store1,
            courier=courier,
            status='waiting',
            started_at=started_at,
            closes_at=closes_at,
            delivery_type='foot',
        )

        # редактируем
        started_at += timedelta(minutes=3)
        closes_at += timedelta(minutes=3)

        t = await api(user=user)
        with user.role as role:
            json = {
                'courier_shift_id': shift.courier_shift_id,
                'store_id': store2.store_id,
                'status': 'cancelled',
                'started_at': started_at,
                'closes_at': closes_at,
            }

            role.remove_permit('out_of_company')
            role.remove_permit('out_of_store')
            await t.post_ok('api_admin_courier_shifts_save', json=json)
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

            role.add_permit('out_of_store', True)
            await t.post_ok('api_admin_courier_shifts_save', json=json)
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

            role.add_permit('out_of_company', True)
            await t.post_ok('api_admin_courier_shifts_save', json=json)
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('courier_shift.status', 'cancelled', 'status')

            json_courier_shift = t.res['json']['courier_shift']
            t_started = datetime.fromisoformat(json_courier_shift['started_at'])
            t_closes = datetime.fromisoformat(json_courier_shift['closes_at'])
            tap.eq(t_started, started_at, 'started_at')
            tap.eq(t_closes, closes_at, 'closes_at')


async def test_save_inactive_store(tap, api, dataset):
    with tap.plan(6, 'Обновление смены в неактивной лавке'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster, status='disabled')
        shift = await dataset.courier_shift(store=store, status='request')

        t = await api(role='admin')
        await t.post_ok('api_admin_courier_shifts_save', json={
            'courier_shift_id': shift.courier_shift_id,
            'delivery_type': 'rover',
            'status': 'closed',
            'tags': ['superman', 'batman'],
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('courier_shift.delivery_type', 'rover', 'delivery_type')
        t.json_is('courier_shift.status', 'closed', 'status')
        t.json_is('courier_shift.tags', ['superman', 'batman'], 'tags')


async def test_save_alien_cluster(tap, api, dataset):
    with tap.plan(4, 'Редактирование смены с чужим кластером'):
        store1 = await dataset.store()
        store2 = await dataset.store()
        user = await dataset.user(store=store1, role='admin')

        # создаем смену
        shift = await dataset.courier_shift(store=store1, status='request')

        # редактируем
        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            'status': 'request',
                            'store_id': store2.store_id,
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('details.message',
                  'Stores from other clusters are prohibited')


async def test_waiting_event_change(tap, api, dataset, time2iso, time2iso_utc):
    with tap.plan(16, 'При изменении waiting-смены добавляется событие'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)

        _now = now(tz=timezone.utc).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=started_at,
            closes_at=closes_at,
            guarantee=100,
        )

        new_started_at = started_at + timedelta(hours=3)
        new_closes_at = new_started_at + timedelta(hours=2)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'started_at': new_started_at,
                'closes_at': new_closes_at,
                'guarantee': '123.00',
            })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('courier_shift.started_at', time2iso_utc(started_at))
        t.json_is('courier_shift.closes_at', time2iso_utc(closes_at))
        t.json_is('courier_shift.guarantee', '100.00')

        t.json_is('courier_shift.shift_events.0.type', 'edit')
        t.json_is('courier_shift.shift_events.0.user_id', user.user_id)
        t.json_is('courier_shift.shift_events.1.type', 'change')
        t.json_is('courier_shift.shift_events.1.user_id', user.user_id)

        t.json_is(
            'courier_shift.shift_events.1.detail.old.started_at',
            time2iso(started_at)
        )
        t.json_is(
            'courier_shift.shift_events.1.detail.old.closes_at',
            time2iso(closes_at)
        )
        t.json_is(
            'courier_shift.shift_events.1.detail.old.guarantee',
            '100.00',
        )
        t.json_is(
            'courier_shift.shift_events.1.detail.new.started_at',
            time2iso(new_started_at)
        )
        t.json_is(
            'courier_shift.shift_events.1.detail.new.closes_at',
            time2iso(new_closes_at)
        )
        t.json_is(
            'courier_shift.shift_events.1.detail.new.guarantee',
            '123.00',
        )


async def test_waiting_event_reject(tap, api, dataset):
    with tap.plan(25, 'При снятии курьера отклоняются предложенные изменения'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier_1 = await dataset.courier(cluster=cluster)
        courier_2 = await dataset.courier(cluster=cluster)

        _now = now(tz=timezone.utc).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        change_id = uuid()
        shift = await dataset.courier_shift(
            store=store,
            courier=courier_1,
            status='waiting',
            started_at=started_at,
            closes_at=closes_at,
            guarantee=100,
            shift_events=[
                CourierShiftEvent({'type': 'change', 'guarantee': '123.00'}),
                CourierShiftEvent({
                    'shift_event_id': change_id,
                    'type': 'change',
                    'guarantee': '456.00',
                }),
            ],
        )

        t = await api(user=user)

        # меняем курьера
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'courier_id': courier_2.courier_id,
            })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await shift.reload():
            tap.eq(shift.courier_id, courier_2.courier_id, 'курьер сменился')
            tap.eq(shift.guarantee, 100.00, 'guarantee на месте')
            tap.eq(len(shift.shift_events), 3, '2 события change + 1 edit')
            tap.eq(shift.event_change().shift_event_id,
                   change_id,
                   'последнее предложение доступно')

        # снимаем курьера
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'courier_id': None,
            })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await shift.reload():
            tap.eq(shift.status, 'request', 'смена предложена')
            tap.eq(shift.courier_id, None, 'курьер снят')
            tap.eq(shift.guarantee, 100.00, 'guarantee на месте')
            tap.eq(len(shift.shift_events), 6, '+4 события')
            tap.eq(shift.event_change(), None, 'предложений нет')

            with shift.shift_events[-4] as event:
                tap.eq(event.type, 'edit', 'Событие редактирования смены')
                tap.eq(
                    event.detail['old'],
                    {'courier_id': courier_1.courier_id},
                    'Старый курьер'
                )
                tap.eq(
                    event.detail['new'],
                    {'courier_id': courier_2.courier_id},
                    'Новый курьер'
                )

            with shift.shift_events[-3] as event:
                tap.eq(event.type, 'request', 'сменился статус')

            with shift.shift_events[-2] as event:
                tap.eq(event.type, 'rejected', 'rejected')
                tap.eq(event.shift_event_id,
                       f'{change_id}:rejected',
                       'id корректный')
                tap.eq(event.user_id, user.user_id, 'user_id')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'edit', 'Событие редактирования смены')
                tap.eq(
                    event.detail['old'],
                    {'courier_id': courier_2.courier_id, 'status': 'waiting'},
                    'Новый курьер'
                )
                tap.eq(
                    event.detail['new'],
                    {'courier_id': None, 'status': 'request'},
                    'Сняли курьера'
                )


async def test_processing_event_change(
        tap, api, dataset, time2iso, time2iso_utc
):
    with tap.plan(19, 'При изменении processing-смены добавляется событие'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)

        _now = now(tz=timezone.utc).replace(microsecond=0)
        started_at = _now - timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=started_at,
            closes_at=closes_at,
            guarantee=100,
        )

        new_started_at = started_at + timedelta(hours=3)
        new_closes_at = closes_at + timedelta(hours=2)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'started_at': new_started_at,
                'closes_at': new_closes_at,
                'guarantee': '123.00',
            })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_COURIER_SHIFT_RO_FIELD')

        with await shift.reload() as s:
            tap.eq(s.started_at, started_at, 'дата начала не поменялась')
            tap.eq(s.closes_at, closes_at, 'дата окончания не поменялась')
            tap.eq(s.guarantee, 100, 'ЗП не поменялась')
            tap.eq(s.shift_events, [], 'новых событий нет')

        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'closes_at': new_closes_at,
            })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('courier_shift.started_at', time2iso_utc(started_at))
        t.json_is('courier_shift.closes_at', time2iso_utc(closes_at))
        t.json_is('courier_shift.guarantee', '100.00')

        t.json_is('courier_shift.shift_events.0.type', 'edit')
        t.json_is('courier_shift.shift_events.0.user_id', user.user_id)
        t.json_is('courier_shift.shift_events.1.type', 'change')
        t.json_is('courier_shift.shift_events.1.user_id', user.user_id)
        t.json_is('courier_shift.shift_events.1.detail.old.closes_at',
                  time2iso(closes_at))
        t.json_is('courier_shift.shift_events.1.detail.new.closes_at',
                  time2iso(new_closes_at))


async def test_save_cluster_not_found(tap, api, dataset):
    with tap.plan(3, 'Кластер не найден'):
        store = await dataset.store(cluster='bad_cluster', cluster_id='100500')
        user = await dataset.user(role='admin', store=store)

        cs_target = await dataset.courier_shift(store=store)

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': cs_target.courier_shift_id,
                        })
        t.status_is(500, diag=True)
        t.json_is('code', 'ER_INTERNAL')


async def test_save_schedule(tap, api, dataset, time2iso_utc):
    with tap.plan(8, 'Сохранение расписания'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        shift = await dataset.courier_shift(
            store=store,
            status='request',
        )

        showtime = now().replace(microsecond=0) + timedelta(hours=1)

        # создаем смену
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'schedule': [
                    {"tags": ['best'],  "time": time2iso_utc(showtime)},
                    {"tags": [],        "time": time2iso_utc(showtime)},
                ],
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await shift.reload() as shift:
            tap.eq(len(shift.schedule), 2, 'Публикации сохранены')

            with shift.schedule[0] as schedule:
                tap.eq(schedule.tags, ['best'], 'теги сохранены')
                tap.eq(schedule.time, showtime, 'время показа')

            with shift.schedule[1] as schedule:
                tap.eq(schedule.tags, [], 'теги сохранены')
                tap.eq(schedule.time, showtime, 'время показа')


async def test_save_schedule_too_late(tap, api, dataset, time2iso_utc):
    with tap.plan(3, 'Сохранение расписания с датой в прошлом'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        shift = await dataset.courier_shift(
            store=store,
            status='request',
        )

        showtime = now().replace(microsecond=0) - timedelta(hours=1)

        # создаем смену
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'schedule': [
                    {"tags": ['best'],  "time": time2iso_utc(showtime)},
                    {"tags": [],        "time": time2iso_utc(showtime)},
                ],
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_save_after_schedule(tap, api, dataset, time2iso_utc):
    with tap.plan(3, 'Сохранение опубликованной смены'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)

        showtime = now().replace(microsecond=0) - timedelta(hours=1)
        shift = await dataset.courier_shift(
            store=store,
            status='waiting',
            schedule=[
                {"tags": ['best'],  "time": time2iso_utc(showtime)},
                {"tags": [],        "time": time2iso_utc(showtime)},
            ],
        )

        # редактируем смену
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'courier_id': courier.courier_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_save_schedule_to_past(tap, api, dataset, time2iso_utc):
    with tap.plan(3, 'Сохранение расписания из будущего в прошлое'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        showtime = now().replace(microsecond=0) + timedelta(hours=1)
        shift = await dataset.courier_shift(
            store=store,
            status='waiting',
            schedule=[
                {"tags": ['best'],  "time": time2iso_utc(showtime)},
                {"tags": [],        "time": time2iso_utc(showtime)},
            ],
        )

        # редактируем смену
        showtime = now().replace(microsecond=0) - timedelta(hours=1)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'schedule': [
                    {"tags": ['best'],  "time": time2iso_utc(showtime)},
                    {"tags": [],        "time": time2iso_utc(showtime)},
                ],
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_save_schedule_published(tap, api, dataset, time2iso_utc):
    with tap.plan(6, 'Сохранение расписания уже опубликованной смены'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        showtime = now().replace(microsecond=0) - timedelta(hours=1)
        shift = await dataset.courier_shift(
            store=store,
            status='waiting',
            schedule=[{
                "tags": ['best'],
                "time": time2iso_utc(showtime + timedelta(seconds=1))
            }, {
                "tags": [],
                "time": time2iso_utc(showtime)
            }],
        )

        t = await api(user=user)

        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'schedule': [{
                    "tags": [],
                    "time": time2iso_utc(showtime)
                }, {
                    "tags": ['best'],
                    "time": time2iso_utc(showtime + timedelta(seconds=1))
                }],
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        # редактируем смену
        showtime = now().replace(microsecond=0) + timedelta(hours=1)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'schedule': [
                    {"tags": ['best'],  "time": time2iso_utc(showtime)},
                    {"tags": [],        "time": time2iso_utc(showtime)},
                ],
            }
        )
        t.status_is(429, diag=True)
        t.json_is('code', 'ER_SCHEDULE_PUBLISHED')


async def test_limit_far_future_admin_ok(tap, api, dataset, cfg):
    with tap.plan(3, 'До ограничения в будущем создавать можно - логисты'):
        cfg.set('business.courier_shift.limit_far_future.admin.days', 100)
        cfg.set('business.courier_shift.limit_far_future.admin.weeks', None)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        shift = await dataset.courier_shift(
            store=store,
            status='request',
        )

        with user.role as role:
            role.add_permit('out_of_store', True)
            t = await api(user=user)

            _less = now() + timedelta(
                hours=1,
                days=cfg(
                    'business.courier_shift.limit_far_future.admin.days'
                ) - 1,
            )
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift.courier_shift_id,
                    'started_at': _less,
                    'closes_at': _less + timedelta(hours=1),
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')


async def test_limit_far_future_admin_fail(tap, api, dataset, cfg):
    with tap.plan(3, 'Слишком далеко в будущее - логисты'):
        cfg.set('business.courier_shift.limit_far_future.admin.days', 100)
        cfg.set('business.courier_shift.limit_far_future.admin.weeks', None)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        shift = await dataset.courier_shift(
            store=store,
            status='request',
        )

        with user.role as role:
            role.add_permit('out_of_store', True)
            t = await api(user=user)

            _high = now() + timedelta(
                hours=1,
                days=cfg(
                    'business.courier_shift.limit_far_future.admin.days'
                ) + 1,
            )
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift.courier_shift_id,
                    'started_at': _high,
                    'closes_at': _high + timedelta(hours=1),
                }
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_BAD_TIME_RANGE')


async def test_limit_far_future_store_ok(tap, api, dataset, cfg, time_mock):
    time_mock.set('2022-07-17 12:00:00+00:00')
    with tap.plan(3, 'До ограничения в будущем создавать можно - директор'):
        cfg.set('business.courier_shift.limit_far_future.store.days', 1)
        cfg.set('business.courier_shift.limit_far_future.store.weeks', None)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        shift = await dataset.courier_shift(
            store=store,
            status='request',
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)

            _less = time_mock.now() + timedelta(
                hours=1,
                days=cfg(
                    'business.courier_shift.limit_far_future.store.days'
                ) - 1,
            )
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift.courier_shift_id,
                    'started_at': _less,
                    'closes_at': _less + timedelta(hours=1),
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')


async def test_limit_far_future_store_fail(tap, api, dataset, cfg, time_mock):
    time_mock.set('2022-07-17 12:00:00+00:00')
    with tap.plan(3, 'Слишком далеко в будущее - директора'):
        cfg.set('business.courier_shift.limit_far_future.store.days', 1)
        cfg.set('business.courier_shift.limit_far_future.store.weeks', None)

        _high = time_mock.now() + timedelta(
            hours=1,
            days=cfg(
                'business.courier_shift.limit_far_future.store.days'
            ) + 1,
        )

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        shift = await dataset.courier_shift(
            store=store,
            status='request',
            started_at=_high,
            closes_at=_high + timedelta(hours=1),
        )

        with user.role as role:
            role.remove_permit('out_of_store')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift.courier_shift_id,
                    'started_at': _high + timedelta(minutes=1),
                    'closes_at': _high + timedelta(hours=1, minutes=1),
                }
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_BAD_TIME_RANGE')


async def test_limit_far_future_week_ok(tap, api, dataset, cfg, time_mock):
    time_mock.set('2022-07-17 12:00:00+00:00')
    with tap.plan(3, 'До ограничения в будущем создавать можно - с неделями'):
        cfg.set('business.courier_shift.limit_far_future.store.days', 3)
        cfg.set('business.courier_shift.limit_far_future.store.weeks', 1)

        _less = time_mock.now() + timedelta(
            hours=1,
            days=cfg(
                'business.courier_shift.limit_far_future.store.days'
            ) + cfg(
                'business.courier_shift.limit_far_future.store.weeks'
            ) * 7 - 1,
        )

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        shift = await dataset.courier_shift(
            store=store,
            status='request',
            started_at=_less,
            closes_at=_less + timedelta(hours=1),
        )

        with user.role as role:
            role.remove_permit('out_of_store')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift.courier_shift_id,
                    'started_at': _less + timedelta(minutes=1),
                    'closes_at': _less + timedelta(hours=1, minutes=1),
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')


async def test_limit_far_future_week_fail(tap, api, dataset, cfg, time_mock):
    time_mock.set('2022-07-17 12:00:00+00:00')
    with tap.plan(3, 'Слишком далеко в будущее - с неделями'):
        cfg.set('business.courier_shift.limit_far_future.store.days', 3)
        cfg.set('business.courier_shift.limit_far_future.store.weeks', 1)

        _high = time_mock.now() + timedelta(
            hours=1,
            days=cfg(
                'business.courier_shift.limit_far_future.store.days'
            ) + cfg(
                'business.courier_shift.limit_far_future.store.weeks'
            ) * 14 + 1,
        )

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        shift = await dataset.courier_shift(
            store=store,
            status='request',
            started_at=_high,
            closes_at=_high + timedelta(hours=1),
        )

        with user.role as role:
            role.remove_permit('out_of_store')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift.courier_shift_id,
                    'started_at': _high + timedelta(minutes=1),
                    'closes_at': _high + timedelta(hours=1, minutes=1),
                }
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_BAD_TIME_RANGE')


@pytest.mark.parametrize('name,value', [
    ('cluster_id', 'unknown'),
    ('company_id', 'unknown'),
    # store_id не тестируем т.к. валидируется в over и даст ER_ACCESS
    ('guarantee', '111.22'),
])
async def test_denied_fields(tap, api, dataset, name, value):
    with tap.plan(4, 'Директорам нельзя редактировать некоторые поля'):

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        shift = await dataset.courier_shift(
            store=store,
            status='request',
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)

            old_value = getattr(shift, name)

            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift.courier_shift_id,
                    name: value,
                }
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_COURIER_SHIFT_RO_FIELD')

            with await shift.reload():
                new_value = getattr(shift, name)

                tap.eq(new_value, old_value, 'значение не менялось')


async def test_denied_fields_not_change(tap, api, dataset):
    with tap.plan(3, 'Ошибка редактирования ro полей только если менялись'):

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        shift = await dataset.courier_shift(
            store=store,
            status='request',
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)

            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift.courier_shift_id,
                    'store_id': shift.store_id,
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')


async def test_store_own_courier(tap, api, dataset):
    with tap.plan(4, 'Директорам можно снимать своих курьеров'):

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        courier = await dataset.courier(
            cluster=cluster,
            tags_store=[store.store_id],
        )

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)

            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift.courier_shift_id,
                    'courier_id': None,
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            with await shift.reload():
                tap.eq(shift.courier_id, None, 'курьер снят')


async def test_store_not_own_courier(tap, api, dataset):
    with tap.plan(5, 'Директорам нельзя снимать не своих курьеров'):

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
        )

        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)

            await t.post_ok(
                'api_admin_courier_shifts_save',
                json={
                    'courier_shift_id': shift.courier_shift_id,
                    'courier_id': None,
                }
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_COURIER_SHIFT_RO_FIELD')
            t.json_is(
                'message',
                'Can not change courier from outside your store'
            )

            with await shift.reload():
                tap.eq(shift.courier_id, courier.courier_id, 'курьер не снят')


async def test_working_interval(tap, api, dataset):
    with tap.plan(3, 'выход за рабочее время'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'forbidden_before_time': time(12, 0, 0),
                'forbidden_after_time': time(16, 0, 0),
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        day = (now(pytz.timezone(cluster.tz)) + timedelta(days=2)) \
            .replace(hour=0, minute=0, second=0, microsecond=0)

        started_at = day.replace(hour=12)
        closes_at = day.replace(hour=16)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            started_at=started_at,
            closes_at=closes_at,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'started_at': started_at - timedelta(hours=1),
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_WORKING_INTERVAL')
