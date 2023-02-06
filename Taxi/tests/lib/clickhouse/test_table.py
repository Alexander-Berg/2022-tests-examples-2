import os
import pytest

import utils.common as common

import lib.clickhouse.table as clickhouse_table
from lib.exceptions import ConfigError

rmt_metadata_file_path = os.path.dirname(__file__) + '/test.table.yaml'
rmt_metadata = common.read_yaml(rmt_metadata_file_path)

rcmt_metadata_file_path = os.path.dirname(__file__) + '/test.table_rcmt.yaml'
rcmt_metadata = common.read_yaml(rcmt_metadata_file_path)

rrmt_metadata_file_path = os.path.dirname(__file__) + '/test.table_rrmt.yaml'
rrmt_metadata = common.read_yaml(rrmt_metadata_file_path)

distr_metadata_file_path = os.path.dirname(__file__) + '/test.table_distr.yaml'
distr_metadata = common.read_yaml(distr_metadata_file_path)

distr_nested_metadata_file_path = os.path.dirname(__file__) + '/test.table_distr_nested.yaml'
distr_nested_metadata = common.read_yaml(distr_nested_metadata_file_path)

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


class TestReplicatedMergeTreeTable(object):
    def test_main(self):
        table = clickhouse_table.Table.from_config(rmt_metadata)
        assert table._create_table_query == rmt_create_query
        assert table.meta.engine == 'ReplicatedMergeTree'

        # atlastest should overlap custom_cluster_name
        assert table.meta.cluster_name == 'atlastest'

    def test_empty(self):
        test_config = {}
        with pytest.raises(ConfigError):
            clickhouse_table.Table.from_config(test_config)


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


class TestReplicatedCollapsingMergeTreeTable(object):
    def test_main(self):
        table = clickhouse_table.Table.from_config(rcmt_metadata)
        assert table.meta.engine == 'ReplicatedCollapsingMergeTree'
        assert table.meta.sign_column == 'sign'
        assert table._create_table_query == rcmt_create_query


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


class TestReplicatedReplacingMergeTreeTable(object):
    def test_main(self):
        table = clickhouse_table.Table.from_config(rrmt_metadata)
        assert table.meta.engine == 'ReplicatedReplacingMergeTree'
        assert table._create_table_query == rrmt_create_query


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


class TestDistributedTable(object):
    def test_main(self):
        table = clickhouse_table.DistributedTable.from_config(distr_metadata)

        assert table.meta.engine == 'Distributed'
        assert table.meta.database == 'test'
        assert table.meta.table_name == 'distr_data_table'
        assert table.meta.sharding_key == 'intDiv(toUnixTimestamp(date), 60)'
        assert table.meta.cluster_name == 'test_cluster'
        assert table.distr_data_table.meta.engine == 'ReplicatedCollapsingMergeTree'
        assert table.distr_data_table.meta.database == 'distr_data_db'
        assert table.distr_data_table.meta.table_name == 'distr_data_table'
        assert table.distr_data_table.meta.cluster_name == 'distr_data_cluster'

        assert table._create_table_query == distr_create_query
        assert table.distr_data_table._create_table_query == distr_data_create_query

    def test_changed_meta_fields(self):
        table = clickhouse_table.DistributedTable.from_config(distr_metadata)
        table.meta.table_name = 'new_table_name'
        table.distr_data_table.meta.table_name = 'other_table_name'
        table.meta.cluster_name = 'new_cluster_name'
        table.distr_data_table.meta.database = 'new_data_database'

        assert table.distr_data_table._create_table_query == changed_distr_data_create_query
        assert table._create_table_query == changed_distr_create_query

    def test_empty(self):
        test_config = {}
        with pytest.raises(ConfigError):
            clickhouse_table.DistributedTable.from_config(test_config)

    def test_nested_table(self):
        table = clickhouse_table.DistributedTable.from_config(distr_nested_metadata)

        assert table.distr_data_table._create_table_query == distr_data_nested_create_query
        assert table._create_table_query == distr_nested_create_query
