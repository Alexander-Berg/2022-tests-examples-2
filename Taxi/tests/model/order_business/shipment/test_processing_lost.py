# pylint: disable=too-many-locals, too-many-statements

from libstall.util import now
from stall.model.stock import Stock
from stall.model.suggest import Suggest


async def test_lost(tap, uuid, dataset, wait_order_status):
    with tap.plan(45, 'Разрешение пропаж'):

        product = await dataset.product()
        store   = await dataset.store()
        shelf1  = await dataset.shelf(store=store, type='store', order=1)
        shelf2  = await dataset.shelf(store=store, type='store', order=2)
        lost    = await dataset.shelf(store=store, type='lost',  order=100)
        user    = await dataset.user(store=store)

        stock1 = await dataset.stock(
            product=product,
            shelf=shelf1,
            store=store,
            count=25,
            lot=uuid(),
        )
        tap.eq(stock1.count, 25, 'Остаток 1 положен')
        tap.eq(stock1.reserve, 0, 'Резерва 1 нет')

        stock2 = await dataset.stock(
            product=product,
            shelf=shelf2,
            store=store,
            count=40,
            lot=uuid(),
        )
        tap.eq(stock2.count, 40, 'Остаток 2 положен')
        tap.eq(stock2.reserve, 0, 'Резерва 2 нет')

        order = await dataset.order(
            store=store,
            type = 'shipment',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required = [
                {
                    'product_id': product.product_id,
                    'count': 25,
                },
            ],
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дождались выполнения'
        )

        tap.eq(len(order.problems), 0, 'Нет проблем')

        reserved = await Stock.list_by_order(order)
        tap.eq(len(reserved), 1, 'Резерв по заказу')
        with reserved[0] as reserve:
            tap.eq(
                reserve.reserves[order.order_id],
                25,
                'Товар зарезервирован'
            )

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Саджесты получены')

        with suggests[0] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'type')
            tap.eq(suggest.count, 25, 'count')
            tap.eq(suggest.shelf_id, shelf1.shelf_id, 'shelf_id')
            tap.eq(suggest.status, 'request', 'status')
            tap.ok(
                await suggest.done('error', reason={
                    'code': 'PRODUCT_ABSENT',
                    'count': 3,
                }),
                'Ошибка'
            )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'lost', 'lost')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'check_target', 'check_target')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 0, 'Саджест удален')

        reserved = await Stock.list_by_order(order)
        tap.eq(len(reserved), 2, 'Резервы увеличились')

        with [x for x in reserved if x.shelf_id == shelf1.shelf_id][0] as (
                reserve):
            tap.eq(
                reserve.reserves[order.order_id],
                22,
                'Резерв только того, что нашли'
            )
            tap.eq(reserve.shelf_id, shelf1.shelf_id, 'На полке хранения')

        with [x for x in reserved if x.shelf_id == lost.shelf_id][0] as (
                reserve):
            tap.eq(reserve.reserves[order.order_id], 3, 'Ненайденный товар')
            tap.eq(reserve.shelf_id, lost.shelf_id, 'На полке пропаж')

        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дождались выполнения'
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Саджесты получены')

        with suggests[0] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'type')
            tap.eq(suggest.count, 22, 'count на прежней полке')
            tap.eq(suggest.shelf_id, shelf1.shelf_id, 'shelf_id')
            tap.eq(suggest.status, 'request', 'status')

        with suggests[1] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'type')
            tap.eq(suggest.count, 3, 'count с новой полки')
            tap.eq(suggest.shelf_id, shelf2.shelf_id, 'shelf_id')
            tap.eq(suggest.status, 'request', 'status')
