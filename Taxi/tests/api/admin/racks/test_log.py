async def test_log_by_rack_id(tap, dataset, api):
    with tap.plan(12, 'Запрос за логами стеллажа'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        admin = await dataset.user(store=store)
        tap.eq(admin.store_id, store.store_id, 'Админ создан')

        rack = await dataset.rack(store_id=store.store_id)

        order = await dataset.order()
        tap.ok(
            await rack.do_reserve(order=order, user_id=admin.user_id),
            'Сделали резерв места на стеллаже'
        )

        t = await api(user=admin)

        await t.post_ok('api_admin_racks_log',
                        json={'rack_id': rack.rack_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('racks_log.0.rack_id', rack.rack_id)

        t.json_has('racks_log.0.log_id')
        t.json_has('racks_log.0.order_id')
        t.json_has('racks_log.0.order_type')

        t.json_hasnt('racks_log.1')


async def test_log_by_shelf_id(tap, dataset, api):
    with tap.plan(14, 'Запрос за логами стеллажа'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        admin = await dataset.user(store=store)
        tap.eq(admin.store_id, store.store_id, 'Админ создан')

        rack = await dataset.rack(store_id=store.store_id)
        shelf = await dataset.shelf(type='cargo', store_id=rack.store_id)
        order = await dataset.order(store_id=rack.store_id)

        tap.ok(
            await rack.do_reserve(order=order),
            'Сделали резерв места на стеллаже'
        )

        tap.ok(
            await rack.do_link_cargo(cargo=shelf, order=order),
            'Добавили связь'
        )

        t = await api(user=admin)

        await t.post_ok('api_admin_racks_log',
                        json={'shelf_id': shelf.shelf_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('racks_log.0.shelf_id', shelf.shelf_id)
        t.json_is('racks_log.0.rack_id', rack.rack_id)

        t.json_has('racks_log.0.log_id')
        t.json_has('racks_log.0.order_id')
        t.json_has('racks_log.0.order_type')

        t.json_hasnt('racks_log.1')
