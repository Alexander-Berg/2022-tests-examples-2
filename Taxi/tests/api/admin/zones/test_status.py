from datetime import timedelta

import pytest

from stall.model.zone import ZONE_STATUSES


@pytest.mark.parametrize(
    'new_status',
    [x for x in ZONE_STATUSES if x != 'template']
)
async def test_status(tap, api, dataset, now, new_status):
    with tap.plan(5, 'Изменение статуса'):

        store   = await dataset.store()
        user    = await dataset.user(store=store)
        zone    = await dataset.zone(
            store=store,
            status='active',
            effective_from=now() - timedelta(days=1),
        )
        timetable = dataset.TimeTable([
            dataset.TimeTableItem({
                'type': 'monday',
                'begin': '12:00',
                'end': '13:59:59',
            })
        ])

        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_status',
            json={
                'zone_id': zone.zone_id,
                'status': new_status,
                'timetable': timetable,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('zone.status', new_status)
        t.json_is(
            'zone.timetable',
            timetable,
        )


async def test_status_template(tap, api, dataset, now):
    with tap.plan(3, 'На доработку отправлять текущие зоны нельзя'):

        store   = await dataset.store()
        user    = await dataset.user(store=store)
        zone    = await dataset.zone(
            store=store,
            status='active',
            effective_from=now() - timedelta(days=1),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_status',
            json={
                'zone_id': zone.zone_id,
                'status': 'template',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ALREADY_APPROVED')


async def test_status_done(tap, api, dataset, now):
    with tap.plan(3, 'Не трогаем уже исполненные зоны'):

        store   = await dataset.store()
        user    = await dataset.user(store=store)
        zone    = await dataset.zone(
            store=store,
            status='active',
            effective_from=now() - timedelta(days=10),
            effective_till=now() - timedelta(days=5),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_status',
            json={
                'zone_id': zone.zone_id,
                'status': 'disabled',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ALREADY_DONE')


@pytest.mark.parametrize(
    'new_status',
    [x for x in ZONE_STATUSES if x != 'template']
)
async def test_status_future(tap, api, dataset, now, new_status):
    with tap.plan(4, 'Изменение статуса для будущей зоны'):

        effective_from = now() + timedelta(days=1)

        store   = await dataset.store()
        user    = await dataset.user(store=store)
        zone    = await dataset.zone(
            store=store,
            status='active',
            effective_from=effective_from,
        )

        effective_from += timedelta(days=1)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_status',
            json={
                'zone_id': zone.zone_id,
                'status': new_status,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('zone.status', new_status)


async def test_active_to_template(tap, api, dataset, now):
    with tap.plan(3, 'Изменение статуса из active в template'):

        effective_from = now() + timedelta(days=1)

        store   = await dataset.store()
        user    = await dataset.user(store=store)
        zone    = await dataset.zone(
            store=store,
            status='active',
            effective_from=effective_from,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_status',
            json={
                'zone_id': zone.zone_id,
                'status': 'template',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ALREADY_APPROVED')


async def test_template(tap, api, dataset):
    with tap.plan(3, 'Шаблонам нельзя менять статус'):

        store   = await dataset.store()
        user    = await dataset.user(store=store)
        zone    = await dataset.zone(store=store, status='template')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_status',
            json={
                'zone_id': zone.zone_id,
                'status': 'active',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_APPROVE_REQUIRED')
