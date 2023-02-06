async def test_signal(tap, dataset):
    with tap.plan(9, 'отправка сигналов ордеру'):
        order = await dataset.order()
        tap.ok(order, 'ордер создан')

        tap.ok(await order.signal({'type': 'inventory_done'}),
               'сигнал отправлен')
        tap.eq(len(order.signals), 1, 'один сигнал сохранён')
        with order.signals[0] as s:
            tap.eq(s.type, 'inventory_done', 'тип')
            tap.ok(s.sigid, 'идентификатор')

        tap.ok(await order.signal(order.signals[0]),
               'сигнал отправлен ещё раз')
        tap.eq(len(order.signals), 1, 'идемпотентность')


        logs = [
            l
            for l in await dataset.OrderLog.list_by_order(order)
            if l.source == 'signal'
        ]
        tap.eq(len(logs), 1, 'одна запись в логе')
        with logs[0] as l:
            tap.eq(l.user_id, None, 'user_id у неё не проставлен')


async def test_signal_log_user(tap, dataset):
    with tap.plan(10, 'отправка сигналов ордеру с простановкой пользователя'):
        order = await dataset.order()
        tap.ok(order, 'ордер создан')

        user = await dataset.user(store_id=order.store_id)
        tap.eq(user.store_id, order.store_id, 'пользователь создан')

        tap.ok(await order.signal({'type': 'inventory_done'}, user=user),
               'сигнал отправлен')
        tap.eq(len(order.signals), 1, 'один сигнал сохранён')
        with order.signals[0] as s:
            tap.eq(s.type, 'inventory_done', 'тип')
            tap.ok(s.sigid, 'идентификатор')

        tap.ok(await order.signal(order.signals[0]),
               'сигнал отправлен ещё раз')
        tap.eq(len(order.signals), 1, 'идемпотентность')


        logs = [
            l
            for l in await dataset.OrderLog.list_by_order(order)
            if l.source == 'signal'
        ]
        tap.eq(len(logs), 1, 'одна запись в логе')
        with logs[0] as l:
            tap.eq(l.user_id, user.user_id, 'user_id у неё проставлен')
