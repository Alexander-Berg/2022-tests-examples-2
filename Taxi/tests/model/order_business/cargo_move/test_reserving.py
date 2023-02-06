async def test_success_rack(tap, dataset, wait_order_status):
    with tap.plan(12, 'Переходы до request в стеллаж'):
        store = await dataset.store(type='dc')
        rack = await dataset.rack(store_id=store.store_id)
        cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo'
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
            ]
        )
        tap.ok(
            await wait_order_status(order, ('request', 'begin')),
            'Дотолкали ордер до request,begin'
        )
        tap.eq(
            order.shelves,
            [cargo.shelf_id],
            'Нужные полки прописались'
        )
        tap.ok(await cargo.reload(), 'Перезабрали груз')
        tap.eq(
            cargo.order_id,
            order.order_id,
            'В груз прописался мув'
        )
        tap.ok(await new_rack.reload(), 'Перезабрали целевой стеллаж')
        tap.eq(new_rack.reserve, 1, 'Один резерв')
        tap.eq(
            new_rack.reserves.get(order.order_id, 0),
            1,
            'Одно место в резерве стеллажа'
        )
        suggests = await dataset.Suggest.list_by_order(order=order)
        tap.eq(len(suggests), 1, 'Один саджест')
        suggest = suggests[0]
        tap.eq(suggest.type, 'take_cargo', 'Тип саджеста взять груз')
        tap.eq(suggest.shelf_id, cargo.shelf_id, 'Груз в саджесте')
        tap.eq(suggest.rack_id, cargo.rack_id, 'Стеллаж полки')


async def test_success_zone(tap, dataset, wait_order_status):
    with tap.plan(9, 'Переходы до request в стеллаж'):
        store = await dataset.store(type='dc')
        rack = await dataset.rack(store_id=store.store_id)
        cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo'
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
            ]
        )
        tap.ok(
            await wait_order_status(order, ('request', 'begin')),
            'Дотолкали ордер до request,begin'
        )
        tap.eq(
            order.shelves,
            [cargo.shelf_id],
            'Нужные полки прописались'
        )
        tap.ok(await cargo.reload(), 'Перезабрали груз')
        tap.eq(
            cargo.order_id,
            order.order_id,
            'В груз прописался мув'
        )
        reserved_racks = await dataset.Rack.list_by_order(order=order)
        tap.eq(len(reserved_racks), 0, 'Нет резервов')
        suggests = await dataset.Suggest.list_by_order(order=order)
        tap.eq(len(suggests), 1, 'Один саджест')
        suggest = suggests[0]
        tap.eq(suggest.type, 'take_cargo', 'Тип саджеста взять груз')
        tap.eq(suggest.shelf_id, cargo.shelf_id, 'Груз в саджесте')


async def test_required_empty(tap, dataset, wait_order_status):
    with tap.plan(4, 'Тут required пустой'):
        store = await dataset.store(type='dc')

        order = await dataset.order(
            store=store,
            type='cargo_move',
            status='reserving',
            estatus='begin',
            required=[]
        )
        tap.ok(
            await wait_order_status(order, ('failed', 'done')),
            'Дотолкали ордер до request,begin'
        )
        tap.eq(len(order.problems), 1, 'Одна проблемка')
        tap.eq(
            order.problems[0].type,
            'required_is_empty',
            'Пустой required'
        )


async def test_required(tap, dataset, wait_order_status):
    with tap.plan(4, 'Тут required большой'):
        store = await dataset.store(type='dc')
        rack = await dataset.rack(store_id=store.store_id)
        cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo'
        )
        second_cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo'
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
                },
                {
                    'shelf_id': second_cargo.shelf_id,
                    'dst_rack_id': new_rack.rack_id,
                }
            ]
        )
        tap.ok(
            await wait_order_status(order, ('failed', 'done')),
            'Дотолкали ордер до request,begin'
        )
        tap.eq(len(order.problems), 1, 'Одна проблемка')
        tap.eq(
            order.problems[0].type,
            'required_too_big',
            'Слишком много в required'
        )


async def test_inactive_cargo(tap, dataset, wait_order_status):
    with tap.plan(5, 'Неактивный груз тащим'):
        store = await dataset.store(type='dc')
        rack = await dataset.rack(store_id=store.store_id)
        cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo',
            status='removed'
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
            ]
        )
        tap.ok(
            await wait_order_status(order, ('failed', 'done')),
            'Дотолкали ордер до failed,done'
        )
        tap.eq(len(order.problems), 1, 'Одна проблемка')
        tap.eq(
            order.problems[0].type,
            'shelf_not_found',
            'Не нашли среди активных грузов'
        )
        tap.eq(order.problems[0].shelf_id, cargo.shelf_id, 'Груз')


async def test_cargo_blocked(tap, dataset, wait_order_status):
    with tap.plan(5, 'Груз заблокирован'):
        store = await dataset.store(type='dc')
        rack = await dataset.rack(store_id=store.store_id)
        cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo',
            vars={'order_external_id': 'order'},
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
            ]
        )
        tap.ok(
            await wait_order_status(order, ('failed', 'done')),
            'Дотолкали ордер до failed,done'
        )
        tap.eq(len(order.problems), 1, 'Одна проблемка')
        tap.eq(
            order.problems[0].type,
            'cargo_is_blocked',
            'Груз заблокирован'
        )
        tap.eq(order.problems[0].shelf_id, cargo.shelf_id, 'Груз')


async def test_rack_full(tap, dataset, wait_order_status):
    with tap.plan(9, 'Стеллаж полный'):
        store = await dataset.store(type='dc')
        rack = await dataset.rack(store_id=store.store_id)
        cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo'
        )
        new_rack = await dataset.rack(store_id=store.store_id, capacity=1)
        await dataset.shelf(
            store_id=store.store_id,
            rack_id=new_rack.rack_id,
            type='cargo'
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
            ]
        )
        tap.ok(
            await wait_order_status(order, ('failed', 'done')),
            'Дотолкали ордер до failed'
        )
        tap.eq(
            order.shelves,
            [cargo.shelf_id],
            'Нужные полки прописались'
        )
        tap.ok(await cargo.reload(), 'Перезабрали груз')
        tap.ok(
            'external_order_id' not in cargo.vars,
            'В грузе ничего не осталось'
        )

        suggests = await dataset.Suggest.list_by_order(order=order)
        tap.eq(len(suggests), 0, 'Нет саджестов')
        reserved_racks = (
            await dataset.Rack.list(by='full', order_id=order.order_id, sort=())
        ).list
        tap.eq(len(reserved_racks), 0, 'Нет резервов')
        tap.eq(len(order.problems), 1, 'Одна проблемка')
        tap.eq(
            order.problems[0].type,
            'rack_reserve_failure',
            'Не смогли взять резерв'
        )
