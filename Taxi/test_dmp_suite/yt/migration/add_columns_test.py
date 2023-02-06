import pytest

from dmp_suite.task.execution import run_task
from dmp_suite.yt import YTTable, Int, Datetime, resolve_meta, DayPartitionScale, String
from dmp_suite.yt.migration import add_columns
from test_dmp_suite.yt import utils

from .utils import create, read, write, get_real_schema, append


def test_lock_name():
    class TestTable(YTTable):
        a = Int()

    task = add_columns(TestTable)
    assert task.get_lock() == ('add_columns_to_test_dmp_suite_yt_migration_add_columns_test_TestTable',)


@pytest.mark.slow
def test_add_columns_to_static():
    # Проверим как добавятся две простые колонки в статическую таблицу
    # Ожидаем, что старые данные будут отдаваться без колонок.

    @utils.random_yt_table
    class TableBefore(YTTable):
        a = Int()

    class TableAfter(TableBefore):
        b = Int()
        c = Datetime()

    create(TableBefore)
    write(TableBefore, [{'a': 100500}])

    task = add_columns(TableAfter)
    run_task(task)

    schema = get_real_schema(TableAfter)
    assert schema == {'a': 'int64', 'b': 'int64', 'c': 'string'}

    # Теперь попробуем добавить данные с новыми колонками
    append(TableAfter, [{'a': 1, 'b': 2, 'c': 'Hello'}])

    result = read(TableAfter)
    assert result == [
        {'a': 100500}, # Эта строка была добавлена до alter
        {'a': 1, 'b': 2, 'c': 'Hello'}, # а эта – после.
    ]


@pytest.mark.slow
def test_add_columns_to_dynamic():
    # Проверим как добавятся две простые колонки в динамическую таблицу.

    @utils.random_yt_table
    class TableBefore(YTTable):
        __dynamic__ = True
        __unique_keys__ = True
        a = Int(sort_key=True)
        b = Int()

    class TableAfter(TableBefore):
        c = Int()
        d = Datetime()


    create(TableBefore)
    write(TableBefore, [{'a': 100500, 'b': 1}])

    task = add_columns(TableAfter)
    run_task(task)

    schema = get_real_schema(TableAfter)
    assert schema == {'a': 'int64', 'b': 'int64', 'c': 'int64', 'd': 'string'}

    # Теперь попробуем добавить данные с новыми колонками
    append(TableAfter, [{'a': 1, 'b': 2, 'c': 3, 'd': 'Hello'}])

    result = read(TableAfter)
    assert result == [
        # Эта строка добавлена после alter.
        {'a': 1, 'b': 2, 'c': 3, 'd': 'Hello'},
        # А эта – до alter. В отличие от статических таблиц,
        # для динамических YT возвращает None в добавленных колонках:
        {'a': 100500, 'b': 1, 'c': None, 'd': None},
    ]


@pytest.mark.slow
def test_add_columns_to_partitioned_static():
    # Проверим как добавятся две простые колонки в партиционированную статическую таблицу.

    @utils.random_yt_table
    class TableBefore(YTTable):
        __partition_scale__ = DayPartitionScale(
            partition_key='created_at'
        )

        created_at = Datetime(sort_key=True)

        a = Int()

    class TableAfter(TableBefore):
        b = Int()
        c = Datetime()

    # Создадим две партиции
    p1 = resolve_meta(TableBefore, partition='2020-01-01')
    p2 = resolve_meta(TableBefore, partition='2020-01-09')

    create(p1)
    write(p1, [{'created_at': '2020-01-01', 'a': 100500}])

    create(p2)
    write(p2, [{'created_at': '2020-01-09', 'a': 42}])

    # Запустим изменение схемы, оно должно примениться
    # к обоим парициям
    task = add_columns(TableAfter)
    run_task(task)

    schema = get_real_schema(p1)
    assert schema == {'created_at': 'string', 'a': 'int64', 'b': 'int64', 'c': 'string'}

    schema = get_real_schema(p2)
    assert schema == {'created_at': 'string', 'a': 'int64', 'b': 'int64', 'c': 'string'}

    # Теперь попробуем добавить данные с новыми колонками
    p1 = resolve_meta(TableAfter, partition='2020-01-01')
    p2 = resolve_meta(TableAfter, partition='2020-01-09')

    append(p1, [{'created_at': '2020-01-01', 'a': 1, 'b': 2, 'c': 'Hello'}])
    append(p2, [{'created_at': '2020-01-09', 'a': 1, 'b': 2, 'c': 'World'}])

    result = read(p1)
    assert result == [
        {'created_at': '2020-01-01', 'a': 100500}, # Эта строка была добавлена до alter
        {'created_at': '2020-01-01', 'a': 1, 'b': 2, 'c': 'Hello'}, # а эта – после.
    ]

    result = read(p2)
    assert result == [
        {'created_at': '2020-01-09', 'a': 42},  # Эта строка была добавлена до alter
        {'created_at': '2020-01-09', 'a': 1, 'b': 2, 'c': 'World'},  # а эта – после.
    ]


@pytest.mark.slow
def test_add_columns_to_partitioned_dynamic():
    # Проверим как добавятся две простые колонки в партиционированную динамическую таблицу.

    @utils.random_yt_table
    class TableBefore(YTTable):
        __partition_scale__ = DayPartitionScale(
            partition_key='created_at'
        )
        __dynamic__ = True
        __unique_keys__ = True

        created_at = Datetime(sort_key=True)
        a = Int(sort_key=True)
        b = Int()

    class TableAfter(TableBefore):
        c = Int()
        d = Datetime()

    # Создадим две партиции
    p1 = resolve_meta(TableBefore, partition='2020-01-01')
    p2 = resolve_meta(TableBefore, partition='2020-01-09')

    create(p1)
    write(p1, [{'created_at': '2020-01-01', 'a': 100500, 'b': 1}])

    create(p2)
    write(p2, [{'created_at': '2020-01-09', 'a': 42, 'b': 2}])

    # Запустим изменение схемы, оно должно примениться
    # к обоим парициям
    task = add_columns(TableAfter)
    run_task(task)

    schema = get_real_schema(p1)
    assert schema == {'created_at': 'string', 'a': 'int64', 'b': 'int64', 'c': 'int64', 'd': 'string'}

    schema = get_real_schema(p2)
    assert schema == {'created_at': 'string', 'a': 'int64', 'b': 'int64', 'c': 'int64', 'd': 'string'}

    # Теперь попробуем добавить данные с новыми колонками
    p1 = resolve_meta(TableAfter, partition='2020-01-01')
    p2 = resolve_meta(TableAfter, partition='2020-01-09')

    append(p1, [{'created_at': '2020-01-01', 'a': 1, 'b': 3, 'c': 100, 'd': 'Hello'}])
    append(p2, [{'created_at': '2020-01-09', 'a': 1, 'b': 4, 'c': 100, 'd': 'World'}])

    result = read(p1)
    assert result == [
        # Строки в YT отсортированы по полю "a", поэтому
        # cначала идёт та, что добавлена позже:
        {'created_at': '2020-01-01', 'a': 1, 'b': 3, 'c': 100, 'd': 'Hello'},
        # а эта строка была добавлена до alter
        {'created_at': '2020-01-01', 'a': 100500, 'b': 1, 'c': None, 'd': None},
    ]

    result = read(p2)
    assert result == [
        {'created_at': '2020-01-09', 'a': 1, 'b': 4, 'c': 100, 'd': 'World'},
        {'created_at': '2020-01-09', 'a': 42, 'b': 2, 'c': None, 'd': None},
    ]


@pytest.mark.slow
def test_add_and_fill_columns():
    # Проверим как добавятся две простые колонки в статическую таблицу
    # Ожидаем, что старые данные будут отдаваться без колонок.

    @utils.random_yt_table
    class TableBefore(YTTable):
        a = Int()

    class TableAfter(TableBefore):
        b = Int()
        c = Datetime()

    create(TableBefore)
    write(TableBefore, [{'a': 100500}])

    task = add_columns(TableAfter, extractors={'b': 'a'})
    run_task(task)

    schema = get_real_schema(TableAfter)
    assert schema == {'a': 'int64', 'b': 'int64', 'c': 'string'}

    result = read(TableAfter)
    assert result == [
        {'a': 100500, 'b': 100500, 'c': None},
    ]


@pytest.mark.slow
def test_add_and_fill_columns_using_custom_mapper():
    # В этот раз мы используем кастомную функцию mapper
    # для перевода числа в строку
    @utils.random_yt_table
    class TableBefore(YTTable):
        a = Int()

    class TableAfter(TableBefore):
        b = String()
        c = Datetime()

    create(TableBefore)
    write(TableBefore, [{'a': 100500}])

    task = add_columns(
        TableAfter,
        extractors={
            'b': lambda rec: str(rec['a'])
        }
    )
    run_task(task)

    schema = get_real_schema(TableAfter)
    assert schema == {'a': 'int64', 'b': 'string', 'c': 'string'}

    result = read(TableAfter)
    assert result == [
        {'a': 100500, 'b': '100500', 'c': None},
    ]
