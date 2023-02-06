from stall.model.event_cache import EventCache

async def test_evcache_order(tap, dataset):
    with tap.plan(11):
        order = await dataset.order(store_job_event=True)
        events = await EventCache.list(
            tbl='orders',
            pk=order.order_id,
            by='object',
            db={'shard': order.shardno},
            full=True)

        tap.ok(events.list, f'События получены {len(events.list)}')
        for i, e in enumerate(events.list):
            tap.ne(e.shardno, None, 'Номер шарда определён')

            if e.type == 'lp':
                lpe = [x for x in e.events if x['type'] == 'lp']
                tap.ok(lpe, 'Есть lp-отправки')

                lpes = [x for x in lpe if x['key'][-1] == order.store_id]
                tap.ok(lpes, f'Есть отправки по складу {i}')

            if e.type == 'queue':
                qe = [x for x in events.list[i].events if x['type'] == 'queue']
                tap.ok(qe, 'есть queue таски')

                tap.ok(qe, 'Есть задания в очередь')

            with tap.subtest(5, 'загрузка') as taps:

                loaded = await EventCache.load(e.serial,
                                               db={'shard': e.shardno})
                taps.ok(loaded, 'Загружен по id с шарда')
                taps.eq(loaded.shardno, e.shardno, 'shardno')

                shardno = e.shardno

                taps.ok(await loaded.rm(), 'удалено')
                taps.eq(loaded.shardno, None, 'шард больше не определён')
                taps.ok(not await EventCache.load(e.serial,
                                                  db={'shard': shardno}),
                        'в БД не осталось')
