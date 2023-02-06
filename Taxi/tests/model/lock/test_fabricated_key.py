from itertools import cycle
from stall.model.lock import Lock


async def test_schema(tap, cfg):
    """Локи по нашему id должны прилетать на тот же шард"""
    shards = int(cfg('pg.databases.main.nshards', 2))
    with tap.plan(3 * 5 * shards, 'Блокировка приходит на нужный шард'):
        shards_gen = cycle(range(shards))
        for _ in range(shards * 5):
            shard = next(shards_gen)
            name = Lock.shard_module.eid_for_shard(shard)
            lock = Lock({'name': name})
            tap.ok(lock, 'Создали блокировку')
            tap.ok(await lock.lock(), 'заблокировали блокировку')
            tap.eq(lock.shardno, shard, 'На том же шарде')
