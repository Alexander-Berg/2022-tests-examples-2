# pylint: disable=invalid-name, protected-access
import os.path

import pytest

from replication.common.pytest import replication_rules
from replication.common.pytest import sources_util
from replication.common.queue_mongo import model
from replication.common.queue_mongo import sharding as queue_mongo_sharding
from replication.foundation import consts
from replication.foundation import loaders

source_definitions = sources_util.source_definitions

QUEUE_DATA_1 = model.QueueData(
    collection_base_name='queue_mongo_one_shard',
    base_source_type='mongo',
    base_replicate_by='updated',
    need_sequence_key=False,
    extra_indexes=None,
    sharding=[
        queue_mongo_sharding.QueueSharding(
            shards_num=1, db_cluster='replication_queue_mdb_0',
        ),
    ],
)
QUEUE_DATA_2 = model.QueueData(
    collection_base_name='queue_mongo_shards',
    base_source_type='mongo',
    base_replicate_by='updated',
    need_sequence_key=False,
    extra_indexes=None,
    sharding=[
        queue_mongo_sharding.QueueSharding(
            shards_num=2, db_cluster='replication_queue_mdb_0',
        ),
    ],
)


SOURCE_TEST_CASES = [
    (
        consts.SOURCE_TYPE_MONGO,
        'mongo_simple',
        {'collection_name': 'mongo_simple', 'replicate_by': 'updated'},
        ['mongo_simple'],
        {'collection_name': ['mongo_simple'], 'replicate_by': ['updated']},
    ),
    (
        consts.SOURCE_TYPE_QUEUE_MONGO,
        'queue_mongo_one_shard',
        {'queue_data': QUEUE_DATA_1},
        [  # queue_data.staging_collection_names -> source names
            'staging_queue_mongo_one_shard',
        ],
        {
            'collection_name': ['staging_queue_mongo_one_shard'],
            'queue_data': [QUEUE_DATA_1],
        },
    ),
    (
        consts.SOURCE_TYPE_QUEUE_MONGO,
        'queue_mongo_shards',
        {'queue_data': QUEUE_DATA_2},
        [  # queue_data.staging_collection_names -> source names
            'staging_queue_mongo_shards_0_2',
            'staging_queue_mongo_shards_1_2',
        ],
        {
            'collection_name': [
                'staging_queue_mongo_shards_0_2',
                'staging_queue_mongo_shards_1_2',
            ],
            'queue_data': [QUEUE_DATA_2, QUEUE_DATA_2],
        },
    ),
]


@pytest.mark.parametrize(
    'source_type,source_name,raw_meta,expected_names,expected_meta_attrs',
    SOURCE_TEST_CASES,
)
@pytest.mark.nofilldb
async def test_sources_construct(
        source_meta_checker,
        source_type,
        source_name,
        raw_meta,
        expected_names,
        expected_meta_attrs,
):
    source_meta_checker(
        source_type,
        source_name,
        raw_meta,
        expected_names,
        expected_meta_attrs,
    )


@pytest.mark.nofilldb
def test_api_source_core(replication_ctx):
    builder = loaders.SourceCoreBuilder(
        replication_ctx.pluggy_deps.source_definitions,
        '',
        'api_simple',
        consts.ReplicationType.QUEUE,
        {'type': 'api'},
    )
    source_core = builder.load_source_core()
    assert source_core.name == 'api_simple'
    assert source_core.type == 'api'
    assert source_core.raw_meta == {}
    assert source_core.base_source_meta is not None


_PATCHED_PRIMARY_KEYS = ['id', 'doc_type']


@pytest.mark.parametrize(
    'source_type',
    sorted(
        set(source_definitions.replication_types)
        - set(consts.ALL_QUEUE_SOURCE_TYPES),
    ),
)
@pytest.mark.nofilldb
def test_to_queue_mappers(mapper_check, mapper_to_queue, source_type):
    primary_key = None
    if source_definitions.data[source_type].primary_keys is None:
        primary_key = _PATCHED_PRIMARY_KEYS
    mapper = mapper_to_queue(
        source_type,
        primary_key=primary_key,
        extra_indexes=['foo.bar', 'extra_index'],
    )
    test_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        source_type,
        'static',
        'map_to_queue.json',
    )
    mapper_check(test_path, mapper, check_fullness=False)


_PARAMETRIZE_SOURCES_ENVS = pytest.mark.parametrize(
    '_test_env_id,source_type',
    [
        ('source#' + source_type, source_type)
        for source_type in source_definitions.replication_types
        if source_type
        not in (
            consts.SOURCE_TYPE_QUEUE_MONGO,
            consts.SOURCE_TYPE_MONGO,
            consts.SOURCE_TYPE_API,
        )
    ],
    indirect=['_test_env_id'],
)


@_PARAMETRIZE_SOURCES_ENVS
@pytest.mark.nofilldb
async def test_has_test_rule(
        replication_ctx, source_type, replication_yaml_path, mock_secrets_dir,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        source_types=[source_type],
    )
    assert rules, (
        f'Test rules for {source_type!r} source type '
        f'not found in: {replication_yaml_path}'
    )


@pytest.mark.config(
    REPLICATION_SERVICE_CTL={
        'replication': {
            'time_overlaps': {
                'past': {'queue_mongo': 120},
                'future': {'queue_mongo': 90},
            },
        },
    },
    REPLICATION_CRON_MAIN_SETUP={
        'use_chains': ['test/test_struct_sharded', 'dummy'],
        'use_new_chains_logic': True,
    },
)
@pytest.mark.parametrize(
    'source_type, filters, test_file',
    [
        (
            'mongo',
            {'replication_types': [consts.ReplicationType.QUEUE]},
            'full_cycle/mongo.json',
        ),
        pytest.param(
            'mongo',
            {'replication_types': [consts.ReplicationType.QUEUE_SNAPSHOT]},
            'full_cycle/mongo.json',
            marks=pytest.mark.now('2020-03-17T09:20:00.000Z'),  # actual period
        ),
    ],
)
async def test_replicate_full_cycle(
        check_queue_data,
        no_ensure_queue_indexes,
        replication_runner,
        replication_ctx,
        source_type,
        filters,
        test_file,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        source_types=[source_type], rule_scope='all_sources', **filters,
    )
    rule_name = rules[0].name

    replication_runner.setup_data(
        {source_type: f'full_cycle/{source_type}.json'},
    )
    targets_data = await replication_runner.run(rule_name)

    await check_queue_data(
        targets_data.queue_data,
        source_type,
        rule_scope='all_sources',
        **filters,
    )


@_PARAMETRIZE_SOURCES_ENVS
@pytest.mark.nofilldb
def test_schemas(monkeypatch, replication_ctx, _test_env_id, source_type):
    replication_rules.run_test_schemas(
        monkeypatch, replication_ctx, _test_env_id,
    )


@pytest.fixture
def test_env_id_setter(test_env_testsuite):
    return test_env_testsuite
