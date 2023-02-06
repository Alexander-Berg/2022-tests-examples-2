async def test_begin(tap, dataset, wait_order_status):
    with tap.plan(3):
        stop_list = await dataset.order(
            type='stop_list', status='reserving',
        )

        tap.ok(stop_list, 'Стоп-лист создан')
        tap.ok(await stop_list.cancel(), 'Стоп-лист отменен')
        await wait_order_status(stop_list, ('canceled', 'done'))
