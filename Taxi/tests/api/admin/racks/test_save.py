async def test_save_rack(tap, dataset, api):
    with tap.plan(10, 'изменяем стеллаж'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        rack = await dataset.rack(store_id=store.store_id, title='медвед')

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        t = await api()
        t.set_user(user)

        await t.post_ok(
            'api_admin_racks_save',
            json={
                'rack_id': rack.rack_id,
                'external_id': rack.external_id,
                'title': 'привет',
                'status': 'disabled',
                'capacity': 10,
                'warehouse_group': 'banany',
            })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('rack.title', 'привет', 'title')
        t.json_is('rack.status', 'disabled', 'status')
        t.json_is('rack.capacity', 10, 'capacity')
        t.json_is('rack.warehouse_group', 'banany', 'warehouse_group')


async def test_create_rack(tap, dataset, api, uuid):
    with tap.plan(10, 'создем стеллаж'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        rack_zone = await dataset.rack_zone(store_id=store.store_id)

        t = await api()
        t.set_user(user)

        await t.post_ok(
            'api_admin_racks_save',
            json={
                'external_id': uuid(),
                'title': 'привет',
                'status': 'disabled',
                'capacity': 10,
                'warehouse_group': 'banany',
                'rack_zone_id': rack_zone.rack_zone_id,
            })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('rack.title', 'привет', 'title')
        t.json_is('rack.status', 'disabled', 'status')
        t.json_is('rack.capacity', 10, 'capacity')
        t.json_is('rack.warehouse_group', 'banany', 'warehouse_group')


async def test_change_rack_zone(tap, dataset, api):
    with tap.plan(9, 'изменяем зону у стеллажа'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        rack = await dataset.rack(store_id=store.store_id)
        new_rack_zone = await dataset.rack_zone(store_id=store.store_id)

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        t = await api()
        t.set_user(user)

        await t.post_ok(
            'api_admin_racks_save',
            json={
                'rack_id': rack.rack_id,
                'rack_zone_id': new_rack_zone.rack_zone_id,
            })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is(
            'rack.rack_zone_id',
            new_rack_zone.rack_zone_id,
            'rack_zone_id',
        )
        rack = await dataset.Rack.load(rack.rack_id)
        tap.eq(rack.rack_zone_id, new_rack_zone.rack_zone_id, 'Зона изменена')
        tap.eq(rack.rack_zone_type, new_rack_zone.type, 'И тип тоже')


async def test_create_rack_no_title(tap, dataset, api, uuid):
    with tap.plan(6, 'создем стеллаж без названия'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        rack_zone = await dataset.rack_zone(store_id=store.store_id)

        t = await api()
        t.set_user(user)

        await t.post_ok(
            'api_admin_racks_save',
            json={
                'external_id': uuid(),
                'rack_zone_id': rack_zone.rack_zone_id,
            })
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')
