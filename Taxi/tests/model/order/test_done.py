from stall.model.order import ErOrderIsNotProcessing


async def test_done(tap, dataset):
    with tap.plan(8, 'Завершение заказа'):

        store = await dataset.store()
        user  = await dataset.user(store=store)

        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'Заказ создан')
        tap.eq(order.user_done, None, 'Завершающего нет')

        tap.ok(await order.done('complete', user=user), 'Завершен')
        tap.ok(await order.reload(), 'Заказ перезабрали')
        tap.eq(order.status, 'processing', 'Статус не поменялся')
        tap.eq(order.estatus, 'waiting', 'СабСтатус не поменялся')
        tap.eq(order.target, 'complete', 'Цель установлена')
        tap.eq(order.user_done, user.user_id, 'Пользователь завершивший')
#         tap.in_ok(user.user_id, order.users,
#                   'Пользователь в списке участников')


async def test_processing_only(tap, dataset):
    with tap.plan(5, 'Только в статусе processing'):

        store = await dataset.store()
        user  = await dataset.user(store=store)

        order = await dataset.order(status='reserving', estatus='waiting')
        tap.ok(order, 'Заказ создан')
        tap.eq(order.user_done, None, 'Завершающего нет')

        try:
            await order.done('complete', user=user)
        except ErOrderIsNotProcessing:
            tap.passed('Ошибка')
        else:
            tap.failed('Ошибки нет')
        tap.eq(order.user_done, None, 'Пользователь завершивший')
        tap.not_in_ok(user.user_id, order.users,
                      'Пользователь в списке участников')


async def test_failed(tap, dataset):
    with tap.plan(10, 'Завершение заказа'):

        store = await dataset.store()
        user  = await dataset.user(store=store)

        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'Заказ создан')
        tap.eq(order.user_done, None, 'Завершающего нет')

        tap.ok(await order.done(
            'failed',
            user=user,
            reason='my_fail',
            comment='Моя ошибка',
        ), 'Сорван')
        tap.ok(await order.reload(), 'Заказ перезабрали')
        tap.eq(order.status, 'processing', 'Статус не поменялся')
        tap.eq(order.estatus, 'waiting', 'СабСтатус не поменялся')
        tap.eq(order.target, 'failed', 'Цель установлена')
        tap.eq(order.user_done, user.user_id, 'Пользователь завершивший')

        tap.ok(order.problems, 'problems не пуста')
        tap.eq(order.problems[-1].type, 'human_failed', 'тип посл записи')
#         tap.in_ok(user.user_id, order.users,
#                   'Пользователь в списке участников')


async def test_attr_done(tap, dataset):
    with tap.plan(8, 'данные при завершении ордера'):
        user = await dataset.user()
        tap.ok(user.store_id, 'пользователь создан')

        order = await dataset.order(
            attr={'hello': 'world 1'},
            store_id=user.store_id,
            status='processing',
            estatus='waiting',
        )
        tap.eq(order.store_id, user.store_id, 'ордер создан')
        tap.in_ok('hello', order.attr, 'ключ в attr есть')

        tap.ok(
            await order.done(
                target='complete',
                attr={'hello': 'world 2'},
                user=user,
            ),
            'ордер завершён'
        )

        tap.in_ok('complete', order.attr, 'complete в attr появилось')
        tap.in_ok('hello', order.attr, 'старый ключ сохранился')
        tap.eq(order.attr['complete'], {'hello': 'world 2'}, 'done запись')
        tap.eq(order.attr['hello'], 'world 1', 'первичная запись')
