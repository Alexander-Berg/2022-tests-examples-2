from datetime import datetime

import mock
import pytest

from init_py_env import settings
from connection.yt import get_yt_client
from dmp_suite.table import LayeredLayout
from dmp_suite.yt import YTTable, Int, Datetime, resolve_meta, DayPartitionScale, TabletCellBundle
from dmp_suite.yt import operation as op
from dmp_suite.yt.dyntable_operation import operations as dop
from dmp_suite.yt.migration.move_table import _move_yt_object
from dmp_suite.yt.migration import move_table
from dmp_suite.yt.migration.utils import parse_yt_datetime_attr
from test_dmp_suite.yt import utils
from .utils import create


def _cut_off_the_path(path: str) -> str:
    pos = path.rfind('/')
    if pos > -1 and len(path) > 2:
        return path[:pos]
    return ''


@pytest.mark.slow
@mock.patch('dmp_suite.yt.migration.move_table.TABLET_CELL_BUNDLE', '_test_tablet_cell_bundle')
def test_move_table_wo_partition():
    @utils.random_yt_table
    class TableBefore(YTTable):
        __dynamic__ = True
        __unique_keys__ = True

        created_at = Datetime()
        a = Int(sort_key=True)

    @utils.random_yt_table
    class TableAfter(YTTable):
        __layout__ = LayeredLayout('test', 'test')  # layout будет переопределен декоратором
        __dynamic__ = True
        __unique_keys__ = True
        __tablet_cell_bundle__ = TabletCellBundle.TAXI_DWH  # Ожидаемый (правильный) бандл

        created_at = Datetime()
        a = Int(sort_key=True)

    create(TableBefore)

    meta_before = resolve_meta(TableBefore)
    meta_after = resolve_meta(TableAfter)

    op.set_yt_attr(
        _cut_off_the_path(meta_before.target_folder_path) + f'/@{move_table.TABLET_CELL_BUNDLE}', 'wrong_bundle'
    )
    op.set_yt_attr(meta_before.target_path() + f'/@{move_table.TABLET_CELL_BUNDLE}', 'wrong_bundle')

    _move_yt_object(TableBefore, TableAfter, expiration_date=datetime(9999, 1, 1))

    # Check that bundle is right
    bundles = settings('yt.bundles')
    expected_bundle = bundles.get(TableAfter.__tablet_cell_bundle__.value)
    assert get_yt_client().get_attribute(meta_after.target_path(), move_table.TABLET_CELL_BUNDLE) == expected_bundle

    # Check link
    meta_before = resolve_meta(TableBefore)
    meta_after = resolve_meta(TableAfter)

    link_path = meta_before.target_path_wo_partition + '&'

    obj_type = get_yt_client().get_attribute(link_path, 'type')
    assert obj_type == 'link'

    expiration_time_raw = get_yt_client().get_attribute(link_path, 'expiration_time')
    expiration_time = parse_yt_datetime_attr(expiration_time_raw)

    assert expiration_time == datetime(9999, 1, 1)

    assert dop.is_table_mounted(meta_before.target_folder_path)  # Доступаемся до таблицы по старой мете
    assert dop.is_table_mounted(meta_after.target_folder_path)  # По новой мете

    # И по старой и по новой мете доступны таблицы
    lst1 = list(get_yt_client().search(meta_before.target_folder_path, node_type=["link"]))
    lst2 = list(get_yt_client().search(meta_after.target_folder_path, node_type=["table"]))
    assert len(lst1) == 1
    assert len(lst2) == 1

    # Проверка идемпотентности
    _move_yt_object(TableBefore, TableAfter, expiration_date=datetime(9999, 1, 1))


@pytest.mark.slow
@mock.patch('dmp_suite.yt.migration.move_table.TABLET_CELL_BUNDLE', '_test_tablet_cell_bundle')
def test_move_table_with_partition():
    @utils.random_yt_table
    class TableBefore(YTTable):
        __partition_scale__ = DayPartitionScale(
            partition_key='created_at'
        )
        __dynamic__ = True
        __unique_keys__ = True
        __tablet_cell_bundle__ = TabletCellBundle.TAXI_DWH

        created_at = Datetime()
        a = Int(sort_key=True)

    @utils.random_yt_table
    class TableAfter(YTTable):
        __layout__ = LayeredLayout('test', 'test')  # layout будет переопределен декоратором
        __partition_scale__ = DayPartitionScale(
            partition_key='created_at'
        )
        __dynamic__ = True
        __unique_keys__ = True

        created_at = Datetime()
        a = Int(sort_key=True)

    meta_before = resolve_meta(TableBefore)
    meta_after = resolve_meta(TableAfter)

    meta_before2021_1_1 = resolve_meta(TableBefore, partition=datetime(2021, 1, 1))
    meta_before2021_1_2 = resolve_meta(TableBefore, partition=datetime(2021, 1, 2))
    create(meta_before2021_1_1)
    create(meta_before2021_1_2)

    op.set_yt_attr(meta_before2021_1_1.target_path() + f'/@{move_table.TABLET_CELL_BUNDLE}', 'wrong_bundle')
    op.set_yt_attr(meta_before2021_1_2.target_path() + f'/@{move_table.TABLET_CELL_BUNDLE}', 'wrong_bundle')

    # А это ожидаемый (праввильный) бандл
    op.set_yt_attr(meta_before.target_folder_path + f'/@{move_table.TABLET_CELL_BUNDLE}', 'expected_bundle')

    _move_yt_object(TableBefore, TableAfter, expiration_date=datetime(9999, 1, 1))

    link_path = meta_before.target_folder_path + '&'

    obj_type = get_yt_client().get_attribute(link_path, 'type')
    assert obj_type == 'link'

    expiration_time_raw = get_yt_client().get_attribute(link_path, 'expiration_time')
    expiration_time = parse_yt_datetime_attr(expiration_time_raw)
    assert expiration_time == datetime(9999, 1, 1)

    assert dop.is_table_mounted(meta_before.target_folder_path)  # Доступаемся до таблицы по старой мете
    assert dop.is_table_mounted(meta_after.target_folder_path)  # По новой мете

    # И по старой и по новой мете доступны таблицы
    lst1 = list(get_yt_client().search(meta_before.target_folder_path, node_type=["table"]))
    lst2 = list(get_yt_client().search(meta_after.target_folder_path, node_type=["table"]))
    assert len(lst1) == 2
    assert len(lst2) == 2
    assert (list(map(lambda x: x.rsplit('/', maxsplit=1)[1], lst1)) ==
            list(map(lambda x: x.rsplit('/', maxsplit=1)[1], lst2))
    )

    # Проверяем, что бандл появился в соответствии с атрибутом __tablet_cell_bundle__
    meta_after2021_1_1 = resolve_meta(TableAfter, partition=datetime(2021, 1, 1))
    meta_after2021_1_2 = resolve_meta(TableAfter, partition=datetime(2021, 1, 2))

    assert get_yt_client().get_attribute(
        meta_after2021_1_1.target_path(), move_table.TABLET_CELL_BUNDLE) == 'expected_bundle'
    assert get_yt_client().get_attribute(
        meta_after2021_1_2.target_path(), move_table.TABLET_CELL_BUNDLE) == 'expected_bundle'
    # Проверка идемпотентности
    _move_yt_object(TableBefore, TableAfter, expiration_date=datetime(9999, 1, 1))
