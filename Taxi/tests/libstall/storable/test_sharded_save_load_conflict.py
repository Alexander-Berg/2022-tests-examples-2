import uuid

# pylint: disable=unused-import
from libstall.model.storable import Attribute, Table
from libstall.model.storable.sharded import ShardedPg

from . import shard_schema


class ShardedConflictRecord(
        ShardedPg,
        table=Table(
            'conflicts',
            pkey='conflict_id',
            keys={
                'ekey': 'ekey',
            },
            conflict='ekey'
        )):
    database = 'tlibstall'

    conflict_id = Attribute(types=str, required=False)
    ekey        = Attribute(types=str,
                            required=True,
                            default=lambda: uuid.uuid4().hex)
    name        = Attribute(types=str, required=False, default='hello')

    shard_module = shard_schema


async def test_save_load(tap):

    tap.plan(9)

    item = ShardedConflictRecord({'name': 'Vasya'})
    tap.ok(item, 'инстанцирован')
    tap.ok(await item.save(), 'сохранен')
    tap.ok(item.conflict_id, 'идентификатор назначен')
    tap.eq(item.shardno, int(item.conflict_id[-1]), 'номер шарда')

    loaded = await ShardedConflictRecord.load(item.conflict_id)
    tap.ok(loaded, 'загружено')
    tap.eq(loaded.conflict_id, item.conflict_id, 'идентификатор')
    tap.eq(loaded.shardno, item.shardno, 'номер шарда')

    loaded = await ShardedConflictRecord.load(item.ekey, by='conflict')
    tap.ok(loaded, 'загружено')
    tap.eq(loaded.ekey, item.ekey, 'идентификатор')

    tap()
