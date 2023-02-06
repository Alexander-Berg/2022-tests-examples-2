import pytest
from psycopg2.sql import SQL, Identifier

from dmp_suite.greenplum import GPLocation, ExternalGPTable
from test_dmp_suite.greenplum.utils import random_name


@pytest.fixture(scope='session')
def temp_gp_schema(slow_test_settings):
    from connection import greenplum as gp
    schema_name = None
    try:
        schema_name = 'test_' + random_name(8)
        yield schema_name
    finally:
        # не используем готовый коннекшен, так как не знаем в каком он состоянии
        if schema_name:
            with slow_test_settings(), gp._get_default_connection() as conn:
                with conn.transaction():
                    sql = SQL('DROP SCHEMA IF EXISTS {schema} RESTRICT').format(
                        schema=Identifier(schema_name)
                    )
                    conn.execute(sql)


def create_random_table(table_cls, temp_gp_schema):
    random_suffix = random_name(5)

    if table_cls.__location_cls__ == GPLocation:

        class RandomizedGPLocation(GPLocation):
            schema_pattern = temp_gp_schema
            table_name_pattern = "{name}_" + random_suffix

    elif table_cls.__location_cls__ == ExternalGPTable:

        class RandomizedGPLocation(ExternalGPTable):
            schema_pattern = temp_gp_schema
            table_name_pattern = "{table}_" + random_suffix
    else:
        raise ValueError(
            f'Unsupported location: {table_cls.__location_cls__}'
        )

    class RandomizedTable(table_cls):
        __location_cls__ = RandomizedGPLocation

    return RandomizedTable


@pytest.fixture(scope="function")
def random_table(request, temp_gp_schema):
    """
    Creates a table, attaching a random suffix to the name and random schema
    """
    yield create_random_table(request.param, temp_gp_schema)


@pytest.fixture(scope="function")
def throwaway_table(request, temp_gp_schema):
    """Create random table + init + cleanup"""
    from connection import greenplum as gp
    random_table = create_random_table(request.param, temp_gp_schema)
    # Setup.
    with gp.connection.transaction():
        if gp.connection.check_table_schema_exists(random_table):
            gp.connection.drop_table(random_table)
        gp.connection.create_table(random_table)
    # Test.
    yield random_table
    # Cleanup.
    with gp.connection.transaction():
        if gp.connection.check_table_schema_exists(random_table):
            gp.connection.drop_table(random_table)
