import pytest

from dmp_suite.table import LayeredLayout
from dmp_suite.task import cli
from dmp_suite.task.execution import run_migration
from dmp_suite.yt import YTTable, YTMeta, Datetime, resolve_meta, MonthPartitionScale, YearPartitionScale, \
    DayPartitionScale, ETLTable
from dmp_suite.yt.migration.repartition import repartition
from dmp_suite.yt import operation as op
from .utils import create, write
from dmp_suite.migration import migration
from dmp_suite import datetime_utils as dtu


@pytest.mark.slow
def test_repartition_for_partitioned_tables_static():
    # Репартицирование статической таблицы.
    # Имитируем ситуацию, когда в TestTable сначало было месячное партицирование, которое меняется на годовое.

    class TestTable(ETLTable):
        __layout__ = LayeredLayout(layer='raw', name='test', group='test')
        __partition_scale__ = YearPartitionScale('created_at')

        created_at = Datetime()

    # Создадим три партиции
    p1 = resolve_meta(TestTable, partition='2021-11-01')
    p2 = resolve_meta(TestTable, partition='2021-12-01')
    p3 = resolve_meta(TestTable, partition='2022-01-01')

    create(p1)
    create(p2)
    create(p3)

    write(p1, [{'created_at': '2021-11-05'}])
    write(p2, [{'created_at': '2021-12-10'}])
    write(p3, [{'created_at': '2022-01-20'}])

    task = migration('TAXIDWH-13588',
        repartition(TestTable).arguments(
            period=cli.StartEndDate(dtu.Period('2021-11-01', '2022-01-31'))
        )
    )
    run_migration(task)
    partition_list = list(op.get_yt_children(YTMeta(TestTable).target_folder_path, absolute=False))

    assert len(partition_list) == 2
    assert set(partition_list) == {'2021-01-01', '2022-01-01'}
