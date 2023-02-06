async def test_waiting(tap, dataset, wait_order_status):
    with tap.plan(11, 'Стоп-лист ждет отмены'):
        stop_list = await dataset.order(
            type='stop_list',
            status='reserving',
            estatus='begin',
        )

        tap.ok(stop_list, 'Создали стоп-лист')

        await wait_order_status(stop_list, ('processing', 'waiting'))
        await stop_list.business.order_changed()

        tap.ok(await stop_list.reload(), 'Перезабрали заказ')
        revision = stop_list.revision

        for i in range(2):
            await stop_list.business.order_changed()
            tap.ok(await stop_list.reload(), f'Перезабрали заказ {i} раз')
            tap.eq(stop_list.status, 'processing', 'processing')
            tap.eq(stop_list.estatus, 'waiting', 'waiting')

        tap.ok(await stop_list.reload(), 'Перезабрали заказ')
        tap.eq(stop_list.revision, revision, 'Ревизия не менялась')


async def test_waiting_cancel(tap, dataset, wait_order_status):
    with tap.plan(6, 'Стоп-лист отменен'):
        stop_list = await dataset.order(
            type='stop_list',
            status='reserving',
            estatus='begin',
        )

        tap.ok(stop_list, 'Создали стоп-лист')

        await wait_order_status(stop_list, ('processing', 'waiting'))
        await stop_list.business.order_changed()

        tap.ok(await stop_list.cancel(), 'Отмена заказа')

        await stop_list.business.order_changed()

        tap.ok(await stop_list.reload(), 'Перезабрали заказ')
        tap.eq(stop_list.status, 'canceled', 'canceled')
        tap.eq(stop_list.estatus, 'begin', 'begin')
