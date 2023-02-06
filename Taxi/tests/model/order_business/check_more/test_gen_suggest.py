from stall.model.suggest import Suggest

# pylint: disable=too-many-statements
async def test_reserving_shelf(tap, dataset, wait_order_status):
    with tap.plan(21, 'Генерация саджестов для слепой инвентаризации'):
        store = await dataset.store()
        tap.ok(store, 'Склад сгенерирован')

        shelf = await dataset.shelf(store=store)
        tap.ok(shelf, 'полки сгенерированы')

        order = await dataset.order(
            type='check_more',
            shelves=[shelf.shelf_id],
            store=store,
            status='processing',
            estatus='suggests_generate',
        )

        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.type, 'check_more', 'слепая инвентаризация')
        tap.eq(order.status, 'processing', 'статус')
        tap.eq(order.estatus, 'suggests_generate', 'сабстатус')
        tap.ok(order.shelves, 'полки есть')
        tap.eq(order.users, [], 'пользователь не назначен')
        version = order.version

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(await order.reload(), 'перезагружен')
        tap.ok(version < order.version, 'версия ордера инкрементнулась')
        version = order.version

        suggests = await Suggest.list_by_order(order)
        tap.isa_ok(suggests, list, 'саджесты получены')
        tap.eq(len(suggests), 1, 'количество саджестов')


        with suggests[0] as s:
            tap.eq(s.type, 'check_more', 'тип')
            tap.eq(s.shelf_id, shelf.shelf_id, 'полка')
            tap.eq(s.status, 'request', 'предлагается')
            tap.eq(s.count, None, 'количество не определено')
            tap.eq(s.valid, None, 'срок годности не определён')
            tap.ok(s.conditions.all, 'любое количество можно делать')
            tap.ok(not s.conditions.editable, 'не редактируемый')
            tap.eq(s.conditions.need_valid,
                   False, 'не надо указывать сроки хранения')
