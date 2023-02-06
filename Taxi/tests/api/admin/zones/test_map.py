# pylint: disable=unused-variable

from datetime import timedelta

import pytest


@pytest.mark.parametrize('test_data', [
    {
        'box': [[66.2, 33.2], [66.5, 33.5]],
        'zone': [[{'lon': 66.0, 'lat': 33.0},  # без location
                  {'lon': 66.0, 'lat': 33.5},
                  {'lon': 66.5, 'lat': 33.0},
                  {'lon': 66.0, 'lat': 33.0}]]},
    {
        'box': [[66.2, 33.2], [66.5, 33.5]],
        'zone': [[{'lon': 66.0, 'lat': 33.0},  # с разрезом (pacman)
                  {'lon': 66.0, 'lat': 33.5},
                  {'lon': 66.5, 'lat': 33.0},
                  {'lon': 66.0, 'lat': 33.0}]]},
    {
        'box': [[66.11, 33.06], [66.12, 33.07]],
        'zone': [[{'lon': 66.12, 'lat': 33.06},  # с разрезом (pacman)
                  {'lon': 66.09, 'lat': 33.06},
                  {'lon': 66.09, 'lat': 33.09},
                  {'lon': 66.12, 'lat': 33.09},
                  {'lon': 66.12, 'lat': 33.06}]]},
    {
        'box': [[-179.11, -89.06], [-179.12, -89.07]],
        'zone': [[{'lon': -179.12, 'lat': -89.06},
                  {'lon': -179.09, 'lat': -89.06},
                  {'lon': -179.09, 'lat': -89.09},
                  {'lon': -179.12, 'lat': -89.09},
                  {'lon': -179.12, 'lat': -89.06}]]},
    {
        'box': [[66.2, 33.2], [66.5, 33.5]],
        'zone': [[{'lon': 66.0, 'lat': 33.0},   # multipolygon
                  {'lon': 66.0, 'lat': 33.5},   # 1-ый полигон
                  {'lon': 66.5, 'lat': 33.0},   # пересекает box;
                  {'lon': 66.0, 'lat': 33.0}],
                 [{'lon': 66.3, 'lat': 33.6},   # 2-ой полигон
                  {'lon': 66.4, 'lat': 33.6},   # не пересекает box
                  {'lon': 66.3, 'lat': 33.7},
                  {'lon': 66.3, 'lat': 33.6}]]},
    {
        'box': [[66.11, 33.06], [66.12, 33.07]],
        'zone': [[{'lon': 66.7, 'lat': 33.1},    # multipolygon
                  {'lon': 66.8, 'lat': 33.1},    # 1-ый полигон
                  {'lon': 66.7, 'lat': 33.2},    # не пересекает box
                  {'lon': 66.7, 'lat': 33.1}],
                 [{'lon': 66.12, 'lat': 33.06},  # 2-ой полигон
                  {'lon': 66.09, 'lat': 33.06},  # пересекает box
                  {'lon': 66.09, 'lat': 33.09},
                  {'lon': 66.12, 'lat': 33.09},
                  {'lon': 66.12, 'lat': 33.06}]]},
])
async def test_list_box(tap, api, dataset, test_data, now):
    with tap.plan(5):
        store   = await dataset.store()
        zone    = await dataset.zone(
            store=store,
            zone=test_data['zone'],
            effective_from=now() - timedelta(days=1),
        )
        user    = await dataset.user(store=store)

        with user.role as role:
            # Чтобы не искала по всей базе ограничим одним складом
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_zones_map',
                json={
                    'box': {
                        'type': 'MultiPoint',
                        'coordinates': test_data['box'],
                    },
                    'now': now(),
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('zones.0.zone_id', zone.zone_id)
            t.json_hasnt('zones.1')


async def test_over_permit_out_store(tap, api, dataset, now):
    box = [[66.2, 33.2], [66.5, 33.5]]
    zone = [[{'lon': 66.0, 'lat': 33.0},
             {'lon': 66.0, 'lat': 33.5},
             {'lon': 66.5, 'lat': 33.0},
             {'lon': 66.0, 'lat': 33.0}]]

    with tap.plan(8, 'Чужая лавка'):
        company1 = await dataset.company()

        store1 = await dataset.store(company=company1)
        store2 = await dataset.store(company=company1)

        user = await dataset.user(role='admin', store=store1)
        zone = await dataset.zone(
            store=store2,
            zone=zone,
            effective_from=now() - timedelta(days=1)
        )

        t = await api(user=user)
        with user.role as role:
            role.remove_permit('out_of_store')

            await t.post_ok('api_admin_zones_map',
                            json={
                                'box': {
                                    'type': 'MultiPoint',
                                    'coordinates': box,
                                },
                                'now': now(),
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            zone_id = [z['zone_id'] for z in t.res['json']['zones']]
            tap.not_in_ok(zone.zone_id, zone_id, 'зона нашлась')

        with user.role:
            await t.post_ok('api_admin_zones_map',
                            json={
                                'box': {
                                    'type': 'MultiPoint',
                                    'coordinates': box,
                                },
                                'now': now(),
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            zone_id = [z['zone_id'] for z in t.res['json']['zones']]
            tap.in_ok(zone.zone_id, zone_id, 'зона нашлась')


async def test_over_permit_out_company(tap, api, dataset, now):
    box = [[66.2, 33.2], [66.5, 33.5]]
    zone = [[{'lon': 66.0, 'lat': 33.0},
             {'lon': 66.0, 'lat': 33.5},
             {'lon': 66.5, 'lat': 33.0},
             {'lon': 66.0, 'lat': 33.0}]]

    with tap.plan(12, 'Чужая компания'):
        store1 = await dataset.store()
        store2 = await dataset.store()

        user = await dataset.user(role='admin', company=store1)
        zone = await dataset.zone(
            store=store2,
            zone=zone,
            effective_from=now() - timedelta(days=1)
        )

        t = await api(user=user)
        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            await t.post_ok('api_admin_zones_map',
                            json={
                                'box': {
                                    'type': 'MultiPoint',
                                    'coordinates': box,
                                },
                                'now': now(),
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            zone_id = [z['zone_id'] for z in t.res['json']['zones']]
            tap.not_in_ok(zone.zone_id, zone_id, 'зона нашлась')

        with user.role as role:
            role.remove_permit('out_of_company')

            await t.post_ok('api_admin_zones_map',
                            json={
                                'box': {
                                    'type': 'MultiPoint',
                                    'coordinates': box,
                                },
                                'now': now(),
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            zone_id = [z['zone_id'] for z in t.res['json']['zones']]
            tap.not_in_ok(zone.zone_id, zone_id, 'зона нашлась')

        with user.role:
            await t.post_ok('api_admin_zones_map',
                            json={
                                'box': {
                                    'type': 'MultiPoint',
                                    'coordinates': box,
                                },
                                'now': now(),
                            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            zone_id = [z['zone_id'] for z in t.res['json']['zones']]
            tap.in_ok(zone.zone_id, zone_id, 'зона нашлась')
