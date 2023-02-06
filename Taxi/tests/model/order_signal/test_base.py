from stall.model.order_signal import OrderSignal


async def test_instance(tap):
    with tap.plan(6, 'Создание объекта OrderSignal'):
        signal = OrderSignal({
            'type': 'stat',
        })
        tap.ok(signal, 'сигнал')
        tap.ok(signal.sigid, 'sigid')
        tap.eq(signal.user_id, None, 'user_id None')
        tap.eq(signal.type, 'stat', 'тип сигнала совпал')
        tap.eq(signal.data, {}, 'data пустой')
        tap.eq(signal.done, None, 'сигнал не закрыт')


async def test_done(tap, dataset):
    with tap.plan(22, 'Закрытие сигнала'):

        order = await dataset.order()
        signal1 = OrderSignal({'type': 'stat'})
        signal2 = OrderSignal({'type': 'stat'})

        tap.ok(await order.signal(signal1), 'сигнал 1 отправлен')
        tap.ok(await order.signal(signal2), 'сигнал 2 отправлен')

        tap.eq(len(order.signals), 2, 'сигналы')

        with order.signals[0] as s:
            tap.ok(s.sigid, 'sigid')
            tap.eq(s.done, None, 'не закрыт')
            tap.ok(await order.signal_close(s), 'сигнал 1 отмечен выполненным')

        with order.signals[1] as s:
            tap.ok(s.sigid, 'sigid')
            tap.eq(s.done, None, 'сигнал 2 не закрыт')

        tap.ok(await order.reload(), 'Забрали заново')
        tap.eq(len(order.signals), 2, 'сигналы')

        with order.signals[0] as s:
            tap.ok(s.sigid, 'sigid')
            tap.ok(s.done, 'сигнал 1 закрыт')
            tap.ok(
                await order.signal_close(s),
                'сигнал 1 повторяем без проблем'
            )

        with order.signals[1] as s:
            tap.ok(s.sigid, 'sigid')
            tap.eq(s.done, None, 'сигнал 2 не закрыт')
            tap.ok(await order.signal_close(s), 'сигнал 2 отмечен выполненным')

        tap.ok(await order.reload(), 'Забрали заново')
        tap.eq(len(order.signals), 2, 'сигналы')

        with order.signals[0] as s:
            tap.ok(s.sigid, 'sigid')
            tap.ok(s.done, 'сигнал 1 закрыт')

        with order.signals[1] as s:
            tap.ok(s.sigid, 'sigid')
            tap.ok(s.done, 'сигнал 2 закрыт')
