import pytest
from psycopg2.sql import SQL

from dmp_suite.greenplum.maintenance.partition.expired import ExpiredPartition
from dmp_suite.greenplum.maintenance.partition.relocation_nvme_to_ssd import nvme_expired_partitions
from connection import greenplum as gp


@pytest.mark.slow('gp')
def test_nvme_expired_partitions():
    # запрос должен вернуть только партиции с nvme
    sql_expired_partition = SQL('''
SELECT    
    'test_schema' as schemaname,
    'test_table' as tablename,
    1 as partitionlevel,
    'nvme' as gp_tablespace,
    '202005' as partitionname,
    'hist' as parentpartitionname
UNION
SELECT
    'test_schema' as schemaname,
    'test_table' as tablename,
    1 as partitionlevel,
    'ssd' as gp_tablespace,
    '202004' as partitionname,
    'hist' as parent_partition_name
UNION
SELECT
    'test_schema' as schemaname,
    'test_table' as tablename,
    1 as partitionlevel,
    'other' as gp_tablespace,
    '202003' as partitionname,
    '' as parentpartitionname
    ''').format()
    partitions = nvme_expired_partitions(gp.connection, sql_expired_partition)
    expected = [ExpiredPartition('test_schema', 'test_table', '202005', 'hist', 1)]
    assert list(partitions) == expected
