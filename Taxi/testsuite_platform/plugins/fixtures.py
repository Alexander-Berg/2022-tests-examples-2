"""
    Describe here service specific fixtures.
"""
# pylint: disable=redefined-outer-name
import base64
import json
import typing

import pytest


@pytest.fixture(name='upsert_robot_state')
async def _upsert_robot_state(pgsql):
    def wrapper(name, state, *, status=None):
        if status is None:
            status = '{"status":"ACTIVE","last_flush":1632400798,' '"host":"rva3ukeypv63m5rm.sas.yp-c.yandex.net"}'
        cursor = pgsql['logistic_platform'].cursor()
        cursor.execute(
            """
            INSERT INTO rt_background_state
                (
                    bp_name,
                    bp_type,
                    bp_state,
                    bp_status
                )
            VALUES (
                %(name)s,
                'some_robot',
                %(state)s,
                %(status)s
            )
            ON CONFLICT (bp_name) DO UPDATE SET
                bp_state = EXCLUDED.bp_state,
                bp_status = EXCLUDED.bp_status
            """,
            dict(name=name, state=state, status=status),
        )

    return wrapper


@pytest.fixture(name='upsert_robot_settings')
async def _upsert_robot_settings(pgsql):
    def wrapper(name, settings, *, enabled=True):
        cursor = pgsql['logistic_platform'].cursor()
        cursor.execute(
            """
            INSERT INTO rt_background_settings
                (
                    bp_name,
                    bp_type,
                    bp_settings,
                    bp_enabled
                )
            VALUES (
                %(name)s,
                'some_robot',
                %(settings)s,
                %(enabled)s
            )
            ON CONFLICT (bp_name) DO UPDATE SET
                bp_settings = EXCLUDED.bp_settings,
                bp_enabled = EXCLUDED.bp_enabled
            """,
            dict(name=name, settings=settings, enabled=enabled),
        )

    return wrapper


@pytest.fixture(name='get_worker_state')
async def _get_worker_state(pgsql):
    def wrapper(worker_name):
        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute(
            """
            SELECT
                payload
            FROM united_dispatch.worker_state
            WHERE worker_name = %s
            """,
            (worker_name,),
        )
        state = cursor.fetchone()
        if state is None:
            return None
        return state['payload']

    return wrapper


@pytest.fixture(name='execute_pg_query')
async def _execute_pg_query(pgsql):
    def wrapper(query, db='ld'):
        cursor = pgsql[db].dict_cursor()
        cursor.execute(query)
        return cursor.fetchall()

    return wrapper


@pytest.fixture(name='print_pg_table')
async def _print_pg_table(pgsql):
    def wrapper(table_name, db='ld', schema=None):
        print(f'\n\n\n{schema}.{table_name} ROWS:')
        cursor = pgsql[db].dict_cursor()
        if schema is None:
            cursor.execute(f'select * from {table_name}')
        else:
            cursor.execute(f'select * from {schema}.{table_name}')
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            print(f'\t{dict(row)}')

    return wrapper


@pytest.fixture(name='print_pg_database')
async def _print_pg_database(print_pg_table, pgsql):
    def wrapper(db='ld'):
        cursor = pgsql[db].dict_cursor()
        cursor.execute('select table_name from information_schema.tables where table_schema=\'public\'')
        while True:
            row = cursor.fetchone()
            if row is None:
                break

            table_name = dict(row)['table_name']
            print_pg_table(table_name, db)

    return wrapper


def _serialize_cursor(index: int) -> str:
    return base64.b64encode(
        json.dumps({'index': index}).encode('utf-8'),
    ).decode()


def _deserialize_cursor(cursor: typing.Optional[str]) -> int:
    if not cursor:
        return 0
    doc = json.loads(base64.b64decode(cursor))
    return doc['index']


@pytest.fixture(name="default_configs_v3", autouse=True)
def _default_configs_v3(mockserver):
    @mockserver.json_handler('/v1/configs')
    def experiments(request):
        return {
            'items': [],
            'version': 0,
        }
