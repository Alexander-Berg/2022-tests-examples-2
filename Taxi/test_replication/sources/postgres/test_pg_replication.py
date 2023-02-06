# pylint: disable=protected-access

import datetime

import attr
import pytest

from replication.common.pgsql import aiopg_wrapper
from replication.common.pgsql import wrapper as pg_wrapper
from replication.foundation import consts
from replication.replication.core import replication
from replication.sources.postgres import core as postgres

PG_RULE_NAME = 'test_sharded_pg'

NOW = datetime.datetime(2018, 11, 26, 0)


# TODO: use run_replication fixture, move expected queue to json
@pytest.mark.pgsql('example_pg@0', files=['example_pg_shard0.sql'])
@pytest.mark.pgsql('example_pg@1', files=['example_pg_shard1.sql'])
@pytest.mark.parametrize(
    'use_aiopg',
    [
        pytest.param(False, id='use pg driver'),
        pytest.param(True, id='use aiopg'),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_replicate_pg_to_yt(
        monkeypatch,
        replication_ctx,
        yt_clients_storage,
        replication_tasks_getter,
        patch_queue_current_date,
        use_aiopg,
        replace_frozen,
):
    async def get_now(self):
        return NOW

    monkeypatch.setattr(
        replication.settings, 'POSTGRES_AIOPG_SSLMODE', 'disable',
    )

    monkeypatch.setattr(pg_wrapper.PoolExecutor, 'utc_now', get_now)
    monkeypatch.setattr(aiopg_wrapper.PoolExecutorAiopg, 'utc_now', get_now)

    tasks = await replication_tasks_getter(
        postgres.SOURCE_TYPE_POSTGRES, PG_RULE_NAME,
    )

    assert len(tasks) == 2
    for task in tasks:
        if use_aiopg:
            meta = attr.evolve(task.source.meta, use_aiopg=True)
            task = replace_frozen(
                task, {'source': replace_frozen(task.source, {'meta': meta})},
            )
        await replication.replicate_to_targets(replication_ctx, [task])

    staging_rule_db = (
        replication_ctx.rule_keeper.staging_db.get_queue_mongo_shard(
            'test_sharded_pg',
        ).primary
    )
    staging_docs = {
        doc['_id']: doc for doc in await staging_rule_db.find().to_list(None)
    }
    expected_staging_docs = [
        {
            '_id': '_id_1__order',
            'created': datetime.datetime(2018, 11, 26, 0, 0),
            'data': (
                '{"created_at": {"$a": {"raw_type": "datetime"}, '
                '"$v": "2018-11-24T07:00:00"}, "doc_type": '
                '"order", "id": "_id_1_", "modified_at": null, '
                '"total": {"$a": {"raw_type": "decimal"}, '
                '"$v": "0.000000"}}'
            ),
            'updated': datetime.datetime(2018, 11, 26, 0, 0),
            'v': 1,
            'unit': 'shard0',
        },
        {
            '_id': '_id_2__order',
            'created': datetime.datetime(2018, 11, 26, 0, 0),
            'data': (
                '{"created_at": {"$a": {"raw_type": "datetime"}, '
                '"$v": "2018-11-24T08:00:00"}, "doc_type": '
                '"order", "id": "_id_2_", "modified_at": '
                '{"$a": {"raw_type": "datetime"}, "$v": '
                '"2018-11-24T08:20:00"}, "total": {"$a": '
                '{"raw_type": "decimal"}, "$v": "1.000001"}}'
            ),
            'updated': datetime.datetime(2018, 11, 26, 0, 0),
            'v': 2,
            'unit': 'shard0',
            'bs': datetime.datetime(2018, 11, 24, 8, 20),
        },
        {
            '_id': '_id_3__order',
            'created': datetime.datetime(2018, 11, 26, 0, 0),
            'data': (
                '{"created_at": {"$a": {"raw_type": "datetime"}, '
                '"$v": "2018-11-23T07:00:00"}, "doc_type": "order", '
                '"id": "_id_3_", "modified_at": {"$a": {"raw_type": '
                '"datetime"}, "$v": "2018-11-23T07:00:00"}, '
                '"total": {"$a": {"raw_type": "decimal"}, '
                '"$v": "11.111000"}}'
            ),
            'updated': datetime.datetime(2018, 11, 26, 0, 0),
            'v': 3,
            'unit': 'shard1',
            'bs': datetime.datetime(2018, 11, 23, 7, 0),
        },
        {
            '_id': '_id_3__ride',
            'created': datetime.datetime(2018, 11, 26, 0, 0),
            'data': (
                '{"created_at": {"$a": {"raw_type": "datetime"}, '
                '"$v": "2018-11-23T07:10:00"}, "doc_type": '
                '"ride", "id": "_id_3_", "modified_at": '
                '{"$a": {"raw_type": "datetime"}, "$v": '
                '"2018-11-23T07:11:00"}, "total": '
                '{"$a": {"raw_type": "decimal"}, "$v": "11.101010"}}'
            ),
            'updated': datetime.datetime(2018, 11, 26, 0, 0),
            'v': 3,
            'unit': 'shard1',
            'bs': datetime.datetime(2018, 11, 23, 7, 11),
        },
    ]
    expected_staging_docs = {doc['_id']: doc for doc in expected_staging_docs}
    assert (
        staging_docs == expected_staging_docs
    ), 'Postgres replication to queue failed'

    with yt_clients_storage() as all_clients:
        tasks = await replication_tasks_getter(
            consts.SOURCE_TYPE_QUEUE_MONGO, PG_RULE_NAME,
        )
        assert len(tasks) == 1
        await replication.replicate_to_targets(replication_ctx, tasks)

    expected = {
        'test/test_sharded_pg': {
            ('_id_1_', 'order'): {
                'created_at': 1543042800.0,
                'doc_type': 'order',
                'id': '_id_1_',
                'modified_at': None,
                'total': 0,
            },
            ('_id_2_', 'order'): {
                'created_at': 1543046400.0,
                'doc_type': 'order',
                'id': '_id_2_',
                'modified_at': 1543047600.0,
                'total': 1000001,
            },
            ('_id_3_', 'order'): {
                'created_at': 1542956400.0,
                'doc_type': 'order',
                'id': '_id_3_',
                'modified_at': 1542956400.0,
                'total': 11111000,
            },
            ('_id_3_', 'ride'): {
                'created_at': 1542957000.0,
                'doc_type': 'ride',
                'id': '_id_3_',
                'modified_at': 1542957060.0,
                'total': 11101010,
            },
        },
    }
    for cluster in ['hahn', 'arni']:
        assert all_clients[cluster].rows_by_ids == expected, (
            f'Postgres replication from queue to yt-{cluster} failed',
        )


@pytest.mark.pgsql('sequence', files=['sequence.sql'])
@pytest.mark.parametrize(
    'rule_name,expected_queue_file,expected_queue_file_without_lag',
    [
        (
            'basic_source_postgres_sequence',
            'expected_queue_pg_sequence.json',
            'expected_queue_pg_sequence2.json',
        ),
        (
            'basic_source_postgres_strict_sequence',
            'expected_queue_pg_strict_sequence.json',
            'expected_queue_pg_strict_sequence2.json',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_pg_replication(
        load_py_json,
        run_replication,
        patch_queue_current_date,
        rule_name,
        expected_queue_file,
        expected_queue_file_without_lag,
):
    targets_data = await run_replication(rule_name)
    queue_docs = targets_data.queue_data_by_id()

    expected_queue_docs = {
        doc['_id']: doc for doc in load_py_json(expected_queue_file)
    }
    assert (
        queue_docs == expected_queue_docs
    ), f'pg replication to queue failed for {rule_name}'

    # hack for skip lag-checking
    # for state in targets_data.states_from_queue:
    #     await state.update_last_replication(
    #         datetime.datetime.utcnow() - datetime.timedelta(minutes=20),
    #         log_it=True,
    #     )
    expected_queue_docs = {
        doc['_id']: doc
        for doc in load_py_json(expected_queue_file_without_lag)
    }
    targets_data = await run_replication(rule_name)
    queue_docs = targets_data.queue_data_by_id()
    assert (
        queue_docs == expected_queue_docs
    ), f'pg replication2 to queue failed for {rule_name}'


@pytest.mark.pgsql('sequence', files=['sequence_with_duplicates.sql'])
@pytest.mark.parametrize(
    'rule_name',
    ['postgres_sequence_with_duplicates', 'basic_source_postgres_sequence_ts'],
)
@pytest.mark.now(NOW.isoformat())
async def test_pg_replication_duplicates(
        run_replication, rule_name, patch_queue_current_date,
):
    targets_data = await run_replication(rule_name)
    queue_docs = targets_data.queue_data
    assert (
        len(queue_docs) == 11
    ), f'pg replication to queue failed for {rule_name}'
    assert all(
        'confirmations' in doc for doc in queue_docs
    ), f'queue replication to yt failed for {rule_name}'


@pytest.fixture
def test_env_id_setter(test_env_testsuite):
    return test_env_testsuite
