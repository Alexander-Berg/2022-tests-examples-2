from psycopg2 import extensions
from psycopg2 import extras


def register_user_types(cursor):
    extras.register_composite('persey_payments.bound_uids', cursor)


def fill_db_table(cursor, table, values):
    caster = extras.register_composite(table, cursor)
    tuples = []
    for value in values:
        value_tuple = []
        for name in caster.attnames:
            pg_value = value.get(name, None)
            value_tuple.append(pg_value)
        tuples.append(tuple(value_tuple))
    cursor.execute(
        'INSERT INTO %(table)s SELECT (__inner.__val).* FROM ('
        'SELECT UNNEST(%(tuples)s::%(table)s[]) "__val") "__inner"',
        {'tuples': tuples, 'table': extensions.AsIs(table)},
    )


def fill_db(cursor, tables):
    if isinstance(tables, list):
        for nested_tables in tables:
            fill_db(cursor, nested_tables)
    else:
        for table, values in tables.items():
            fill_db_table(cursor, table, values)
