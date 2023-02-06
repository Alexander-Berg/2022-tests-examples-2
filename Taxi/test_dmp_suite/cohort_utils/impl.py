from pprint import pformat

from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL, Identifier
from typing import Iterable, Dict

from connection import greenplum as gp

from dmp_suite.greenplum import resolve_meta, GPEtlTable


def gp_table_to_dict(gp_etl_table: GPEtlTable) -> Iterable[Dict]:
    """
    Get all rows from GPtable in a dict format, excluding '_etl_processed_dttm' field.
    """
    meta = resolve_meta(gp_etl_table)
    sql = SQL('SELECT * FROM {schema}.{table}').format(
        schema=Identifier(meta.schema),
        table=Identifier(meta.table_name)
    )
    with gp.connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql)
        res = [dict(row) for row in cur.fetchall()]
        for row in res:
            # exclude _etl_processed_dttm from result
            del row['_etl_processed_dttm']

        return res


def compare_expected_actual(expected_data, actual_data):
    expected_data = sorted(expected_data, key=lambda d: sorted(d.items()))
    actual_data = sorted(actual_data, key=lambda d: sorted(d.items()))
    if len(expected_data) != len(actual_data):
        raise ValueError(f"The expected data differs in length from the actual data:\n"
            f"{pformat(expected_data)}\n"
            f"{pformat(actual_data)}")
    for expected_row, actual_row in zip(expected_data, actual_data):
        if expected_row != actual_row:
            raise ValueError(
                f"The expected row differs from the actual row:\n"
                f"{pformat(expected_row)}\n"
                f"{pformat(actual_row)}"
            )


def recreate_and_fill(table, data):
    with gp.connection.transaction():
        gp.connection.create_schema(table)
        gp.connection.create_table(table)
        gp.connection.insert(table, data)
