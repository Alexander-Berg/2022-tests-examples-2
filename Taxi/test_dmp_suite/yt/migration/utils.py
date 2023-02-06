import random

from connection.yt import get_yt_client
from dmp_suite.yt import resolve_meta
from dmp_suite.yt import etl
from dmp_suite.yt.dyntable_operation.operations import insert_chunk_in_dynamic_table, unmount_all_partitions
from dmp_suite.yt.operation import get_yt_attr, write_yt_table


def create(table):
    meta = resolve_meta(table)
    etl.init_target_table(meta)


def write(table, data):
    meta = resolve_meta(table)
    if meta.is_dynamic:
        insert_chunk_in_dynamic_table(meta, data)
    else:
        write_yt_table(
            meta.target_path(),
            data,
        )


def append(table, data):
    meta = resolve_meta(table)
    if meta.is_dynamic:
        # В этом вызове могут логгироваться ошибки, так как изменение схемы
        insert_chunk_in_dynamic_table(meta, data)
        # Чтобы следующее за append чтение увидело полные данные,
        # динамическую таблицу надо отмонтировать:
        unmount_all_partitions(meta)
    else:
        write_yt_table(
            meta.target_path(),
            data,
            append=True
        )


def read(table):
    meta = resolve_meta(table)
    rows = get_yt_client().read_table(
        meta.target_path(),
    )
    return list(rows)


def get_real_schema(table):
    """ Возвращает упрощённую схему в в виде словаря поле -> тип. """
    meta = resolve_meta(table)
    yt_schema = get_yt_attr(meta, 'schema')
    simple_schema = {
        item['name']: item['type']
        for item in yt_schema
    }
    return simple_schema


def random_ticket():
    number = random.randint(1, 100000)
    return f'TEST-{number}'
