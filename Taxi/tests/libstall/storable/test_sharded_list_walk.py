# pylint: disable=invalid-name,too-many-statements,too-many-lines

from datetime import timedelta

from .record import ShardedRecord


async def test_simple(tap, uuid):
    with tap.plan(3, 'Простое получение данных по списку'):

        group = uuid()

        items = []
        for i in range(10):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)
        items.sort(key=lambda x: (x.value, x.serial))
        items.reverse()

        with tap.subtest(10, 'Первая порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                limit=5,
                sort=[('value', 'DESC'), ('serial', 'DESC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'DESC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [x.test_id for x in items[0:5]],
                    'Все отсортированные записи получены'
                )

        with tap.subtest(10, 'Последняя порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('value', 'DESC'), ('serial', 'DESC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'DESC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [x.test_id for x in items[5:10]],
                    'Все отсортированные записи получены'
                )

        with tap.subtest(10, 'Все забрали') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('value', 'DESC'), ('serial', 'DESC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'DESC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [],
                    'Больше данных для просмотра нет'
                )


async def test_serialization(tap, uuid):
    with tap.plan(3, 'Исползуем сериализованный курсор'):

        group = uuid()

        items = []
        for i in range(10):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)
        items.sort(key=lambda x: (x.value, x.serial))
        items.reverse()

        with tap.subtest(10, 'Первая порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                limit=5,
                sort=[('value', 'DESC'), ('serial', 'DESC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'DESC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [x.test_id for x in items[0:5]],
                    'Все отсортированные записи получены'
                )

        with tap.subtest(10, 'Последняя порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor_str=cursor.cursor_str,
                sort=[('value', 'DESC'), ('serial', 'DESC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'DESC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [x.test_id for x in items[5:10]],
                    'Все отсортированные записи получены'
                )

        with tap.subtest(10, 'Все забрали') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor_str=cursor.cursor_str,
                sort=[('value', 'DESC'), ('serial', 'DESC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'DESC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [],
                    'Больше данных для просмотра нет'
                )


async def test_limit(tap, uuid):
    with tap.plan(2, 'Лимит задается на первой итерации'):

        group = uuid()

        items = []
        for i in range(10):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)
        items.sort(key=lambda x: (x.value, x.serial))

        with tap.subtest(10, 'Первая порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                limit=2,
                sort=[('value', 'ASC'), ('serial', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 2, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [x.test_id for x in items[0:2]],
                    'Все отсортированные записи получены'
                )

        with tap.subtest(10, 'Последняя порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('value', 'ASC'), ('serial', 'ASC')],

                # Игнорируется уже созданным курсором
                limit=100,
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 2, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [x.test_id for x in items[2:4]],
                    'Все отсортированные записи получены'
                )


async def test_serial_asc(tap, uuid):
    with tap.plan(4, 'Проверяем что можем пройти базу по serial ASC'):

        group = uuid()

        items = []
        for i in range(10):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)
        items.sort(key=lambda x: x.serial)

        with tap.subtest(8, 'Первая порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                limit=5,
                sort=[('serial', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'serial', 'serial')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                # serial раскидан по шардам и может повторятся, поэтому
                # не проверяем тут порядок
                _tap.eq(len(cursor.list), 5, 'Выбраны записи по лимиту')

        with tap.subtest(4, 'Данные изменились') as _tap:
            _tap.ok(await items[6].save(), 'Изменилось')
            _tap.ok(await items[0].save(), 'Изменилось')
            _tap.ok(await items[2].save(), 'Изменилось')
            _tap.ok(await items[9].save(), 'Изменилось')

        with tap.subtest(8, 'Последняя порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('serial', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'serial', 'serial')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                # serial раскидан по шардам и может повторятся, поэтому
                # не проверяем тут порядок
                _tap.eq(len(cursor.list), 5, 'Выбраны записи по лимиту')

        with tap.subtest(8, 'Все забрали') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('serial', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'serial', 'serial')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    # serial раскидан по шардам и может повторятся, поэтому
                    # не проверяем тут порядок
                    set(x.test_id for x in cursor.list),
                    set(),
                    'Больше данных для просмотра нет'
                )


async def test_serial_desc(tap, uuid):
    with tap.plan(4, 'Проверяем что можем пройти базу по serial DESC'):

        group = uuid()

        items = []
        for i in range(10):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)
        items.sort(key=lambda x: x.serial)
        items.reverse()

        with tap.subtest(8, 'Первая порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                limit=5,
                sort=[('serial', 'DESC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'serial', 'serial')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                # serial раскидан по шардам и может повторятся, поэтому
                # не проверяем тут порядок
                _tap.eq(len(cursor.list), 5, 'Выбраны записи по лимиту')

        with tap.subtest(4, 'Данные изменились') as _tap:
            _tap.ok(await items[6].save(), 'Изменилось')
            _tap.ok(await items[0].save(), 'Изменилось')
            _tap.ok(await items[2].save(), 'Изменилось')
            _tap.ok(await items[9].save(), 'Изменилось')

        with tap.subtest(8, 'Последняя порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('serial', 'DESC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'serial', 'serial')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                # serial раскидан по шардам и может повторятся, поэтому
                # не проверяем тут порядок
                _tap.eq(len(cursor.list), 5, 'Выбраны записи по лимиту')

        with tap.subtest(8, 'Все забрали') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('serial', 'DESC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'serial', 'serial')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                _tap.eq(
                    # serial раскидан по шардам и может повторятся, поэтому
                    # не проверяем тут порядок
                    set(x.test_id for x in cursor.list),
                    set(),
                    'Больше данных для просмотра нет'
                )


async def test_lsn_asc(tap, uuid):
    with tap.plan(6, 'Проверяем что можем пройти базу по lsn ASC'):

        group = uuid()

        items = []
        for i in range(10):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)
        items.sort(key=lambda x: x.lsn)

        with tap.subtest(8, 'Первая порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                limit=5,
                sort=[('lsn', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'lsn', 'lsn')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(len(cursor.list), 5, 'Выбраны записи по лимиту')

        with tap.subtest(8, 'Последняя порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('lsn', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'lsn', 'lsn')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(len(cursor.list), 5, 'Выбраны записи по лимиту')

        with tap.subtest(8, 'Все забрали') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('lsn', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'lsn', 'lsn')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    # lsn раскидан по шардам и может повторятся, поэтому
                    # не проверяем тут порядок
                    set(x.test_id for x in cursor.list),
                    set(),
                    'Больше данных для просмотра нет'
                )

        with tap.subtest(3, 'Данные изменились') as _tap:
            _tap.ok(await items[6].save(), 'Изменилось')
            _tap.ok(await items[0].save(), 'Изменилось')
            _tap.ok(await items[2].save(), 'Изменилось')

            changed = [items[6], items[0], items[2]]
            changed.sort(key=lambda x: x.lsn)

        with tap.subtest(8, 'Новые изменения получены') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('lsn', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'lsn', 'lsn')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    # lsn раскидан по шардам и может повторятся, поэтому
                    # не проверяем тут порядок
                    set(x.test_id for x in cursor.list),
                    set(x.test_id for x in changed),
                    'Изменения получены и в правильном порядке'
                )

        with tap.subtest(8, 'Опять нет новых изменений') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('lsn', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'lsn', 'lsn')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    # lsn раскидан по шардам и может повторятся, поэтому
                    # не проверяем тут порядок
                    set(x.test_id for x in cursor.list),
                    set(),
                    'Больше данных для просмотра нет'
                )


async def test_empty(tap, uuid):
    with tap.plan(2, 'Пустой список'):

        group = uuid()

        with tap.subtest(11, 'Нет данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                sort=[('value', 'ASC'), ('serial', 'ASC')],
                limit=5,
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].values,
                        None, 'Курсор не инициализирован')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [],
                    'Данных нет'
                )

        items = []
        for i in range(3):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)
        items.sort(key=lambda x: (x.value, x.serial))

        with tap.subtest(10, 'Данные получены') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('value', 'ASC'), ('serial', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [x.test_id for x in items],
                    'Все отсортированные записи получены'
                )


async def test_repeats(tap, uuid):
    with tap.plan(3, 'Данные не уникальны по первому ключу, только со вторым'):

        group = uuid()

        items = []
        for _ in range(7):
            with ShardedRecord({'value': 'AAA', 'group': group}) as item:
                await item.save()
                items.append(item)
        for _ in range(3):
            with ShardedRecord({'value': 'BBB', 'group': group}) as item:
                await item.save()
                items.append(item)
        items.sort(key=lambda x: (x.value, x.serial))

        with tap.subtest(10, 'Первая порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                limit=5,
                sort=[('value', 'ASC'), ('serial', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    # сравнение сортировкой не работает т.к. ключ не уникален
                    set(x.test_id for x in cursor.list),
                    set(x.test_id for x in items[0:5]),
                    'Все отсортированные записи получены'
                )

        with tap.subtest(10, 'Последняя порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('value', 'ASC'), ('serial', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    # сравнение сортировкой не работает т.к. ключ не уникален
                    set(x.test_id for x in cursor.list),
                    set(x.test_id for x in items[5:10]),
                    'Все отсортированные записи получены'
                )

        with tap.subtest(10, 'Все забрали') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('value', 'ASC'), ('serial', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    # сравнение сортировкой не работает т.к. ключ не уникален
                    set(x.test_id for x in cursor.list),
                    set(),
                    'Больше данных для просмотра нет'
                )


async def test_random(tap, uuid):
    with tap.plan(3, 'Ключи могут никак не кореллировать'):

        group = uuid()

        items = []
        for i in [
            'C', 'T', 'S', 'Q', 'O', 'J', 'K', 'F', 'E', 'A', 'B', 'L', 'V'
        ]:
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)
        items.sort(key=lambda x: (x.value, x.serial))

        with tap.subtest(10, 'Первая порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                limit=10,
                sort=[('value', 'ASC'), ('serial', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 10, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [x.test_id for x in items[0:10]],
                    'Все отсортированные записи получены'
                )

        with tap.subtest(10, 'Последняя порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('value', 'ASC'), ('serial', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 10, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [x.test_id for x in items[10:20]],
                    'Все отсортированные записи получены'
                )

        with tap.subtest(10, 'Все забрали') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[('value', 'ASC'), ('serial', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 10, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [],
                    'Больше данных для просмотра нет'
                )


async def test_random3(tap, uuid):
    with tap.plan(3, 'Еще больше рандомных ключей сортировки'):

        group = uuid()

        items = []
        values          = [9, 6, 2, 9, 3, 4, 8, 2, 9, 6, 3, 8, 1]
        second_values   = [8, 4, 0, 1, 7, 3, 1, 5, 2, 3, 1, 9, 2]
        for i in range(len(values)):  # pylint: disable=consider-using-enumerate
            with ShardedRecord({
                    'value':        str(values[i]),
                    'second_value': str(second_values[i]),
                    'group': group,
            }) as item:
                await item.save()
                items.append(item)
        items.sort(key=lambda x: (-int(x.value), x.second_value, x.serial))

        with tap.subtest(12, 'Первая порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                limit=10,
                sort=[
                    ('value', 'DESC'),
                    ('second_value', 'ASC'),
                    ('serial', 'ASC'),
                ],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 10, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'second_value', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[2][0],
                        'serial', 'третий ключ')
                _tap.eq(cursor.shards[0].sort[2][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [x.test_id for x in items[0:10]],
                    'Все отсортированные записи получены'
                )

        with tap.subtest(12, 'Последняя порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[
                    ('value', 'DESC'),
                    ('second_value', 'ASC'),
                    ('serial', 'ASC'),
                ],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 10, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'second_value', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[2][0],
                        'serial', 'третий ключ')
                _tap.eq(cursor.shards[0].sort[2][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [x.test_id for x in items[10:20]],
                    'Все отсортированные записи получены'
                )

        with tap.subtest(12, 'Все забрали') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[
                    ('value', 'DESC'),
                    ('second_value', 'ASC'),
                    ('serial', 'ASC'),
                ],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 10, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'second_value', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[2][0],
                        'serial', 'третий ключ')
                _tap.eq(cursor.shards[0].sort[2][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [],
                    'Больше данных для просмотра нет'
                )


async def test_non_random3(tap, uuid):
    with tap.plan(3, 'Частично не уникальный ключ'):

        group = uuid()

        items = []
        for _ in range(15):
            with ShardedRecord({
                    'value':        '1',
                    'second_value': '2',
                    'group': group,
            }) as item:
                await item.save()
                items.append(item)
        items.sort(key=lambda x: (-int(x.value), x.second_value, x.serial))

        with tap.subtest(12, 'Первая порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                limit=10,
                sort=[
                    ('value', 'DESC'),
                    ('second_value', 'ASC'),
                    ('serial', 'ASC'),
                ],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 10, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'second_value', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[2][0],
                        'serial', 'третий ключ')
                _tap.eq(cursor.shards[0].sort[2][1],
                        'ASC', 'Направление установлено')
                # serial раскидан по шардам и может повторятся, поэтому
                # не проверяем тут порядок
                _tap.eq(len(cursor.list), 10, 'Выбраны записи по лимиту')

        with tap.subtest(12, 'Последняя порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[
                    ('value', 'DESC'),
                    ('second_value', 'ASC'),
                    ('serial', 'ASC'),
                ],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 10, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'second_value', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[2][0],
                        'serial', 'третий ключ')
                _tap.eq(cursor.shards[0].sort[2][1],
                        'ASC', 'Направление установлено')
                # serial раскидан по шардам и может повторятся, поэтому
                # не проверяем тут порядок
                _tap.eq(len(cursor.list), 5, 'Выбраны записи по лимиту')

        with tap.subtest(12, 'Все забрали') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor=cursor,
                sort=[
                    ('value', 'DESC'),
                    ('second_value', 'ASC'),
                    ('serial', 'ASC'),
                ],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 10, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'value', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'DESC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'second_value', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[2][0],
                        'serial', 'третий ключ')
                _tap.eq(cursor.shards[0].sort[2][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [],
                    'Больше данных для просмотра нет'
                )


async def test_random_sum_uniq_key(tap, cfg, uuid):
    with tap.plan(1, 'составной уникальный ключ'):
        cfg.set('cursor.limit', 5)

        group = uuid()

        items = []
        cnt = 4
        for i in range(cnt*cnt):
            with ShardedRecord(
                    {
                        'value': str(i // cnt),
                        'second_value': str(i % cnt),
                        'group': group,
                    }
            ) as item:
                await item.save()
                items.append(item)
        items.sort(key=lambda x: (x.value, -int(x.second_value), x.serial))

        values = set(range(cnt)) - {1, 4}
        second_values = set(range(cnt)) - {3}
        values = [str(i) for i in values]
        second_values = [str(i) for i in second_values]
        items_walk = []
        async for item in ShardedRecord.ilist(
            by='walk',
            conditions=(
                ('group', group),
                ('test_id', [
                 x.test_id for x in items if x.value
                 in values and x.second_value in second_values]),
            ),
            sort=['value', ('second_value', 'DESC'), 'serial'],
        ):
            items_walk.append(item)

        tap.eq(
            len(items_walk),
            len(values)*len(second_values),
            'вытащили всё'
        )


async def test_datetime(tap, uuid, now):
    with tap.plan(3, 'Список сортированный по времени'):

        group = uuid()

        _now = now()

        items = []
        for i in range(10):
            with ShardedRecord({
                # Иначе записи все создадутся в одну секунду и тест станет
                # бессмысленным и флапающим
                'created': _now + timedelta(minutes=i),
                'value': str(i),
                'group': group,
            }) as item:
                await item.save()
                items.append(item)
        items.sort(key=lambda x: (x.created, x.serial))

        with tap.subtest(10, 'Первая порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                limit=5,
                sort=[('created', 'ASC'), ('serial', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'created', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [x.test_id for x in items[0:5]],
                    'Все отсортированные записи получены'
                )

        with tap.subtest(10, 'Последняя порция данных') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor_str=cursor.cursor_str,
                sort=[('created', 'ASC'), ('serial', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'created', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [x.test_id for x in items[5:10]],
                    'Все отсортированные записи получены'
                )

        with tap.subtest(10, 'Все забрали') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                cursor_str=cursor.cursor_str,
                sort=[('created', 'ASC'), ('serial', 'ASC')],
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(cursor.type, 'walk', 'Тип walk')
                _tap.ok(cursor.time, 'Время установлено')
                _tap.eq(cursor.limit, 5, 'Лимит установлен')
                _tap.ok(len(cursor.shards) > 1, 'Тест с шардированием')
                _tap.eq(cursor.shards[0].sort[0][0],
                        'created', 'первый ключ')
                _tap.eq(cursor.shards[0].sort[0][1],
                        'ASC', 'Направление установлено')
                _tap.eq(cursor.shards[0].sort[1][0],
                        'serial', 'второй ключ')
                _tap.eq(cursor.shards[0].sort[1][1],
                        'ASC', 'Направление установлено')
                _tap.eq(
                    [x.test_id for x in cursor.list],
                    [],
                    'Больше данных для просмотра нет'
                )


async def test_default_limit(tap, uuid, cfg):
    with tap.plan(2, 'По умолчанию лимит берется стандартный'):

        cursor = await ShardedRecord.list(
            by='walk',
            conditions=[('group', uuid())],
            sort=[('serial', 'ASC')],
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.limit, cfg('cursor.limit'), 'Лимит установлен')


async def test_sort_str(tap, uuid):
    with tap.plan(3, 'Простое задание сортировки строкой'):

        cursor = await ShardedRecord.list(
            by='walk',
            conditions=[('group', uuid())],
            sort='serial',
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.shards[0].sort[0][0], 'serial', 'serial')
            tap.eq(cursor.shards[0].sort[0][1], 'ASC', 'по умолчанию ASC')


async def test_sort_strs(tap, uuid):
    with tap.plan(5, 'Простое задание сортировки строками'):

        cursor = await ShardedRecord.list(
            by='walk',
            conditions=[('group', uuid())],
            sort=['value', 'serial'],
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.shards[0].sort[0][0], 'value', 'value')
            tap.eq(cursor.shards[0].sort[0][1], 'ASC', 'по умолчанию ASC')
            tap.eq(cursor.shards[0].sort[1][0], 'serial', 'serial')
            tap.eq(cursor.shards[0].sort[1][1], 'ASC', 'по умолчанию ASC')


async def test_sort_tuple(tap, uuid):
    with tap.plan(3, 'Простое задание сортировки таплом'):

        cursor = await ShardedRecord.list(
            by='walk',
            conditions=[('group', uuid())],
            sort=[('serial')],
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.shards[0].sort[0][0], 'serial', 'serial')
            tap.eq(cursor.shards[0].sort[0][1], 'ASC', 'по умолчанию ASC')


async def test_sort_tuples(tap, uuid):
    with tap.plan(5, 'Простое задание сортировки таплами'):

        cursor = await ShardedRecord.list(
            by='walk',
            conditions=[('group', uuid())],
            sort=[('value'), ('serial')],
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.shards[0].sort[0][0], 'value', 'value')
            tap.eq(cursor.shards[0].sort[0][1], 'ASC', 'по умолчанию ASC')
            tap.eq(cursor.shards[0].sort[1][0], 'serial', 'serial')
            tap.eq(cursor.shards[0].sort[1][1], 'ASC', 'по умолчанию ASC')
