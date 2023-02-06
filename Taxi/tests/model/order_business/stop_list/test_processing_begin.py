async def test_begin(tap, dataset, wait_order_status):
    with tap.plan(2):
        stop_list = await dataset.order(
            type='stop_list',
            status='reserving',
            estatus='begin',
        )

        tap.ok(stop_list, 'Создали стоп-лист на всю полку')
        await wait_order_status(stop_list, ('processing', 'begin'))
