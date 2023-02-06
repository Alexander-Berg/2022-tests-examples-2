from datetime import timedelta

import pytest


async def test_export_shifts(tap, api, dataset, now):
    with tap.plan(8, 'Экспортирование смен курьеров в CSV'):
        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store1)
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': 52345,
                },
            },
        )

        _now = now().replace(microsecond=0)

        shift1 = await dataset.courier_shift(
            store=store1,
            tags=[
                (await dataset.courier_shift_tag()).title,
                (await dataset.courier_shift_tag()).title,
            ]
        )
        shift2 = await dataset.courier_shift(
            store=store1,
            tags=[
                (await dataset.courier_shift_tag()).title,
                (await dataset.courier_shift_tag()).title,
            ],
            status='complete',
            courier=courier,
            started_at=_now - timedelta(hours=4),
            closes_at=_now - timedelta(hours=1),
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'started',
                    'location': {'lon': 33, 'lat': 55},
                    'created': _now - timedelta(hours=4, minutes=1),
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'paused',
                    'location': {'lon': 33, 'lat': 55},
                    'created': _now - timedelta(hours=2, minutes=10),
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'unpaused',
                    'location': {'lon': 33, 'lat': 55},
                    'created': _now - timedelta(hours=2),
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'paused',
                    'location': {'lon': 33, 'lat': 55},
                    'created': _now - timedelta(hours=1, minutes=30),
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'unpaused',
                    'location': {'lon': 33, 'lat': 55},
                    'created': _now - timedelta(hours=1, minutes=29),
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'stopped',
                    'detail': {
                        'reason': 'close_time',
                    },
                    'created': _now - timedelta(hours=1, minutes=1),
                }
            ],
        )

        await dataset.courier_shift(store=store2)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_export_shifts', json={
                'store_id': store1.store_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('csv', f'{shift1.courier_shift_id}', 'Смена 1')
        t.json_like('csv', f'{shift2.courier_shift_id}', 'Смена 1')
        t.json_like('csv', f'{store1.external_id}', 'depot_id')
        t.json_like('csv', f'{courier.eda_id}', 'Едовый id курьера')
        t.json_like('csv', 'close_time', 'причина закрытия')


@pytest.mark.parametrize(
    'reason,expected', [
        (None, ''),
        ('police', 'police'),
        ('admin', 'admin'),
    ]
)
async def test_reason_for_stop(tap, api, dataset, now, reason, expected):
    with tap.plan(5, 'Экспорт причины закрытия смены'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store)
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': 52345,
                },
            },
        )

        _now = now().replace(microsecond=0)

        await dataset.courier_shift(
            store=store,
            tags=[
                (await dataset.courier_shift_tag()).title,
                (await dataset.courier_shift_tag()).title,
            ],
            status='complete',
            courier=courier,
            started_at=_now - timedelta(hours=4),
            closes_at=_now - timedelta(hours=1),
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'started',
                    'location': {'lon': 33, 'lat': 55},
                    'created': _now - timedelta(hours=4, minutes=1),
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'stopped',
                    'detail': {
                        'reason': reason,
                    },
                    'created': _now - timedelta(hours=1, minutes=1),
                }
            ],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_export_shifts', json={
                'store_id': store.store_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        rows = t.res['json']['csv'].strip().split('\n')
        tap.eq(len(rows), 2, 'заголовок + одна строка')
        tap.eq(rows[-1].split(';')[-2], expected, 'причина закрытия')


async def test_reason_for_stop_null(tap, api, dataset, now):
    with tap.plan(5, 'Экспорт причины закрытия, когда detail нет'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store)
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': 52345,
                },
            },
        )

        _now = now().replace(microsecond=0)

        await dataset.courier_shift(
            store=store,
            tags=[
                (await dataset.courier_shift_tag()).title,
                (await dataset.courier_shift_tag()).title,
            ],
            status='complete',
            courier=courier,
            started_at=_now - timedelta(hours=4),
            closes_at=_now - timedelta(hours=1),
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'started',
                    'location': {'lon': 33, 'lat': 55},
                    'created': _now - timedelta(hours=4, minutes=1),
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'stopped',
                    'detail': None,
                    'created': _now - timedelta(hours=1, minutes=1),
                }
            ],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_export_shifts', json={
                'store_id': store.store_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        rows = t.res['json']['csv'].strip().split('\n')
        tap.eq(len(rows), 2, 'заголовок + одна строка')
        tap.eq(rows[-1].split(';')[-1], '', 'причина закрытия отсутствует')


@pytest.mark.parametrize(
    'detail,expected', [
        # одна причина задана
        (
            [{'reason': 'got_wet'}],
            'got_wet'
        ),
        # сразу несколько причин
        (
            [
                {'reason': 'got_wet'},
                {'reason': 'device_problem'},
            ],
            'got_wet,device_problem',
        ),
        # несколько одинаковых причин
        (
            [
                {'reason': 'got_wet'},
                {'reason': 'got_wet'},
                {'reason': 'got_wet'},
            ],
            'got_wet,got_wet,got_wet',
        ),
        # явно не задана (по доке это возможный кейс)
        (
            [{'reason': None}],
            '',
        ),
        # детали пустые (в старых иногда)
        (
            [{}],
            '',
        ),
        # детали отсутствуют (такое тоже должен обрабатывать и не падать)
        (
            [None],
            '',
        ),
    ]
)
async def test_reason_for_pause(tap, api, dataset, now, detail, expected):
    with tap.plan(5, 'Экспорт причин постановки на паузу'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store)
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': 52345,
                },
            },
        )

        _now = now().replace(microsecond=0)

        pauses = []
        for _detail in detail:
            pauses.extend([
                {
                    'courier_id': courier.courier_id,
                    'type': 'paused',
                    'location': {'lon': 33, 'lat': 55},
                    'created': _now - timedelta(hours=1, minutes=30),
                    'detail': _detail,
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'unpaused',
                    'location': {'lon': 33, 'lat': 55},
                    'created': _now - timedelta(hours=1, minutes=29),
                },
            ])

        await dataset.courier_shift(
            store=store,
            tags=[
                (await dataset.courier_shift_tag()).title,
                (await dataset.courier_shift_tag()).title,
            ],
            status='processing',
            courier=courier,
            started_at=_now - timedelta(hours=4),
            closes_at=_now - timedelta(hours=1),
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'started',
                    'location': {'lon': 33, 'lat': 55},
                    'created': _now - timedelta(hours=4, minutes=1),
                },
                *pauses,
            ],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_export_shifts', json={
                'store_id': store.store_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        rows = t.res['json']['csv'].strip().split('\n')
        tap.eq(len(rows), 2, 'заголовок + одна строка')
        tap.eq(rows[-1].split(';')[-1], expected, 'причина закрытия')
