async def test_attr(tap, dataset):
    with tap.plan(6, 'работа с attr как с vars'):
        order = await dataset.order(attr={'hello': 'world'})
        tap.ok(order, 'ордер создан')
        tap.eq(order.attr['hello'], 'world', 'начальное значение')

        order.attr['foo'] = 'bar'
        tap.ok(await order.save(), 'сохранён')

        tap.eq(order.attr['hello'], 'world', 'начальное значение')
        tap.eq(order.attr['foo'], 'bar', 'новое значение')

        tap.ok(order.attr['doc_number'], 'номер документа есть')


async def test_attr_nodefault(tap, dataset):
    with tap.plan(7, 'работа с attr как с vars'):
        order = await dataset.order()
        tap.ok(order, 'ордер создан')

        order.attr['foo'] = 'bar'
        tap.ok(await order.save(), 'сохранён')

        tap.eq(order.attr['foo'], 'bar', 'новое значение')

        order.attr['bar'] = 'baz'
        tap.ok(await order.save(), 'ещё сохранён')
        tap.eq(order.attr['foo'], 'bar', 'предыдущее значение')
        tap.eq(order.attr['bar'], 'baz', 'новое значение')

        tap.ok(order.attr['doc_number'], 'номер документа есть')
