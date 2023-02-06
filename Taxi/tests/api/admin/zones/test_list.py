# pylint: disable=unused-variable
from datetime import datetime, timezone

# NOTE: при создании dataset.store автоматически создается зона


async def test_list_empty(api, dataset, tap):
    with tap.plan(4):
        store   = await dataset.store()
        user    = await dataset.user(store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_list',
            json={'store_id': store.store_id,
                  'status': ['template'],
                  },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('zones', [])


async def test_list_nonempty(api, dataset, tap):
    with tap.plan(10, 'Список отсортированный по дате начала действия'):

        store1   = await dataset.store()
        store2   = await dataset.store()

        user    = await dataset.user(store=store1)

        zone1   = await dataset.zone(
            store=store1,
            effective_from='2021-02-01',
        )
        zone2   = await dataset.zone(
            store=store1,
            effective_from='2021-01-01',
        )
        zone3   = await dataset.zone(
            store=store2,
            effective_from='2021-01-01',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_list',
            json={'store_id': store1.store_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('zones')
        t.json_has('zones.0')
        t.json_is('zones.0.zone_id', zone2.zone_id, 'сортировано')
        t.json_has('zones.1')
        t.json_is('zones.1.zone_id', zone1.zone_id, 'сортировано')
        t.json_has('zones.2', 'только свои')
        t.json_hasnt('zones.3', 'только свои')


async def test_list_array(api, dataset, tap):
    with tap.plan(11, 'Список складов'):

        store1   = await dataset.store()
        store2   = await dataset.store()

        user    = await dataset.user(store=store1)

        zone1   = await dataset.zone(
            store=store1,
            effective_from='2021-02-01',
        )
        zone2   = await dataset.zone(
            store=store1,
            effective_from='2021-01-01',
        )
        zone3   = await dataset.zone(
            store=store2,
            effective_from='2021-03-01',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_list',
            json={'store_id': [store1.store_id, store2.store_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('zones')
        t.json_has('zones.0')
        t.json_is('zones.0.zone_id', zone2.zone_id, 'сортировано')
        t.json_has('zones.1')
        t.json_is('zones.1.zone_id', zone1.zone_id, 'сортировано')
        t.json_has('zones.2')
        t.json_is('zones.2.zone_id', zone3.zone_id, 'сортировано')
        # еще 2 создаются по умолчанию
        t.json_hasnt('zones.5', 'только указанные')


async def test_status(api, dataset, tap):
    with tap.plan(27, 'Фильтр по статусу'):

        store   = await dataset.store()
        user    = await dataset.user(store=store)

        zone1   = await dataset.zone(
            store=store,
            status='template',
            effective_from='2021-01-01',
        )
        zone2   = await dataset.zone(
            store=store,
            status='active',
            effective_from='2021-01-02',
        )
        zone3   = await dataset.zone(
            store=store,
            status='disabled',
            effective_from='2021-01-03',
        )

        # Фильтр строкой
        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_list',
            json={
                'store_id': store.store_id,
                'status': 'active',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('zones')
        t.json_has('zones.0')
        t.json_is('zones.0.zone_id', zone2.zone_id)
        t.json_hasnt('zones.2')

        # Фильтр списком
        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_list',
            json={
                'store_id': store.store_id,
                'status': ['active', 'template'],
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('zones')
        t.json_has('zones.0')
        t.json_is('zones.0.zone_id', zone1.zone_id)
        t.json_has('zones.1')
        t.json_is('zones.1.zone_id', zone2.zone_id)
        t.json_hasnt('zones.3')

        # Фильтр с пустым массивом отдаст все
        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_list',
            json={
                'store_id': store.store_id,
                'status': [],
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('zones')
        t.json_has('zones.0')
        t.json_is('zones.0.zone_id', zone1.zone_id)
        t.json_has('zones.1')
        t.json_is('zones.1.zone_id', zone2.zone_id)
        t.json_has('zones.2')
        t.json_is('zones.2.zone_id', zone3.zone_id)
        t.json_hasnt('zones.4')


async def test_delivery_type(api, dataset, tap):
    with tap.plan(7, 'Фильтр по типу'):

        store   = await dataset.store()
        user    = await dataset.user(store=store)

        zone1   = await dataset.zone(
            store=store,
            status='active',
            effective_from='2021-01-01',
            delivery_type='foot',
        )
        zone2   = await dataset.zone(
            store=store,
            status='active',
            effective_from='2021-01-02',
            delivery_type='rover',
        )

        # Фильтр строкой
        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_list',
            json={
                'store_id': store.store_id,
                'delivery_type': 'foot',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('zones')
        t.json_has('zones.0')
        t.json_is('zones.0.zone_id', zone1.zone_id)
        t.json_hasnt('zones.2')


async def test_now(api, dataset, tap):
    with tap.plan(7, 'Фильтр получения только текущих'):

        store   = await dataset.store()
        user    = await dataset.user(store=store)

        zone   = await dataset.zone(
            store=store,
            status='active',
            effective_from=datetime(2021, 1, 1, tzinfo=timezone.utc),
            effective_till=datetime(2021, 1, 31, 23, 59,
                                    59, tzinfo=timezone.utc),
            delivery_type='foot',
        )
        zone_future = await dataset.zone(
            store=store,
            status='active',
            effective_from=datetime(2021, 2, 1, tzinfo=timezone.utc),
            delivery_type='foot',
        )
        zone_past = await dataset.zone(
            store=store,
            status='active',
            effective_from=datetime(2020, 1, 1, tzinfo=timezone.utc),
            effective_till=datetime(
                2020, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
            delivery_type='foot',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_zones_list',
            json={
                'store_id': store.store_id,
                'now': datetime(2021, 1, 15, tzinfo=timezone.utc),
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('zones')
        t.json_has('zones.0')
        t.json_is('zones.0.zone_id', zone.zone_id)
        t.json_hasnt('zones.1')


async def test_list_store_fail(api, dataset, tap):
    with tap.plan(6, 'Нельзя получать не свои'):
        store1  = await dataset.store()
        store2  = await dataset.store()
        user    = await dataset.user(store=store1)

        with user.role as role:
            role.add_permit('out_of_store', True)
            role.add_permit('out_of_company', True)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_zones_list',
                json={'store_id': store2.store_id},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_zones_list',
                json={'store_id': store2.store_id},
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')
