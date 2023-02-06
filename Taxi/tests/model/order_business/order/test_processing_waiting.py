# pylint: disable=too-many-statements

from libstall.util import now
from stall.model.suggest import Suggest


async def test_waiting(tap, dataset):
    with tap.plan(9, 'Сборка заказа'):

        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type = 'order',
            status='processing',
            estatus='waiting',
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')


async def test_waiting_suggests_done(tap, dataset):
    with tap.plan(12, 'Ожидаем закрытие саджестов'):

        product = await dataset.product()
        store   = await dataset.store()
        shelf   = await dataset.shelf(store=store, type='store')
        user    = await dataset.user(store=store)

        order = await dataset.order(
            store=store,
            type = 'order',
            status='processing',
            estatus='waiting',
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        suggest = await dataset.suggest(
            order,
            type='box2shelf',
            shelf_id=shelf.shelf_id,
            product_id=product.product_id,
        )
        tap.ok(suggest, f'suggest_id={suggest.suggest_id}')

        order.user_done = user.user_id
        tap.ok(await order.save(), 'Пользователь зафорсен')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.eq(order.user_done, None, 'Пользователь сброшен')


async def test_next(tap, dataset):
    with tap.plan(10, 'Сборка заказа'):

        store = await dataset.store()
        user = await dataset.user(store=store)

        order = await dataset.order(
            store=store,
            type = 'order',
            status='processing',
            estatus='waiting',
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok(await order.done('complete', user=user), 'Завершение заказа')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')


async def test_waiting_suggests_error(tap, dataset):
    with tap.plan(10, 'Ожидаем закрытие саджестов'):

        product = await dataset.product()
        store   = await dataset.store()
        shelf   = await dataset.shelf(store=store, type='store')

        order = await dataset.order(
            store=store,
            type = 'order',
            status='processing',
            estatus='waiting',
            required = [
                {
                    'product_id': product.product_id,
                    'count': 10,
                },
            ],
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        suggest = await dataset.suggest(
            order,
            type='shelf2box',
            status='error',
            count=10,
            result_count=6,
            shelf_id=shelf.shelf_id,
            product_id=product.product_id,
        )
        tap.ok(suggest, f'suggest_id={suggest.suggest_id}')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'prepare_lost', 'prepare_lost')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')


async def test_waiting_cancel(tap, dataset, wait_order_status):
    with tap.plan(15, 'Закрытие заказа ведет к откату саджестов'):

        product = await dataset.product()
        store   = await dataset.store()
        user    = await dataset.user(store=store)

        trash   = await dataset.shelf(store=store, type='trash')
        tap.ok(trash, 'полка для списания')

        order = await dataset.order(
            store=store,
            type = 'order',
            status='processing',
            estatus='waiting',
            target='canceled',
            required = [
                {
                    'product_id': product.product_id,
                    'count': 10,
                },
            ],
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'canceled', 'target: canceled')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_error', 'suggests_error')
        tap.eq(order.target, 'canceled', 'target: canceled')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'canceled', 'target: canceled')


# pylint: disable=too-many-locals
async def test_waiting_cancel2(tap, dataset, wait_order_status):
    with tap.plan(44, 'Проверка петли при отмене: ревизия всегда растет.'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()
        product4 = await dataset.product()
        store   = await dataset.store()
        shelf   = await dataset.shelf(store=store)
        user    = await dataset.user(store=store)

        trash   = await dataset.shelf(store=store, type='trash')
        tap.ok(trash, 'полка для списания')

        await dataset.stock(shelf=shelf, product=product1, count=100)
        await dataset.stock(shelf=shelf, product=product2, count=200)
        await dataset.stock(shelf=shelf, product=product3, count=300)
        await dataset.stock(shelf=shelf, product=product4, count=400)

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            target='complete',
            acks=[user.user_id],
            approved=now(),
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 10,
                },
                {
                    'product_id': product2.product_id,
                    'count': 20,
                },
                {
                    'product_id': product3.product_id,
                    'count': 30,
                },
                {
                    'product_id': product4.product_id,
                    'count': 40,
                },
            ],
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        tap.ok(await order.reload(), 'Заказ получен')

        suggests = await Suggest.list_by_order(order)
        suggests = dict((x.product_id, x) for x in suggests)

        with suggests[product1.product_id] as suggest:
            tap.eq(suggest.status, 'request', 'request')
            tap.ok(await suggest.done('done'), 'Выполнили саджест')

        with suggests[product2.product_id] as suggest:
            tap.eq(suggest.status, 'request', 'request')
            tap.ok(await suggest.done('done'), 'Выполнили саджест')

        with suggests[product3.product_id] as suggest:
            tap.eq(suggest.status, 'request', 'request')

        with suggests[product4.product_id] as suggest:
            tap.eq(suggest.status, 'request', 'request')

        with order:
            tap.ok(await order.reload(), 'Перезабрали заказ')
            revision = order.revision
            for _ in range(0, 2):
                await order.business.order_changed()

                tap.ok(await order.reload(), 'Перезабрали заказ')
                tap.eq(order.status, 'processing', 'processing')
                tap.eq(order.estatus, 'waiting', 'waiting')
                tap.eq(order.target, 'complete', 'target: complete')

            tap.ok(await order.reload(), 'Перезабрали заказ')
            tap.eq(order.revision, revision,
                   'Просто ожидали, ничего не менялось')

        tap.ok(await order.cancel(user=user), 'Отмена заказа')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        tap.ok(await order.reload(), 'Перезабрали заказ')

        suggests = await Suggest.list_by_order(order)
        suggests = dict(((x.product_id, x.type), x) for x in suggests)

        with suggests[(product1.product_id, 'shelf2box')] as suggest:
            tap.eq(suggest.status, 'done', 'shelf2box done')
        with suggests[(product1.product_id, 'box2shelf')] as suggest:
            tap.eq(suggest.status, 'request', 'box2shelf request')
            tap.ok(await suggest.done('done'), 'Выполнили саджест возврата')

        with suggests[(product2.product_id, 'shelf2box')] as suggest:
            tap.eq(suggest.status, 'done', 'shelf2box done')
        with suggests[(product2.product_id, 'box2shelf')] as suggest:
            tap.eq(suggest.status, 'request', 'box2shelf request')

        tap.ok((product3.product_id, 'shelf2box') not in suggests,
               'shelf2box request удален')
        tap.ok((product3.product_id, 'box2shelf') not in suggests,
               'box2shelf request не создавался')

        tap.ok((product4.product_id, 'shelf2box') not in suggests,
               'shelf2box request удален')
        tap.ok((product4.product_id, 'box2shelf') not in suggests,
               'box2shelf request не создавался')

        with order:
            tap.ok(await order.reload(), 'Перезабрали заказ')
            revision = order.revision

            for _ in range(0, 2):
                await order.business.order_changed()

                tap.ok(await order.reload(), 'Перезабрали заказ')
                tap.eq(order.status, 'processing', 'processing')
                tap.eq(order.estatus, 'waiting', 'waiting')
                tap.eq(order.target, 'canceled', 'target: canceled')

            tap.ok(await order.reload(), 'Перезабрали заказ')
            tap.eq(order.user_done, None, 'Пользователь сброшен')
            tap.eq(
                order.revision, revision + 1,
                'Ревизия поднялась на 1 т.к. сбросили пользователя, '
                'но не растет на каждой итерации'
            )
