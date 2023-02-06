# pylint: disable=protected-access
import pytest

from replication.sources.postgres import core as postgres


@pytest.mark.parametrize(
    ('task_name', 'prepared_statement_disabled'),
    [
        ('basic_source_postgres', False),
        ('prepared_statement_disabled_source_postgres', True),
    ],
)
async def test_prepared_statement_disabled(
        replication_tasks_getter,
        task_name: str,
        prepared_statement_disabled: bool,
):
    tasks = await replication_tasks_getter(
        postgres.SOURCE_TYPE_POSTGRES, task_name,
    )
    assert len(tasks) == 1
    assert (
        tasks[0].source.meta.prepared_statement_disabled
        == prepared_statement_disabled
    )
