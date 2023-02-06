from .record import PgRecord

# pylint: disable=unused-argument,too-many-statements


async def test_list(tap):
    with tap.plan(9):

        ids = []
        with tap.subtest(10 * 2, 'создаём записи') as taps:
            for i in range(10):
                with PgRecord({'value': str(i)}) as item:
                    taps.ok(item, 'Инстанцирован')
                    taps.ok(await item.save(), 'сохранён')
                    ids.append(item.test_id)

        tap.ok(ids, 'созданы записи')
        ids.sort()

        pager = await PgRecord.list(ids=ids, limit=5, sort='test_id')

        tap.ok(pager, 'получен список')
        tap.eq(
            [x.test_id for x in pager.list[0:5]],
            ids[0:5],
            'Порция отсортированных записей получена'
        )
        tap.ok(not pager.latest, 'не последняя страница')

        pager2 = await PgRecord.list(ids=ids, limit=5, sort='test_id', page=2)

        tap.ok(pager2, 'получен список страница 2')
        tap.eq(
            [x.test_id for x in pager2.list[0:5]],
            ids[5:10],
            'Порция отсортированных записей получена'
        )
        tap.ok(pager2.latest, 'последняя страница')

        tap.ne(
            pager2.list[0].test_id,
            pager.list[0].test_id,
            'Следующая страница с OFFSET'
        )


async def test_list_full(tap):
    with tap.plan(7):

        ids = []
        for i in range(10):
            with PgRecord({'value': str(i)}) as item:
                await item.save()
                ids.append(item.test_id)

        tap.ok(ids, 'созданы записи')
        ids.sort()

        cursor = await PgRecord.list(
            by='full',
            conditions=[
                {'name': 'test_id', 'value': ids},
            ],
            full=True,
            sort='test_id',
        )

        tap.ok(cursor, 'Курсор получен')
        tap.eq(cursor.type, 'full', 'Тип full')
        tap.ok(cursor.time, 'Время установлено')
        tap.eq(
            [x.test_id for x in cursor.list],
            ids,
            'Все отсортированные записи получена'
        )

        cursor_limited = await PgRecord.list(
            by='full',
            conditions=[
                {'name': 'test_id', 'value': ids},
            ],
            full=True,
            sort='test_id',
            limit=5,
        )
        tap.ok(cursor_limited, 'Курсор получен')
        tap.eq(
            [x.test_id for x in cursor_limited.list],
            ids[0:5],
            'Запрошенное количество записей получено'
        )


async def test_list_replication(tap, uuid):
    with tap.plan(29):

        group = uuid()

        items = []
        for i in range(10):
            with PgRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.lsn)

        tap.note('Начало получения')
        cursor = await PgRecord.list(
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
            tap.eq(
                [x.test_id for x in cursor.list],
                [x.test_id for x in items[0:5]],
                'Все отсортированные записи получена'
            )

        tap.note('Вторая итерация')
        cursor = await PgRecord.list(
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
                [x.test_id for x in cursor.list],
                [x.test_id for x in items[5:10]],
                'Все отсортированные записи получена'
            )

        tap.note('Все забрали')
        cursor = await PgRecord.list(
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
                [x.test_id for x in cursor.list],
                [],
                'Больше данных для репликации нет'
            )

        tap.note('Что-то поменялось')
        tap.ok(await items[6].save(), 'Изменилось')
        tap.ok(await items[0].save(), 'Изменилось')
        tap.ok(await items[2].save(), 'Изменилось')

        tap.note('Новые изменения получены')
        cursor = await PgRecord.list(
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
                [x.test_id for x in cursor.list],
                [items[6].test_id, items[0].test_id, items[2].test_id],
                'Изменения получены и в правильном порядке'
            )

        tap.note('Опять нет новых изменений')
        cursor = await PgRecord.list(
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
                [x.test_id for x in cursor.list],
                [],
                'Больше данных для репликации нет'
            )


async def test_list_look_desc(tap, uuid):
    with tap.plan(39):

        group = uuid()

        items = []
        for i in range(10):
            with PgRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.serial)
        items.reverse()

        tap.note('Начало получения')
        cursor = await PgRecord.list(
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
            tap.eq(int(cursor.serial), items[4].serial, 'Счетчик установлен')
            tap.eq(cursor.direction, 'DESC', 'Направление установлено')
            tap.eq(
                [x.serial for x in cursor.list],
                [x.serial for x in items[0:5]],
                'Все отсортированные записи получена'
            )

        tap.note('Вторая итерация')
        cursor = await PgRecord.list(
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
            tap.eq(int(cursor.serial), items[9].serial, 'Счетчик установлен')
            tap.eq(cursor.direction, 'DESC', 'Направление установлено')
            tap.eq(
                [x.serial for x in cursor.list],
                [x.serial for x in items[5:10]],
                'Все отсортированные записи получена'
            )

        tap.note('Все забрали')
        cursor = await PgRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.eq(int(cursor.serial), items[9].serial, 'Счетчик установлен')
            tap.eq(cursor.direction, 'DESC', 'Направление установлено')
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
        cursor = await PgRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.eq(int(cursor.serial), items[9].serial, 'Счетчик установлен')
            tap.eq(cursor.direction, 'DESC', 'Направление установлено')
            tap.eq(
                [x.test_id for x in cursor.list],
                [],
                'Больше данных для просмотра нет'
            )

        tap.note('Добавились новые строки')
        with PgRecord({'value': '11'}) as item:
            await item.save()
            items.append(item)
        with PgRecord({'value': '12'}) as item:
            await item.save()
            items.append(item)
        items.sort(key=lambda x: x.serial)
        items.reverse()

        tap.note('Новые строки уже не войдут в выборку')
        cursor = await PgRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.eq(int(cursor.serial), items[11].serial, 'Счетчик установлен')
            tap.eq(cursor.direction, 'DESC', 'Направление установлено')
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
            with PgRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.serial)

        tap.note('Начало получения')
        cursor = await PgRecord.list(
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
            tap.eq(int(cursor.serial), items[4].serial, 'Счетчик установлен')
            tap.eq(cursor.direction, 'ASC', 'Направление установлено')
            tap.eq(
                [x.serial for x in cursor.list],
                [x.serial for x in items[0:5]],
                'Все отсортированные записи получена'
            )

        tap.note('Вторая итерация')
        cursor = await PgRecord.list(
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
            tap.eq(int(cursor.serial), items[9].serial, 'Счетчик установлен')
            tap.eq(cursor.direction, 'ASC', 'Направление установлено')
            tap.eq(
                [x.serial for x in cursor.list],
                [x.serial for x in items[5:10]],
                'Все отсортированные записи получена'
            )

        tap.note('Все забрали')
        cursor = await PgRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.eq(int(cursor.serial), items[9].serial, 'Счетчик установлен')
            tap.eq(cursor.direction, 'ASC', 'Направление установлено')
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
        cursor = await PgRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.eq(int(cursor.serial), items[9].serial, 'Счетчик установлен')
            tap.eq(cursor.direction, 'ASC', 'Направление установлено')
            tap.eq(
                [x.test_id for x in cursor.list],
                [],
                'Больше данных для просмотра нет'
            )

        tap.note('Добавились новые строки')
        with PgRecord({'value': '11', 'group': group}) as item:
            await item.save()
            items.append(item)
        with PgRecord({'value': '12', 'group': group}) as item:
            await item.save()
            items.append(item)
        items.sort(key=lambda x: x.serial)

        tap.note('Новые строки получены')
        cursor = await PgRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.eq(int(cursor.serial), items[11].serial, 'Счетчик установлен')
            tap.eq(cursor.direction, 'ASC', 'Направление установлено')
            tap.eq(
                [x.serial for x in cursor.list],
                [x.serial for x in items[10:12]],
                'Все отсортированные записи получены'
            )

        tap.note('Опять нет новых изменений')
        cursor = await PgRecord.list(
            by='look',
            conditions=[('group', group)],
            cursor=cursor,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(cursor.type, 'look', 'Тип look')
            tap.ok(cursor.time, 'Время установлено')
            tap.eq(cursor.limit, 5, 'Лимит установлен')
            tap.eq(int(cursor.serial), items[11].serial, 'Счетчик установлен')
            tap.eq(cursor.direction, 'ASC', 'Направление установлено')
            tap.eq(
                [x.test_id for x in cursor.list],
                [],
                'Больше данных для просмотра нет'
            )
