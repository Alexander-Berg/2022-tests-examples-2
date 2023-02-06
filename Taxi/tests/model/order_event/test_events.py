import pytest


async def test_events(tap, dataset):
    with tap.plan(34, 'кеш событий'):
        order = await dataset.order(problems=[{'type': 'shelf_not_found'}])
        revision = order.revision
        tap.ok(order, 'ордер создан')

        events = await dataset.OrderEvent.list_by_order(order)
        tap.isa_ok(events, list, 'Список выбран')
        tap.eq(len(events), 1, 'одно событие')

        tap.ok(await order.save(), 'ордер пересохранён')
        tap.ne(order.revision, revision, 'ревизия поменялась')

        events = await dataset.OrderEvent.list_by_order(order)
        tap.isa_ok(events, list, 'Список выбран')
        tap.eq(len(events), 1, 'одно событие')

        with events[0] as e:
            tap.isa_ok(e, dataset.OrderEvent, 'Событие тип')
            tap.eq(e.order_id, order.order_id, 'order_id')
            tap.eq(e.external_id, order.external_id, 'external_id')
            tap.eq(e.eda_status, order.eda_status, 'eda_status')
            tap.eq(e.problems, order.problems, 'problems')
            tap.eq(e.revision, revision, 'revision')
            tap.eq(e.order_version, order.version, 'order_version')
            tap.is_ok(e.external_order_revision, None,
                      'external_order_revision')
            tap.eq(e.status, order.status, 'status')
            tap.ok(e.created, 'created')
            tap.eq(e.shardno, order.shardno, 'shardno')

        order.rehashed('status', True)
        tap.ok(await order.save(), 'ордер пересохранён')

        events = await dataset.OrderEvent.list_by_order(order)
        tap.isa_ok(events, list, 'Список выбран')
        tap.eq(len(events), 2, 'Ещё одно событие')

        with events[-1] as e:
            tap.isa_ok(e, dataset.OrderEvent, 'Событие тип')
            tap.eq(e.order_id, order.order_id, 'order_id')
            tap.eq(e.external_id, order.external_id, 'external_id')
            tap.eq(e.problems, order.problems, 'problems')
            tap.eq(e.revision, order.revision, 'revision')
            tap.eq(e.status, order.status, 'status')
            tap.ok(e.created, 'created')
            tap.eq(e.shardno, order.shardno, 'shardno')

            tap.ok(await e.rm(), 'Удаление работает')

        events = await dataset.OrderEvent.list_top(shard_limit=5)
        tap.isa_ok(events, list, 'Записи в топе получены')
        tap.ok(len(events) > 0, 'есть записи')

        e = events[0]
        order = await dataset.Order.load(e.order_id)
        tap.ok(order, 'ордер получен')
        tap.eq(order.shardno, e.shardno, 'shardno соответствует')


@pytest.mark.parametrize('external_order_revision', [None, '', 'v1', '123'])
async def test_external_revision(
        tap, dataset, external_order_revision
):
    with tap:
        order = await dataset.order(vars={
            'external_order_revision': external_order_revision
        })
        tap.ok(order, 'ордер создан')

        events = await dataset.OrderEvent.list_by_order(order)
        tap.isa_ok(events, list, 'Список выбран')
        tap.eq(len(events), 1, 'одно событие')

        with events[-1] as e:
            tap.eq(e.external_order_revision, external_order_revision,
                   f'external_order_revision = {external_order_revision}')


async def test_external_revision_empty(tap, dataset):
    with tap:
        order = await dataset.order()
        tap.ok(order, 'ордер создан')

        events = await dataset.OrderEvent.list_by_order(order)
        tap.isa_ok(events, list, 'Список выбран')
        tap.eq(len(events), 1, 'одно событие')

        with events[-1] as e:
            tap.is_ok(e.external_order_revision, None,
                      'external_order_revision empty')


async def test_rm_list(tap, dataset):
    with tap:
        order = await dataset.order()
        tap.ok(order, 'ордер создан')

        events = await dataset.OrderEvent.list_top(shard_limit=3)
        tap.isa_ok(events, list, 'Записи в топе получены')
        tap.ok(len(events) > 0, 'есть записи')

        res = await dataset.OrderEvent.rm_list(events)
        tap.isa_ok(res, list, 'Записи удалены')

        tap.eq(
            {(e.shardno, e.serial): e.order_id for e in res },
            {(e.shardno, e.serial): e.order_id for e in events },
            'Удалены все записи что запрошены к удалению')
