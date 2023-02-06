import typing as tp

from connection import greenplum as gp
from dmp_suite.greenplum import (
    GPTable,
)
from dmp_suite.task.execution import _run_migration


def create(table):
    gp.connection.create_table(table)


def write(table, data):
    gp.connection.insert(table, data)


def read(table, key='a'):
    rows = list(map(dict, gp.connection.select_all(table)))
    # так как select_all не задаёт ORDER, а в тестах нам
    # нужны стабильные результаты, то отсортируем строки сами
    # по полю 'a', оно в тестах должно быть всегда
    # p.s переопределение значения аргумента key допустимо только для
    # тестирования hnhm-сущностей
    rows.sort(key=lambda d: d[key], reverse=True)
    return rows


def run_migration_in_same_process(migration_task):
    """
    В тестах таблицы могут создаваться в транзакции, а так как по-умолчанию
    миграции запускаются в подпроцессе (из-за лока), то там таблицы будут не видны.
    Поэтому в тестах нам надо запускать миграции в том же процессе.
    """
    _run_migration(migration_task, use_lock=False)


def assert_real_field_type(table: tp.Type[GPTable], column_name: str, expected_type: str) -> None:
    """Функция-алиас, для большей читаемости тестов."""
    gp.connection._assert_real_field_type(table, column_name, expected_type)


def assert_no_field_in_db(table: tp.Type[GPTable], column_name: str) -> None:
    if gp.connection._is_field_in_db(table, column_name):
        raise AssertionError(f'Column "{column_name}" exists in database.')
