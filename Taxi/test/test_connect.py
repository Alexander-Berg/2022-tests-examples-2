# -*- coding: utf-8 -*-
from psycopg2.sql import SQL, Identifier
import pytest
import uuid

from core.connection import PGaaSConnection

CREATE_TABLE = '''
        CREATE TABLE {schema_name}.{table_name}
        (
            id   INT,
            name VARCHAR
        );
    '''

DROP_TABLE = '''
        DROP TABLE {schema_name}.{table_name};
    '''

CHECK_TABLE_EXISTS = '''
        SELECT count(*) AS cnt
        FROM pg_tables
        WHERE schemaname = %(schema_name)s
              AND tablename = %(table_name)s;
    '''

SCHEMA_NAME = 'public'
TABLE_NAME = 't_{0}'.format(uuid.uuid4().__str__().replace('-', '_'))

PGAAS_CONN: PGaaSConnection = PGaaSConnection()


def check_table_exists():
    table_exists = 0
    query = CHECK_TABLE_EXISTS, dict(
        schema_name=SCHEMA_NAME,
        table_name=TABLE_NAME
    )
    for row in PGAAS_CONN.execute_and_get_dict_result(query):
        table_exists = row['cnt']
    return table_exists > 0


@pytest.mark.fast
def test_create_table():
    query = SQL(CREATE_TABLE).format(
        schema_name=Identifier(SCHEMA_NAME),
        table_name=Identifier(TABLE_NAME)
    )
    PGAAS_CONN.execute(query)

    assert check_table_exists()


@pytest.mark.fast
def test_insert_into_table():
    query = SQL('''INSERT INTO {schema_name}.{table_name} (id, name) VALUES (%(id)s, %(name)s)''').format(
        schema_name=Identifier(SCHEMA_NAME),
        table_name=Identifier(TABLE_NAME)
    ), dict(id=1, name='Test')
    PGAAS_CONN.execute(query)
    data = []
    query = SQL('''SELECT id, name FROM {schema_name}.{table_name}''').format(
        schema_name=Identifier(SCHEMA_NAME),
        table_name=Identifier(TABLE_NAME)
    )
    for row in PGAAS_CONN.execute_and_get_dict_result(query):
        data.append(row)

    assert [{'id': 1, 'name': 'Test'}] == data


@pytest.mark.fast
def test_update_table():
    query = SQL('''UPDATE {schema_name}.{table_name} SET name = %(name)s WHERE id = %(id)s''').format(
        schema_name=Identifier(SCHEMA_NAME),
        table_name=Identifier(TABLE_NAME)
    ), dict(id=1, name='T')
    PGAAS_CONN.execute(query)
    data = []
    query = SQL('''SELECT id, name FROM {schema_name}.{table_name}''').format(
        schema_name=Identifier(SCHEMA_NAME),
        table_name=Identifier(TABLE_NAME)
    )
    for row in PGAAS_CONN.execute_and_get_dict_result(query):
        data.append(row)

    assert [{'id': 1, 'name': 'T'}] == data


@pytest.mark.fast
def test_drop_table():
    query = SQL(DROP_TABLE).format(
        schema_name=Identifier(SCHEMA_NAME),
        table_name=Identifier(TABLE_NAME)
    )
    PGAAS_CONN.execute(query)

    assert not check_table_exists()


@pytest.mark.fast
def test_none_select():
    count = 0
    query = "SELECT schemaname, tablename FROM pg_tables WHERE tablename = 'nonexistent_table';"
    for row in PGAAS_CONN.execute_and_get_dict_result(query):
        count += 1
    assert count == 0
