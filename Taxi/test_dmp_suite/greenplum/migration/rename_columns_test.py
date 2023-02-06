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
def test_rename_columns(generate_new_taxidwh_run_id):
    # Проверим как сработает переименование колонки "b" в "c"
    with gp.connection.transaction():
        class TableBefore(GPTable):
            __layout__ = utils.TestLayout(name='example')

            a = Int()
            b = Int()

        class TableAfter(GPTable):
            __layout__ = utils.TestLayout(name='example')

            a = Int()
            c = Int()

        create(TableBefore)
        write(TableBefore, [{'a': 100500, 'b': 42}])

        task = migration.rename_column(TableAfter, 'b', 'c')
        run_migration_in_same_process(task)

        # Колонки "b" теперь быть не должно:
        assert_real_field_type(TableAfter, 'a', 'integer')
        assert_no_field_in_db(TableAfter, 'b')
        assert_real_field_type(TableAfter, 'c', 'integer')

        result = read(TableAfter)
        assert result == [
            {'a': 100500, 'c': 42},
        ]

        # Повторный вызов таска не должен приводить к ошибке,
        # так как состояние базы уже такое как нужно

        task = migration.rename_column(TableAfter, 'b', 'c')
        # необходимо сгененировать новый id запуска, тк выполнять несколько раз таск в рамках одного run_id недопустимо
        generate_new_taxidwh_run_id()
        run_migration_in_same_process(task)
        assert_no_field_in_db(TableAfter, 'b')
        assert_real_field_type(TableAfter, 'c', 'integer')


@pytest.mark.slow('gp')
def test_rename_columns_dds_group(generate_new_taxidwh_run_id):
    # Проверим как сработает переименование колонки "b" в "c" для атрибута группы в ДДС
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
            b = Int(group='group')
            d = String(group='group')
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

        task = migration.rename_column(TableAfter, 'c', 'd')
        run_migration_in_same_process(task)

        TblAfter_a = list(TableAfter().get_field_classes())[0]
        TblAfter_g = list(TableAfter().get_group_classes())[0]

        # Колонки "c" теперь быть не должно:
        assert_real_field_type(TblAfter_a, 'a', 'integer')
        assert_no_field_in_db(TblAfter_g, 'c')
        assert_real_field_type(TblAfter_g, 'd', 'varchar')

        result = list(map(dict, gp.connection.select_all(TblAfter_g)))
        assert result == [
            {'b': 42, 'd': 'aaaa', '_source_id': -1, '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
             'id': 'a3afd0b3-d24f-2e8b-d2c7-8000f30d259b', 'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
             'utc_valid_to_dttm': datetime(9999, 12, 31, 0, 0)},
        ]

        # Повторный вызов таска не должен приводить к ошибке,
        # так как состояние базы уже такое как нужно

        task = migration.rename_column(TableAfter, 'c', 'd')
        # необходимо сгененировать новый id запуска, тк выполнять несколько раз таск в рамках одного run_id недопустимо
        generate_new_taxidwh_run_id()
        run_migration_in_same_process(task)
        assert_no_field_in_db(TblAfter_g, 'c')
        assert_real_field_type(TblAfter_g, 'd', 'varchar')


@pytest.mark.slow('gp')
def test_rename_columns_dds_attr(generate_new_taxidwh_run_id):
    # Проверим как сработает переименование колонки "b" в "c"
    with gp.connection.transaction():
        class TableBefore(HnhmEntity):
            __layout__ = DdsLayout(name="some_name", group="some_group", prefix_key='test')

            a = Int()
            b = Int()
            __keys__ = [a]

        class TableAfter(HnhmEntity):
            __layout__ = DdsLayout(name="some_name", group="some_group", prefix_key='test')

            a = Int()
            c = Int()
            __keys__ = [a]

        Tbl_hub = TableBefore().get_main_class()
        create(Tbl_hub)
        write(Tbl_hub, [
            {'_source_id': -1, '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
             'id': 'a3afd0b3-d24f-2e8b-d2c7-8000f30d259b', 'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0)
             }])

        TblBefore_attr_a = TableBefore().get_field_class('a')
        TblBefore_attr_b = TableBefore().get_field_class('b')
        create(TblBefore_attr_a)
        write(TblBefore_attr_a, [
                    {'a': 42, '_source_id': -1, '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
                     'id': 'a3afd0b3-d24f-2e8b-d2c7-8000f30d259b', 'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
                     'utc_valid_to_dttm': datetime(9999, 12, 31, 0, 0)}])
        create(TblBefore_attr_b)
        write(TblBefore_attr_b, [
                    {'b': 52, '_source_id': -1, '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
                     'id': 'a3afd0b3-d24f-2e8b-d2c7-8000f30d259b', 'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
                     'utc_valid_to_dttm': datetime(9999, 12, 31, 0, 0)}])

        task = migration.rename_column(TableAfter, 'b', 'c')
        run_migration_in_same_process(task)
        TblAfter_attr_a = TableAfter().get_field_class('a')
        TblAfter_attr_c = TableAfter().get_field_class('c')

        # Колонки "c" теперь быть не должно:
        assert_real_field_type(TblAfter_attr_a, 'a', 'integer')
        assert_no_field_in_db(TblAfter_attr_c, 'b')
        assert_real_field_type(TblAfter_attr_c, 'c', 'integer')

        result = list(map(dict, gp.connection.select_all(TblAfter_attr_c)))
        assert result == [
            {'c': 52, '_source_id': -1, '_utc_etl_processed_dttm': datetime(2019, 1, 1, 0, 0),
             'id': 'a3afd0b3-d24f-2e8b-d2c7-8000f30d259b', 'utc_valid_from_dttm': datetime(2018, 1, 1, 0, 0),
             'utc_valid_to_dttm': datetime(9999, 12, 31, 0, 0)},
        ]

        # Повторный вызов таска не должен приводить к ошибке,
        # так как состояние базы уже такое как нужно

        task = migration.rename_column(TableAfter, 'b', 'c')
        # необходимо сгененировать новый id запуска, тк выполнять несколько раз таск в рамках одного run_id недопустимо
        generate_new_taxidwh_run_id()
        run_migration_in_same_process(task)
        assert_no_field_in_db(TblAfter_attr_c, 'b')
        assert_real_field_type(TblAfter_attr_c, 'c', 'integer')


@pytest.mark.slow('gp')
def test_rename_should_fail_if_original_column_is_missing():
    # Если колонки которая должна быть переименована,
    # уже нет, то это явная ошибка.
    with gp.connection.transaction():
        class TableBefore(GPTable):
            __layout__ = utils.TestLayout(name='example')

            a = Int()
            # Колонка оставлена закомментированой специально,
            # чтобы показать, что она должна отсутствовать в базе
            # b = Int()

        class TableAfter(GPTable):
            __layout__ = utils.TestLayout(name='example')

            a = Int()
            c = Int()

        create(TableBefore)

        task = migration.rename_column(TableAfter, 'b', 'c')

        with pytest.raises(RuntimeError):
            run_migration_in_same_process(task)

        # Состояние в базе должно остаться прежним:
        assert_real_field_type(TableAfter, 'a', 'integer')
        assert_no_field_in_db(TableAfter, 'b')
        assert_no_field_in_db(TableAfter, 'c')


@pytest.mark.slow('gp')
def test_rename_should_fail_if_target_column_already_exists():
    # В этой ситуации колонка "c" уже существует, таск тоже должен упасть.
    with gp.connection.transaction():
        class TableBefore(GPTable):
            __layout__ = utils.TestLayout(name='example')

            a = Int()
            b = Int()
            c = Int()

        create(TableBefore)

        task = migration.rename_column(TableBefore, 'b', 'c')

        with pytest.raises(RuntimeError):
            run_migration_in_same_process(task)

        # Состояние в базе должно остаться прежним:
        assert_real_field_type(TableBefore, 'a', 'integer')
        assert_real_field_type(TableBefore, 'b', 'integer')
        assert_real_field_type(TableBefore, 'c', 'integer')


@pytest.mark.slow('gp')
def test_rename_should_fail_if_types_are_different():
    # Если в метаданных тип колонки отличается от прежней,
    # то такая миграция тоже должна быть невозможна.
    with gp.connection.transaction():
        class TableBefore(GPTable):
            __layout__ = utils.TestLayout(name='example')

            a = Int()
            b = Int()
            c = Int()
            d = Int()

        class TableAfter(GPTable):
            __layout__ = utils.TestLayout(name='example')

            a = Int()
            b = String()  # Не трограем
            e = String()  # Делаем ренейминг + меняем тип
            d = String()  # Не трограем

        create(TableBefore)

        task = migration.rename_column(TableAfter, 'c', 'e')

        run_migration_in_same_process(task)

        # Произошел каст + ренейминг там где нужно
        assert_real_field_type(TableAfter, 'a', 'integer')
        assert_real_field_type(TableAfter, 'b', 'integer')  # Тип не поменялся
        assert_real_field_type(TableAfter, 'e', 'varchar')  # Тип поменялся
        assert_real_field_type(TableAfter, 'd', 'integer')  # Тип не поменялся


@pytest.mark.slow('gp')
def test_rename_should_fail_if_target_column_missing_in_metadata():
    # Если в метаданных нет указанной колонки,
    # то такая миграция тоже должна быть невозможна.
    with gp.connection.transaction():
        class TableBefore(GPTable):
            __layout__ = utils.TestLayout(name='example')

            a = Int()
            b = Int()

        class TableAfter(GPTable):
            __layout__ = utils.TestLayout(name='example')

            a = Int()
            # У новой таблицы колонки 'с' на самом деле нет
            # c = Int()

        create(TableBefore)

        task = migration.rename_column(TableAfter, 'b', 'c')

        with pytest.raises(AssertionError):
            run_migration_in_same_process(task)

        # Состояние в базе должно остаться прежним:
        assert_real_field_type(TableAfter, 'a', 'integer')
        assert_real_field_type(TableAfter, 'b', 'integer')
        assert_no_field_in_db(TableAfter, 'c')
