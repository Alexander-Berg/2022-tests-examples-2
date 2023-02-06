from datetime import timedelta
from libstall.util import time2iso_utc


async def test_save(tap, api, dataset, uuid, now):
    with tap.plan(20, 'Создание полигона'):

        effective_from = now() + timedelta(days=10)

        store   = await dataset.store()
        user1   = await dataset.user(store=store)
        user2   = await dataset.user(store=store)

        timetable1 = dataset.TimeTable([
            dataset.TimeTableItem({
                'type': 'monday',
                'begin': '12:00',
                'end': '13:59:59',
            })
        ])

        t = await api(user=user1)
        await t.post_ok(
            'api_admin_zones_save',
            json={
                'external_id': uuid(),
                'delivery_type': 'foot',
                'zone': {
                    'type': 'Feature',
                    'properties': {},
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [
                            [
                                [37.30, 55.60],
                                [37.90, 55.60],
                                [37.90, 55.80],
                                [37.30, 55.80],
                                [37.30, 55.60],
                            ],
                        ]
                    },
                },
                'effective_from': effective_from,
                'timetable': timetable1,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('zone')

        t.json_has('zone.zone_id')
        t.json_is('zone.status', 'template')
        t.json_has('zone.zone')
        t.json_is('zone.users', [user1.user_id])
        t.json_is('zone.effective_from', time2iso_utc(effective_from))
        t.json_is(
            'zone.timetable',
            timetable1,
        )

        zone_id         = t.res['json']['zone']['zone_id']
        effective_from  = now() + timedelta(days=20)
        timetable2 = dataset.TimeTable([
            dataset.TimeTableItem({
                'type': 'friday',
                'begin': '10:00',
                'end': '18:59:59',
            })
        ])

        t = await api(user=user2)
        await t.post_ok(
            'api_admin_zones_save',
            json={
                'zone_id': zone_id,
                'delivery_type': 'foot',
                'zone': {
                    'type': 'Feature',
                    'properties': {},
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [
                            [
                                [37.30, 55.60],
                                [37.90, 55.60],
                                [37.90, 55.80],
                                [37.30, 55.80],
                                [37.30, 55.60],
                            ],
                        ]
                    },
                },
                'effective_from': effective_from,
                'timetable': timetable2,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('zone')

        t.json_has('zone.zone_id')
        t.json_is('zone.status', 'template')
        t.json_has('zone.zone')
        t.json_is('zone.users', [user1.user_id, user2.user_id])
        t.json_is('zone.effective_from', time2iso_utc(effective_from))
        t.json_is(
            'zone.timetable',
            timetable2,
        )


async def test_read_only(tap, api, dataset):
    with tap.plan(3, 'После активации становится только для чтения'):

        store   = await dataset.store()
        user    = await dataset.user(store=store)
        zone    = await dataset.zone(store=store, status='active')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_save',
            json={
                'zone_id': zone.zone_id,
                'delivery_type': 'foot',
                'zone': {
                    'type': 'Feature',
                    'properties': {},
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [
                            [
                                [37.30, 55.60],
                                [37.90, 55.60],
                                [37.90, 55.80],
                                [37.30, 55.80],
                                [37.30, 55.60],
                            ],
                        ]
                    },
                },
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_READONLY_AFTER_CREATE')
