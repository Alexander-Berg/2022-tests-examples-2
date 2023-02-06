import os

import pytest
from metrika.pylib import clickhouse
from yatest.common import source_path


@pytest.fixture()
def cfg_with_cluster_parts():
    return """
        user: default
        password:
        hosts:
            - 127.0.0.1
        parts: 3
        databases:
            test:
                tables:
                    - test_table
    """


@pytest.fixture()
def cfg_with_db_parts():
    return """
        user: default
        password:
        hosts:
            - 127.0.0.1
        parts: 3
        databases:
            test:
                parts: 5
                tables:
                    - test_table
    """


@pytest.fixture()
def cfg_with_table_parts():
    return """
        user: default
        password:
        hosts:
            - 127.0.0.1
        parts: 3
        databases:
            test:
                parts: 5
                tables:
                    test_table:
                        parts: 7
    """


@pytest.fixture()
def cfg_with_cluster_port():
    return """
        user: default
        password:
        port: 1337
        hosts:
            - 127.0.0.1
        parts: 3
        databases:
            test:
                tables:
                    - test_table
    """


@pytest.fixture()
def cfg_with_host_port():
    return """
        user: default
        password:
        port: 1337
        hosts:
            127.0.0.1: 1337
            127.0.0.2:
        parts: 3
        databases:
            test:
                tables:
                    - test_table
    """


@pytest.fixture()
def cfg_with_all_tables():
    return """
        user: default
        password:
        port: 1337
        hosts:
            - 127.0.0.1
        parts: 3
        databases:
            test:
                tables: all
    """


@pytest.fixture()
def test_ch_cfg():
    def fixture(*tables: str, regexp: str = None, parts: int = 3):
        return f"""
            user: default
            password:
            port: {int(os.environ['RECIPE_CLICKHOUSE_HTTP_PORT'])}
            hosts:
                - 127.0.0.1
            parts: {parts}
            databases:
                test:
                    tables: {f"[{', '.join(tables)}]" if tables else regexp}
        """

    return fixture


@pytest.fixture()
def ch():
    ch = clickhouse.ClickHouse(user='default', port=int(os.environ['RECIPE_CLICKHOUSE_HTTP_PORT']))

    dir = source_path('metrika/admin/python/scripts/clickhouse_parts_cleaner/tests/data')
    tables = os.listdir(dir)
    for table in tables:
        values = ', '.join(f"('{l.strip()}')" for l in open(os.path.join(dir, table), encoding='utf8').readlines())
        ch.execute(clickhouse.Query(f'INSERT INTO TABLE {table} VALUES {values}', method='POST'))

    yield ch

    for table in tables:
        ch.execute(clickhouse.Query(f'ALTER TABLE {table} DELETE WHERE 1', method='POST'))
