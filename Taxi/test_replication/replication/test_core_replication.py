# pylint: disable=protected-access
# pylint: disable=redefined-outer-name
import datetime
import operator

import pytest
import yt.wrapper

from taxi import yt_wrapper

from replication.common import queue_mongo
from replication.common.queue_mongo import exceptions
from replication.foundation import consts
from replication.replication.core import replication
from replication.utils import data_helpers

TEST_RULE_NAME = 'test_rule'

_SCHEMA_VIOLATION_CODE = 307


# base dummy test
async def test_replicate_to_targets(run_replication):
    await run_replication(TEST_RULE_NAME)


async def test_finalize(replication_ctx, replication_tasks_getter):
    tasks = await replication_tasks_getter(
        consts.SOURCE_TYPE_QUEUE_MONGO, TEST_RULE_NAME,
    )
    assert len(tasks) == 1
    args_kit = replication._get_args_kit(replication_ctx, None)
    managers_store = await replication._get_managers_store(args_kit, tasks)

    assert replication._finalize(managers_store) is None

    for manager in managers_store.managers.values():
        manager.active_units.clear()
        manager.fail_reasons['yt-test_rule_bson-arni'] = 'fail'
    assert replication._finalize(managers_store) == (
        '4 replication units failed:\n'
        '* yt-test_rule_bson-arni: fail\n'
        '* yt-test_rule_bson-hahn: None\n'
        '* yt-test_rule_struct-arni: None\n'
        '* yt-test_rule_struct-hahn: None'
    )


NOW = datetime.datetime(2018, 11, 26, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.mongodb_collections('test_coll')
async def test_replicate_mongo_to_yt(
        replication_ctx,
        yt_clients_storage,
        dummy_sha1,
        replication_tasks_getter,
        load_json,
        run_replication,
        patch_solomon_client,
):
    # pylint: disable=too-many-locals
    with yt_clients_storage() as all_clients:
        await run_replication(TEST_RULE_NAME)

    expected_stats = load_json('expected_performance.json')
    solomon_sensors = patch_solomon_client

    for expected_metrics, received_metrics in zip(
            expected_stats, solomon_sensors,
    ):
        assert expected_metrics['labels'] == received_metrics['labels']
        assert expected_metrics['value'] == received_metrics['value']

    staging_test_rule_db = (
        replication_ctx.rule_keeper.staging_db.get_queue_mongo_shard(
            'test_rule',
        ).primary
    )
    staging_docs = await staging_test_rule_db.find().to_list(None)

    raw_doc1 = (
        b';\x00\x00\x00\x02_id\x00\x02\x00\x00'
        b'\x001\x00\tupdated\x00@\x15\xd9J'
        b'g\x01\x00\x00\x10value_1\x00\x01\x00\x00'
        b'\x00\x10value_2\x00\x02\x00\x00\x00\x00'
    )
    raw_doc2 = (
        b';\x00\x00\x00\x02_id\x00\x02\x00\x00'
        b'\x002\x00\tupdated\x00@\xac"Lg\x01\x00\x00'
        b'\x10value_1\x00\x0b\x00\x00\x00\x10value_'
        b'2\x00\x16\x00\x00\x00\x00'
    )
    raw_doc_unindexed = (
        b'2\x00\x00\x00\x02'
        b'_id\x00\n\x00\x00\x00unindexed\x00\x10'
        b'value_1\x00\n\x00\x00\x00\x10'
        b'value_2\x00\x14\x00\x00\x00\x00'
    )
    staging_docs_copy = []
    for doc in staging_docs:
        doc = doc.copy()
        assert doc.pop(queue_mongo.CONFIRMATIONS_FIELD)
        assert doc.pop(queue_mongo.TARGETS_UPDATED_FIELD)
        staging_docs_copy.append(doc)
    staging_docs = staging_docs_copy
    assert sorted(staging_docs, key=operator.itemgetter('_id')) == [
        {
            '_id': '1',
            'data': raw_doc1,
            'created': NOW,
            'updated': NOW,
            'v': 3,
            'indexes': {'value_1': 1},
            '_sha1_hash': 'doc hash must be here',
            'bs': datetime.datetime(2018, 11, 25, 12, 30),
        },
        {
            '_id': '2',
            'data': raw_doc2,
            'created': NOW,
            'updated': NOW,
            'v': 2,
            'indexes': {'value_1': 11},
            '_sha1_hash': 'doc hash must be here',
            'bs': datetime.datetime(2018, 11, 25, 18, 30),
        },
        {
            '_id': 'unindexed',
            'data': raw_doc_unindexed,
            'created': NOW,
            'updated': NOW,
            'v': 1,
            'indexes': {'value_1': 10},
            '_sha1_hash': 'doc hash must be here',
        },
    ]

    expected = {
        'test/test_struct': {
            '1': {'id': '1', 'value_1': 1, 'value_2': 2},
            '2': {'id': '2', 'value_1': 11, 'value_2': 22},
            'unindexed': {'id': 'unindexed', 'value_1': 10, 'value_2': 20},
        },
        'test/test_bson': {
            b'1': {b'doc': raw_doc1, b'id': b'1'},
            b'2': {b'doc': raw_doc2, b'id': b'2'},
            b'unindexed': {b'doc': raw_doc_unindexed, b'id': b'unindexed'},
        },
    }
    for cluster in ['hahn', 'arni']:
        assert all_clients[cluster].rows_by_ids == expected, (
            f'Mongo replication from queue to yt-{cluster} failed',
        )

    states = replication_ctx.rule_keeper.states_wrapper.state_items(
        rule_name='test_rule',
    )
    states_dumps = {state_id: state.to_dict() for state_id, state in states}
    for value in states_dumps.values():
        value.pop('last_synced', None)
    expected_states_dump = load_json(
        'expected_states_dump.json', object_hook=None,
    )
    assert states_dumps == expected_states_dump


@pytest.mark.config(
    REPLICATION_SERVICE_CTL={
        'quota': {
            'quotas_enabled': True,
            'quotas': {'test_rule': 37, 'test_map_data': 39},
        },
    },
)
async def test_quota_runtime_check(replication_ctx, monkeypatch):
    async def dummy_space(*args, **kwargs):
        return 38 * 1024 ** 2

    monkeypatch.setattr(queue_mongo, 'get_occupied_space', dummy_space)
    queue_mongo_quotas = replication_ctx.rule_keeper.queue_mongo_quotas
    rules_storage = replication_ctx.rule_keeper.rules_storage

    target_no_quota = rules_storage.get_rules_list(
        rule_name='test_rule', target_types=['queue_mongo'],
    )[0].targets[0]
    with pytest.raises(exceptions.QuotaExceededError):
        await replication._check_queue_target_quota(
            queue_mongo_quotas, target_no_quota,
        )

    target_quota_ok = rules_storage.get_rules_list(
        rule_name='test_map_data', target_types=['queue_mongo'],
    )[0].targets[0]
    await replication._check_queue_target_quota(
        queue_mongo_quotas, target_quota_ok,
    )

    target_quota_ok2 = rules_storage.get_rules_list(
        rule_name='test_errors_rule', target_types=['queue_mongo'],
    )[0].targets[0]
    await replication._check_queue_target_quota(
        queue_mongo_quotas, target_quota_ok2,
    )


# pylint: disable=unused-variable
# pylint: disable=no-member
# pylint: disable=arguments-differ
# pylint: disable=too-many-locals
@pytest.mark.filldb(test_coll='errors')
@pytest.mark.mongodb_collections('test_coll')
@pytest.mark.config(
    REPLICATION_INVALID_DOCS_THRESHOLDS={
        '__default__': {'invalid_docs_can_continue': 2},
    },
)
async def test_errors_confirm(
        monkeypatch,
        patch,
        replication_ctx,
        replication_tasks_getter,
        yt_clients_storage,
):
    test_rule_name = 'test_errors_rule'
    original_handle = data_helpers.handle_raw_bson

    @patch('replication.utils.data_helpers.handle_raw_bson')
    def handle_raw_bson(doc):
        decoded_doc = original_handle(doc)
        if decoded_doc['_id'] == 'raise_invalid_bson':
            raise data_helpers.InvalidBSONError(
                'Decode failed', doc_id='invalid_bson',
            )
        return decoded_doc

    tasks = await replication_tasks_getter(
        consts.SOURCE_TYPE_MONGO, test_rule_name,
    )
    assert len(tasks) == 1
    await replication.replicate_to_targets(replication_ctx, tasks)
    staging_db = replication_ctx.rule_keeper.staging_db
    staging_test_rule_db = staging_db.get_queue_mongo_shard(
        'test_errors_rule',
    ).primary
    staging_docs = await staging_test_rule_db.find().to_list(None)
    assert set(doc['_id'] for doc in staging_docs) == {
        'ok_doc',
        'raise_mapper_error_struct_cast',
        'raise_hahn_error_struct',
    }

    class SchemaError(yt.wrapper.YtResponseError):
        def contains_code(self, code, *args, **kwargs):
            if code == _SCHEMA_VIOLATION_CODE:
                return True
            return False

        def contains_text(self, text, *args, **kwargs):
            return False

        def __str__(self):
            return 'SchemaError'

    class ClientRaisingErrorIfHahn(yt_wrapper.YtClient):
        def insert_rows(self, table, rows, **kwargs):
            if (
                    self.cluster_name == 'hahn'
                    and table == 'test/errors/test_struct'
                    and any(row.get('value_2') < 0 for row in rows)
            ):
                raise SchemaError(
                    {
                        'message': 'Column value_2 is uint64',
                        'code': _SCHEMA_VIOLATION_CODE,
                    },
                )
            super().insert_rows(table, rows, **kwargs)

        def get(self, path, *args, **kwargs):
            if (
                    self.cluster_name == 'hahn'
                    and path == 'test/errors/test_struct/@schema'
            ):
                return [
                    {'name': 'hash', 'type': 'uint64'},
                    {'name': 'id', 'type': 'string'},
                    {'name': 'value_1', 'type': 'int64'},
                    {'name': 'value_2', 'type': 'uint64'},
                ]
            return super().get(path, *args, **kwargs)

    monkeypatch.setattr(yt_wrapper, 'YtClient', ClientRaisingErrorIfHahn)

    with yt_clients_storage() as all_clients:
        tasks = await replication_tasks_getter(
            consts.SOURCE_TYPE_QUEUE_MONGO, test_rule_name,
        )
        assert len(tasks) == 1
        await replication.replicate_to_targets(replication_ctx, tasks)

    errors_dict = {
        'hahn': {
            'test/errors/test_struct': {
                'ok_doc': {'id': 'ok_doc', 'value_1': 1, 'value_2': 2},
            },
            'test/test_struct_2': {
                'ok_doc': {'id': 'ok_doc', 'value_1': 1, 'value_2': 2},
                'raise_hahn_error_struct': {
                    'id': 'raise_hahn_error_struct',
                    'value_1': 11,
                    'value_2': -1,
                },
            },
        },
        'arni': {
            'test/errors/test_struct': {
                'ok_doc': {'id': 'ok_doc', 'value_1': 1, 'value_2': 2},
                'raise_hahn_error_struct': {
                    'id': 'raise_hahn_error_struct',
                    'value_1': 11,
                    'value_2': -1,
                },
                # real YT won't accept this row
                'raise_mapper_error_struct_cast': {
                    'id': 'raise_mapper_error_struct_cast',
                    'value_1': '10',
                    'value_2': 20,
                },
            },
            'test/test_struct_2': {
                'ok_doc': {'id': 'ok_doc', 'value_1': 1, 'value_2': 2},
                'raise_hahn_error_struct': {
                    'id': 'raise_hahn_error_struct',
                    'value_1': 11,
                    'value_2': -1,
                },
            },
        },
    }
    assert all_clients['hahn'].rows_by_ids == errors_dict['hahn']
    assert all_clients['arni'].rows_by_ids == errors_dict['arni']
    staging_docs = await staging_test_rule_db.find().to_list(None)
    expected_confirms = {
        'ok_doc': {
            '1',  # 'yt-test_errors_rule_struct-arni',
            '2',  # 'yt-test_errors_rule_struct-hahn',
            '3',  # 'yt-test_errors_rule_struct_2-arni',
            '4',  # 'yt-test_errors_rule_struct_2-hahn',
        },
        'raise_mapper_error_struct_cast': {
            '1',  # 'yt-test_errors_rule_struct-arni',
        },
        'raise_hahn_error_struct': {
            '1',  # 'yt-test_errors_rule_struct-arni',
            '3',  # 'yt-test_errors_rule_struct_2-arni',
            '4',  # 'yt-test_errors_rule_struct_2-hahn',
        },
    }
    for doc in staging_docs:
        confirmed_to = set(
            target_name
            for target_name, target_info in doc['confirmations'].items()
            if target_info['v'] == doc['v']
        )
        assert expected_confirms[doc['_id']] == confirmed_to
    errors = await replication_ctx.db.replication_invalid_docs.find().to_list(
        None,
    )
    errors_dict = {}
    for error in errors:
        error_info = {}
        for field, value in error.items():
            if field not in ['_id', 'error_ts']:
                error_info[field] = value
        errors_dict[error['doc_id']] = error_info
    assert errors_dict == {
        'invalid_bson': {
            'doc_id': 'invalid_bson',
            'errors': [{'message': 'Decode failed'}],
            'rule_name': 'test_errors_rule',
            'stage': 'source',
            'unit_id': 'mongo-test_errors_rule',
        },
        'raise_hahn_error_struct': {
            'doc_id': 'raise_hahn_error_struct',
            'errors': [
                {
                    'details': {
                        'column': 'value_2',
                        'message': (
                            'expected uint64, but got value '
                            'not in [0, 2**64)'
                        ),
                        'value': -1,
                    },
                    'message': (
                        'column value_2, value -1, error: expected uint64,'
                        ' but got value not in [0, 2**64)'
                    ),
                },
            ],
            'rule_name': 'test_errors_rule',
            'stage': 'target',
            'unit_id': 'yt-test_errors_rule_struct-hahn',
        },
        'raise_mapper_error_struct_cast': {
            'doc_id': 'raise_mapper_error_struct_cast',
            'errors': [
                {
                    'details': {
                        'column': 'value_1',
                        'message': (
                            'expected int64, but got value '
                            'of type <class \'yt.yson.yson_types'
                            '.YsonUnicode\'>'
                        ),
                        'value': '10',
                    },
                    'message': (
                        'column value_1, value \'10\', error: expected '
                        'int64, but got value of type <class \'yt.yson.'
                        'yson_types.YsonUnicode\'>'
                    ),
                },
            ],
            'rule_name': 'test_errors_rule',
            'stage': 'target',
            'unit_id': 'yt-test_errors_rule_struct-hahn',
        },
    }


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'source_type,rule_name,doc,expected_base_stamp',
    [
        (
            consts.SOURCE_TYPE_QUEUE_MONGO,
            TEST_RULE_NAME,
            {
                '_id': 'doc_id',
                'updated': datetime.datetime(2018, 1, 1, 10),
                queue_mongo.DATA_FIELD: {
                    'updated': datetime.datetime(2017, 1, 1, 10),
                },
            },
            datetime.datetime(2017, 1, 1, 10),
        ),
        (
            consts.SOURCE_TYPE_MONGO,
            TEST_RULE_NAME,
            {
                '_id': 'doc_id',
                'updated': datetime.datetime(2018, 1, 1, 10),
                queue_mongo.DATA_FIELD: {
                    'updated': datetime.datetime(2017, 1, 1, 10),
                },
            },
            None,
        ),
        (
            consts.SOURCE_TYPE_QUEUE_MONGO,
            'basic_source_postgres_sequence',
            {
                '_id': 'doc_id',
                'updated': datetime.datetime(2019, 1, 1, 10),
                queue_mongo.DATA_FIELD: {'id': 1230},
            },
            1230,
        ),
        (
            consts.SOURCE_TYPE_QUEUE_MONGO,
            'basic_source_postgres_strict_sequence',
            {
                '_id': 'doc_id',
                'updated': datetime.datetime(2019, 1, 1, 10),
                queue_mongo.DATA_FIELD: {'id': 1230},
            },
            1230,
        ),
        (
            consts.SOURCE_TYPE_QUEUE_MONGO,
            'api_replicate_by',
            {
                '_id': 'doc_id',
                'updated': datetime.datetime(2019, 1, 1, 10),
                queue_mongo.DATA_FIELD: {'updated': '2020-02-02T12:00:00'},
            },
            datetime.datetime(2020, 2, 2, 12),
        ),
    ],
)
async def test_get_max_base_stamp(
        replication_ctx,
        units_getter,
        source_type,
        rule_name,
        doc,
        expected_base_stamp,
):
    source, _ = (await units_getter(source_type, rule_name))[0]
    assert (
        replication._get_max_base_stamp(replication_ctx, source, doc)
        == expected_base_stamp
    )


@pytest.fixture(autouse=True)
def _patch_current_date(patch_queue_current_date):
    pass


@pytest.fixture
def patch_solomon_client(replication_ctx, monkeypatch):
    metrics = []

    async def mock_solomon_push(data, *args, **kwargs):
        metrics.extend(data._sensors)

    monkeypatch.setattr(
        replication_ctx.shared_deps.client_solomon,
        'push_data',
        mock_solomon_push,
    )
    return metrics
