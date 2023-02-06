# pylint: disable=too-many-statements

from stall.model.event_cache import EventCache


async def test_suggest_events(tap, dataset):
    with tap.plan(7, 'События для отправки в монгу'):
        order = await dataset.order()
        tap.ok(order, 'Ордер создан')

        suggest = await dataset.suggest(order=order)
        tap.ok(order, 'Саджест создан и сохранен')

        candidates = await EventCache.list(
            tbl='suggests',
            pk=suggest.order_id,
            by='object',
            db={'shard': suggest.shardno},
            full=True
        )
        tap.eq_ok(len(candidates.list), 0, 'Групп событий нет')

        tap.ok(await suggest.save(), 'саджест пересохранён')
        candidates = await EventCache.list(
            tbl='suggests',
            pk=suggest.order_id,
            by='object',
            db={'shard': suggest.shardno},
            full=True
        )
        tap.eq_ok(len(candidates.list), 2, '2 группы событий добавилось')
        candidates = {it.type: it for it in candidates.list}

        with tap.subtest(2, 'Проверка событий queue') as taps:
            taps.eq_ok(len(candidates['queue'].events), 1, '1 событие в группе')
            event = candidates['queue'].events[0]
            taps.eq_ok(event['type'], 'queue', 'queue.events.0.type')

        with tap.subtest(5, 'Проверка событий lp') as taps:
            taps.eq_ok(len(candidates['lp'].events), 1, '1 событие в группе')
            event = candidates['lp'].events[0]
            taps.eq_ok(event['type'], 'lp', 'lp.events.0.type')
            taps.eq_ok(event['key'], ['order', 'store', order.store_id],
                       'lp.events.0.key')
            taps.eq_ok(event['data']['type'], 'suggest',
                       'lp.events.0.data.type')
            taps.eq_ok(event['data']['suggest_id'], suggest.suggest_id,
                       'Внутри sql подставляется созданный id')
