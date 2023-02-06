from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL, Identifier
from typing import Iterable, Dict
import os

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


def recreate_and_fill(table, data):
    with gp.connection.transaction():
        gp.connection.create_schema(table)
        gp.connection.create_table(table)
        gp.connection.insert(table, data)


def from_directory(as_file, offset, file_path):
    path = os.sep.join(as_file.split(os.sep)[:-offset])
    return os.path.join(path, file_path)
