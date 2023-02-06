from stall.model.event_cache import EventCache


async def test_events(tap, dataset):
    with tap.plan(20, 'тесты евентов при изменении estatus'):
        store = await dataset.store(status='active', estatus='processing')
        tap.eq((store.status, store.estatus),
               ('active', 'processing'),
               'склад создан')

        events = await EventCache.list(
            tbl='stores',
            pk=store.store_id,
            by='object',
            db={'shard': store.shardno},
            full=True)
        tap.ok(not events.list, 'при создании склада нет очередей/событий')

        store.estatus = 'inventory_begin'
        tap.ok(await store.save(), 'сохранён')

        events = await EventCache.list(
            tbl='stores',
            pk=store.store_id,
            by='object',
            db={'shard': store.shardno},
            full=True)
        tap.ok(events.list, 'при изменении estatus появились события')
        tap.eq(len(events.list), 2, 'две записи в кеше событий')

        events_by_type = {event.type: event for event in events.list}
        with events_by_type['queue'] as e:
            tap.isa_ok(e, EventCache, 'событие')

            q = [e for e in e.events if e['type'] == 'queue']
            lp = [e for e in e.events if e['type'] == 'lp']
            tap.eq(len(q), 1, 'одно событие для очереди')
            tap.eq(len(lp), 0, 'нет событий для lp')

            q = q[0]
            tap.isa_ok(q, dict, 'сообщение очереди')
            tap.isa_ok(q['data'], dict, 'data')
            tap.eq(q['tube'], 'job', 'очередь')
            tap.eq(q['data']['store_id'], store.store_id, 'store_id')
            tap.eq(q['data']['callback'],
                   'stall.model.store.Store.job_save',
                   'обработчик')

        with events_by_type['lp'] as e:
            tap.isa_ok(e, EventCache, 'событие')

            q = [e for e in e.events if e['type'] == 'queue']
            lp = [e for e in e.events if e['type'] == 'lp']

            tap.eq(len(q), 0, 'нет событий для очереди')
            tap.eq(len(lp), 1, 'одно событие для lp')

            lp = lp[0]
            tap.isa_ok(lp, dict, 'сообщение очереди')
            tap.isa_ok(lp['data'], dict, 'data')
            tap.eq(lp['data']['store_id'], store.store_id, 'store_id')
            tap.eq(lp['data']['type'], 'store', 'тип')
