from .record import ShardedRecord


async def test_save_load(tap):
    with tap.plan(7):
        item = ShardedRecord({'value': 'Vasya'})
        tap.ok(item, 'инстанцирован')
        tap.ok(await item.save(), 'сохранен')
        tap.ok(item.test_id, 'идентификатор назначен')
        tap.eq(item.shardno, int(item.test_id[-1]), 'номер шарда')
    #     tap.eq(item.shardno, item.shard, 'номер шарда на момент SQL')

        loaded = await ShardedRecord.load(item.test_id)
        tap.ok(loaded, 'загружено')
        tap.eq(loaded.test_id, item.test_id, 'идентификатор')
        tap.eq(loaded.shardno, item.shardno, 'номер шарда')
    #     tap.eq(loaded.shard, loaded.shardno, 'по ID и по SQL одинаковый')


async def test_save_load_shardno(tap):
    with tap.plan(9):
        item = ShardedRecord({'value': 'Vasya'})
        tap.ok(item, 'инстанцирован')
        tap.ok(await item.save(by='shard_as_value'), 'сохранен')
        tap.ok(item.test_id, 'идентификатор назначен')
        tap.eq(item.shardno, int(item.test_id[-1]), 'номер шарда')
        tap.eq(item.shardno, int(item.value), 'номер шарда на момент SQL')

        loaded = await ShardedRecord.load(item.test_id)
        tap.ok(loaded, 'загружено')
        tap.eq(loaded.test_id, item.test_id, 'идентификатор')
        tap.eq(loaded.shardno, item.shardno, 'номер шарда')
        tap.eq(int(loaded.value), loaded.shardno, 'по ID и по SQL одинаковый')


async def test_update_lsn(tap):
    with tap.plan(5):
        item = ShardedRecord({'value': 'Vasya'})
        tap.ok(item, 'инстанцирован')
        tap.ok(await item.save(), 'сохранен')
        tap.ok(item.lsn, 'lsn выставлен')

        item.value = 'Vasya2'
        old_lsn = item.lsn
        await item.save()

        tap.ok(item.lsn > old_lsn, 'lsn обновился')

        old_lsn = item.lsn
        await item.save(do_not_update_lsn=True)
        tap.eq_ok(item.lsn, old_lsn, 'lsn не обновился')


async def test_load_bad_key(tap, uuid):
    with tap.plan(3):
        loaded = await ShardedRecord.load(uuid()[:31])
        tap.ok(loaded is None, 'Объект не найден; ключ короче 32 символов')

        loaded = await ShardedRecord.load(uuid() + '1111')
        tap.ok(loaded is None, 'Объект не найден; ключ 36 символов')

        loaded = await ShardedRecord.load(uuid() + uuid())
        tap.ok(loaded is None, 'Объект не найден; ключ длиннее 36 символов')
