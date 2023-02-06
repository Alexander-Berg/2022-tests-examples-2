import dataclasses
import typing as tp

import pytest

from dmp_suite import yt
from dmp_suite.personal.yt import task as personal_task
from dmp_suite.task import splitters
from dmp_suite.task.source import SourceAccessor
from test_dmp_suite.personal.yt.tables import (
    PartitionedRawTable,
    RawTable,
)


@dataclasses.dataclass()
class DummySource(personal_task.PdTaskSource):
    table: tp.Type[yt.YTTable]

    def get_source(self) -> SourceAccessor:
        pass

    @property
    def source_table(self):
        return self.table


def test_task_fails_on_different_raw_tables():
    with pytest.raises(personal_task.PdMigrationTaskError):
        personal_task.pd_migration_task(
            name='test',
            source=DummySource(RawTable),
            target_table=PartitionedRawTable,
        )


@pytest.mark.parametrize('table, splitter', [
    (RawTable, splitters.NoOpSplitter),
    (PartitionedRawTable, splitters.SplitInMonths),
])
def test_task_has_correct_splitter_and_arguments(table, splitter):
    task = personal_task.pd_migration_task(
        name='test',
        source=DummySource(table),
        target_table=table,
    )

    if yt.resolve_meta(table).has_partition_scale:
        assert 'period' in task.get_arguments()
    else:
        assert 'period' not in task.get_arguments()

    assert isinstance(task.splitter, splitter)
