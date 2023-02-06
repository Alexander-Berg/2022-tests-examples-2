import pytest

from connection.yt import get_yt_client
from dmp_suite.task.execution import run_task
from dmp_suite.yt import YTTable, Int, Datetime, String, resolve_meta, DayPartitionScale
from dmp_suite.yt.migration import drop_columns
from test_dmp_suite.yt import utils

from .utils import create, read, write, get_real_schema, append


def test_lock_name():
    class TestTable(YTTable):
        a = Int()

    task = drop_columns(TestTable)
    assert task.get_lock() == ('drop_columns_from_test_dmp_suite_yt_migration_drop_columns_test_TestTable',)


@pytest.mark.slow
def test_drop_columns_from_static():
    # Проверим сработает ли удаление колонки

    @utils.random_yt_table
    class TableBefore(YTTable):
        a = Int(required=True)
        b = Int(required=True)

    class TableAfter(YTTable):
        __layout__ = TableBefore.__layout__
        __location_cls__ = TableBefore.__location_cls__
        # Тут только одна колонка:
        a = Int(required=True)


    create(TableBefore)
    write(TableBefore, [{'a': 100500, 'b': 42}])

    task = drop_columns(TableAfter)
    run_task(task)

    schema = get_real_schema(TableAfter)
    assert schema == {'a': 'int64'}

    # Теперь попробуем добавить данные
    append(TableAfter, [{'a': 1}])

    result = read(TableAfter)
    assert result == [
        {'a': 100500}, # Эта строка была добавлена до alter
        {'a': 1}, # а эта – после.
    ]


@pytest.mark.slow
def test_drop_columns_from_dynamic():
    # Проверим сработает ли удаление колонки из динамической таблицы

    @utils.random_yt_table
    class TableBefore(YTTable):
        __dynamic__ = True
        __unique_keys__ = True
        a = Int(sort_key=True)
        b = Int()
        c = String()

    class TableAfter(YTTable):
        __layout__ = TableBefore.__layout__
        __location_cls__ = TableBefore.__location_cls__
        __dynamic__ = True
        __unique_keys__ = True
        a = Int(sort_key=True)
        b = Int() # Должна быть хотя бы одна колонка, не являющаяся ключём


    create(TableBefore)
    write(TableBefore, [{'a': 100500, 'b': 42, 'c': 'Blah'}])

    task = drop_columns(TableAfter)
    run_task(task)

    schema = get_real_schema(TableAfter)
    assert schema == {'a': 'int64', 'b': 'int64'}

    # Теперь попробуем добавить данные
    append(TableAfter, [{'a': 1, 'b': 123}])

    result = read(TableAfter)
    assert result == [
        # Эта строка добавлена после миграции, но
        # так как динамическая таблица сортирована, то
        # она идёт первой:
        {'a': 1, 'b': 123},
        {'a': 100500, 'b': 42},
    ]


@pytest.mark.slow
def test_drop_columns_from_partitioned_dynamic():
    # Проверим как удалятся две простые колонки из партиционированной динамическую таблицу.

    @utils.random_yt_table
    class TableBefore(YTTable):
        __partition_scale__ = DayPartitionScale(
            partition_key='created_at'
        )
        __dynamic__ = True
        __unique_keys__ = True

        created_at = Datetime(sort_key=True)
        a = Int(sort_key=True)
        b = Int(required=True)
        # Эти две колонки будем удалять
        c = Int(required=True)
        d = String(required=True)

    class TableAfter(YTTable):
        __layout__ = TableBefore.__layout__
        __location_cls__ = TableBefore.__location_cls__
        __partition_scale__ = DayPartitionScale(
            partition_key='created_at'
        )
        __dynamic__ = True
        __unique_keys__ = True

        created_at = Datetime(sort_key=True)
        a = Int(sort_key=True)
        b = Int()


    # Создадим две партиции
    p1 = resolve_meta(TableBefore, partition='2020-01-01')
    p2 = resolve_meta(TableBefore, partition='2020-01-09')

    create(p1)
    write(p1, [{'created_at': '2020-01-01', 'a': 1, 'b': 3, 'c': 100, 'd': 'Hello'}])

    create(p2)
    write(p2, [{'created_at': '2020-01-09', 'a': 1, 'b': 4, 'c': 100, 'd': 'World'}])

    path_1 = p1.target_path()
    path_2 = p2.target_path()

    # Запустим изменение схемы, оно должно примениться
    # к обоим парициям
    task = drop_columns(TableAfter)
    run_task(task)

    # Убедимся, что таблички остались динамическими
    assert get_yt_client().get_attribute(p1.target_path(), 'dynamic') == True
    assert get_yt_client().get_attribute(p2.target_path(), 'dynamic') == True

    schema = get_real_schema(p1)
    assert schema == {'created_at': 'string', 'a': 'int64', 'b': 'int64'}

    schema = get_real_schema(p2)
    assert schema == {'created_at': 'string', 'a': 'int64', 'b': 'int64'}

    # Теперь попробуем добавить данные без удалённых колонок
    p1 = resolve_meta(TableAfter, partition='2020-01-01')
    p2 = resolve_meta(TableAfter, partition='2020-01-09')

    append(p1, [{'created_at': '2020-01-01', 'a': 100500, 'b': 1}])
    append(p2, [{'created_at': '2020-01-09', 'a': 42, 'b': 2}])

    result = read(p1)
    assert result == [
        {'created_at': '2020-01-01', 'a': 1, 'b': 3},
        {'created_at': '2020-01-01', 'a': 100500, 'b': 1},
    ]

    result = read(p2)
    assert result == [
        {'created_at': '2020-01-09', 'a': 1, 'b': 4},
        {'created_at': '2020-01-09', 'a': 42, 'b': 2},
    ]

