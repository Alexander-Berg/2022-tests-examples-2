import pytest


@pytest.mark.parametrize('role', ['admin'])
async def test_load(api, dataset, tap, role):
    with tap.plan(7, 'Получение одной записи'):
        store = await dataset.store()
        zone  = await dataset.zone(store=store)

        t = await api(role=role)
        await t.post_ok(
            'api_admin_zones_load',
            json={'zone_id': zone.zone_id},
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('zone.zone_id', zone.zone_id)
        t.json_is('zone.store_id', zone.store_id)
        t.json_is('zone.company_id', zone.company_id)
        t.json_is('zone.status', zone.status)


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5, 'Получение списка записей'):
        store = await dataset.store()
        zone1 = await dataset.zone(store=store)
        zone2 = await dataset.zone(store=store)

        t = await api(role=role)
        await t.post_ok(
            'api_admin_zones_load',
            json={'zone_id': [zone1.zone_id, zone2.zone_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('zone')

        res = t.res['json']['zone']
        tap.eq_ok(
            sorted([x.get('zone_id') for x in res]),
            sorted([zone1.zone_id, zone2.zone_id]),
            'Записи получены'
        )


@pytest.mark.parametrize('role', ['admin'])
async def test_load_not_found(api, dataset, tap, uuid, role):
    with tap.plan(8):
        t = await api(role=role)

        with tap.subtest(None, 'Одна запись'):
            await t.post_ok(
                'api_admin_zones_load',
                json={'zone_id': uuid()},
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

        with tap.subtest(None, 'Список'):
            store = await dataset.store()
            zone  = await dataset.zone(store=store)
            await t.post_ok(
                'api_admin_zones_load',
                json={'zone_id': [zone.zone_id, uuid()]},
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


async def test_over_permit_out_store(tap, api, dataset):
    with tap.plan(6, 'Чужая лавка'):
        company = await dataset.company()

        store1 = await dataset.store(company=company)
        store2 = await dataset.store(company=company)

        user = await dataset.user(role='admin', store=store1)
        zone = await dataset.zone(store=store2)

        t = await api(user=user)
        with user.role as role:
            role.remove_permit('out_of_store')

            await t.post_ok('api_admin_zones_load',
                            json={'zone_id': zone.zone_id})
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

        with user.role:
            await t.post_ok('api_admin_zones_load',
                            json={'zone_id': zone.zone_id})
            t.status_is(200, diag=True)
            t.json_is('zone.zone_id', zone.zone_id)


async def test_over_permit_out_company(tap, api, dataset):
    with tap.plan(9, 'Чужая компания'):
        store1 = await dataset.store()
        store2 = await dataset.store()

        user = await dataset.user(role='admin', company=store1)
        zone = await dataset.zone(store=store2)

        t = await api(user=user)
        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            await t.post_ok('api_admin_zones_load',
                            json={'zone_id': zone.zone_id})
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

        with user.role as role:
            role.remove_permit('out_of_company')

            await t.post_ok('api_admin_zones_load',
                            json={'zone_id': zone.zone_id})
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

        with user.role:
            await t.post_ok('api_admin_zones_load',
                            json={'zone_id': zone.zone_id})
            t.status_is(200, diag=True)
            t.json_is('zone.zone_id', zone.zone_id)
