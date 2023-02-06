import contextlib
import datetime

import pytest

from replication.local_replication import context as local_context
from replication.local_replication import main
from replication.local_replication import runner as local_runner

_YT_DOCS = {
    '1': {'id': '1', 'value_1': None, 'value_2': None},
    '2': {'id': '2', 'value_1': None, 'value_2': None},
}


@pytest.mark.now(datetime.datetime(2020, 2, 14, 3).isoformat())
@pytest.mark.mongodb_collections('test_coll')
@pytest.mark.parametrize('no_clean', [True, False])
@pytest.mark.parametrize(
    'run_args,expected_yt_ids',
    [
        ([], _YT_DOCS),
        (['--replicate-from', '2019-01-01T01:00:00'], {'2'}),
        (['--replicate-to', '2019-01-01T01:00:00'], {'1'}),
        (
            [
                '--replicate-from',
                '2019-01-01T01:00:00',
                '--replicate-to',
                '2019-01-02T01:00:00',
            ],
            {},
        ),
        (
            ['--replicate-to', '2019-01-01T01:00:00', '--indent', '400-days'],
            {'1'},
        ),
        (['--replicate-to', '2019-01-01T01:00:00', '--indent', '1-days'], {}),
        (['--indent', '60-days'], {'2'}),
    ],
)
async def test_local_runner(
        replication_ctx,
        patch_queue_current_date,
        monkeypatch,
        yt_clients_storage,
        run_args,
        expected_yt_ids,
        no_clean,
):
    @contextlib.asynccontextmanager
    async def pytest_context_scope():
        yield replication_ctx

    monkeypatch.setattr(local_context, 'context_scope', pytest_context_scope)

    staging_collection = (
        replication_ctx.rule_keeper.staging_db.get_queue_mongo_shard(
            'test_rule',
        ).primary
    )
    assert await staging_collection.count() == 0

    all_run_args = ['run', 'test_rule_struct'] + run_args
    if no_clean:
        all_run_args.append('--no-clean-queue')

    with yt_clients_storage() as all_clients:
        await main.main(all_run_args)

    expected_yt_docs = {doc_id: _YT_DOCS[doc_id] for doc_id in expected_yt_ids}
    for cluster in ['hahn', 'arni']:
        assert all_clients[cluster].rows_by_ids == {
            'test/test_struct': expected_yt_docs,
        }

    assert await staging_collection.count() == (
        len(expected_yt_docs) if no_clean else 0
    )

    runner = local_runner.ReplicationRunner(
        replication_ctx, target_names=['test_rule_struct'],
    )
    await runner.clean_queue()
    assert await staging_collection.count() == 0
