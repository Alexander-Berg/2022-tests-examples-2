# pylint: disable=invalid-name, protected-access
import typing
import uuid

import attr
import pytest

from replication_core.rules import classes as core_classes
from taxi import db

from replication import settings
from replication.common import sharded_mongo
from replication.common.queue_mongo import db_clusters as queue_mongo_clusters
from replication.common.queue_mongo import sharding
from replication.foundation import constructors
from replication.foundation import consts
from replication.foundation import loaders
from replication.foundation.mappers import constructor as mapper_constructor
from replication.foundation.responsible import flaky_config as responsible_mod
from replication.foundation.targets import constructor as target_constructor
from replication.plugin_register import flaky_config
from replication.sources.postgres import core as postgres
from replication.targets.logbroker import logbroker_targets
from replication.targets.yt import all_validators
from replication.targets.yt import prefixes
from replication.targets.yt import yt_targets as yt_target_classes

DEFAULT_QUEUE_CONNECTION = queue_mongo_clusters.get_connection_by_cluster(
    settings.DEFAULT_QUEUE_MONGO_DB_CLUSTER,
)
DEFAULT_QUEUE_DATABASE = queue_mongo_clusters.get_queue_database_by_cluster(
    settings.DEFAULT_QUEUE_MONGO_DB_CLUSTER,
)


@pytest.mark.parametrize(
    'rule_name,rule_doc,expected_connections',
    [
        (
            'one_shard',
            {
                'replication_type': consts.ReplicationType.QUEUE.value,
                'source': {
                    'type': consts.SOURCE_TYPE_MONGO,
                    'collection_name': 'orders',
                    'replicate_by': 'updated',
                },
            },
            [
                sharding.CollectionSettings(
                    'staging_one_shard',
                    db.CollectionData(
                        DEFAULT_QUEUE_CONNECTION,
                        DEFAULT_QUEUE_DATABASE,
                        'one_shard',
                    ),
                    queue_db_cluster=DEFAULT_QUEUE_CONNECTION,
                    shard_num=0,
                    source_unit_name=None,
                ),
            ],
        ),
        (
            'multi_shard',
            {
                'replication_type': consts.ReplicationType.QUEUE.value,
                'queue_data': {'shards_num': 4},
                'source': {
                    'type': consts.SOURCE_TYPE_MONGO,
                    'collection_name': 'orders',
                    'replicate_by': 'updated',
                },
            },
            [
                sharding.CollectionSettings(
                    'staging_multi_shard_0_4',
                    db.CollectionData(
                        DEFAULT_QUEUE_CONNECTION,
                        DEFAULT_QUEUE_DATABASE,
                        'multi_shard_0_4',
                    ),
                    queue_db_cluster=DEFAULT_QUEUE_CONNECTION,
                    shard_num=0,
                    source_unit_name='0_4',
                ),
                sharding.CollectionSettings(
                    'staging_multi_shard_1_4',
                    db.CollectionData(
                        DEFAULT_QUEUE_CONNECTION,
                        DEFAULT_QUEUE_DATABASE,
                        'multi_shard_1_4',
                    ),
                    queue_db_cluster=DEFAULT_QUEUE_CONNECTION,
                    shard_num=1,
                    source_unit_name='1_4',
                ),
                sharding.CollectionSettings(
                    'staging_multi_shard_2_4',
                    db.CollectionData(
                        DEFAULT_QUEUE_CONNECTION,
                        DEFAULT_QUEUE_DATABASE,
                        'multi_shard_2_4',
                    ),
                    queue_db_cluster=DEFAULT_QUEUE_CONNECTION,
                    shard_num=2,
                    source_unit_name='2_4',
                ),
                sharding.CollectionSettings(
                    'staging_multi_shard_3_4',
                    db.CollectionData(
                        DEFAULT_QUEUE_CONNECTION,
                        DEFAULT_QUEUE_DATABASE,
                        'multi_shard_3_4',
                    ),
                    queue_db_cluster=DEFAULT_QUEUE_CONNECTION,
                    shard_num=3,
                    source_unit_name='3_4',
                ),
            ],
        ),
        (
            'multi_pg_multi_shard',
            {
                'replication_type': consts.ReplicationType.QUEUE.value,
                'queue_data': {'shards_num': 4},
                'source': {
                    'type': postgres.SOURCE_TYPE_POSTGRES,
                    'replicate_by': 'updated',
                    'table': 'table',
                    'primary_key': ['id'],
                    'connection': {
                        'path': (
                            '_testsuite_postgresql.example'
                            '_pg.*.hosts.$random'
                        ),
                    },
                    'timezone': 'UTC',
                },
            },
            [
                sharding.CollectionSettings(
                    'staging_multi_pg_multi_shard_0_4',
                    db.CollectionData(
                        DEFAULT_QUEUE_CONNECTION,
                        DEFAULT_QUEUE_DATABASE,
                        'multi_pg_multi_shard_0_4',
                    ),
                    queue_db_cluster=DEFAULT_QUEUE_CONNECTION,
                    shard_num=0,
                    source_unit_name='0_4',
                ),
                sharding.CollectionSettings(
                    'staging_multi_pg_multi_shard_1_4',
                    db.CollectionData(
                        DEFAULT_QUEUE_CONNECTION,
                        DEFAULT_QUEUE_DATABASE,
                        'multi_pg_multi_shard_1_4',
                    ),
                    queue_db_cluster=DEFAULT_QUEUE_CONNECTION,
                    shard_num=1,
                    source_unit_name='1_4',
                ),
                sharding.CollectionSettings(
                    'staging_multi_pg_multi_shard_2_4',
                    db.CollectionData(
                        DEFAULT_QUEUE_CONNECTION,
                        DEFAULT_QUEUE_DATABASE,
                        'multi_pg_multi_shard_2_4',
                    ),
                    queue_db_cluster=DEFAULT_QUEUE_CONNECTION,
                    shard_num=2,
                    source_unit_name='2_4',
                ),
                sharding.CollectionSettings(
                    'staging_multi_pg_multi_shard_3_4',
                    db.CollectionData(
                        DEFAULT_QUEUE_CONNECTION,
                        DEFAULT_QUEUE_DATABASE,
                        'multi_pg_multi_shard_3_4',
                    ),
                    queue_db_cluster=DEFAULT_QUEUE_CONNECTION,
                    shard_num=3,
                    source_unit_name='3_4',
                ),
            ],
        ),
        (
            'multi_pg_multi_cluster',
            {
                'replication_type': consts.ReplicationType.QUEUE.value,
                'queue_data': {
                    'sharding': [
                        {
                            'db_cluster': 'replication_queue_mdb_0',
                            'shards_num': 2,
                        },
                        {
                            'db_cluster': 'replication_queue_mdb_1',
                            'shards_num': 3,
                        },
                    ],
                },
                'source': {
                    'type': postgres.SOURCE_TYPE_POSTGRES,
                    'replicate_by': 'updated',
                    'tables': ['table'],
                    'primary_key': ['id'],
                    'connection': {
                        'path': (
                            '_testsuite_postgresql.example'
                            '_pg.*.hosts.$random'
                        ),
                    },
                    'timezone': 'UTC',
                },
            },
            [
                sharding.CollectionSettings(
                    'staging_multi_pg_multi_cluster_0_5',
                    db.CollectionData(
                        queue_mongo_clusters.get_connection_by_cluster(
                            'replication_queue_mdb_0',
                        ),
                        queue_mongo_clusters.get_queue_database_by_cluster(
                            'replication_queue_mdb_0',
                        ),
                        'multi_pg_multi_cluster_0_5',
                    ),
                    queue_db_cluster='replication_queue_mdb_0',
                    shard_num=0,
                    source_unit_name='0_5',
                ),
                sharding.CollectionSettings(
                    'staging_multi_pg_multi_cluster_1_5',
                    db.CollectionData(
                        queue_mongo_clusters.get_connection_by_cluster(
                            'replication_queue_mdb_0',
                        ),
                        queue_mongo_clusters.get_queue_database_by_cluster(
                            'replication_queue_mdb_0',
                        ),
                        'multi_pg_multi_cluster_1_5',
                    ),
                    queue_db_cluster='replication_queue_mdb_0',
                    shard_num=1,
                    source_unit_name='1_5',
                ),
                sharding.CollectionSettings(
                    'staging_multi_pg_multi_cluster_2_5',
                    db.CollectionData(
                        queue_mongo_clusters.get_connection_by_cluster(
                            'replication_queue_mdb_1',
                        ),
                        queue_mongo_clusters.get_queue_database_by_cluster(
                            'replication_queue_mdb_1',
                        ),
                        'multi_pg_multi_cluster_2_5',
                    ),
                    queue_db_cluster='replication_queue_mdb_1',
                    shard_num=2,
                    source_unit_name='2_5',
                ),
                sharding.CollectionSettings(
                    'staging_multi_pg_multi_cluster_3_5',
                    db.CollectionData(
                        queue_mongo_clusters.get_connection_by_cluster(
                            'replication_queue_mdb_1',
                        ),
                        queue_mongo_clusters.get_queue_database_by_cluster(
                            'replication_queue_mdb_1',
                        ),
                        'multi_pg_multi_cluster_3_5',
                    ),
                    queue_db_cluster='replication_queue_mdb_1',
                    shard_num=3,
                    source_unit_name='3_5',
                ),
                sharding.CollectionSettings(
                    'staging_multi_pg_multi_cluster_4_5',
                    db.CollectionData(
                        queue_mongo_clusters.get_connection_by_cluster(
                            'replication_queue_mdb_1',
                        ),
                        queue_mongo_clusters.get_queue_database_by_cluster(
                            'replication_queue_mdb_1',
                        ),
                        'multi_pg_multi_cluster_4_5',
                    ),
                    queue_db_cluster='replication_queue_mdb_1',
                    shard_num=4,
                    source_unit_name='4_5',
                ),
            ],
        ),
    ],
)
@pytest.mark.nofilldb()
def test_load_queue_data(rule_name, rule_doc, expected_connections):
    queue_data = loaders._load_queue_data(
        rule_name,
        rule_doc,
        rule_doc['source']['type'],
        base_replicate_by=rule_doc['source'].get('replicate_by'),
        need_sequence_key=False,
    )
    assert queue_data.staging_collection_settings == expected_connections
    assert queue_data.staging_collection_names == [
        collection_settings[0] for collection_settings in expected_connections
    ]


class ExpectedRuleUnit(typing.NamedTuple):
    name: str
    type: str
    exp_meta_attrs: dict


class ExpectedRule(typing.NamedTuple):
    name: str
    source: ExpectedRuleUnit
    targets: typing.List[ExpectedRuleUnit]


@pytest.mark.parametrize(
    'rule_doc, expected_rules',
    [
        (
            {
                'name': 'one_shard',
                'replication_type': consts.ReplicationType.QUEUE.value,
                'source': {
                    'type': consts.SOURCE_TYPE_MONGO,
                    'collection_name': 'one_shard_coll_name',
                    'replicate_by': 'updated',
                },
            },
            [
                ExpectedRule(
                    'one_shard',
                    source=ExpectedRuleUnit(
                        'one_shard',
                        consts.SOURCE_TYPE_MONGO,
                        {
                            'collection_name': 'one_shard_coll_name',
                            'shard_settings': None,
                        },
                    ),
                    targets=[
                        ExpectedRuleUnit(
                            'staging_one_shard',
                            consts.TARGET_TYPE_QUEUE_MONGO,
                            {'collections_names': ['staging_one_shard']},
                        ),
                    ],
                ),
            ],
        ),
        (
            {
                'name': 'from_sharded_mongo',
                'replication_type': consts.ReplicationType.QUEUE.value,
                'source': {
                    'type': consts.SOURCE_TYPE_MONGO,
                    'collection_name': 'sharded_mongo',
                    'connection': {
                        'path': '_testsuite_mongo.users_connections',
                    },
                    'replicate_by': 'updated',
                },
            },
            [
                ExpectedRule(
                    'from_sharded_mongo',
                    source=ExpectedRuleUnit(
                        'from_sharded_mongo_shard0',
                        consts.SOURCE_TYPE_MONGO,
                        {
                            'collection_name': 'sharded_mongo',
                            'shard_settings': (
                                sharded_mongo.ShardSettings(
                                    'sharded_mongo_shard0',
                                    'shard0',
                                    0,
                                    connection_string='conn_string_0',
                                )
                            ),
                        },
                    ),
                    targets=[
                        ExpectedRuleUnit(
                            'staging_from_sharded_mongo',
                            consts.TARGET_TYPE_QUEUE_MONGO,
                            {
                                'collections_names': [
                                    'staging_from_sharded_mongo',
                                ],
                            },
                        ),
                    ],
                ),
                ExpectedRule(
                    'from_sharded_mongo',
                    source=ExpectedRuleUnit(
                        'from_sharded_mongo_shard1',
                        consts.SOURCE_TYPE_MONGO,
                        {
                            'collection_name': 'sharded_mongo',
                            'shard_settings': (
                                sharded_mongo.ShardSettings(
                                    'sharded_mongo_shard1',
                                    'shard1',
                                    1,
                                    connection_string='conn_string_1',
                                )
                            ),
                        },
                    ),
                    targets=[
                        ExpectedRuleUnit(
                            'staging_from_sharded_mongo',
                            consts.TARGET_TYPE_QUEUE_MONGO,
                            {
                                'collections_names': [
                                    'staging_from_sharded_mongo',
                                ],
                            },
                        ),
                    ],
                ),
            ],
        ),
        (
            {
                'name': 'multi_shard',
                'replication_type': consts.ReplicationType.QUEUE.value,
                'queue_data': {'shards_num': 4},
                'source': {
                    'type': consts.SOURCE_TYPE_MONGO,
                    'collection_name': 'any_coll_name',
                    'replicate_by': 'updated',
                },
            },
            [
                ExpectedRule(
                    'multi_shard',
                    source=ExpectedRuleUnit(
                        'multi_shard',
                        consts.SOURCE_TYPE_MONGO,
                        {'collection_name': 'any_coll_name'},
                    ),
                    targets=[
                        ExpectedRuleUnit(
                            'staging_multi_shard',
                            consts.TARGET_TYPE_QUEUE_MONGO,
                            {
                                'collections_names': [
                                    'staging_multi_shard_0_4',
                                    'staging_multi_shard_1_4',
                                    'staging_multi_shard_2_4',
                                    'staging_multi_shard_3_4',
                                ],
                            },
                        ),
                    ],
                ),
            ],
        ),
        (
            {
                'name': 'multi_pg_multi_shard',
                'replication_type': consts.ReplicationType.QUEUE.value,
                'queue_data': {'shards_num': 4},
                'source': {
                    'type': postgres.SOURCE_TYPE_POSTGRES,
                    'replicate_by': 'updated_ts',
                    'table': 'table',
                    'primary_key': ['id'],
                    'connection': {'secret': 'example_pg'},
                    'timezone': 'UTC',
                },
            },
            [
                ExpectedRule(
                    'multi_pg_multi_shard',
                    source=ExpectedRuleUnit(
                        'multi_pg_multi_shard_shard0',
                        postgres.SOURCE_TYPE_POSTGRES,
                        {
                            'replicate_by': 'updated_ts',
                            'table': 'table',
                            'primary_key': ['id'],
                            'shard_num': 0,
                            'connection_kwargs': {
                                'host',
                                'database',
                                'port',
                                'password',
                                'user',
                                'ssl',
                            },
                            'timezone': 'UTC',
                        },
                    ),
                    targets=[
                        ExpectedRuleUnit(
                            'staging_multi_pg_multi_shard',
                            consts.TARGET_TYPE_QUEUE_MONGO,
                            {
                                'collections_names': [
                                    'staging_multi_pg_multi_shard_0_4',
                                    'staging_multi_pg_multi_shard_1_4',
                                    'staging_multi_pg_multi_shard_2_4',
                                    'staging_multi_pg_multi_shard_3_4',
                                ],
                            },
                        ),
                    ],
                ),
                ExpectedRule(
                    'multi_pg_multi_shard',
                    source=ExpectedRuleUnit(
                        'multi_pg_multi_shard_shard1',
                        postgres.SOURCE_TYPE_POSTGRES,
                        {
                            'replicate_by': 'updated_ts',
                            'table': 'table',
                            'primary_key': ['id'],
                            'shard_num': 1,
                            'connection_kwargs': {
                                'host',
                                'database',
                                'port',
                                'password',
                                'user',
                                'ssl',
                            },
                            'timezone': 'UTC',
                        },
                    ),
                    targets=[
                        ExpectedRuleUnit(
                            'staging_multi_pg_multi_shard',
                            consts.TARGET_TYPE_QUEUE_MONGO,
                            {
                                'collections_names': [
                                    'staging_multi_pg_multi_shard_0_4',
                                    'staging_multi_pg_multi_shard_1_4',
                                    'staging_multi_pg_multi_shard_2_4',
                                    'staging_multi_pg_multi_shard_3_4',
                                ],
                            },
                        ),
                    ],
                ),
            ],
        ),
    ],
)
@pytest.mark.nofilldb()
def test_load_master_rule_from_source_to_queue(
        monkeypatch, replication_ctx, rule_doc, expected_rules,
):
    monkeypatch.setattr(  # test only [source -> queue_mongo] case
        loaders, '_load_target_cores', lambda *args, **kwargs: [],
    )
    rule_obj = core_classes.RuleObj(
        rule_doc,
        rule_doc['name'],
        {},
        source=rule_doc['source'],
        flaky_config=flaky_config.FlakyDict({'responsible': ['testsuite']}),
    )
    master_rule = loaders._load_master_rule(
        replication_ctx.pluggy_deps.source_definitions,
        '',
        rule_obj,
        settings.TESTSUITE_MAP_PLUGINS,
        [],
    )
    rules = constructors.construct_replication_groups(
        replication_ctx.rule_keeper, master_rule,
    )

    assert rules
    assert len(rules) == len(expected_rules), 'Actual: %s' % [
        rule.name for rule in rules
    ]
    for rule_group, expected_rule in zip(rules, expected_rules):
        assert rule_group.name == expected_rule.name
        assert rule_group.source.name == expected_rule.source.name
        assert rule_group.source.type == expected_rule.source.type
        for key, exp_value in expected_rule.source.exp_meta_attrs.items():
            if key == 'replicate_by':
                value = rule_group.source.base_meta.replicate_by
            else:
                value = getattr(rule_group.source.meta, key)
            if key == 'connection_kwargs':
                value = set(value.keys())
            assert value == exp_value
        assert len(rule_group.targets) == len(expected_rule.targets)
        for target, expected_target in zip(
                rule_group.targets, expected_rule.targets,
        ):
            assert target.type == expected_target.type
            assert target.name == expected_target.name
            for key, exp_value in expected_target.exp_meta_attrs.items():
                assert getattr(target.meta, key) == exp_value


SCHEMA = [
    {
        'description': 'Значение хеш-функции от идентификатора документа',
        'name': 'hash',
        'expression': 'farm_hash(id)',
        'sort_order': 'ascending',
        'type': 'uint64',
    },
    {
        'description': 'Идентификатор документа',
        'name': 'id',
        'sort_order': 'ascending',
        'type': 'string',
    },
    {'description': 'int value 1', 'name': 'value_1', 'type': 'int64'},
    {'description': 'int value 2', 'name': 'value_2', 'type': 'int64'},
]


_YT_ENTITY = prefixes.load_yt_entity({'yt_prefixes': {}})


@pytest.mark.parametrize(
    'rule_doc,list_expected_meta',
    [
        (
            {
                'name': 'test_rule',
                'destinations': [
                    {
                        'yt_tg': {
                            'type': consts.TARGET_TYPE_YT,
                            'mapper': 'mapper',
                            'target': {
                                'path': 'test/test_struct',
                                'cluster_groups': ['map_reduce'],
                            },
                        },
                    },
                ],
            },
            [
                yt_target_classes.YTTargetMeta(
                    rule_name='test_rule',
                    rule_scope='',
                    client_name='arni',
                    path='test/test_struct',
                    table=yt_target_classes.TableMeta(
                        'test struct', optimize_for='lookup', schema=SCHEMA,
                    ),
                    partitioning=None,
                    rebuildable=True,
                    yt_errors_validators=[
                        all_validators.RowsValidatorsEnum.schema.value,
                    ],
                    yt_entity=_YT_ENTITY,
                    responsible=responsible_mod.FlakyConfigResponsible(
                        ['testsuite'],
                    ),
                    dependencies=None,  # type: ignore
                ),
                yt_target_classes.YTTargetMeta(
                    rule_name='test_rule',
                    rule_scope='',
                    client_name='hahn',
                    path='test/test_struct',
                    table=yt_target_classes.TableMeta(
                        'test struct', optimize_for='lookup', schema=SCHEMA,
                    ),
                    partitioning=None,
                    rebuildable=None,
                    yt_errors_validators=[
                        all_validators.RowsValidatorsEnum.schema.value,
                    ],
                    yt_entity=_YT_ENTITY,
                    responsible=responsible_mod.FlakyConfigResponsible(
                        ['testsuite'],
                    ),
                    dependencies=None,  # type: ignore
                ),
            ],
        ),
        (
            {
                'name': 'test_rule2',
                'destinations': [
                    {
                        'logbroker_tg': {
                            'type': consts.TARGET_TYPE_LOGBROKER,
                            'target': {
                                'installation': 'logbroker',
                                'topic': 'test/test_topic',
                                'partitions': 2,
                            },
                        },
                    },
                ],
            },
            [
                logbroker_targets.LogbrokerTargetMeta(
                    rule_name='test_rule2',
                    rule_scope='',
                    topic='/taxi/replication/unittests/topics/test/test_topic',
                    source_id=b'uuid',
                    installation='logbroker',
                    partitions=2,
                    responsible=responsible_mod.FlakyConfigResponsible(
                        ['testsuite'],
                    ),
                    dependencies=None,  # type: ignore
                ),
            ],
        ),
    ],
)
@pytest.mark.nofilldb()
def test_targets_construct(
        monkeypatch, replication_ctx, rule_doc, list_expected_meta,
):
    monkeypatch.setattr(
        mapper_constructor, 'construct', lambda *args, **kwargs: None,
    )

    class FakeUuid:
        hex = 'uuid'

    monkeypatch.setattr(uuid, 'uuid4', FakeUuid)

    mapper_doc = {'mapper': True}
    target_doc = {
        'attributes': {'schema': SCHEMA, 'optimize_for': 'lookup'},
        'description': 'test struct',
    }
    target_objects = {
        name: core_classes.TargetObj(
            obj,
            target_group_index,
            name,
            obj['type'],
            target_doc=target_doc,
            target_path='',
            mapper_doc=mapper_doc,
            mapper_path='',
            flaky_config=flaky_config.FlakyDict(
                {'responsible': ['testsuite']},
            ),
        )
        for target_group_index, destinations in enumerate(
            rule_doc['destinations'],
        )
        for name, obj in destinations.items()
    }
    rule_obj = core_classes.RuleObj(rule_doc, rule_doc['name'], target_objects)
    target_cores_list = loaders._load_target_cores(
        rule_doc['name'], rule_obj, '',
    )
    assert len(target_cores_list) == 1
    target_cores = target_cores_list[0]
    assert len(target_cores) == 1

    class DummySourceCore:
        raw_meta = None

        class base_source_meta:
            iteration_type = None
            replication_type = consts.ReplicationType.QUEUE

    targets = target_constructor.construct(
        replication_ctx.rule_keeper,
        source=None,
        source_core=DummySourceCore,
        target_core=target_cores[0],
    )
    assert len(targets) == len(list_expected_meta)
    for target, expected_meta in zip(targets, list_expected_meta):
        target_meta_dict = attr.asdict(target.meta)
        expeceted_dict = attr.asdict(expected_meta)
        for meta in [target_meta_dict, expeceted_dict]:
            meta.pop('dependencies', None)
        assert target_meta_dict == expeceted_dict
        assert target.meta == expected_meta
