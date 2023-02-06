async def test_simple(tap, dataset, api):
    with tap.plan(10, 'Завершение саджеста положить груз'):
        user = await dataset.user()
        rack = await dataset.rack(store_id=user.store_id)
        new_rack = await dataset.rack(store_id=user.store_id)
        cargo = await dataset.shelf(
            store_id=user.store_id,
            rack_id=rack.rack_id,
            type='cargo'
        )
        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
            type='cargo_move',
            required=[{
                'shelf_id': cargo.shelf_id,
                'dst_rack_id': new_rack.rack_id
            }],
        )
        suggest = await dataset.suggest(
            order=order,
            count=None,
            type='put_cargo',
            shelf_id=cargo.shelf_id,
            rack_id=new_rack.rack_id,
        )
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_done_put_cargo',
            json={'suggest_id': suggest.suggest_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Suggest was done.')
        t.json_is('suggests.0.suggest_id', suggest.suggest_id)
        t.json_is('suggests.0.status', 'done')

        tap.ok(await suggest.reload(), 'саджест перегружен')
        tap.eq(suggest.status, 'done', 'саджест завершён')
        tap.eq(suggest.user_done, user.user_id, 'user_done')
        tap.eq(suggest.result_rack_id, new_rack.rack_id, 'Стеллаж тот')


async def test_reserve(tap, dataset, api):
    with tap.plan(7, 'Положили груз и взяли резерв'):
        user = await dataset.user()
        rack = await dataset.rack(store_id=user.store_id)
        new_rack = await dataset.rack(store_id=user.store_id)
        cargo = await dataset.shelf(
            store_id=user.store_id,
            rack_id=rack.rack_id,
            type='cargo'
        )
        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
            type='cargo_move',
            required=[{
                'shelf_id': cargo.shelf_id,
                'dst_rack_id': new_rack.rack_id
            }],
        )
        suggest = await dataset.suggest(
            order=order,
            count=None,
            type='put_cargo',
            shelf_id=cargo.shelf_id,
        )
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_done_put_cargo',
            json={
                'suggest_id': suggest.suggest_id,
                'rack_id': new_rack.rack_id,
                'status': 'done',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.ok(await suggest.reload(), 'саджест перегружен')
        tap.eq(suggest.result_rack_id, new_rack.rack_id, 'Стеллаж тот')

        racks = await dataset.Rack.list_by_order(order=order)
        tap.eq(len(racks), 1, 'Один стеллаж')
        reserved_rack = racks[0]
        tap.eq(reserved_rack.rack_id, new_rack.rack_id, 'Появился резерв')


async def test_zone(tap, dataset, api):
    with tap.plan(7, 'Положили груз в зону'):
        user = await dataset.user()
        rack = await dataset.rack(store_id=user.store_id)
        cargo = await dataset.shelf(
            store_id=user.store_id,
            rack_id=rack.rack_id,
            type='cargo'
        )
        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
            type='cargo_move',
            required=[{
                'shelf_id': cargo.shelf_id,
                'dst_rack_zone_id': rack.rack_zone_id
            }],
        )
        suggest = await dataset.suggest(
            order=order,
            count=None,
            type='put_cargo',
            shelf_id=cargo.shelf_id,
            rack_zone_id=rack.rack_zone_id,
            conditions={'need_rack': True},
        )
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_done_put_cargo',
            json={
                'suggest_id': suggest.suggest_id,
                'rack_id': rack.rack_id,
                'status': 'done',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.ok(await suggest.reload(), 'саджест перегружен')
        tap.eq(suggest.result_rack_id, rack.rack_id, 'Стеллаж тот')
        racks = await dataset.Rack.list_by_order(order=order)
        tap.eq(len(racks), 1, 'Один стеллаж')
        reserved_rack = racks[0]
        tap.eq(reserved_rack.rack_id, rack.rack_id, 'Появился резерв')


async def test_error(tap, dataset, api):
    with tap.plan(7, 'Взятие груза в ошибку LIKE_RACK'):
        user = await dataset.user()
        rack = await dataset.rack(store_id=user.store_id)
        new_rack = await dataset.rack(store_id=user.store_id)
        cargo = await dataset.shelf(
            store_id=user.store_id,
            rack_id=rack.rack_id,
            type='cargo'
        )
        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
            type='cargo_move',
            required=[{
                'shelf_id': cargo.shelf_id,
                'dst_rack_id': rack.rack_id
            }],
        )
        suggest = await dataset.suggest(
            order=order,
            count=None,
            type='put_cargo',
            shelf_id=cargo.shelf_id,
            rack_id=rack.rack_id,
        )
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_done_put_cargo',
            json={
                'suggest_id': suggest.suggest_id,
                'status': 'error',
                'reason': {
                    'code': 'LIKE_RACK',
                    'rack_id': new_rack.rack_id,
                }
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.ok(await suggest.reload(), 'саджест перегружен')
        tap.eq(suggest.status, 'error', 'саджест в ошибке')
        tap.eq(suggest.user_done, user.user_id, 'user_done')
        tap.eq(
            suggest.reason.rack_id,
            new_rack.rack_id,
            'Стеллаж тот в причине'
        )


async def test_wrong_order_status(tap, dataset, api):
    with tap.plan(3, 'Заказ не в том статусе'):
        user = await dataset.user()
        rack = await dataset.rack(store_id=user.store_id)
        new_rack = await dataset.rack(store_id=user.store_id)
        cargo = await dataset.shelf(
            store_id=user.store_id,
            rack_id=rack.rack_id,
            type='cargo'
        )
        order = await dataset.order(
            status='processing',
            estatus='begin',
            store_id=user.store_id,
            users=[user.user_id],
            type='cargo_move',
            required=[{
                'shelf_id': cargo.shelf_id,
                'dst_rack_id': new_rack.rack_id
            }],
        )
        suggest = await dataset.suggest(
            order=order,
            count=None,
            type='put_cargo',
            shelf_id=cargo.shelf_id,
            rack_id=new_rack.rack_id,
        )
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_done_put_cargo',
            json={'suggest_id': suggest.suggest_id}
        )
        t.status_is(423, diag=True)
        t.json_is('code', 'ER_LOCKED')


async def test_no_rack_id(tap, dataset, api):
    with tap.plan(3, 'Нужен стеллаж'):
        user = await dataset.user()
        rack = await dataset.rack(store_id=user.store_id)
        new_rack = await dataset.rack(store_id=user.store_id)
        cargo = await dataset.shelf(
            store_id=user.store_id,
            rack_id=rack.rack_id,
            type='cargo'
        )
        order = await dataset.order(
            status='processing',
            estatus='begin',
            store_id=user.store_id,
            users=[user.user_id],
            type='cargo_move',
            required=[{
                'shelf_id': cargo.shelf_id,
                'dst_rack_id': new_rack.rack_id
            }],
        )
        suggest = await dataset.suggest(
            order=order,
            count=None,
            type='put_cargo',
            shelf_id=cargo.shelf_id,
            conditions={'need_rack': True}
        )
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_done_put_cargo',
            json={'suggest_id': suggest.suggest_id}
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_RACK_REQUIRED')


async def test_wrong_rack_id(tap, dataset, api):
    with tap.plan(3, 'Не тот стеллаж'):
        user = await dataset.user()
        rack = await dataset.rack(store_id=user.store_id)
        new_rack = await dataset.rack(store_id=user.store_id)
        cargo = await dataset.shelf(
            store_id=user.store_id,
            rack_id=rack.rack_id,
            type='cargo'
        )
        order = await dataset.order(
            status='processing',
            estatus='begin',
            store_id=user.store_id,
            users=[user.user_id],
            type='cargo_move',
            required=[{
                'shelf_id': cargo.shelf_id,
                'dst_rack_id': rack.rack_id
            }],
        )
        suggest = await dataset.suggest(
            order=order,
            count=None,
            type='put_cargo',
            shelf_id=cargo.shelf_id,
            rack_id=rack.rack_id,
            conditions={'need_rack': True}
        )
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_done_put_cargo',
            json={
                'suggest_id': suggest.suggest_id,
                'rack_id': new_rack.rack_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_WRONG_RACK')


async def test_wrong_zone(tap, dataset, api):
    with tap.plan(3, 'Положили груз не в ту зону'):
        user = await dataset.user()
        rack = await dataset.rack(store_id=user.store_id)
        new_rack = await dataset.rack(store_id=user.store_id)
        cargo = await dataset.shelf(
            store_id=user.store_id,
            rack_id=rack.rack_id,
            type='cargo'
        )
        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
            type='cargo_move',
            required=[{
                'shelf_id': cargo.shelf_id,
                'dst_rack_zone_id': rack.rack_zone_id
            }],
        )
        suggest = await dataset.suggest(
            order=order,
            count=None,
            type='put_cargo',
            shelf_id=cargo.shelf_id,
            rack_zone_id=rack.rack_zone_id,
            conditions={'need_rack': True},
        )
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_done_put_cargo',
            json={
                'suggest_id': suggest.suggest_id,
                'rack_id': new_rack.rack_id,
                'status': 'done',
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_WRONG_RACK')


async def test_rack_full(tap, dataset, api):
    with tap.plan(3, 'Положили груз и не хватило места'):
        user = await dataset.user()
        rack = await dataset.rack(store_id=user.store_id)
        cargo = await dataset.shelf(
            store_id=user.store_id,
            rack_id=rack.rack_id,
            type='cargo'
        )
        new_rack = await dataset.rack(store_id=user.store_id, capacity=1)
        await dataset.shelf(
            store_id=user.store_id,
            rack_id=new_rack.rack_id,
            type='cargo'
        )
        order = await dataset.order(
            status='processing',
            estatus='waiting',
            store_id=user.store_id,
            users=[user.user_id],
            type='cargo_move',
            required=[{
                'shelf_id': cargo.shelf_id,
                'dst_rack_id': new_rack.rack_id
            }],
        )
        suggest = await dataset.suggest(
            order=order,
            count=None,
            type='put_cargo',
            shelf_id=cargo.shelf_id,
        )
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_done_put_cargo',
            json={
                'suggest_id': suggest.suggest_id,
                'rack_id': new_rack.rack_id,
                'status': 'done',
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_FULL_RACK')
