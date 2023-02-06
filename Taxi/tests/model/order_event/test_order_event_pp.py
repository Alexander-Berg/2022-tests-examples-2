async def test_with_eda_status(tap, dataset):
    eda_status = 'CALL_CENTER_CONFIRMED'

    with tap:
        order = await dataset.order()
        tap.ok(order, 'ордер создан')
        tap.is_ok(order.eda_status, None, 'eda_status нет')
        tap.eq(order.version, 1, 'версия 1')

        old_events = await dataset.OrderEvent.list_by_order(order)
        tap.eq(len(old_events), 1, 'запись создана')

        serialized = old_events[-1].order_event_pp()
        tap.ok(serialized, 'сериализация ок')
        tap.ok('external_type' not in serialized, 'external_type not exists')

        order.eda_status = eda_status
        await order.save()
        tap.eq(order.eda_status, eda_status, 'eda_status установлена')
        tap.eq(order.version, 1, 'версия не обновлена')

        new_events = await dataset.OrderEvent.list_by_order(order)
        tap.eq(len(new_events), 2, 'запись создана')
        tap.eq(new_events[0], old_events[-1], 'записи идентичны')

        serialized = new_events[-1].order_event_pp()
        tap.ok(serialized, 'сериализация ок')
        tap.eq(serialized['external_type'], eda_status,
               f'external_type = {eda_status}')


async def test_with_external_revision(tap, dataset):
    with tap:
        order = await dataset.order(vars={'external_order_revision': 'v1'})
        tap.ok(order, 'ордер создан')
        tap.eq(order.vars['external_order_revision'], 'v1',
               'external_order_revision = "v1"')

        events = await dataset.OrderEvent.list_by_order(order)
        tap.eq(len(events), 1, 'запись создана')

        serialized = events[-1].order_event_pp()
        tap.ok(serialized, 'сериализация ок')
        tap.ok('external_order_revision' in serialized,
               'external_order_revision exists')
        tap.eq(serialized['external_order_revision'], 'v1',
               'external_order_revision = "v1"')


async def test_without_external_revision(tap, dataset):
    with tap:
        order = await dataset.order()
        tap.ok(order, 'ордер создан')
        tap.ok('external_order_revision' not in order.vars,
               'order.external_order_revision empty')

        events = await dataset.OrderEvent.list_by_order(order)
        tap.eq(len(events), 1, 'запись создана')

        serialized = events[-1].order_event_pp()
        tap.ok(serialized, 'сериализация ок')
        tap.ok('external_order_revision' not in serialized,
               'event.external_order_revision empty')
