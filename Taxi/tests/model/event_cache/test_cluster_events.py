from stall.model.event_cache import EventCache, EventLP

async def test_save_events(tap, dataset, uuid):
    with tap.plan(10, 'Проверим сохранение ивентов'):
        key = [uuid()]
        cluster = await dataset.Cluster(title=uuid()).save(
            events=[
                EventLP(
                    key=key,
                    data={
                        'some_key': 'some_value',
                    }
                )
            ]
        )
        tap.ok(cluster, 'Кластер создан')

        candidates = await EventCache.list(
            tbl='clusters',
            pk=cluster.cluster_id,
            by='object',
            db={'shard': cluster.shardno},
            full=True
        )
        tap.eq_ok(len(candidates.list), 1, 'Создана 1 обёртка для ивентов')
        with candidates.list[0] as event_cache:
            tap.eq_ok(event_cache['tbl'], 'clusters', 'tbl')
            tap.eq_ok(event_cache['pk'], cluster.cluster_id, 'pk')
            tap.eq_ok(len(event_cache['events']), 1, 'Создан 1 ивент')

            event = event_cache['events'][0]
            tap.eq_ok(event['type'], 'lp', 'events.0.type')
            tap.eq_ok(event['key'], key, 'events.0.key')
            tap.ok(event['data'], 'events.0.data')
            tap.eq_ok(event['data']['some_key'], 'some_value',
                      'events.0.data.some_key')
            tap.eq_ok(event['data']['cluster_id'], cluster.cluster_id,
                      'В sql подставляется сохранённый id')

async def test_save_events_pk_field(tap, dataset, uuid):
    with tap.plan(5, 'Проверим сохранение ивентов c другим pk'):
        title = uuid()
        cluster = await dataset.Cluster(title=title).save(
            events=[
                EventLP(
                    key=(uuid(), ),
                    data={
                        'some_key': 'some_value',
                    }
                )
            ],
            events_pk_field='title'
        )
        tap.ok(cluster, 'Кластер создан')

        candidates = await EventCache.list(
            tbl='clusters',
            pk=cluster.title,
            by='object',
            db={'shard': cluster.shardno},
            full=True
        )
        tap.eq_ok(len(candidates.list), 1, 'Создана 1 обёртка для ивентов')
        with candidates.list[0] as event_cache:
            tap.eq_ok(event_cache['tbl'], 'clusters', 'tbl')
            tap.eq_ok(event_cache['pk'], cluster.title, 'pk')
            tap.eq_ok(len(event_cache['events']), 1, 'Создан 1 ивент')
