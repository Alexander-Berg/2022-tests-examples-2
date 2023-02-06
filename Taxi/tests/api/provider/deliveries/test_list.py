# pylint: disable=unused-variable


async def test_list(api, dataset, tap):
    with tap.plan(7, 'Список постаовк поставщика'):
        store1 = await dataset.store()
        await dataset.gate(store=store1, title='A1')

        store2 = await dataset.store()

        store3 = await dataset.store()

        provider1 = await dataset.provider(
            stores=[store1.store_id, store2.store_id, store3.store_id]
        )
        provider2 = await dataset.provider(
            stores=[store1.store_id, store2.store_id, store3.store_id]
        )

        delivery1_1 = await dataset.delivery(store=store1, provider=provider1)
        delivery1_2 = await dataset.delivery(store=store2, provider=provider1)
        delivery1_3 = await dataset.delivery(store=store3, provider=provider1)

        # Не будут в списках:
        # Не свои доставки
        await dataset.delivery(store=store1, provider=provider2)
        # Завершенные
        await dataset.delivery(
            store=store1, provider=provider1, status='canceled')

        user = await dataset.user(
            provider=provider1,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_deliveries_list',
        )
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
            provider1.provider_id,
            'Поставщик'
        )

        tap.eq(
            deliveries[delivery1_3.delivery_id]['provider_id'],
            provider1.provider_id,
            'Поставщик'
        )
