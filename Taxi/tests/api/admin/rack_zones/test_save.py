async def test_save_rack_zone(tap, dataset, api):
    with tap.plan(9, 'изменяем зону'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        rack_zone = await dataset.rack_zone(
            store_id=store.store_id,
            title='медвед',
        )

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        t = await api()
        t.set_user(user)

        await t.post_ok(
            'api_admin_rack_zones_save',
            json={
                'rack_zone_id': rack_zone.rack_zone_id,
                'title': 'привет',
                'status': 'disabled',
                'type': 'shipment',
            })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('rack.title', 'привет', 'title')
        t.json_is('rack.status', 'disabled', 'status')
        t.json_is('rack.type', 'shipment', 'type')


async def test_create_rack_zone(tap, dataset, api, uuid):
    with tap.plan(9, 'создаем зону'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        t = await api()
        t.set_user(user)

        await t.post_ok(
            'api_admin_rack_zones_save',
            json={
                'external_id': uuid(),
                'title': 'привет',
                'status': 'disabled',
                'type': 'shipment',
            })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('rack.title', 'привет', 'title')
        t.json_is('rack.status', 'disabled', 'status')
        t.json_is('rack.type', 'shipment', 'type')
