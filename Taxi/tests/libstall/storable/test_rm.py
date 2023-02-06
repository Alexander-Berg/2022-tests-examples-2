import pytest

from .record import ShardedRecord, ShardedRecordSerial


async def test_save_load_rm(tap):
    with tap.plan(5):
        item = ShardedRecord({'value': 'Vasya'})
        tap.ok(item, 'инстанцирован')
        tap.ok(await item.save(), 'сохранен')
        tap.ok(item.test_id, 'идентификатор назначен')

        loaded = await ShardedRecord.load(item.test_id)
        tap.ok(loaded, 'загружено')

        await loaded.rm()
        loaded = await ShardedRecord.load(item.test_id)
        tap.ok(not loaded, 'удалено')


@pytest.mark.parametrize('by', ['look', 'full', 'replication', 'walk'])
async def test_save_list_rm(tap, by, uuid):
    with tap.plan(2):
        group = uuid()

        items = [
            ShardedRecord({'value': 'Vasya', 'group': group})
            for _ in range(10)
        ]
        for item in items:
            await item.save()

        loaded = await ShardedRecord.list(
            by=by,
            conditions=('group', group),
        )
        tap.ok(len(loaded.list), 10, 'загружено')

        for item in loaded.list:
            await item.rm()
        loaded = await ShardedRecord.list(
            by='full',
            conditions=('group', group),
        )
        tap.ok(not loaded.list, 'удалено')


@pytest.mark.parametrize('by', ['look', 'full', 'replication', 'walk'])
async def test_save_list_rm_serial(tap, by, uuid):
    with tap.plan(2):
        group = uuid()
        items = [
            ShardedRecord({'value': f'Vasya{i}', 'group': group})
            for i in range(10)
        ]
        for item in items:
            await item.save()

        loaded = await ShardedRecordSerial.list(
            by=by,
            conditions=('group', group),
        )
        tap.ok(len(loaded.list), 10, 'загружено')

        for item in loaded.list:
            await item.rm()
        loaded = await ShardedRecordSerial.list(
            by=by,
            conditions=('group', group),
        )
        tap.ok(not loaded.list, 'удалено')
