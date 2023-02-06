from datetime import datetime
from itertools import repeat, chain

import logging
import random
import string
import uuid
import typing as tp

from collections import namedtuple
from contextlib import contextmanager

from psycopg2.sql import SQL, Identifier
from yt.wrapper import YsonFormat

from context.settings import settings
from core.errors import BasicError
from . cli_tools.generate_data import generate_data

from core.statuses_storage import ProcessLog

logger = logging.getLogger(__name__)


GP_TABLE_CREATE_STATEMENT = """
    create table {}
    (
      col1 int8,
      col2 varchar
    )
    distributed by (col1);
"""

GP_TABLE_CREATE_STATEMENT_WITH_FLOAT = """
    create table {}
    (
      col1 float,
      col2 varchar
    )
    distributed by (col1);
"""

GP_GENERIC_CREATE_STATEMENT = """
    CREATE TABLE {}
    ({})
    DISTRIBUTED BY (distr);
"""

GP_GENERIC_INSERT_STATEMENT = """
    INSERT INTO {} ({})
    VALUES
    {};
"""


def generate_random_string():
    return uuid.uuid4().hex


def generate_gp_tmp_table_name(schema, prefix):
    return '{}.{}_{}'.format(
        schema, prefix, generate_random_string())


@contextmanager
def with_tmp_gp_table(
    schema,
    prefix,
    gp_connection,
    create_statement=GP_TABLE_CREATE_STATEMENT
):
    table_name = generate_gp_tmp_table_name(schema, prefix)
    create_statement = create_statement.format(table_name)
    gp_connection.execute(create_statement)

    yield table_name


Column = namedtuple('Column', ['name', 'yt_type', 'gp_type', 'gen_func', 'is_key', 'required'],
                    defaults=(False, False))  # is_key=False and required=False by default


@contextmanager
def prepare_generic_gp_table(
    schema: str,
    prefix: str,
    gp_connection: str,
    columns: tp.List[Column],
    data: tp.Optional[type] = None
):
    table_name = generate_gp_tmp_table_name(schema, prefix)
    create_statement = GP_GENERIC_CREATE_STATEMENT.format(
        table_name,
        ',\n'.join(f'{c.name} {c.gp_type}' for c in columns)
    )
    gp_connection.execute(create_statement)
    try:
        if data:
            # generate pattern_for_values = '(%s, %s,...), (%s, %s,...), ...'
            row_pattern = '({})'.format(', '.join(repeat('%s', len(columns))))
            pattern_for_values = ', '.join(repeat(row_pattern, len(data)))
            d = tuple(chain(*data))
            q = GP_GENERIC_INSERT_STATEMENT.format(table_name, ','.join([c.name for c in columns]), pattern_for_values)
            logger.debug(q, d)
            gp_connection.execute((q, d))
        yield table_name
    finally:
        try:
            gp_connection.execute('drop table {}'.format(table_name))
        except BasicError:
            pass


def grant_all_on_gp(gp_connection, table_name, grant, user):
    schema, table = table_name.split('.')
    sql = SQL('GRANT {grant} ON {schema}.{table} TO {user}').format(
        schema=Identifier(schema),
        table=Identifier(table),
        grant=SQL(grant),
        user=Identifier(user)
    ).as_string(gp_connection._connection)
    gp_connection.execute(sql)


def revoke_all_on_gp(gp_connection, table_name, grant, user):
    schema, table = table_name.split('.')
    sql = SQL('REVOKE {grant} ON {schema}.{table} FROM {user}').format(
        schema=Identifier(schema),
        table=Identifier(table),
        grant=SQL(grant),
        user=Identifier(user)
    ).as_string(gp_connection._connection)
    gp_connection.execute(sql)


def prepare_generic_yt_table(yt_client, prefix, attributes, data=None):
    yt_table = yt_client.create_temp_table(
        path=settings('tests.YT_PATH_PREFIX'),
        prefix=prefix,
        attributes=attributes
    )
    if data:
        if attributes.get('dynamic', False):
            yt_client.mount_table(yt_table, sync=True)
            yt_client.insert_rows(yt_table, data)

        else:
            yt_client.write_table(
                table=yt_table,
                input_stream=data,
                format=YsonFormat()
            )

    return yt_table


def prepare_yt_table(yt_client, rows, chunk_table):

    data = generate_data(rows, chunk_table)

    attributes = None
    if not chunk_table:
        attributes = {
            'schema': [
                {
                    'name': 'col1',
                    'type': 'int64'
                },
                {
                    'name': 'col2',
                    'type': 'string'
                }
            ]
        }

    return prepare_generic_yt_table(
        yt_client, 'gp_transfer_test', attributes or {}, data)


def prepare_yt_table_with_infinities(yt_client):

    def generate_data():
        float_values = [
            random.random(),
            float('inf'),
            float('-inf'),
            float('nan')
        ]
        for float_value in float_values:
            random_string = ''.join([
                random.choice(string.ascii_lowercase) for _ in range(64)])
            yield {'col1': float_value, 'col2': random_string}

    data = generate_data()

    attributes = {
        'schema': [
            {
                'name': 'col1',
                'type': 'double'
            },
            {
                'name': 'col2',
                'type': 'string'
            }
        ]
    }

    return prepare_generic_yt_table(
        yt_client, 'gp_transfer_test_with_infs', attributes, data)


def prepare_yt_table_with_errors_in_data(yt_client):

    def generate_data():
        random_string = ''.join([
            random.choice(string.ascii_lowercase) for _ in range(64)])
        yield {'chunk': '{}\t{}'.format(random_string, random_string)}

    data = generate_data()

    return prepare_generic_yt_table(
        yt_client, 'gp_transfer_test_with_errors', {}, data)


def gen_process_log(
        to_row: int = None,
        rows_count: int = 100,
        force_last_percent: float = None
) -> tp.List[ProcessLog]:
    """
    Возвращает список логов, эмулирует получение логов из PGaaS
    :param to_row: до какой записи создать логи
    :param rows_count: количество записей
    :param force_last_percent: форсить процент в последней строке
    :return:
    """
    def _append(item, finished_flg):
        percent = force_last_percent if (finished_flg and force_last_percent) else item / float(rows_count) * 100
        logs.append(ProcessLog(
            process_uuid='process_uuid',
            page=0,
            attempt=0,
            log_text='text',
            rows_processed=item,
            progress_pcnt=percent,
            finished_flg=finished_flg,
            error_flg=True if (finished_flg and item != rows_count) else False,
            log_dttm=datetime.utcnow(),
        ))
    to_row = rows_count if to_row is None else to_row
    logs = []
    i = 1
    while i < to_row:
        _append(i, finished_flg=False)
        i += 1

    _append(i, finished_flg=True)

    return logs
