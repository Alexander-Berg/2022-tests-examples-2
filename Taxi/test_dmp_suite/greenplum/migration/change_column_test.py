from datetime import datetime

import pytest

from connection import greenplum as gp
from dmp_suite.greenplum import (
    Datetime,
    GPTable,
    Int,
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
def test_change_column_types():
    with gp.connection.transaction():
        class TableBefore(GPTable):
            __layout__ = utils.TestLayout(name='example')

            a = Int()
            b = String()
            c = String()

        class TableAfter(GPTable):
            __layout__ = utils.TestLayout(name='example')

            a = String()
            b = Datetime()
            c = Int()

        create(TableBefore)
        write(TableBefore, [{'a': 100500, 'b': '2021-12-31 23:59:59', 'c': '500100'}])

        task = migration.change_column_types(TableAfter)
        run_migration_in_same_process(task)

        assert_real_field_type(TableAfter, 'a', 'VARCHAR')
        assert_real_field_type(TableAfter, 'b', 'TIMESTAMP WITHOUT TIME ZONE')
        assert_real_field_type(TableAfter, 'c', 'INT')

        result = read(TableAfter)
        assert result == [
            {'a': '100500', 'b': datetime(2021, 12, 31, 23, 59, 59), 'c': 500100}
        ]


@pytest.mark.slow('gp')
def test_change_column_types_hnhm():
    class TableBefore(HnhmEntity):
        __layout__ = DdsLayout(name="some_name", group="some_group", prefix_key='test')

        a = Int(change_type=ChangeType.IGNORE)
        b = String(change_type=ChangeType.IGNORE)
        c = String(
            change_type=ChangeType.IGNORE,
            group='test_core'
        )
        d = String(
            change_type=ChangeType.IGNORE,
            group='test_core'
        )

        __keys__ = [a]

    class TableAfter(HnhmEntity):
        __layout__ = DdsLayout(name="some_name", group="some_group", prefix_key='test')

        a = Int(change_type=ChangeType.IGNORE)
        b = Datetime(change_type=ChangeType.IGNORE)
        c = String(
            change_type=ChangeType.IGNORE,
            group='test_core'
        )
        d = Int(
            change_type=ChangeType.IGNORE,
            group='test_core'
        )

        __keys__ = [a]

    # Инициализируем таблицу хаба для сущности до изменений
    tbl_before_hub = TableBefore().get_main_class()
    # Создаем таблицы-атрибуты сущности
    tbl_before_a_attr = TableBefore().get_field_class('a')
    tbl_before_b_attr = TableBefore().get_field_class('b')
    # Инициализируем таблицу группы для сущности до изменений
    tbl_before_group = list(TableBefore().get_group_classes())[0]

    with gp.connection.transaction():
        # заполняем таблицы и проводим миграции

        create(tbl_before_hub)
        write(tbl_before_hub, [{
            '_source_id': -1,
            '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
            'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
            'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000000',
        }])
        create(tbl_before_a_attr)
        write(tbl_before_a_attr, [{
            '_source_id': -1,
            '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
            'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
            'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000000',
            'a': 1
        }])
        create(tbl_before_b_attr)
        write(tbl_before_b_attr, [{
            '_source_id': -1,
            '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
            'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
            'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000000',
            'b': '2021-12-31 23:59:59'
        }])
        create(tbl_before_group)
        write(tbl_before_group, [{
            'c': '100500', 'd': '500100',
            '_source_id': -1,
            '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
            'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
            'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000000'
        }])

        task = migration.change_column_types(TableAfter)
        run_migration_in_same_process(task)

    tbl_after_a_attr = TableAfter().get_field_class('a')
    tbl_after_b_attr = TableAfter().get_field_class('b')
    tbl_after_grp = list(TableAfter().get_group_classes())[0]

    assert_real_field_type(tbl_after_a_attr, 'a', 'INT')
    assert_real_field_type(tbl_after_b_attr, 'b', 'TIMESTAMP WITHOUT TIME ZONE')
    assert_real_field_type(tbl_after_grp, 'c', 'VARCHAR')
    assert_real_field_type(tbl_after_grp, 'd', 'INT')

    result_a = read(tbl_after_a_attr, key='id')
    assert result_a == [{
        '_source_id': -1,
        '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
        'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
        'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000000',
        'a': 1
    }]

    result_b = read(tbl_after_b_attr, key='id')
    assert result_b == [{
        '_source_id': -1,
        '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
        'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
        'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000000',
        'b': datetime(2021, 12, 31, 23, 59, 59)
    }]

    result_grp = read(tbl_after_grp, key='id')
    assert result_grp == [{
        'c': '100500', 'd': 500100,
        '_source_id': -1,
        '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
        'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
        'id': 'aaaaaaaa-aaaa-aaaa-aaaa-000000000000'
    }]
