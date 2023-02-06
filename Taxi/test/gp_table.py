# -*- coding: utf-8 -*-
import uuid

from core.connection import GPConnection, PostgreSQLConnection
from suite.gp import GPMeta

CREATE_OBJECTS = '''
        CREATE SEQUENCE {schema_name}.{sequence_name};
        CREATE TABLE {schema_name}.{table_name}
        (
          id_column   INT,
          text_column VARCHAR,
          dttm_column TIMESTAMP WITHOUT TIME ZONE,
          seq_column  INT                          DEFAULT nextval('{schema_name}.{sequence_name}')
        )
        WITH (APPENDONLY=true, COMPRESSLEVEL=2, ORIENTATION=column, COMPRESSTYPE=zlib)
        DISTRIBUTED BY (id_column)
        PARTITION BY LIST(text_column)
        SUBPARTITION BY RANGE(dttm_column) (
          PARTITION first VALUES ('first') (
            SUBPARTITION "2012" START ('2012-01-01' :: DATE) END ('2013-01-01' :: DATE) EVERY ('1 year'::interval),
            SUBPARTITION "2013" START ('2013-01-01' :: DATE) END ('2014-01-01' :: DATE) EVERY ('1 year'::interval),
            SUBPARTITION "2014" START ('2014-01-01' :: DATE) END ('2015-01-01' :: DATE) EVERY ('1 year'::interval),
            SUBPARTITION "2015" START ('2015-01-01' :: DATE) END ('2016-01-01' :: DATE) EVERY ('1 year'::interval)
          ),
          DEFAULT PARTITION last (
            SUBPARTITION "2012" START ('2012-01-01' :: DATE) END ('2013-01-01' :: DATE) EVERY ('1 year'::interval),
            SUBPARTITION "2013" START ('2013-01-01' :: DATE) END ('2014-01-01' :: DATE) EVERY ('1 year'::interval),
            SUBPARTITION "2014" START ('2014-01-01' :: DATE) END ('2015-01-01' :: DATE) EVERY ('1 year'::interval),
            SUBPARTITION "2015" START ('2015-01-01' :: DATE) END ('2016-01-01' :: DATE) EVERY ('1 year'::interval)
          )
        );
        CREATE VIEW {schema_name}.{view_name} AS SELECT * FROM {schema_name}.{table_name};
    '''

DROP_OBJECTS = '''
        DROP VIEW {schema_name}.{view_name};
        DROP TABLE {schema_name}.{table_name};
        DROP SEQUENCE {schema_name}.{sequence_name};
    '''

CHECK_TABLE = '''
        SELECT count(*) AS cnt
        FROM pg_tables
        WHERE schemaname || '.' || tablename = '{schema_name}.{table_name}';
    '''

SCHEMA_NAME = 'snb_taxi'
TABLE_NAME = 't_{0}'.format(uuid.uuid4().__str__().replace('-', '_'))
SEQUENCE_NAME = 's_{0}'.format(uuid.uuid4().__str__().replace('-', '_'))
VIEW_NAME = 'v_{0}'.format(uuid.uuid4().__str__().replace('-', '_'))

DATABASE_NAME = 'butthead'

_GP_CONN: GPConnection = GPConnection()
GP_CONN: PostgreSQLConnection = _GP_CONN[DATABASE_NAME]


def create_gp_object():
    GP_CONN.execute(CREATE_OBJECTS.format(
        sequence_name=SEQUENCE_NAME,
        schema_name=SCHEMA_NAME,
        table_name=TABLE_NAME,
        view_name=VIEW_NAME
    ))


def drop_gp_object():
    GP_CONN.execute(DROP_OBJECTS.format(
        sequence_name=SEQUENCE_NAME,
        schema_name=SCHEMA_NAME,
        table_name=TABLE_NAME,
        view_name=VIEW_NAME
    ))


def check_table_exists():
    table_exists = 0
    for row in GP_CONN.execute_and_get_dict_result(CHECK_TABLE.format(
            schema_name=SCHEMA_NAME,
            table_name=TABLE_NAME
    )):
        table_exists = row['cnt']
    return table_exists > 0


def get_gp_object(schema_name: str, object_name: str, database_name: str) -> GPMeta:
    return GPMeta(database_name, schema_name, object_name, logger_extra={})
