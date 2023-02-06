import pytest

from replication.sources import exceptions as sources_exceptions
from replication.sources.postgres import core as postgres


@pytest.mark.pgsql('sequence')
@pytest.mark.parametrize(
    ('task_name', 'should_be_ready'),
    [('basic_source_postgres', False), ('indexed_source_postgres', True)],
)
async def test_replication_cannot_start_if_source_unindexed(
        replication_tasks_getter, task_name: str, should_be_ready: bool,
):
    tasks = await replication_tasks_getter(
        postgres.SOURCE_TYPE_POSTGRES, task_name,
    )
    assert len(tasks) == 1
    if should_be_ready:
        await tasks[0].source.check_before_start()
    else:
        with pytest.raises(sources_exceptions.SourceNotReadyError):
            await tasks[0].source.check_before_start()
