# pylint: disable=protected-access, redefined-outer-name
import contextlib
import datetime
import typing
from typing import Optional

import pytest

from replication.archiving import loaders
from replication.archiving import run
from replication.archiving.classes import _mongo
from replication.common import queue_mongo
from replication.common.solomon import consts as solomon_const
from replication.common.solomon import pusher as solomon_pusher
from replication.common.ydb_tools import ydb_client
from replication.targets import verifiers


NOW = datetime.datetime(2018, 11, 14, 12, 0)


@pytest.mark.parametrize('custom_bulk_size', [1, 20, None])
@pytest.mark.parametrize(
    'rule_name,expected_removed_ids,expected_stats,setup_archiving_test',
    [
        pytest.param(
            'queue_mongo-staging_test_rule',
            {
                'to_remove',
                'ready_to_remove',
                'ready_to_remove_partial_confirmation_arni_disabled',
                'ready_to_remove_new',
                'ready_to_remove_combo',
                '6_fresh_targets_updated',
            },
            {'db_read': 11, 'filter': 11, 'remove': 6, 'aggregation': 7},
            {'yt': 'default_clients_data.json'},
            marks=pytest.mark.now(NOW.isoformat()),
        ),
        pytest.param(
            'queue_mongo-staging_test_rule',
            {
                'to_remove',
                'ready_to_remove',
                'ready_to_remove_partial_confirmation_arni_disabled',
                'ready_to_remove_new',
                'ready_to_remove_combo',
                '6_fresh_targets_updated',
                'cannot ready, yt hahn doc hash mismatch',
            },
            {'db_read': 11, 'filter': 11, 'remove': 7, 'aggregation': 7},
            {'yt': 'default_clients_data_insert_rows.json'},
            marks=pytest.mark.now(NOW.isoformat()),
        ),
        pytest.param(
            'queue_mongo-staging_test_ydb',
            {'2_ydb_doc_1'},
            {'db_read': 1, 'filter': 1, 'remove': 1, 'aggregation': 1},
            {'ydb': 'ydb_data.json'},
            marks=pytest.mark.now(NOW.isoformat()),
        ),
        pytest.param(
            'queue_mongo-staging_test_sharded_pg',
            {
                'to_remove-arni_triggered_initial_ts-arni_no_confirm',
                'to_remove-arni_triggered_initial_ts-arni_bad_confirm',
                '3_fresh_targets_updated',
            },
            {'db_read': 5, 'filter': 5, 'remove': 3},
            None,
            marks=pytest.mark.now(NOW.isoformat()),
        ),
        pytest.param(
            'queue_mongo-staging_test_errors_rule',
            {
                'to_remove',
                'ready_to_remove',
                'ready_to_remove_partial_confirmation_arni_disabled',
                '6_fresh_targets_updated',
            },
            {'db_read': 7, 'filter': 7, 'remove': 4},
            None,
            marks=pytest.mark.now(NOW.isoformat()),
        ),
        pytest.param(
            'queue_mongo-staging_api_replicate_by',
            {'to_remove'},
            {'db_read': 2, 'filter': 2, 'remove': 1},
            None,
            marks=[
                pytest.mark.config(
                    REPLICATION_SERVICE_CTL={
                        'quota': {
                            'quotas_enabled': True,
                            'quotas': {'__default__': 2},  # 2 Mb
                        },
                    },
                ),
                pytest.mark.now('2019-05-07T12:00:00'),
            ],
            id='queue_mongo-archiving-deadlock',
        ),
        pytest.param(
            'queue_mongo-staging_api_replicate_by',
            set(),
            {},
            None,
            marks=pytest.mark.now('2019-05-07T12:00:00'),
            id='queue_mongo-archiving-ok_quota',
        ),
    ],
    indirect=['setup_archiving_test'],
)
async def test_archive_documents(
        monkeypatch,
        replication_ctx,
        setup_archiving_test: Optional['SetupTest'],
        custom_bulk_size,
        rule_name,
        expected_removed_ids,
        expected_stats,
):
    archiver = (await loaders.get_from_replication_rules(replication_ctx))[
        rule_name
    ]
    collection = archiver._collection_primary
    doc_ids_before = await _get_ids(collection)
    assert doc_ids_before
    archived_count = []

    class MockBulk(_mongo.QueueMongoBulkRemover):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if custom_bulk_size is not None:
                self.bulk_size = custom_bulk_size

        async def _remove(self):
            archived_count.append(await super()._remove())

    monkeypatch.setattr(_mongo, 'QueueMongoBulkRemover', MockBulk)

    monitor_solomon_stats = {}

    async def fake_solomon_rules_performance(
            client_solomon,
            monitor_metrics: typing.List[solomon_pusher.BaseStat],
            performance_name: solomon_const.PerformanceName,
    ):
        assert (
            performance_name.value
            == solomon_const.PerformanceName.ARCHIVING_PERFORMANCE_NAME.value
        )
        for metrics in monitor_metrics:
            labels = metrics.get_labels()
            op_type = labels['op_type']
            for stat_type, value in metrics.get_stats():
                if stat_type == 'time_sec':
                    continue
                monitor_solomon_stats[op_type] = value

    monkeypatch.setattr(
        solomon_pusher,
        'solomon_rules_performance',
        fake_solomon_rules_performance,
    )

    async def dummy_space(*args, **kwargs):
        return 3 * 1024 ** 2  # 3 Mb occupied

    monkeypatch.setattr(queue_mongo, 'get_occupied_space', dummy_space)
    if setup_archiving_test is not None:
        with setup_archiving_test.ctx_manager as setup_ctx:
            await run.archive_documents(replication_ctx, archiver)
        setup_archiving_test.check_at_finish(setup_ctx)
    else:
        await run.archive_documents(replication_ctx, archiver)

    docs_ids_after = await _get_ids(collection)
    removed_ids = doc_ids_before - docs_ids_after
    assert removed_ids == expected_removed_ids
    assert sum(archived_count) == len(removed_ids)
    assert monitor_solomon_stats == expected_stats


async def _get_ids(collection):
    docs = await collection.find({}, ['_id']).to_list(None)
    return {doc['_id'] for doc in docs}


class SetupTest:
    def __init__(self, ctx_manager, check_at_finish):
        self.ctx_manager = ctx_manager
        self.check_at_finish = check_at_finish


@pytest.fixture
def setup_archiving_test(
        request, yt_clients_storage, load_py_json, monkeypatch,
):
    params = request.param or {}

    if 'yt' in params:
        total_failed = []
        old_check_hashes = verifiers._YTVerifier._check_hashes

        def _check_hashes(*args, **kwargs):
            verified, failed = old_check_hashes(*args, **kwargs)
            total_failed.extend(failed)
            return verified, failed

        monkeypatch.setattr(
            verifiers._YTVerifier, '_check_hashes', _check_hashes,
        )
        yt_data = load_py_json(params['yt'])
        expected_yt_data = yt_data['__expected_yt_data__']
        monkeypatch.setattr(
            verifiers._YTVerifier,
            '_get_verifier_type',
            lambda self: self._VerifierType[yt_data['__type__']],
        )
        default_clients_data = _generate_yt_mock(yt_data)
        ctx = yt_clients_storage(default_clients_data=default_clients_data)

        def _at_finish(all_clients):
            if yt_data['__type__'] == 'lookup_rows':
                assert total_failed == expected_yt_data
            else:
                for cluster in yt_data['__common__']['clusters']:
                    assert (
                        dict(all_clients[cluster].rows_by_ids)
                        == expected_yt_data
                    )

        yield SetupTest(ctx, _at_finish)

    elif 'ydb' in params:
        ydb_data = load_py_json(params['ydb'])
        expected_ydb_data = ydb_data['expected_ydb_data']

        ydb_data = []
        ydb_cls = lambda *args, **kwargs: _DummyYdbClient(  # noqa: E731
            ydb_data,
        )
        monkeypatch.setattr(ydb_client, 'YdbClient', ydb_cls)

        @contextlib.contextmanager
        def _dummy_ctx():
            yield

        def _at_finish(all_clients):
            assert ydb_data == expected_ydb_data

        yield SetupTest(_dummy_ctx(), _at_finish)

    else:
        yield None


def _generate_yt_mock(yt_params):
    common = yt_params['__common__']
    default_clients_data = {}
    # yt_clients_storage interface: cluster -> table -> doc_id -> doc
    for cluster in common['clusters']:
        yt_data = default_clients_data.setdefault(cluster, {}).setdefault(
            common['table'], {},
        )
        overrides = yt_params.get(cluster, {})
        for doc_id in common['ids']:
            if doc_id in overrides:
                doc_hash = overrides[doc_id]
            else:
                doc_hash = common['doc_hash']
            yt_data[doc_id] = {'id': doc_id, 'doc_hash': doc_hash}
    return default_clients_data


class _DummyYdbClient:
    def __init__(self, data: list):
        self._data = data

    async def create_table(self, *args, **kwargs):
        pass

    async def insert_rows(self, *, path_to_table: str, data, schema):
        self._data.extend(data)
