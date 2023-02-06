import pytest

import dmp_suite.yt as yt
import dmp_suite.yt.operation as op
from connection.yt import get_yt_client
from dmp_suite.exceptions import DWHError
from test_dmp_suite.yt.utils import random_yt_table


@pytest.mark.slow
def test_write_yt_table():
    with op.get_temp_table() as tmp:
        op.write_yt_table(tmp, [dict(a=1, b=2)])
        assert list(op.read_yt_table(tmp)) == [dict(a=1, b=2)]
        op.write_yt_table(tmp, [dict(a=1, b=3)])
        assert list(op.read_yt_table(tmp)) == [dict(a=1, b=3)]
        op.write_yt_table(tmp, [dict(a=1, b=2)], append=True)
        assert list(op.read_yt_table(tmp)) == [dict(a=1, b=3), dict(a=1, b=2)]
        op.write_yt_table(tmp, [dict(a=1, b=3)])
        assert list(op.read_yt_table(tmp)) == [dict(a=1, b=3)]
        # legacy
        path = op.get_yt_path(table_name=tmp, append=True)
        op.write_yt_table(path, [dict(a=1, b=4)])
        assert list(op.read_yt_table(tmp)) == [dict(a=1, b=3), dict(a=1, b=4)]


@pytest.mark.slow
def test_copy_yt_node_static_table():
    @random_yt_table
    class DummyStaticSourceTable(yt.YTTable):
        id = yt.String()
        number = yt.Int()
    source_meta = yt.resolve_meta(DummyStaticSourceTable)

    @random_yt_table
    class DummyStaticTargetTable(yt.YTTable):
        id = yt.String()
        number = yt.Int()
    target_meta = yt.resolve_meta(DummyStaticTargetTable)

    data = [{'id': '10', 'number': 500}]

    op.init_yt_table(source_meta.target_path(), source_meta.attributes())
    op.write_yt_table(source_meta.target_path(), data)
    op.copy_yt_node(
        source_path=source_meta.target_path(),
        target_path=target_meta.target_path(),
        force=True,
        recursive=True,
    )
    assert data == list(op.read_yt_table(target_meta.target_path()))


@pytest.mark.slow
def test_copy_yt_node_partitioned_table():
    @random_yt_table
    class DummyPartitionedSourceTable(yt.YTTable):
        __partition_scale__ = yt.DayPartitionScale('date')

        id = yt.Int(sort_key=True)
        date = yt.Datetime()
    source_meta = yt.resolve_meta(DummyPartitionedSourceTable)

    @random_yt_table
    class DummyPartitionedTargetTable(yt.YTTable):
        __partition_scale__ = yt.DayPartitionScale('date')

        id = yt.Int(sort_key=True)
        date = yt.Datetime()
    target_meta = yt.resolve_meta(DummyPartitionedTargetTable)

    data = [{'id': 25, 'date': '2021-04-04'}, {'id': 5, 'date': '2021-08-08'}]
    for row in data:
        op.init_yt_table(
            yt.resolve_meta(DummyPartitionedSourceTable, row['date']).target_path(),
            source_meta.attributes(),
        )
        op.write_yt_table(
            yt.resolve_meta(DummyPartitionedSourceTable, row['date']).target_path(),
            [row],
        )

    op.copy_yt_node(
        source_path=source_meta.target_folder_path,
        target_path=target_meta.target_folder_path,
        force=True,
        recursive=True,
    )

    for row in data:
        assert [row] == list(op.read_yt_table(
            yt.resolve_meta(DummyPartitionedTargetTable, row['date']).target_path()
        ))

    assert op.get_yt_children(source_meta.target_folder_path, absolute=False) \
           == op.get_yt_children(target_meta.target_folder_path, absolute=False)


@pytest.mark.slow
def test_copy_yt_node_dynamic_table():
    @random_yt_table
    class DummyDynamicSourceTable(yt.YTTable):
        __dynamic__ = True
        id = yt.String(sort_key=True)
        number = yt.Int()
    source_meta = yt.resolve_meta(DummyDynamicSourceTable)

    @random_yt_table
    class DummyDynamicTargetTable(yt.YTTable):
        __dynamic__ = True
        id = yt.String(sort_key=True)
        number = yt.Int()
    target_meta = yt.resolve_meta(DummyDynamicTargetTable)

    ytc = get_yt_client()

    data = [{'id': '50', 'number': 10}]

    op.init_yt_table(source_meta.target_path(), source_meta.attributes())

    ytc.mount_table(source_meta.target_path(), sync=True)
    ytc.insert_rows(source_meta.target_path(), data)
    ytc.unmount_table(source_meta.target_path(), sync=True)

    op.copy_yt_node(
        source_path=source_meta.target_path(),
        target_path=target_meta.target_path(),
        force=True,
        recursive=True,
        mount=False,
    )

    assert ytc.get_attribute(source_meta.target_path(), attribute='tablet_state') == 'unmounted'
    assert ytc.get_attribute(target_meta.target_path(), attribute='tablet_state') == 'unmounted'
    ytc.mount_table(target_meta.target_path(), sync=True)
    assert data == list(op.read_yt_table(target_meta.target_path()))
    ytc.unmount_table(target_meta.target_path(), sync=True)


@pytest.mark.slow
def test_copy_yt_node_exception():
    with pytest.raises(ValueError):
        op.copy_yt_node(
            source_path='//home/taxi-dwh-dev/DoIExist!?',
            target_path='//home/taxi-dwh-dev/iDo!(not)',
        )


@pytest.mark.slow
def test_init_temp_yt_table_only_in_transaction():
    with pytest.raises(DWHError):
        op.init_temp_yt_table(None)

    with get_yt_client().Transaction():
        op.init_temp_yt_table(None)
