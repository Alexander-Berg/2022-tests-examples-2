import pytest

from atlas_etl.lib import exceptions
from atlas_etl.lib.clickhouse_table import metadata_utils as meta_lib


@pytest.mark.parametrize('yaml_name', ['table_rmt.yaml'])
async def test_main_table_meta(clickhouse_table_config, yaml_name):
    meta = meta_lib.TableMeta(clickhouse_table_config['table'])
    assert meta.table_name == 'table'
    assert meta.database == 'test'
    assert meta.engine == 'ReplicatedMergeTree'
    assert meta.table_path_clause == 'test.table'


@pytest.mark.parametrize('yaml_name', ['table_rmt.yaml'])
async def test_table_name_missed_table_meta(
        clickhouse_table_config, yaml_name,
):
    config_missed_table_name = clickhouse_table_config['table']
    del config_missed_table_name['table_name']
    with pytest.raises(exceptions.ConfigError):
        meta_lib.TableMeta(config_missed_table_name)


@pytest.mark.parametrize('yaml_name', ['table_rmt.yaml'])
async def test_fake_engine_table_meta(clickhouse_table_config, yaml_name):
    test_metadata_fake_engine = clickhouse_table_config['table']
    test_metadata_fake_engine.update(engine='FakeEngine')
    with pytest.raises(exceptions.ConfigError):
        meta_lib.TableMeta(test_metadata_fake_engine)


@pytest.mark.parametrize('yaml_name', ['table_rmt.yaml'])
async def test_main_mt(clickhouse_table_config, yaml_name):
    meta = meta_lib.MergeTreeTableMeta(clickhouse_table_config['table'])
    assert meta.table_name == 'table'
    assert meta.database == 'test'
    assert meta.engine == 'ReplicatedMergeTree'
    assert meta.engine_spec_clause() == 'ReplicatedMergeTree()'
    assert meta.index_columns == ['date', 'car_class']
    assert meta.partition == 'toYYYYMM(date)'
    assert (
        meta.engine_settings_clause == 'PARTITION BY toYYYYMM(date)\n'
        'ORDER BY (date, car_class)\n'
        'SETTINGS index_granularity = 8192'
    )


@pytest.mark.parametrize('yaml_name', ['table_rmt.yaml'])
async def test_missing_index_columns_mt(clickhouse_table_config, yaml_name):
    config_missed_index_columns = clickhouse_table_config['table']
    del config_missed_index_columns['index_columns']
    with pytest.raises(exceptions.ConfigError):
        meta_lib.MergeTreeTableMeta(config_missed_index_columns)


@pytest.mark.parametrize('yaml_name', ['table_rmt.yaml'])
async def test_missing_partition_mt(clickhouse_table_config, yaml_name):
    test_metadata_wo_partition = clickhouse_table_config['table']
    test_metadata_wo_partition.update(partition='')
    with pytest.raises(exceptions.ConfigError):
        meta_lib.MergeTreeTableMeta(test_metadata_wo_partition)


@pytest.mark.parametrize('yaml_name', ['table_rmt.yaml'])
async def test_main_rmt(clickhouse_table_config, yaml_name):
    meta = meta_lib.ReplicatedMergeTreeTableMeta(
        clickhouse_table_config['table'],
    )
    assert (
        meta.engine_settings_clause == 'PARTITION BY toYYYYMM(date)\n'
        'ORDER BY (date, car_class)\n'
        'SETTINGS index_granularity = 8192'
    )
    assert (
        meta.engine_spec_clause()
        == 'ReplicatedMergeTree(\'/clickhouse/tables/{shard}/test/table\', '
        '\'{replica}\')'
    )


@pytest.mark.parametrize('yaml_name', ['table_rcmt.yaml'])
async def test_main_rcmt(clickhouse_table_config, yaml_name):
    meta = meta_lib.ReplicatedCollapsingMergeTreeTableMeta(
        clickhouse_table_config['table'],
    )
    assert meta.sign_column == 'sign'
    assert (
        meta.engine_spec_clause() == 'ReplicatedCollapsingMergeTree('
        '\'/clickhouse/tables/{shard}/test/table_rcmt\', '
        '\'{replica}\', sign)'
    )
    assert (
        meta.engine_settings_clause == 'PARTITION BY toYYYYMM(date)\n'
        'ORDER BY (date, car_class)\n'
        'SETTINGS index_granularity = 8192'
    )


@pytest.mark.parametrize('yaml_name', ['table_rrmt.yaml'])
async def test_main_rrmt(clickhouse_table_config, yaml_name):
    meta = meta_lib.ReplicatedReplacingMergeTreeTableMeta(
        clickhouse_table_config['table'],
    )
    assert meta.version == ''
    assert (
        meta.engine_spec_clause() == 'ReplicatedReplacingMergeTree('
        '\'/clickhouse/tables/{shard}/test/table_rrmt\', \'{replica}\')'
    )
    assert (
        meta.engine_settings_clause == 'PARTITION BY toYYYYMM(date)\n'
        'ORDER BY (date, car_class)\n'
        'SETTINGS index_granularity = 8192'
    )


@pytest.mark.parametrize('yaml_name', ['table_distr.yaml'])
async def test_main_distr(clickhouse_table_config, yaml_name):
    meta = meta_lib.DistributedTableMeta(
        clickhouse_table_config['distributed_table'],
    )
    assert meta.sharding_key == 'intDiv(toUnixTimestamp(date), 60)'
    assert (
        meta.engine_spec_clause('atlastest')
        == 'Distributed(atlastest, {distr_data_database}, '
        '{distr_data_table_name}, intDiv(toUnixTimestamp(date), 60))'
    )
