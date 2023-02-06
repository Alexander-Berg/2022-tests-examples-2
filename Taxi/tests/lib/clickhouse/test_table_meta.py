# -*- coding: utf-8 -*-
import os
import pytest
import copy

import lib.exceptions as exceptions
import utils.common as common
import lib.clickhouse.metadata_utils as metadata_utils

rmt_metadata_file_path = os.path.dirname(__file__) + '/test.table.yaml'
rmt_metadata = common.read_yaml(rmt_metadata_file_path)

rcmt_metadata_file_path = os.path.dirname(__file__) + '/test.table_rcmt.yaml'
rcmt_metadata = common.read_yaml(rcmt_metadata_file_path)

rrmt_metadata_file_path = os.path.dirname(__file__) + '/test.table_rrmt.yaml'
rrmt_metadata = common.read_yaml(rrmt_metadata_file_path)

distr_metadata_file_path = os.path.dirname(__file__) + '/test.table_distr.yaml'
distr_metadata = common.read_yaml(distr_metadata_file_path)


class TestTableMeta(object):
    def test_main(self):
        meta = metadata_utils.TableMeta(rmt_metadata['table'])
        assert meta is not None
        assert meta.table_name == 'table'
        assert meta.database == 'test'
        assert meta.cluster_name == 'atlastest'
        assert meta.engine == 'ReplicatedMergeTree'
        assert meta.table_path_clause == 'test.table'

    def test_table_name_missed(self):
        config_missed_table_name = copy.deepcopy(rmt_metadata['table'])
        del config_missed_table_name['table_name']
        with pytest.raises(exceptions.ConfigError):
            metadata_utils.TableMeta(config_missed_table_name)

    def test_fake_engine(self):
        test_metadata_fake_engine = copy.deepcopy(rmt_metadata['table'])
        test_metadata_fake_engine.update(engine='FakeEngine')
        with pytest.raises(exceptions.ConfigError):
            metadata_utils.TableMeta(test_metadata_fake_engine)


class TestMergeTreeTableMeta(object):
    def test_main(self):
        meta = metadata_utils.MergeTreeTableMeta(rmt_metadata['table'])
        assert meta is not None
        assert meta.table_name == 'table'
        assert meta.database == 'test'
        assert meta.cluster_name == 'atlastest'
        assert meta.engine == 'ReplicatedMergeTree'
        assert meta.engine_spec_clause == 'ReplicatedMergeTree()'
        assert meta.index_columns == ['date', 'car_class']
        assert meta.partition == 'toYYYYMM(date)'
        assert meta.engine_settings_clause == \
            "PARTITION BY toYYYYMM(date)\nORDER BY (date, car_class)\nSETTINGS index_granularity = 8192"

    def test_missing_index_columns(self):
        config_missed_index_columns = copy.deepcopy(rmt_metadata['table'])
        del config_missed_index_columns['index_columns']
        with pytest.raises(exceptions.ConfigError):
            metadata_utils.MergeTreeTableMeta(config_missed_index_columns)

    def test_missing_partition(self):
        test_metadata_wo_partition = copy.deepcopy(rmt_metadata['table'])
        test_metadata_wo_partition.update(partition='')
        with pytest.raises(exceptions.ConfigError):
            metadata_utils.MergeTreeTableMeta(test_metadata_wo_partition)


class TestReplicatedMergeTreeTable(object):
    def test_main(self):
        meta = metadata_utils.ReplicatedMergeTreeTableMeta(rmt_metadata['table'])
        assert meta.engine_settings_clause == "PARTITION BY toYYYYMM(date)\n" \
                                              "ORDER BY (date, car_class)\n" \
                                              "SETTINGS index_granularity = 8192"
        assert meta.engine_spec_clause == "ReplicatedMergeTree('/clickhouse/tables/{shard}/test/table', '{replica}')"


class TestReplicatedCollapsingMergeTreeTableMeta(object):
    def test_main(self):
        meta = metadata_utils.ReplicatedCollapsingMergeTreeTableMeta(rcmt_metadata['table'])
        assert meta.sign_column == 'sign'
        assert meta.engine_spec_clause == \
            "ReplicatedCollapsingMergeTree('/clickhouse/tables/{shard}/test/table_rcmt', '{replica}', sign)"
        assert meta.engine_settings_clause == \
            "PARTITION BY toYYYYMM(date)\nORDER BY (date, car_class)\nSETTINGS index_granularity = 8192"


class TestReplicatedReplacingMergeTreeTableMeta(object):
    def test_main(self):
        meta = metadata_utils.ReplicatedReplacingMergeTreeTableMeta(rrmt_metadata['table'])
        assert meta.version == ''
        assert meta.engine_spec_clause == \
            "ReplicatedReplacingMergeTree('/clickhouse/tables/{shard}/test/table_rrmt', '{replica}')"
        assert meta.engine_settings_clause == \
            "PARTITION BY toYYYYMM(date)\nORDER BY (date, car_class)\nSETTINGS index_granularity = 8192"


class TestDistributedTableMeta(object):
    def test_main(self):
        meta = metadata_utils.DistributedTableMeta(distr_metadata['distributed_table'])
        meta.cluster_name = 'atlastest'
        assert meta.sharding_key == 'intDiv(toUnixTimestamp(date), 60)'
        assert meta.engine_spec_clause == \
            "Distributed(atlastest, {distr_data_database}, {distr_data_table_name}, intDiv(toUnixTimestamp(date), 60))"
