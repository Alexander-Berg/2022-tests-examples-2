async def test_begin(tap, dataset):
    with tap.plan(6, 'Создали стоп-лист'):
        store = await dataset.store()
        stop_list = await dataset.order(
            store=store,
            type='stop_list',
            status='reserving',
        )

        tap.ok(stop_list, 'Стоп-лист создан')
        tap.eq(stop_list.status, 'reserving', 'reserving')
        tap.eq(stop_list.estatus, 'begin', 'begin')
        tap.eq(stop_list.target, 'complete', 'target: complete')

        await stop_list.business.order_changed()

        tap.eq(stop_list.status, 'reserving', 'reserving')
        tap.eq(stop_list.estatus, 'reserve', 'reserve')
