# pylint: disable=unused-variable
from datetime import datetime, timedelta

import pytest

from libstall.util import tzone, time2iso_utc


async def test_approve(tap, api, dataset, job, now):
    with tap.plan(7, 'Аппрувим'):

        effective_from = now().replace(minute=0, second=0, microsecond=0)
        effective_from += timedelta(hours=2)

        store   = await dataset.store()
        user1   = await dataset.user(store=store)
        user2   = await dataset.user(store=store)
        zone    = await dataset.zone(
            store=store,
            status='template',
            users=[user1.user_id],
            effective_from=effective_from,
        )

        t = await api(user=user2)
        await t.post_ok(
            'api_admin_zones_approve',
            json={
                'zone_id': zone.zone_id,
                'status': 'active',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is(
            'zone.effective_from',
            time2iso_utc(effective_from),
        )
        t.json_is('zone.effective_till', None)

        with await job.take() as task:
            tap.ok(task, 'Таска получена')
            tap.eq(
                task.callback,
                'stall.model.zone.Zone.job_fix_till',
                'Задание перерасчета поставлено'
            )


async def test_read_only(tap, api, dataset):
    with tap.plan(3, 'После активации становится только для чтения'):

        store   = await dataset.store()
        user    = await dataset.user(store=store)
        zone    = await dataset.zone(store=store, status='active')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_approve',
            json={
                'zone_id': zone.zone_id,
                'status': 'active',
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_READONLY_AFTER_CREATE')


async def test_permit(tap, api, dataset):
    with tap.plan(3, 'Аппрув только с пермитом'):

        store   = await dataset.store()
        user    = await dataset.user(store=store)
        zone    = await dataset.zone(store=store, status='template')

        with user.role as role:
            role.remove_permit('zones_approve')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_zones_approve',
                json={
                    'zone_id': zone.zone_id,
                    'status': 'active',
                },
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


async def test_users(tap, api, dataset):
    with tap.plan(3, 'Подтверждать может только тот, кто не редакторовал'):

        store   = await dataset.store()
        user    = await dataset.user(store=store)
        zone    = await dataset.zone(
            store=store,
            status='template',
            users=[user.user_id],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_approve',
            json={
                'zone_id': zone.zone_id,
                'status': 'active',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_USER_CANNOT_APPROVE')


async def test_copy(tap, api, dataset, now):
    with tap.plan(3, 'Пересечение с уже созданной'):

        store   = await dataset.store()
        user    = await dataset.user(store=store)

        time1 = datetime(2021, 1, 1, 0, 0, 0, tzinfo=tzone('UTC'))
        time3 = (
            now() + timedelta(days=10)
        ).replace(hour=0, minute=0, second=0, microsecond=0)
        time2 = time3 - timedelta(seconds=1)

        # Зона которая будет работать еще 10 дней
        zone1 = await dataset.zone(
            store=store,
            status='active',
            effective_from=time1,
            effective_till=time2,
        )
        # Зона которая начент работать через 10 дней
        zone2 = await dataset.zone(
            store=store,
            status='active',
            effective_from=time3,
            effective_till=None,
        )

        # Создали копию будущей зоны и отредактировали ее
        zone3   = await dataset.zone(
            store=store,
            status='template',
            effective_from=zone2.effective_from,
            effective_till=zone2.effective_till,
        )

        with user.role as role:
            role.add_permit('zones_approve', True)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_zones_approve',
                json={
                    'zone_id': zone3.zone_id,
                    'status': 'active',
                },
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_EXISTS')


@pytest.mark.parametrize(['timetable', 'zone'], [
    # -1 is for default
    (None, -1), (-1, []), (None, []),
])
async def test_zone_fill(tap, api, dataset, timetable, zone):
    with tap:
        store = await dataset.store()
        user1 = await dataset.user(store=store)
        user2 = await dataset.user(store=store)

        zone_params = {}
        if timetable != -1:
            zone_params['timetable'] = timetable
        if zone != -1:
            zone_params['zone'] = zone

        zone = await dataset.zone(
            store=store,
            status='template',
            users=[user1.user_id],
            **zone_params
        )

        t = await api(user=user2)
        await t.post_ok(
            'api_admin_zones_approve',
            json={
                'zone_id': zone.zone_id,
                'status': 'active',
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
