import inspect

from stall.model.event_cache import (
    EventCache,
    EventLP,
    EventQueue,
    EVENT_TYPES,
)


async def test_top_candidates(tap, dataset, uuid):
    with tap:
        cluster = dataset.Cluster(title=uuid())
        await cluster.save(
            events=[
                EventLP(
                    key=[uuid()],
                    data={'some_key': 'some_value'},
                ),
                EventQueue.create(
                    tube='job',
                    caller=inspect.stack()[1],
                    callback='stall.keyword.noun',
                )
            ]
        )
        tap.ok(cluster, 'Кластер создан')

        for shardno in range(EventCache.nshards()):
            candidates_only_shard = await EventCache.top_candidates(
                shard=shardno, limit=5,
            )
            tap.ok(
                candidates_only_shard,
                f'только с прокидываением шарда: {shardno}',
            )

            for ev_type in EVENT_TYPES:
                candidates = await EventCache.top_candidates(
                    shard=shardno, ev_type=ev_type, limit=5,
                )

                if not candidates:
                    continue

                tap.ok(len(candidates) <= 5, 'не больше лимита')

                serials = [i.serial for i in candidates]
                tap.eq(
                    serials,
                    sorted(serials),
                    f'в правильном порядке: {shardno}: {ev_type}',
                )

                ev_types = set(i.type for i in candidates)
                tap.eq(
                    ev_types,
                    set([ev_type]),
                    f'корректный тип: {shardno}: {ev_type}',
                )
