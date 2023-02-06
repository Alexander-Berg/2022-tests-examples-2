# pylint: disable=invalid-name,too-many-locals

import asyncio
import pytest

from .record import ShardedRecord


async def test_list(tap, uuid):
    with tap.plan(7):

        group = uuid()

        items = []
        for i in range(10):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items.append(item)

        tap.ok(items, 'созданы записи')
        items.sort(key=lambda x: x.test_id)

        cursor = await ShardedRecord.list(
            group=group,
            limit=5,
            sort='test_id',
        )
        with cursor:
            tap.ok(cursor, 'получен список')
            tap.eq(
                [x.test_id for x in cursor.list],
                [x.test_id for x in items[0:5]],
                'Порция отсортированных записей получена'
            )
            tap.ok(not cursor.latest, 'не последняя страница')

        cursor = await ShardedRecord.list(
            group=group,
            limit=5,
            sort='test_id',
            cursor_str=cursor.cursor_str,
            #             page=2,
        )
        with cursor:
            tap.ok(cursor, 'получен список страница 2')
            tap.eq(
                [x.test_id for x in cursor.list],
                [x.test_id for x in items[5:10]],
                'Порция отсортированных записей получена'
            )
            tap.ok(cursor.latest, 'последняя страница')


@pytest.mark.skip(reason='fix after arcadia')
@pytest.mark.parametrize('by', ['look', 'replication'])
async def test_shards(tap, dbh, by, uuid):
    with tap.plan(
            14,
            'Изменение количества шардов, создает новый курсор по нему'
    ):
        group = uuid()

        nshards = dbh.nshards(ShardedRecord.database)

        # Соберем тестовые данные в списки по шардам.
        # Данных создаем по лимиту выборки, чтобы проверять за один раз
        # точное поведение курсора
        tasks = []
        for i in range(100):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                tasks.append(item.save())

        items   = [[] for _ in range(nshards)]
        for item in await asyncio.gather(*tasks):
            items[item.shardno].append(item)
        for shardno in range(nshards):
            items[shardno].sort(key=lambda x: x.serial)

        with tap.subtest(nshards, 'Проверим создание') as _tap:
            for shardno in range(nshards):
                _tap.ok(
                    items[shardno],
                    f'Шард {shardno} создано {len(items[shardno])} строк'
                )

        tap.note('Получение курсора')
        cursor = await ShardedRecord.list(
            by=by,
            conditions=[('group', group)],
            limit=100,
            direction='ASC',
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(len(cursor.shards), nshards, 'Курсоры для всех шардов')

            result = [[] for _ in range(nshards)]
            for item in cursor.list:
                result[item.shardno].append(item)

            with tap.subtest(nshards, 'Проверим выборку') as _tap:
                for shardno in range(nshards):
                    _tap.eq(
                        result[shardno],
                        items[shardno],
                        f'Шард {shardno} получено {len(result[shardno])} строк'
                    )

        deleted = cursor.shards.pop()
        tap.ok(deleted, 'Убрали один шард из курсора')

        tap.note('Идем с курсором в котором нет всех шардов')
        cursor = await ShardedRecord.list(
            by=by,
            conditions=[('group', group)],
            cursor=cursor,
        )

        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(len(cursor.shards), nshards, 'Курсоры опять для всех шардов')

            result = [[] for _ in range(nshards)]
            for item in cursor.list:
                result[item.shardno].append(item)

            with cursor.shards[0] as exists:
                shardno = 0

                tap.ok(exists, 'Курсор остался')

                with tap.subtest(1, f'Выборка шарда {shardno}') as _tap:
                    _tap.eq(len(result[shardno]), 0, 'Все записи уже выбраны')

            # NOTE: поскольку второй запрос продвинул первый курсор дальше,
            # выборка изменится. И поле serial для восстановленого курсора
            # изменится по сравнению с удаленным
            with cursor.shards[-1] as recovered:
                shardno = len(cursor.shards) - 1

                tap.eq(deleted.type, recovered.type, 'Тип восстановлен')
                tap.eq(deleted.limit, recovered.limit, 'Лимит')

                if by == 'look':
                    tap.ok(recovered.serial, 'Счетчик восстановлен')
                    tap.eq(
                        deleted.direction,
                        recovered.direction,
                        'Направление'
                    )
                elif by == 'replication':
                    tap.ok(recovered.lsn, 'Счетчик восстановлен')
                    tap.passed('***')
                else:
                    raise f'Доработайте тест для {by}'

                with tap.subtest(1, f'Выборка шарда {shardno}') as _tap:
                    _tap.eq(
                        result[shardno],
                        items[shardno],
                        'Выборка получена заново'
                    )


async def test_shards_walk(tap, dbh, uuid):
    with tap.plan(
            4,
            'Изменение количества шардов, создает новый курсор по нему'
    ):
        nshards = dbh.nshards(ShardedRecord.database)

        group = uuid()

        # Соберем тестовые данные в списки по шардам.
        # Данных создаем по лимиту выборки, чтобы проверять за один раз
        # точное поведение курсора
        items   = [[] for _ in range(nshards)]
        for i in range(100):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                await item.save()
                items[item.shardno].append(item)
        for shardno in range(nshards):
            items[shardno].sort(key=lambda x: x.serial)

        with tap.subtest(nshards, 'Проверим создание') as _tap:
            for shardno in range(nshards):
                _tap.ok(
                    items[shardno],
                    f'Шард {shardno} создано {len(items[shardno])} строк'
                )

        with tap.subtest(3, 'Получение курсора') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                sort=[('serial', 'ASC')],
                limit=100,
            )
            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(len(cursor.shards), nshards, 'Курсоры для всех шардов')

                result = [[] for _ in range(nshards)]
                for item in cursor.list:
                    result[item.shardno].append(item)

                with _tap.subtest(nshards, 'Проверим выборку') as _tap2:
                    for shardno in range(nshards):
                        _tap2.eq(
                            result[shardno],
                            items[shardno],
                            f'Шард {shardno} получено'
                            f' {len(result[shardno])} строк'
                        )

        deleted = cursor.shards.pop()
        tap.ok(deleted, 'Убрали один шард из курсора')

        with tap.subtest(8, 'Курсорор в котором нет всех шардов') as _tap:
            cursor = await ShardedRecord.list(
                by='walk',
                conditions=[('group', group)],
                sort=[('serial', 'ASC')],
                cursor=cursor,
            )

            with cursor:
                _tap.ok(cursor, 'Курсор получен')
                _tap.eq(
                    len(cursor.shards),
                    nshards,
                    'Курсоры опять для всех шардов'
                )

                result = [[] for _ in range(nshards)]
                for item in cursor.list:
                    result[item.shardno].append(item)

                with cursor.shards[0] as exists:
                    shardno = 0

                    _tap.ok(exists, 'Курсор остался')

                    with _tap.subtest(1, f'Выборка шарда {shardno}') as _tap2:
                        _tap2.eq(
                            len(result[shardno]),
                            0,
                            'Все записи уже выбраны'
                        )

                # NOTE: поскольку второй запрос продвинул первый курсор дальше,
                # выборка изменится. И поле serial для восстановленого курсора
                # изменится по сравнению с удаленным
                with cursor.shards[-1] as recovered:
                    shardno = len(cursor.shards) - 1

                    _tap.eq(deleted.type, recovered.type, 'Тип восстановлен')
                    _tap.eq(deleted.limit, recovered.limit, 'Лимит')

                    _tap.ok(recovered.values, 'Счетчик восстановлен')

                    with _tap.subtest(1, f'Выборка шарда {shardno}') as _tap2:
                        _tap2.eq(
                            result[shardno],
                            items[shardno],
                            'Выборка получена заново'
                        )


@pytest.mark.skip(reason='fix after arcadia')
@pytest.mark.parametrize('by', ['full', 'look', 'replication', 'walk'])
async def test_shard_no(tap, dbh, by, uuid):
    with tap.plan(6, 'Выборка с указанием конкретного шарда'):  # LAVKADEV-1557
        group = uuid()

        nshards         = dbh.nshards(ShardedRecord.database)
        manual_shard    = nshards - 1
        tap.ok(
            manual_shard is not None,
            f'В ручную указываем шард {manual_shard}'
        )

        # Соберем тестовые данные в списки по шардам.
        tasks = []
        for i in range(100):
            with ShardedRecord({'value': str(i), 'group': group}) as item:
                tasks.append(item.save())

        items   = [[] for _ in range(nshards)]
        for item in await asyncio.gather(*tasks):
            items[item.shardno].append(item)
        for shardno in range(nshards):
            items[shardno].sort(key=lambda x: x.serial)

        with tap.subtest(nshards, 'Проверим создание') as _tap:
            for shardno in range(nshards):
                _tap.ok(
                    items[shardno],
                    f'Шард {shardno} создано {len(items[shardno])} строк'
                )

        cursor = await ShardedRecord.list(
            db={'shard': manual_shard},
            by=by,
            conditions=[('group', group)],
            sort='serial',
            direction='ASC',
            limit=100,
        )
        with cursor:
            tap.ok(cursor, 'Курсор получен')
            tap.eq(len(cursor.shards), nshards, 'Курсоры опять для всех шардов')

            result = [[] for _ in range(nshards)]
            for item in cursor.list:
                result[item.shardno].append(item)

            for shardno in range(nshards):
                with tap.subtest(1, f'Выборка с шарда {shardno}') as _tap:

                    if shardno == manual_shard:
                        _tap.eq(
                            result[shardno],
                            items[shardno],
                            f'Для выбранного шарда получено'
                            f' {len(result[shardno])} записей'
                        )

                    else:
                        _tap.eq(result[shardno], [], 'Данные не выбирались')
