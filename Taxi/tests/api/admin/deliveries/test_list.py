# pylint: disable=unused-variable
from datetime import datetime, timezone, date


async def test_list(api, dataset, tap):
    with tap.plan(7, 'Список поставок склада'):
        store = await dataset.store()
        user  = await dataset.user(store=store)

        provider1 = await dataset.provider(stores=[store.store_id])
        provider2 = await dataset.provider(stores=[store.store_id])
        provider3 = await dataset.provider(stores=[])

        delivery1_1 = await dataset.delivery(store=store, provider=provider1)
        delivery1_2 = await dataset.delivery(store=store, provider=provider2)
        delivery1_3 = await dataset.delivery(
            store=store,
            provider=provider3,
            plan_date=datetime(3001, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        # Не показан по статусу
        await dataset.delivery(
            store=store, provider=provider1, status='complete')

        t = await api(user=user)
        await t.post_ok('api_admin_deliveries_list', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')

        deliveries = t.res['json']['deliveries']
        tap.eq(len(deliveries), 3, 'Только свои поставки')
        deliveries = dict((x['delivery_id'], x) for x in deliveries)

        tap.eq(
            deliveries[delivery1_1.delivery_id]['provider_id'],
            provider1.provider_id,
            'Поставщик'
        )

        tap.eq(
            deliveries[delivery1_2.delivery_id]['provider_id'],
            provider2.provider_id,
            'Поставщик'
        )

        tap.eq(
            deliveries[delivery1_3.delivery_id]['provider_id'],
            provider3.provider_id,
            'Поставщик'
        )


async def test_list_by_provider(api, dataset, tap):
    with tap.plan(6, 'Список поставок склада с фильтром по поставщику'):
        store = await dataset.store()
        user  = await dataset.user(store=store)

        provider1 = await dataset.provider(stores=[store.store_id])
        provider2 = await dataset.provider(stores=[store.store_id])

        delivery1 = await dataset.delivery(store=store, provider=provider1)
        delivery2 = await dataset.delivery(store=store, provider=provider2)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_deliveries_list',
            json={'provider_id': provider1.provider_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_is('deliveries.0.delivery_id', delivery1.delivery_id)
        t.json_is('deliveries.0.provider_id', provider1.provider_id)
        t.json_hasnt('deliveries.1')


async def test_list_by_plan_date(api, dataset, tap):
    with tap.plan(6, 'Список поставок склада с фильтром по поставщику'):
        store = await dataset.store()
        user  = await dataset.user(store=store)

        provider = await dataset.provider(stores=[store.store_id])

        delivery1 = await dataset.delivery(
            store=store,
            provider=provider,
            plan_date=date(2020, 11, 24),
        )
        delivery2 = await dataset.delivery(
            store=store,
            provider=provider,
            plan_date=date(2020, 11, 25),
        )
        delivery3 = await dataset.delivery(
            store=store,
            provider=provider,
            plan_date=None,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_deliveries_list',
            json={'plan_date': '2020-11-25'},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_is('deliveries.0.delivery_id', delivery2.delivery_id)
        t.json_is('deliveries.0.plan_date', '2020-11-25')
        t.json_hasnt('deliveries.1')
