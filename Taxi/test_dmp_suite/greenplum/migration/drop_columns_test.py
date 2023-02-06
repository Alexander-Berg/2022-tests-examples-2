from datetime import datetime

import pytest

from connection import greenplum as gp
from dmp_suite.greenplum import (
    GPTable,
    Int,
    String,
)
from dmp_suite.greenplum import migration
from dmp_suite.greenplum.hnhm import HnhmEntity
from dmp_suite.table import DdsLayout
from test_dmp_suite.greenplum import utils
from .utils import (
    create,
    read,
    write,
    run_migration_in_same_process,
    assert_real_field_type,
    assert_no_field_in_db,
)


@pytest.mark.slow('gp')
def test_drop_columns():
    # Проверим как добавятся две простые колонки в row ориентированную таблицу.
    with gp.connection.transaction():
        class TableBefore(GPTable):
            __layout__ = utils.TestLayout(name='example')

            a = Int()
            b = Int()
            c = String()

        class TableAfter(GPTable):
            __layout__ = utils.TestLayout(name='example')

            a = Int()

        create(TableBefore)
        write(TableBefore, [{'a': 100500, 'b': 42, 'c': 'Hello World!'}])

        task = migration.drop_columns(TableAfter)
        run_migration_in_same_process(task)

        assert_real_field_type(TableAfter, 'a', 'integer')
        assert_no_field_in_db(TableAfter, 'b')
        assert_no_field_in_db(TableAfter, 'c')

        # Теперь попробуем добавить данные без двух колонок
        write(TableAfter, [{'a': 2}])

        result = read(TableAfter)
        assert result == [
            # Эта строка была добавлена до alter
            {'a': 100500},
            # а эта – после.
            {'a': 2},
        ]


@pytest.mark.slow('gp')
def test_drop_columns_dds():
    # Проверим как добавятся две простые колонки в row ориентированную таблицу.
    with gp.connection.transaction():
        class TableBefore(HnhmEntity):
            __layout__ = DdsLayout(name="some_name", group="some_group", prefix_key='test')

            a = Int()
            b = Int(group='group')
            c = String(group='group')
            __keys__ = [a]

        class TableAfter(HnhmEntity):
            __layout__ = DdsLayout(name="some_name", group="some_group", prefix_key='test')

            a = Int()
            c = String(group='group')
            __keys__ = [a]

        Tbl_hub = TableBefore().get_main_class()
        create(Tbl_hub)
        write(Tbl_hub, [
            {'_source_id': -1, '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
             'id': 'a3afd0b3-d24f-2e8b-d2c7-8000f30d259b', 'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0)
             }])
        Tbl_a = list(TableBefore().get_field_classes())[0]
        create(Tbl_a)
        write(Tbl_a, [
                    {'a': 42, '_source_id': -1, '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
                     'id': 'a3afd0b3-d24f-2e8b-d2c7-8000f30d259b', 'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0)}])
        Tbl_g = list(TableBefore().get_group_classes())[0]
        create(Tbl_g)
        write(Tbl_g, [
            {'b': 42, 'c': 'aaaa', '_source_id': -1, '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
             'id': 'a3afd0b3-d24f-2e8b-d2c7-8000f30d259b', 'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
             'utc_valid_to_dttm': datetime(9999, 12, 31, 0, 0)}])

        task = migration.drop_columns(TableAfter)
        run_migration_in_same_process(task)

        TblAfter_a = list(TableAfter().get_field_classes())[0]
        TblAfter_g = list(TableAfter().get_group_classes())[0]

        # убеждаемся, что колонки b быть не должно, а колонки a и c - на месте
        assert_real_field_type(TblAfter_a, 'a', 'integer')
        assert_no_field_in_db(TblAfter_g, 'b')
        assert_real_field_type(TblAfter_g, 'c', 'varchar')

        # Теперь попробуем добавить данные без колонки b
        write(TblAfter_a, [
            {'a': 52, '_source_id': -1, '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
             'id': 'a3afd0b3-d24f-2e8b-d2c7-8000f30d259a', 'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0)}])
        write(TblAfter_g, [
            {'c': 'abcde', '_source_id': -1, '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
             'id': 'a3afd0b3-d24f-2e8b-d2c7-8000f30d259a', 'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
             'utc_valid_to_dttm': datetime(9999, 12, 31, 0, 0)}])

        result_a = read(TblAfter_a)
        assert result_a == [
            # Эта строка была добавлена после alter
            {'a': 52, '_source_id': -1, '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
             'id': 'a3afd0b3-d24f-2e8b-d2c7-8000f30d259a', 'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0)},
            # а эта - до
            {'a': 42, '_source_id': -1, '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
             'id': 'a3afd0b3-d24f-2e8b-d2c7-8000f30d259b', 'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0)},

        ]

        result_g = list(map(dict, gp.connection.select_all(TblAfter_g)))
        assert result_g == [
            # Эта строка была добавлена после alter
            {'c': 'abcde', '_source_id': -1, '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
             'id': 'a3afd0b3-d24f-2e8b-d2c7-8000f30d259a', 'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
             'utc_valid_to_dttm': datetime(9999, 12, 31, 0, 0)},
            # а эта - до
            {'c': 'aaaa', '_source_id': -1, '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
             'id': 'a3afd0b3-d24f-2e8b-d2c7-8000f30d259b', 'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
             'utc_valid_to_dttm': datetime(9999, 12, 31, 0, 0)},

        ]
