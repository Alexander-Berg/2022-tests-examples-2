from datetime import datetime

import pytest

from connection import greenplum as gp
from dmp_suite.greenplum import (
    GPTable,
    Int,
    Orientation,
    ColumnStorageParameters,
    StorageParameters,
    String,
)
from dmp_suite.greenplum import migration
from dmp_suite.greenplum.hnhm import HnhmEntity
from dmp_suite.table import ChangeType
from dmp_suite.table import DdsLayout
from test_dmp_suite.greenplum import utils
from .utils import (
    create,
    read,
    write,
    run_migration_in_same_process,
    assert_real_field_type,
)


@pytest.mark.slow('gp')
def test_add_columns():
    # Проверим как добавятся две простые колонки в row ориентированную таблицу.
    with gp.connection.transaction():
        class TableBefore(GPTable):
            __layout__ = utils.TestLayout(name='example')

            a = Int()

        class TableAfter(TableBefore):
            b = Int()
            c = String()

        create(TableBefore)
        write(TableBefore, [{'a': 100500}])

        task = migration.add_columns(TableAfter)
        run_migration_in_same_process(task)

        # schema = gp.connection._get_real_fields(TableAfter)
        # assert schema == {'a': 'integer', 'b': 'integer', 'c': 'character varying'}
        assert_real_field_type(TableAfter, 'a', 'integer')
        assert_real_field_type(TableAfter, 'b', 'integer')
        assert_real_field_type(TableAfter, 'c', 'character varying')

        # Теперь попробуем добавить данные с новыми колонками
        write(TableAfter, [{'a': 2, 'b': 3, 'c': 'Hello'}])

        result = read(TableAfter)
        assert result == [
            # Эта строка была добавлена до alter
            {'a': 100500, 'b': None, 'c': None},
            # а эта – после.
            {'a': 2, 'b': 3, 'c': 'Hello'},
        ]


@pytest.mark.slow('gp')
def test_add_columns_hnhm_group():
    # Проверим как добавляется две простые колонки в группу hnhm.

    class TableBefore(HnhmEntity):
        __layout__ = DdsLayout(name="some_name", group="some_group", prefix_key='test')

        a = Int(
            change_type=ChangeType.IGNORE,
            group='test_core'
        )
        __keys__ = [a]

    class TableAfter(TableBefore):

        b = Int(
            change_type=ChangeType.IGNORE,
            group='test_core'
        )
        c = String(
            change_type=ChangeType.IGNORE,
            group='test_core'
        )

    # Инициализируем таблицу хаба для сущности до изменений
    tbl_before_hub = TableBefore().get_main_class()
    # Инициализируем таблицу группы для сущности до изменений
    tbl_before_group = list(TableBefore().get_group_classes())[0]

    with gp.connection.transaction():
        # заполняем таблицы данными и проводим миграцию
        create(tbl_before_hub)
        write(tbl_before_hub, [{
            '_source_id': -1,
            '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
            'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
            'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000000',
        }])
        create(tbl_before_group)
        write(tbl_before_group, [{
            'a': 42,
            '_source_id': -1,
            '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
            'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
            'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000000'
        }])

        task = migration.add_columns(TableAfter)
        run_migration_in_same_process(task)

        tbl_after_group = list(TableAfter().get_group_classes())[0]

        # Теперь попробуем добавить данные с новыми колонками
        write(tbl_after_group, [{
            'a': 2, 'b': 3, 'c': 'Hello',
            '_source_id': -1,
            '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
            'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
            'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000001'
        }])

    # сравниваем типы
    assert_real_field_type(tbl_after_group, 'a', 'integer')
    assert_real_field_type(tbl_after_group, 'b', 'integer')
    assert_real_field_type(tbl_after_group, 'c', 'varchar')

    result = read(tbl_after_group)
    assert result == [
        # Эта строка была добавлена до alter
        {
            '_source_id': -1,
            '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
            'a': 42,
            'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000000',
            'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
            'b': None,
            'c': None
        },
        # а эта – после.
        {
            'a': 2, 'b': 3, 'c': 'Hello',
            '_source_id': -1,
            '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
            'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
            'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000001'
        },
    ]


@pytest.mark.slow('gp')
def test_add_columns_with_compression():
    # Проверим как добавится простая колонка в column ориентированную таблицу.
    # Ожидаем, что у новой колонки будет такой же алгоритм компрессии, как и у всей таблицы.

    class TableBefore(GPTable):
        __layout__ = utils.TestLayout(name='example')
        __storage_parameters__ = StorageParameters(
            orientation=Orientation.COLUMN,
            compress_type='RLE_TYPE',
            compress_level=4,
        )
        a = Int()

    class TableAfter(TableBefore):
        b = String()

    create(TableBefore)

    task = migration.add_columns(TableAfter)
    run_migration_in_same_process(task)

    options = gp.connection._get_real_fields_compression(TableAfter)

    # Убедимся, что у оригинальной колонки параметры сжатия такие,
    # как были заданы
    assert options['a'].compress_type == 'RLE_TYPE'
    assert options['a'].compress_level == 4

    # И у новой колонки сжатие должно быть таким же:
    assert options['b'].compress_type == 'RLE_TYPE'
    assert options['b'].compress_level == 4


@pytest.mark.slow('gp')
def test_add_columns_with_custom_compression():
    # Проверим как добавятся две простые колонки в column ориентированную таблицу.
    # Ожидаем, что у новой колонки будет такой же алгоритм компрессии, как и у всей таблицы.

    class TableBefore(GPTable):
        __layout__ = utils.TestLayout(name='example')
        __storage_parameters__ = StorageParameters(
            orientation=Orientation.COLUMN,
            compress_type='zlib',
            compress_level=2,
        )
        a = Int()

    class TableAfter(TableBefore):
        __storage_parameters__ = StorageParameters(
            orientation=Orientation.COLUMN,
            compress_type='zlib',
            compress_level=2,
            column_compression={
                # У новой колонки тип компрессии отличается от остальных!
                'b': ColumnStorageParameters(
                    compress_type='RLE_TYPE',
                    compress_level=4,
                ),
            }
        )
        b = String()

    create(TableBefore)

    task = migration.add_columns(TableAfter)
    run_migration_in_same_process(task)

    options = gp.connection._get_real_fields_compression(TableAfter)

    # Убедимся, что у оригинальной колонки параметры сжатия такие,
    # как были заданы
    assert options['a'].compress_type == 'zlib'
    assert options['a'].compress_level == 2

    # И у новой колонки сжатие должно быть тем,
    # которое мы отдельно задали с помощью ColumnStorageParameters:
    assert options['b'].compress_type == 'RLE_TYPE'
    assert options['b'].compress_level == 4
