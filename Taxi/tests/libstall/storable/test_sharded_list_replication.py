# pylint: disable=invalid-name,too-many-statements

from libstall import cfg
from .record import ShardedRecord


async def test_list_replication(tap, uuid):
    with tap.plan(30):

        group = uuid()

        items = []
        for i in range(10):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.lsn)

        tap.note('Начало получения')
        cursor = await ShardedRecord.list(
            by='replication',
            conditions=[('group', group)],
            limit=5,

            # Игнорируется
            sort='test_id',
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'replication', 'Тип replication')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(
                [x.lsn for x in cursor.list],
                [x.lsn for x in items[0:5]],
                'Все отсортированные записи получена'
            )

        tap.note('Вторая итерация')
        cursor = await ShardedRecord.list(
            by='replication',
            conditions=[('group', group)],
            cursor=cursor,

            # Игнорируется уже созданным курсором
            limit=6,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'replication', 'Тип replication')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.eq(
                [x.lsn for x in cursor.list],
                [x.lsn for x in items[5:10]],
                'Все отсортированные записи получена'
            )

        tap.note('Все забрали')
        cursor = await ShardedRecord.list(
            by='replication',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'replication', 'Тип replication')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.eq(
                [x.lsn for x in cursor.list],
                [],
                'Больше данных для репликации нет'
            )

        tap.note('Что-то поменялось')
        tap.ok(await items[6].save(), 'Изменилось')
        tap.ok(await items[0].save(), 'Изменилось')
        tap.ok(await items[2].save(), 'Изменилось')

        changed = [items[6], items[0], items[2]]
        changed.sort(key=lambda x: x.lsn)

        tap.note('Новые изменения получены')
        cursor = await ShardedRecord.list(
            by='replication',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'replication', 'Тип replication')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.eq(
                [x.lsn for x in cursor.list],
                [x.lsn for x in changed],
                'Изменения получены и в правильном порядке'
            )

        tap.note('Опять нет новых изменений')
        cursor = await ShardedRecord.list(
            by='replication',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'replication', 'Тип replication')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.eq(
                [x.lsn for x in cursor.list],
                [],
                'Больше данных для репликации нет'
            )


async def test_list_replication_force_limit(tap, uuid):
    with tap.plan(7):

        group = uuid()

        items = []
        for i in range(cfg('cursor.limit') + 1):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.lsn)

        cursor = await ShardedRecord.list(
            by='replication',
            conditions=[('group', group)],
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'replication', 'Тип replication')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, cfg('cursor.limit'), 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(
                [x.lsn for x in cursor.list],
                [x.lsn for x in items[:cfg('cursor.limit')]],
                'Все отсортированные записи получена'
            )


async def test_list_replication_now(tap, uuid):
    with tap.plan(20, 'Репликация от текущего времени'):

        group = uuid()

        items = []
        for i in range(10):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.lsn)

        cursor = await ShardedRecord.list(
            by='replication',
            conditions=[('group', group)],
            limit=5,
            cursor_str='now',
        )

        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'replication', 'Тип replication')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.list, [],  'Первый запрос всегда пустой')

        items = []
        for i in range(3):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.lsn)

        cursor = await ShardedRecord.list(
            by='replication',
            conditions=[('group', group)],
            limit=5,
            cursor=cursor,
        )

        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'replication', 'Тип replication')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(
                [x.lsn for x in cursor.list],
                [x.lsn for x in items[0:3]],
                'Все отсортированные записи получена'
            )

        cursor = await ShardedRecord.list(
            by='replication',
            conditions=[('group', group)],
            limit=5,
            cursor=cursor,
        )

        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'replication', 'Тип replication')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.list, [], 'Все получено')


async def test_list_replication_now_empty(tap, uuid):
    with tap.plan(13, 'Репликация от текущего времени с пустыми данными'):

        group = uuid()

        cursor = await ShardedRecord.list(
            by='replication',
            conditions=[('group', group)],
            limit=5,
            cursor_str='now',
        )

        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'replication', 'Тип replication')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.list, [],  'Первый запрос всегда пустой')

        items = []
        for i in range(3):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.lsn)

        cursor = await ShardedRecord.list(
            by='replication',
            conditions=[('group', group)],
            limit=5,
            cursor=cursor,
        )

        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'replication', 'Тип replication')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(
                [x.lsn for x in cursor.list],
                [x.lsn for x in items[0:3]],
                'Все отсортированные записи получена'
            )
