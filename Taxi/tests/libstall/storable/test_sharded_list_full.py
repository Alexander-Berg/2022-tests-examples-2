# pylint: disable=invalid-name

from libstall import cfg
from .record import ShardedRecord


async def test_list_full(tap, uuid):
    with tap.plan(13):

        group = uuid()

        items = []
        for i in range(cfg('cursor.limit') + 1):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.test_id)

        cursor_unlimited = await ShardedRecord.list(
            by='full',
            conditions=[('group', group)],
            full=True,
            sort='test_id',
        )

        with cursor_unlimited as cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'full', 'Тип full')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, None, 'Лимит не установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(
                [x.test_id for x in cursor.list],
                [x.test_id for x in items],
                'Все отсортированные записи получена'
            )

        cursor_limited = await ShardedRecord.list(
            by='full',
            conditions=[('group', group)],
            full=True,
            sort='test_id',
            limit=5,
        )
        with cursor_limited as cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'full', 'Тип full')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(
                [x.test_id for x in cursor.list],
                [x.test_id for x in items][0:5],
                'Запрошенное количество записей получено'
            )
