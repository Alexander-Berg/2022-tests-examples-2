# pylint: disable=invalid-name,too-many-statements

from libstall import cfg

from .record import ShardedRecord


async def test_list_look_desc(tap, uuid):
    with tap.plan(39):

        group = uuid()

        items = []
        for i in range(10):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.serial)
        items.reverse()

        tap.note('Начало получения')
        cursor = await ShardedRecord.list(
            by='look',
            conditions=[('group', group)],
            limit=5,

            # Игнорируется
            sort='test_id',
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.shards[0].direction,
                   'DESC', 'Направление установлено')
            tap.eq(
                [x.serial for x in cursor.list],
                [x.serial for x in items[0:5]],
                'Все отсортированные записи получены'
            )

        tap.note('Вторая итерация')
        cursor = await ShardedRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,

            # Игнорируется уже созданным курсором
            limit=6,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.shards[0].direction,
                   'DESC', 'Направление установлено')
            tap.eq(
                [x.serial for x in cursor.list],
                [x.serial for x in items[5:10]],
                'Все отсортированные записи получены'
            )

        tap.note('Все забрали')
        cursor = await ShardedRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.shards[0].direction,
                   'DESC', 'Направление установлено')
            tap.eq(
                [x.test_id for x in cursor.list],
                [],
                'Больше данных для просмотра нет'
            )

        tap.note('Что-то поменялось')
        tap.ok(await items[6].save(), 'Изменилось')
        tap.ok(await items[0].save(), 'Изменилось')
        tap.ok(await items[2].save(), 'Изменилось')

        tap.note('На изменения не реагирует')
        cursor = await ShardedRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.shards[0].direction,
                   'DESC', 'Направление установлено')
            tap.eq(
                [x.test_id for x in cursor.list],
                [],
                'Больше данных для просмотра нет'
            )

        tap.note('Добавились новые строки')
        with ShardedRecord({'value': '11', 'group': group}) as item:
            await item.save()
            items.append(item)
        with ShardedRecord({'value': '12', 'group': group}) as item:
            await item.save()
            items.append(item)
        items.sort(key=lambda x: x.serial)
        items.reverse()

        tap.note('Новые строки уже не войдут в выборку')
        cursor = await ShardedRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.shards[0].direction,
                   'DESC', 'Направление установлено')
            tap.eq(
                [x.serial for x in cursor.list],
                [],
                'Новых строк нет'
            )


async def test_list_look_asc(tap, uuid):
    with tap.plan(46):

        group = uuid()

        items = []
        for i in range(10):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.serial)

        tap.note('Начало получения')
        cursor = await ShardedRecord.list(
            by='look',
            conditions=[('group', group)],
            limit=5,
            direction='ASC',

            # Игнорируется
            sort='test_id',
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.shards[0].direction,
                   'ASC', 'Направление установлено')
            tap.eq(
                [x.serial for x in cursor.list],
                [x.serial for x in items[0:5]],
                'Все отсортированные записи получена'
            )

        tap.note('Вторая итерация')
        cursor = await ShardedRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,

            # Игнорируется уже созданным курсором
            limit=6,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.shards[0].direction,
                   'ASC', 'Направление установлено')
            tap.eq(
                [x.serial for x in cursor.list],
                [x.serial for x in items[5:10]],
                'Все отсортированные записи получена'
            )

        tap.note('Все забрали')
        cursor = await ShardedRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.shards[0].direction,
                   'ASC', 'Направление установлено')
            tap.eq(
                [x.test_id for x in cursor.list],
                [],
                'Больше данных для просмотра нет'
            )

        tap.note('Что-то поменялось')
        tap.ok(await items[6].save(), 'Изменилось')
        tap.ok(await items[0].save(), 'Изменилось')
        tap.ok(await items[2].save(), 'Изменилось')

        tap.note('На изменения не реагирует')
        cursor = await ShardedRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.shards[0].direction,
                   'ASC', 'Направление установлено')
            tap.eq(
                [x.test_id for x in cursor.list],
                [],
                'Больше данных для просмотра нет'
            )

        tap.note('Добавились новые строки')
        new = []
        with ShardedRecord({'value': '11', 'group': group}) as item:
            await item.save()
            new.append(item)
        with ShardedRecord({'value': '12', 'group': group}) as item:
            await item.save()
            new.append(item)
        new.sort(key=lambda x: x.serial)

        tap.note('Новые строки получены')
        cursor = await ShardedRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.shards[0].direction,
                   'ASC', 'Направление установлено')
            tap.eq(
                [x.serial for x in cursor.list],
                [x.serial for x in new],
                'Все отсортированные записи получены'
            )

        tap.note('Опять нет новых изменений')
        cursor = await ShardedRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.shards[0].direction,
                   'ASC', 'Направление установлено')
            tap.eq(
                [x.test_id for x in cursor.list],
                [],
                'Больше данных для просмотра нет'
            )


async def test_list_look_force_limit(tap, uuid):
    with tap.plan(8):

        group = uuid()

        items = []
        for i in range(cfg('cursor.limit') + 1):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.serial)

        tap.note('Начало получения')
        cursor = await ShardedRecord.list(
            by='look',
            conditions=[('group', group)],
            direction='ASC',
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, cfg('cursor.limit'), 'Лимит установлен')
            tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
            tap.eq(cursor.shards[0].direction,
                   'ASC', 'Направление установлено')
            tap.eq(
                [x.serial for x in cursor.list],
                [x.serial for x in items[0:cfg('cursor.limit')]],
                'Все отсортированные записи получена'
            )
