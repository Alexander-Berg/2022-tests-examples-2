import collections

import pytest

from taxi_tests.plugins import pgsql

from . import exceptions


@pytest.fixture(scope='session')
def sql_databases(postgresql_connections, pgsql_disabled,
                  ensure_service_started):
    """Obsolete global databases handlers."""
    if postgresql_connections and not pgsql_disabled:
        ensure_service_started('postgresql')
    return pgsql.PostgresqlDatabases(postgresql_connections)


@pytest.fixture(autouse=True)
def sql_apply(request, load, sql_databases):
    """
    Deprecated! Use pgsql instead!

    Takes a markers with *args and **kwargs like that:
        'orders', ['select query', ]
        'orders', 'insert query', 'alter query',
        orders='alias', payments='default',
        where alias is used like this:
            'pg_{db_name}_{alias}.sql'
        anyway it use 'pg_{db_name}.sql' file by default.

        So for orders file should be like: 'pg_orders_alias.sql'
        or 'pg_orders.sql' in case alias == 'default'

    :param request:
    :type sql_databases: PostgresqlDatabases
    :param load: load fixture
    """
    sql_exec_markers = request.node.get_marker('sql')
    if not sql_exec_markers:
        return

    db_queries = collections.defaultdict(list)

    for mark in sql_exec_markers:
        for db_name, db_alias in mark.kwargs.items():
            if db_alias == 'default':
                queries_file = db_name
            else:
                queries_file = '%s_%s' % (db_name, db_alias)

            db_queries[db_name].append(
                load('pg_%s.sql' % queries_file),
            )

        if mark.args:
            db_name = mark.args[0]
            db_queries[db_name].extend(mark.args[1:])

    for db_name, queries in db_queries.items():
        pg_db = _sql_get_database_checked(sql_databases, db_name)
        pg_db.apply_queries(queries)


def _sql_get_database_checked(sql_databases, db_name):
    if not hasattr(sql_databases, db_name):
        raise exceptions.PostgresqlError(
            'postgresql database %s was not configured' % (db_name,))

    return getattr(sql_databases, db_name)
