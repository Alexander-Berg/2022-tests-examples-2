async def test_simple(tap, dataset, wait_order_status):
    with tap.plan(16, 'Все идет по плану по стеллажу'):
        store = await dataset.store(type='dc')
        user = await dataset.user(store_id=store.store_id)
        rack = await dataset.rack(store_id=store.store_id)
        cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo',
        )
        new_rack = await dataset.rack(store_id=store.store_id)

        order = await dataset.order(
            store=store,
            type='cargo_move',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': cargo.shelf_id,
                    'dst_rack_id': new_rack.rack_id,
                }
            ],
            acks=[user.user_id]
        )
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дотолкали ордер до processing'
        )
        suggests = await dataset.Suggest.list_by_order(
            order=order, status='request')
        tap.eq(len(suggests), 1, 'Саджест только один')
        suggest = suggests[0]
        tap.eq(suggest.type, 'take_cargo', 'Саджест взять груз')
        tap.ok(
            await suggest.done(user=user),
            'Закрыли саджест'
        )
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дотолкали ордер снова'
        )
        suggests = await dataset.Suggest.list_by_order(
            order=order, status='request')
        tap.eq(len(suggests), 1, 'Саджест только один')
        suggest = suggests[0]
        tap.eq(suggest.rack_id, new_rack.rack_id, 'Стеллаж тот в саджесте')
        tap.eq(suggest.rack_zone_id, None, 'Зоны нет в стеллаже')
        tap.eq(
            suggest.conditions.need_rack,
            False,
            'Стеллаж не нужно сканировать'
        )
        tap.eq(suggest.type, 'put_cargo', 'Саджест положить груз')
        tap.ok(await suggest.done(user=user), 'Закрыли саджест')
        tap.ok(
            await order.done(target='complete', user=user),
            'Закрыли документ'
        )
        tap.ok(
            await wait_order_status(order, ('complete', 'done')),
            'Дотолкали ордер до конца'
        )


async def test_rack_zone(tap, dataset, wait_order_status):
    with tap.plan(17, 'Все идет по плану по зоне'):
        store = await dataset.store(type='dc')
        user = await dataset.user(store_id=store.store_id)
        rack = await dataset.rack(store_id=store.store_id)
        cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo',
        )
        new_rack = await dataset.rack(store_id=store.store_id)

        order = await dataset.order(
            store=store,
            type='cargo_move',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': cargo.shelf_id,
                    'dst_rack_zone_id': new_rack.rack_zone_id,
                }
            ],
            acks=[user.user_id]
        )
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дотолкали ордер до processing'
        )
        suggests = await dataset.Suggest.list_by_order(
            order=order, status='request')
        tap.eq(len(suggests), 1, 'Саджест только один')
        suggest = suggests[0]
        tap.eq(suggest.type, 'take_cargo', 'Саджест взять груз')
        tap.ok(await suggest.done(user=user), 'Закрыли саджест')
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дотолкали ордер снова'
        )
        suggests = await dataset.Suggest.list_by_order(
            order=order, status='request')
        tap.eq(len(suggests), 1, 'Саджест только один')
        suggest = suggests[0]
        tap.eq(suggest.rack_id, None, 'Стеллажа нет')
        tap.eq(
            suggest.rack_zone_id,
            new_rack.rack_zone_id,
            'Стеллажная зона та самая'
        )
        tap.eq(
            suggest.conditions.need_rack,
            True,
            'Стеллаж нужно сканировать'
        )
        tap.eq(suggest.type, 'put_cargo', 'Саджест положить груз')
        with tap.raises(suggest.ErSuggestRackRequired):
            await suggest.done(user=user)
        tap.ok(
            await suggest.done(user=user, rack_id=new_rack.rack_id),
            'Закрыли саджест'
        )
        tap.ok(
            await order.done(target='complete', user=user),
            'Закрыли документ'
        )
        tap.ok(
            await wait_order_status(order, ('complete', 'done')),
            'Дотолкали ордер до конца'
        )


async def test_change_target_rack(tap, dataset, wait_order_status):
    with tap.plan(22, 'Меняем целевой стеллаж'):
        store = await dataset.store(type='dc')
        user = await dataset.user(store_id=store.store_id)
        rack = await dataset.rack(store_id=store.store_id)
        cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo',
        )
        new_rack = await dataset.rack(store_id=store.store_id)
        another_rack = await dataset.rack(
            store_id=store.store_id,
            rack_zone_id=new_rack.rack_zone_id
        )

        order = await dataset.order(
            store=store,
            type='cargo_move',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': cargo.shelf_id,
                    'dst_rack_id': new_rack.rack_id,
                }
            ],
            acks=[user.user_id]
        )
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дотолкали ордер до processing'
        )
        suggests = await dataset.Suggest.list_by_order(
            order=order, status='request')
        tap.eq(len(suggests), 1, 'Саджест только один')
        suggest = suggests[0]
        tap.eq(suggest.type, 'take_cargo', 'Саджест взять груз')
        tap.ok(await suggest.done(user=user), 'Закрыли саджест')
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дотолкали ордер снова'
        )
        suggests = await dataset.Suggest.list_by_order(
            order=order, status='request')
        tap.eq(len(suggests), 1, 'Саджест только один')
        suggest = suggests[0]
        tap.eq(suggest.rack_id, new_rack.rack_id, 'Стеллаж старый')
        tap.eq(
            suggest.rack_zone_id,
            None,
            'Стеллажной зоны нет'
        )
        tap.eq(suggest.type, 'put_cargo', 'Саджест положить груз')
        tap.ok(
            await suggest.done(user=user, status='error', reason={
                'code': 'LIKE_RACK',
                'rack_id': another_rack.rack_id
            }),
            'Закрыли саджест в ошибку'
        )
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дотолкали ордер снова'
        )
        suggests = await dataset.Suggest.list_by_order(
            order=order, status='request')
        tap.eq(len(suggests), 1, 'Саджест только один')
        new_suggest = suggests[0]
        tap.eq(new_suggest.suggest_id, suggest.suggest_id, 'Тот же саджест')
        tap.eq(new_suggest.status, 'request', 'В статусе запроса')
        tap.eq(new_suggest.rack_id, another_rack.rack_id, 'Новый стеллаж')

        tap.ok(await new_suggest.done(user=user), 'Закрыли саджест')
        tap.ok(
            await order.done(target='complete', user=user),
            'Закрыли документ'
        )
        tap.ok(
            await wait_order_status(order, ('complete', 'begin')),
            'Дотолкали ордер до конца'
        )
