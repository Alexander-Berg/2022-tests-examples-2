import pytest


@pytest.mark.config(
    REPLICATION_SERVICE_CTL={
        'replication': {'erase_queue_snapshot_fast_drop': True},
    },
)
@pytest.mark.pgsql('sequence', files=['sequence.sql'])
async def test_pg_snapshot_to_queue(run_replication, patch_queue_current_date):
    rule_name = 'postgres_example_snapshot'
    targets_data = await run_replication(rule_name)
    queue_docs = targets_data.queue_data
    assert (
        len(queue_docs) == 7
    ), f'pg snapshot replication to queue failed for {rule_name}'


@pytest.mark.config(
    REPLICATION_SERVICE_CTL={
        'replication': {'erase_queue_snapshot_fast_drop': True},
    },
)
@pytest.mark.pgsql('sequence', files=['sequence.sql'])
async def test_pg_snapshot_with_raw_select_to_queue(
        run_replication, patch_queue_current_date,
):
    rule_name = 'postgres_example_snapshot_with_raw_select'
    targets_data = await run_replication(rule_name)
    queue_docs = targets_data.queue_data
    assert len(queue_docs) == 4, (
        f'pg snapshot replication with raw_select to queue '
        f'failed for {rule_name}'
    )
