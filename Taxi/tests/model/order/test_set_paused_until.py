from libstall.util import time2time


async def test_repeat_pause(tap, dataset):
    with tap.plan(7, 'ставим заказ на паузу несколько раз'):
        order = await dataset.order()
        tap.ok(order.paused_until is None, 'по дефолту паузы нет')

        order.set_paused_until(30, time2time('1970-01-01T12:00:00'))
        tap.eq(
            order.paused_until,
            time2time('1970-01-01T12:00:30'),
            'выставлена пауза на 30 сек',
        )
        tap.eq(
            order.vars('total_pause'),
            30,
            'записали продолжительность',
        )

        order.set_paused_until(30, time2time('1970-01-01T12:00:10'))
        tap.eq(
            order.paused_until,
            time2time('1970-01-01T12:00:40'),
            'первая пауза не завершена и пришла вторая',
        )
        tap.eq(
            order.vars('total_pause'),
            40,
            'общая продолжительность увеличилась',
        )

        order.set_paused_until(5, time2time('1970-01-01T12:00:41'))
        tap.eq(
            order.paused_until,
            time2time('1970-01-01T12:00:46'),
            'вторая пауза завершена и пришла третья',
        )
        tap.eq(
            order.vars('total_pause'),
            46,
            'общая продолжительность увеличилась',
        )


async def test_reset_pause(tap, dataset):
    with tap.plan(7, 'снимаем заказ с паузы'):
        order = await dataset.order()
        tap.ok(order.paused_until is None, 'по дефолту паузы нет')

        order.set_paused_until(0)
        tap.ok(order.paused_until is None, 'ничего не выставляем')
        tap.ok(
            order.vars('total_pause', None) is None,
            'продолжительность также не трогаем',
        )

        order.set_paused_until(30, time2time('1970-01-01T12:00:00'))
        tap.eq(
            order.paused_until,
            time2time('1970-01-01T12:00:30'),
            'выставлена пауза на 30 сек',
        )
        tap.eq(
            order.vars('total_pause'),
            30,
            'записали продолжительность',
        )

        order.set_paused_until(0, time2time('1970-01-01T12:00:10'))
        tap.eq(
            order.paused_until,
            time2time('1970-01-01T12:00:10'),
            'снесли паузу',
        )
        tap.eq(
            order.vars('total_pause'),
            10,
            'общая продолжительность паузы уменьшилась',
        )
