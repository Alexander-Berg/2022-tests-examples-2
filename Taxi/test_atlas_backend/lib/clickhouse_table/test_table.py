# flake8: noqa
# pylint: disable=C0103
# pylint: disable=W0212
import pytest

from atlas_backend.lib.clickhouse_table import table as table_lib
from atlas_backend.lib import exceptions


rmt_create_query = """CREATE TABLE IF NOT EXISTS test.table ON CLUSTER atlastest 
(
    "car_class" String,
    "city" Nullable(String),
    "date" Date
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/test/table', '{replica}')
PARTITION BY toYYYYMM(date)
ORDER BY (date, car_class)
SETTINGS index_granularity = 8192"""

rcmt_create_query = """CREATE TABLE IF NOT EXISTS test.table_rcmt ON CLUSTER atlastest 
(
    "car_class" String,
    "city" Nullable(String),
    "date" Date,
    "sign" Int8
)
ENGINE = ReplicatedCollapsingMergeTree('/clickhouse/tables/{shard}/test/table_rcmt', '{replica}', sign)
PARTITION BY toYYYYMM(date)
ORDER BY (date, car_class)
SETTINGS index_granularity = 8192"""

rrmt_create_query = """CREATE TABLE IF NOT EXISTS test.table_rrmt ON CLUSTER atlastest 
(
    "car_class" String,
    "city" Nullable(String),
    "date" Date
)
ENGINE = ReplicatedReplacingMergeTree('/clickhouse/tables/{shard}/test/table_rrmt', '{replica}')
PARTITION BY toYYYYMM(date)
ORDER BY (date, car_class)
SETTINGS index_granularity = 8192"""

distr_data_create_query = """CREATE TABLE IF NOT EXISTS distr_data_db.distr_data_table ON CLUSTER distr_data_cluster 
(
    "car_class" String,
    "city" Nullable(String),
    "date" Date,
    "sign" Int8
)
ENGINE = ReplicatedCollapsingMergeTree('/clickhouse/tables/{shard}/distr_data_db/distr_data_table', '{replica}', sign)
PARTITION BY toYYYYMM(date)
ORDER BY (date, car_class)
SETTINGS index_granularity = 8192"""

distr_create_query = """CREATE TABLE IF NOT EXISTS test.distr_data_table ON CLUSTER test_cluster 
(
    "car_class" String,
    "city" Nullable(String),
    "date" Date,
    "sign" Int8
)
ENGINE = Distributed(test_cluster, distr_data_db, distr_data_table, intDiv(toUnixTimestamp(date), 60))"""

changed_distr_data_create_query = """CREATE TABLE IF NOT EXISTS new_data_database.other_table_name ON CLUSTER distr_data_cluster 
(
    "car_class" String,
    "city" Nullable(String),
    "date" Date,
    "sign" Int8
)
ENGINE = ReplicatedCollapsingMergeTree('/clickhouse/tables/{shard}/new_data_database/other_table_name', '{replica}', sign)
PARTITION BY toYYYYMM(date)
ORDER BY (date, car_class)
SETTINGS index_granularity = 8192"""

changed_distr_create_query = """CREATE TABLE IF NOT EXISTS test.new_table_name ON CLUSTER new_cluster_name 
(
    "car_class" String,
    "city" Nullable(String),
    "date" Date,
    "sign" Int8
)
ENGINE = Distributed(new_cluster_name, new_data_database, other_table_name, intDiv(toUnixTimestamp(date), 60))"""

distr_data_nested_create_query = """CREATE TABLE IF NOT EXISTS distr_data_db.distr_data_table ON CLUSTER distr_data_cluster 
(
    "car_class" String,
    "city" Nullable(String),
    "date" Date,
    "sign" Int8,
    "statuses" Nested("status" String, "date" DateTime, "value" Nullable(Float64))
)
ENGINE = ReplicatedCollapsingMergeTree('/clickhouse/tables/{shard}/distr_data_db/distr_data_table', '{replica}', sign)
PARTITION BY toYYYYMM(date)
ORDER BY (date, car_class)
SETTINGS index_granularity = 8192"""

distr_nested_create_query = """CREATE TABLE IF NOT EXISTS test.distr_data_table ON CLUSTER test_cluster 
(
    "car_class" String,
    "city" Nullable(String),
    "date" Date,
    "sign" Int8,
    "statuses" Nested("status" String, "date" DateTime, "value" Nullable(Float64))
)
ENGINE = Distributed(test_cluster, distr_data_db, distr_data_table, intDiv(toUnixTimestamp(date), 60))"""


@pytest.mark.parametrize('yaml_name', ['table_rcmt.yaml'])
async def test_main_rcmt(clickhouse_table_config, yaml_name):
    table = await table_lib.Table.from_config(clickhouse_table_config)
    assert table.meta.engine == 'ReplicatedCollapsingMergeTree'
    assert table.meta.sign_column == 'sign'
    assert await table.create_table_query('atlastest') == rcmt_create_query


@pytest.mark.parametrize('yaml_name', ['table_rrmt.yaml'])
async def test_main_rrmt(clickhouse_table_config, yaml_name):
    table = await table_lib.Table.from_config(clickhouse_table_config)
    assert table.meta.engine == 'ReplicatedReplacingMergeTree'
    assert await table.create_table_query('atlastest') == rrmt_create_query


@pytest.mark.parametrize('yaml_name', ['table_rmt.yaml'])
async def test_main_rmt(clickhouse_table_config, yaml_name):
    table = await table_lib.Table.from_config(clickhouse_table_config)
    assert table.meta.engine == 'ReplicatedMergeTree'
    assert await table.create_table_query('atlastest') == rmt_create_query


async def test_empty_rmt():
    test_config = {}
    with pytest.raises(exceptions.ConfigError):
        await table_lib.Table.from_config(test_config)


@pytest.mark.parametrize('yaml_name', ['table_distr.yaml'])
async def test_main_distr(clickhouse_table_config, yaml_name):
    table = await table_lib.DistributedTable.from_config(
        clickhouse_table_config,
    )

    assert table.meta.engine == 'Distributed'
    assert table.meta.database == 'test'
    assert table.meta.table_name == 'distr_data_table'
    assert table.meta.sharding_key == 'intDiv(toUnixTimestamp(date), 60)'
    assert (
        table.distr_data_table.meta.engine == 'ReplicatedCollapsingMergeTree'
    )
    assert table.distr_data_table.meta.database == 'distr_data_db'
    assert table.distr_data_table.meta.table_name == 'distr_data_table'

    assert await table.create_table_query('test_cluster') == distr_create_query
    assert (
        await table.distr_data_table.create_table_query('distr_data_cluster')
        == distr_data_create_query
    )


@pytest.mark.parametrize('yaml_name', ['table_distr.yaml'])
async def test_changed_meta_fields_distr(clickhouse_table_config, yaml_name):
    table = await table_lib.DistributedTable.from_config(
        clickhouse_table_config,
    )
    table.meta.table_name = 'new_table_name'
    table.distr_data_table.meta.table_name = 'other_table_name'
    table.distr_data_table.meta.database = 'new_data_database'

    assert (
        await table.distr_data_table.create_table_query('distr_data_cluster')
        == changed_distr_data_create_query
    )
    assert (
        await table.create_table_query('new_cluster_name')
        == changed_distr_create_query
    )


async def test_empty_distr():
    test_config = {}
    with pytest.raises(exceptions.ConfigError):
        await table_lib.DistributedTable.from_config(test_config)


@pytest.mark.parametrize('yaml_name', ['table_distr_nested.yaml'])
async def test_nested_table_distr(clickhouse_table_config, yaml_name):
    table = await table_lib.DistributedTable.from_config(
        clickhouse_table_config,
    )

    assert (
        await table.distr_data_table.create_table_query('distr_data_cluster')
        == distr_data_nested_create_query
    )
    assert (
        await table.create_table_query('test_cluster')
        == distr_nested_create_query
    )
