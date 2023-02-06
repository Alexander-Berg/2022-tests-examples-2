async def test_simple(tap, dataset, api):
    with tap.plan(9, 'Завершение саджеста по взятию груза'):
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
            type='take_cargo',
            shelf_id=cargo.shelf_id,
        )
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_done_take_cargo',
            json={'suggest_id': suggest.suggest_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Suggest was done.')
        t.json_is('suggests.0.suggest_id', suggest.suggest_id)
        t.json_is('suggests.0.status', 'done')

        tap.ok(await suggest.reload(), 'саджест перегружен')
        tap.eq(suggest.status, 'done', 'саджест завершён')
        tap.eq_ok(suggest.user_done, user.user_id, 'user_done')


async def test_error(tap, dataset, api):
    with tap.plan(3, 'Взятия груза в ошибку'):
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
            type='take_cargo',
            shelf_id=cargo.shelf_id,
        )
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_done_take_cargo',
            json={
                'suggest_id': suggest.suggest_id,
                'status': 'error'
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')
