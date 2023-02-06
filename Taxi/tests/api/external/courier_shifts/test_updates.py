# pylint: disable=unused-variable,too-many-locals,too-many-statements
from datetime import timedelta

import pytest


async def test_updates(api, dataset, tap, now, time2iso_utc):
    with tap.plan(45, 'репликация смен'):
        company = await dataset.company()
        store   = await dataset.store(company=company)
        store2  = await dataset.store(company=company)

        courier1 = await dataset.courier()
        courier2 = await dataset.courier()
        courier3 = await dataset.courier()

        _now = now().replace(microsecond=0)

        started_real1 = _now - timedelta(hours=2, minutes=5)
        stopped_plan1 = _now + timedelta(hours=2)

        courier_shift1 = await dataset.courier_shift(
            store=store,
            courier=courier1,
            status='processing',
            started_at=_now - timedelta(hours=2),
            closes_at=stopped_plan1,
            shift_events=[
                {'type': 'started', 'created': started_real1},
            ],
        )

        started_real2 = _now - timedelta(hours=8, minutes=7)
        stopped_real2 = _now + timedelta(hours=6)

        courier_shift2 = await dataset.courier_shift(
            store=store,
            courier=courier2,
            status='leave',
            started_at=_now - timedelta(hours=8),
            closes_at=_now + timedelta(hours=7),
            shift_events=[
                {'type': 'started', 'created': started_real2},
                {'type': 'stopped', 'created': stopped_real2},
            ],
        )

        started_real3 = _now - timedelta(hours=5, minutes=5)
        stopped_real3 = _now - timedelta(hours=4)

        courier_shift3 = await dataset.courier_shift(
            store=store,
            courier=courier1,
            status='complete',
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
            shift_events=[
                {'type': 'started', 'created': started_real3},
                {'type': 'stopped', 'created': stopped_real3},
            ],
        )

        courier_shift4 = await dataset.courier_shift(
            store=store2,
            courier=courier3,
            status='absent',
            started_at=_now - timedelta(hours=3),
            closes_at=_now + timedelta(hours=2),
        )

        started_plan5 = _now + timedelta(hours=2, minutes=5)
        stopped_plan5 = _now + timedelta(hours=4)
        courier_shift5 = await dataset.courier_shift(
            store=store2,
            courier=courier3,
            status='waiting',
            started_at=started_plan5,
            closes_at=stopped_plan5,
        )

        await dataset.courier_shift(
            store=store,
            status='request',
            started_at=_now + timedelta(hours=4),
            closes_at=_now + timedelta(hours=6),
        )

        t = await api(token=company.token)
        await t.get_ok(
            'api_external_courier_shifts_updates',
            form={},
        )
        t.status_is(200, diag=True)

        t.json_has('data')
        t.json_has('data.cursor')
        t.json_has('data.shifts.0')
        t.json_has('data.shifts.1')
        t.json_has('data.shifts.2')
        t.json_has('data.shifts.3')
        t.json_has('data.shifts.4')
        t.json_hasnt('data.shifts.5')

        json = t.res['json']

        shifts = {x['shift_id']: x for x in json['data']['shifts']}

        data1 = shifts[courier_shift1.courier_shift_id]
        tap.eq(
            data1['courier_id'],
            courier1.external_id,
            'В сменах проставлен внешний идентификатор курьера'
        )
        tap.eq(data1['zone_group_id'], store.store_id, 'zone_group_id')
        tap.eq(data1['status'], 'in_progress', 'status')
        tap.eq(data1['started_at'], time2iso_utc(started_real1), 'started_at')
        tap.eq(data1['closes_at'], time2iso_utc(stopped_plan1), 'closes_at')
        tap.eq(data1['store_id'], store.store_id, 'store_id')
        tap.eq(data1['store_external_id'], store.external_id, 'external_id')

        data2 = shifts[courier_shift2.courier_shift_id]
        tap.eq(
            data2['courier_id'],
            courier2.external_id,
            'В сменах проставлен внешний идентификатор курьера'
        )
        tap.eq(data2['zone_group_id'], store.store_id, 'zone_group_id')
        tap.eq(data2['status'], 'closed', 'status')
        tap.eq(data2['started_at'], time2iso_utc(started_real2), 'started_at')
        tap.eq(data2['closes_at'], time2iso_utc(stopped_real2), 'closes_at')
        tap.eq(data2['store_id'], store.store_id, 'store_id')
        tap.eq(data2['store_external_id'], store.external_id, 'external_id')

        data3 = shifts[courier_shift3.courier_shift_id]
        tap.eq(
            data3['courier_id'],
            courier1.external_id,
            'В сменах проставлен внешний идентификатор курьера'
        )
        tap.eq(data3['zone_group_id'], store.store_id, 'zone_group_id')
        tap.eq(data3['status'], 'closed', 'status')
        tap.eq(data3['started_at'], time2iso_utc(started_real3), 'started_at')
        tap.eq(data3['closes_at'], time2iso_utc(stopped_real3), 'closes_at')
        tap.eq(data3['store_id'], store.store_id, 'store_id')
        tap.eq(data3['store_external_id'], store.external_id, 'external_id')

        data4 = shifts[courier_shift4.courier_shift_id]
        tap.eq(
            data4['courier_id'],
            courier3.external_id,
            'В сменах проставлен внешний идентификатор курьера'
        )
        tap.eq(data4['zone_group_id'], store2.store_id, 'zone_group_id')
        tap.eq(data4['status'], 'closed', 'status')
        tap.ok('started_at' not in data4, 'started_at')
        tap.ok('closes_at' not in data4, 'closes_at')
        tap.eq(data4['store_id'], store2.store_id, 'store_id')
        tap.eq(data4['store_external_id'], store2.external_id, 'external_id')

        data5 = shifts[courier_shift5.courier_shift_id]
        tap.eq(
            data5['courier_id'],
            courier3.external_id,
            'В сменах проставлен внешний идентификатор курьера'
        )
        tap.eq(data5['zone_group_id'], store2.store_id, 'zone_group_id')
        tap.eq(data5['status'], 'waiting', 'status')
        tap.eq(data5['started_at'], time2iso_utc(started_plan5), 'started_at')
        tap.eq(data5['closes_at'], time2iso_utc(stopped_plan5), 'closes_at')
        tap.eq(data5['store_id'], store2.store_id, 'store_id')
        tap.eq(data5['store_external_id'], store2.external_id, 'external_id')


async def test_many(api, dataset, tap, now, cfg):
    with tap.plan(19, 'репликация смен, несколько запросов подряд'):
        cfg.set('cursor.limit', 1)

        company = await dataset.company()

        cluster1 = await dataset.cluster()
        cluster2 = await dataset.cluster()
        cluster3 = await dataset.cluster()

        store1   = await dataset.store(company=company, cluster=cluster1)
        store2   = await dataset.store(company=company, cluster=cluster2)
        store3   = await dataset.store(company=company, cluster=cluster3)

        courier1 = await dataset.courier(cluster=cluster1)
        courier2 = await dataset.courier(cluster=cluster2)
        courier3 = await dataset.courier(cluster=cluster3)

        _now = now().replace(microsecond=0)

        shift1 = await dataset.courier_shift(
            store=store1,
            courier=courier1,
            status='processing',
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
            shift_events=[
                {
                    'type': 'started',
                    'created': _now - timedelta(hours=2, minutes=5),
                },
            ],
        )
        shift2 = await dataset.courier_shift(
            store=store2,
            courier=courier2,
            status='processing',
            started_at=_now - timedelta(hours=1, minutes=45),
            closes_at=_now + timedelta(hours=2),
            shift_events=[
                {
                    'type': 'started',
                    'created': _now - timedelta(hours=1, minutes=50),
                },
            ],
        )
        shift3 = await dataset.courier_shift(
            store=store3,
            courier=courier3,
            status='processing',
            started_at=_now - timedelta(hours=1, minutes=30),
            closes_at=_now + timedelta(hours=2),
            shift_events=[
                {
                    'type': 'started',
                    'created': _now - timedelta(hours=1, minutes=35),
                },
            ],
        )

        shifts = sorted([shift1, shift2, shift3], key=lambda x: x.lsn)
        id2lsn = {
            shift1.courier_shift_id: shift1.lsn,
            shift2.courier_shift_id: shift2.lsn,
            shift3.courier_shift_id: shift3.lsn,
        }
        received_lsn = []

        t = await api(token=company.token)
        await t.get_ok(
            'api_external_courier_shifts_updates',
            form={},
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_has('data.cursor')
        t.json_has('data.shifts.0')
        t.json_hasnt('data.shifts.1')
        received_lsn.append(id2lsn[
            t.res['json']['data']['shifts'][0]['shift_id']
        ])

        await t.get_ok(
            'api_external_courier_shifts_updates',
            form={'cursor': t.res['json']['data']['cursor']},
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_has('data.cursor')
        t.json_has('data.shifts.0')
        t.json_hasnt('data.shifts.1')
        received_lsn.append(id2lsn[
            t.res['json']['data']['shifts'][0]['shift_id']
        ])

        await t.get_ok(
            'api_external_courier_shifts_updates',
            form={'cursor': t.res['json']['data']['cursor']},
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_has('data.cursor')
        t.json_has('data.shifts.0')
        t.json_hasnt('data.shifts.1')
        received_lsn.append(id2lsn[
            t.res['json']['data']['shifts'][0]['shift_id']
        ])

        tap.eq(
            received_lsn,
            [shift.lsn for shift in shifts],
            'порядок смен корректный'
        )


async def test_pause(api, dataset, tap, now, time2iso_utc):
    with tap.plan(32, 'репликация смен с паузами'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store1  = await dataset.store(company=company, cluster=cluster)
        store2  = await dataset.store(company=company, cluster=cluster)

        courier1 = await dataset.courier(cluster=cluster)
        courier2 = await dataset.courier(cluster=cluster)
        courier3 = await dataset.courier(cluster=cluster)

        _now = now().replace(microsecond=0)

        started_real1 = _now - timedelta(hours=2, minutes=5)
        paused_real1 = _now - timedelta(hours=2, minutes=0)

        courier_shift1 = await dataset.courier_shift(
            store=store1,
            courier=courier1,
            status='processing',
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
            shift_events=[
                {'type': 'started', 'created': started_real1},
                {'type': 'paused', 'created': paused_real1},
            ],
        )

        started_real2 = _now - timedelta(hours=3, minutes=10)
        paused_real2 = _now - timedelta(hours=3, minutes=5)
        unpaused_real2 = _now - timedelta(hours=3, minutes=0)

        courier_shift2 = await dataset.courier_shift(
            store=store2,
            courier=courier2,
            status='processing',
            started_at=_now - timedelta(hours=3),
            closes_at=_now + timedelta(hours=3),
            shift_events=[
                {'type': 'started', 'created': started_real2},
                {'type': 'paused', 'created': paused_real2},
                {'type': 'unpaused', 'created': unpaused_real2},
            ],
        )

        started_real3 = started_real2
        paused_real3 = _now - timedelta(hours=2, minutes=5)
        unpaused_real3 = _now - timedelta(hours=2, minutes=0)
        courier_shift3 = await dataset.courier_shift(
            store=store2,
            courier=courier3,
            status='processing',
            started_at=_now - timedelta(hours=3),
            closes_at=_now + timedelta(hours=3),
            shift_events=[
                {'type': 'started', 'created': started_real3},
                {'type': 'paused', 'created': paused_real2},
                {'type': 'unpaused', 'created': unpaused_real2},
                {'type': 'paused', 'created': paused_real3},
                {'type': 'unpaused', 'created': unpaused_real3},
            ],
        )

        await dataset.courier_shift(status='request')

        t = await api(token=company.token)
        await t.get_ok(
            'api_external_courier_shifts_updates',
            form={},
        )
        t.status_is(200, diag=True)

        t.json_has('data')
        t.json_has('data.cursor')
        t.json_has('data.shifts.0')
        t.json_has('data.shifts.1')
        t.json_has('data.shifts.2')
        t.json_hasnt('data.shifts.3')

        json = t.res['json']

        shifts = {x['shift_id']: x for x in json['data']['shifts']}

        data1 = shifts[courier_shift1.courier_shift_id]
        tap.eq(
            data1['courier_id'],
            courier1.external_id,
            'В сменах проставлен внешний идентификатор курьера'
        )
        tap.eq(data1['zone_group_id'], store1.store_id, 'zone_group_id')
        tap.eq(data1['status'], 'paused', 'status')
        tap.eq(data1['started_at'], time2iso_utc(started_real1), 'started_at')
        tap.eq(data1['paused_at'], time2iso_utc(paused_real1), 'paused')
        tap.ok('unpauses_at' not in data1, 'unpaused')
        tap.eq(data1['store_id'], store1.store_id, 'store_id')
        tap.eq(data1['store_external_id'], store1.external_id, 'external_id')

        data2 = shifts[courier_shift2.courier_shift_id]
        tap.eq(
            data2['courier_id'],
            courier2.external_id,
            'В сменах проставлен внешний идентификатор курьера'
        )
        tap.eq(data2['zone_group_id'], store2.store_id, 'zone_group_id')
        tap.eq(data2['status'], 'in_progress', 'status')
        tap.eq(data2['started_at'], time2iso_utc(started_real2), 'started_at')
        tap.eq(data2['paused_at'], time2iso_utc(paused_real2), 'paused')
        tap.eq(data2['unpauses_at'], time2iso_utc(unpaused_real2), 'unpaused')
        tap.eq(data2['store_id'], store2.store_id, 'store_id')
        tap.eq(data2['store_external_id'], store2.external_id, 'external_id')

        data3 = shifts[courier_shift3.courier_shift_id]
        tap.eq(
            data3['courier_id'],
            courier3.external_id,
            'В сменах проставлен внешний идентификатор курьера'
        )
        tap.eq(data3['zone_group_id'], store2.store_id, 'zone_group_id')
        tap.eq(data3['status'], 'in_progress', 'status')
        tap.eq(data3['started_at'], time2iso_utc(started_real3), 'started_at')
        tap.eq(data3['paused_at'], time2iso_utc(paused_real3), 'paused')
        tap.eq(data3['unpauses_at'], time2iso_utc(unpaused_real3), 'unpaused')
        tap.eq(data3['store_id'], store2.store_id, 'store_id')
        tap.eq(data3['store_external_id'], store2.external_id, 'external_id')


@pytest.mark.parametrize('form', [
    {},
    {'cursor': None},
    {'cursor': ''},
])
async def test_cursor(api, cfg, dataset, tap, form):
    cfg.set('cursor.limit', 2)

    with tap.plan(13, 'репликация смен'):
        company = await dataset.company()
        store   = await dataset.store(company=company)
        courier = await dataset.courier()

        shift1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )
        shift2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )
        shift3 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        t = await api(token=company.token)
        await t.get_ok(
            'api_external_courier_shifts_updates',
            form=form,
        )
        t.status_is(200, diag=True)

        t.json_has('data')
        t.json_has('data.cursor')
        t.json_has('data.shifts.0')
        t.json_has('data.shifts.1')
        t.json_hasnt('data.shifts.2')

        await t.get_ok(
            'api_external_courier_shifts_updates',
            form={'cursor': t.res['json']['data']['cursor']},
        )
        t.status_is(200, diag=True)

        t.json_has('data')
        t.json_has('data.cursor')
        t.json_has('data.shifts.0')
        t.json_hasnt('data.shifts.1')


@pytest.mark.parametrize('status', ['template', 'request', 'closed'])
async def test_empty(api, dataset, tap, status):
    with tap.plan(5, 'Пустой список'):
        company = await dataset.company()
        store   = await dataset.store(company=company)
        courier = await dataset.courier()
        shift   = await dataset.courier_shift(
            store=store,
            courier=courier,
            status=status,
        )

        t = await api(token=company.token)

        await t.get_ok(
            'api_external_courier_shifts_updates',
            form={'cursor': None},
        )
        t.status_is(200, diag=True)

        t.json_has('data')
        t.json_has('data.cursor')
        t.json_is('data.shifts', [])


async def test_updates_stores_in_cluster(api, dataset, tap):
    with tap.plan(17, 'Несколько лавок в одном кластере'):
        cluster = await dataset.cluster()
        company = await dataset.company(cluster=cluster)
        store1  = await dataset.store(company=company, cluster=cluster)
        store2  = await dataset.store(company=company, cluster=cluster)
        courier = await dataset.courier()

        courier_shift1 = await dataset.courier_shift(
            store=store1,
            courier=courier,
            status='processing',
        )
        courier_shift2 = await dataset.courier_shift(
            store=store2,
            courier=courier,
            status='complete',
        )

        t = await api(token=company.token)
        await t.get_ok(
            'api_external_courier_shifts_updates',
            form={},
        )
        t.status_is(200, diag=True)

        t.json_has('data')
        t.json_has('data.cursor')
        t.json_has('data.shifts.0')
        t.json_has('data.shifts.1')
        t.json_hasnt('data.shifts.2')

        json = t.res['json']

        shifts = {x['shift_id']: x for x in json['data']['shifts']}

        data1 = shifts[courier_shift1.courier_shift_id]
        tap.eq(
            data1['courier_id'],
            courier.external_id,
            'В сменах проставлен внешний идентификатор курьера'
        )
        tap.eq(data1['zone_group_id'], store1.store_id, 'zone_group_id')
        tap.eq(data1['status'], 'in_progress', 'status')
        tap.eq(data1['store_id'], store1.store_id, 'store_id')
        tap.eq(data1['store_external_id'], store1.external_id, 'external_id')

        data2 = shifts[courier_shift2.courier_shift_id]
        tap.eq(
            data2['courier_id'],
            courier.external_id,
            'В сменах проставлен внешний идентификатор курьера'
        )
        tap.eq(data2['zone_group_id'], store2.store_id, 'zone_group_id')
        tap.eq(data2['status'], 'closed', 'status')
        tap.eq(data2['store_id'], store2.store_id, 'store_id2')
        tap.eq(data2['store_external_id'], store2.external_id, 'external_id2')


async def test_old(api, dataset, tap, now):
    with tap.plan(13, 'Репликацию начинаем с недавних смен'):
        company = await dataset.company()
        cluster = await dataset.cluster()
        store   = await dataset.store(company=company, cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        _now = now().replace(microsecond=0)

        started_at_2 =  _now - timedelta(days=2)
        closes_at_2  =  started_at_2 + timedelta(hours=2)
        shift2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='complete',
            started_at=started_at_2,
            closes_at=closes_at_2,
            shift_events=[
                {'type': 'started', 'created': started_at_2},
                {'type': 'stopped', 'created': closes_at_2},
            ],

            # Форсим обновление в прошлое
            created=started_at_2,
            updated=closes_at_2,
        )

        started_at_1 =  _now - timedelta(hours=4)
        closes_at_1  =  started_at_1 + timedelta(hours=2)
        shift1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='complete',
            started_at=started_at_1,
            closes_at=closes_at_1,
            shift_events=[
                {'type': 'started', 'created': started_at_1},
                {'type': 'stopped', 'created': closes_at_1},
            ],
        )

        t = await api(token=company.token)
        await t.get_ok(
            'api_external_courier_shifts_updates',
            form={},
        )
        t.status_is(200, diag=True)

        t.json_has('data')
        t.json_has('data.cursor')
        t.json_has('data.shifts.0')
        t.json_is('data.shifts.0.shift_id', shift1.courier_shift_id)
        t.json_hasnt('data.shifts.1')

        cursor = t.res['json']['data']['cursor']
        tap.ok(cursor, 'Курсор получен')

        await t.get_ok(
            'api_external_courier_shifts_updates',
            form={'cursor': cursor},
        )
        t.status_is(200, diag=True)

        t.json_has('data')
        t.json_has('data.cursor')
        t.json_hasnt('data.shifts.0')


async def test_new(api, dataset, tap, now):
    with tap.plan(5, 'Только за день до начала смены'):
        company = await dataset.company()
        cluster = await dataset.cluster()
        store   = await dataset.store(company=company, cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        _now = now().replace(microsecond=0)

        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='complete',
            started_at=_now + timedelta(days=2),
            closes_at=_now + timedelta(days=2, hours=2),
        )

        t = await api(token=company.token)
        await t.get_ok(
            'api_external_courier_shifts_updates',
            form={},
        )
        t.status_is(200, diag=True)

        t.json_has('data')
        t.json_has('data.cursor')
        t.json_hasnt('data.shifts.0')
