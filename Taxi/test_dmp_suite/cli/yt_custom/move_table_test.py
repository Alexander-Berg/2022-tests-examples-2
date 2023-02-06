from unittest import mock

import pytest
from frozendict import frozendict

from dmp_suite.cli.yt_custom import move_table
from dmp_suite.table import OdsLayout
from dmp_suite.yt import YTTable, YTMeta, MonthPartitionScale, Datetime

non_layout_args = frozendict(
    new_layer=None,
    new_name=None,
    new_group=None,
    new_prefix_key=None,
    new_domain=None,
)


class TestTable(YTTable):
    __layout__ = OdsLayout(source='test', name='foo')
    __partition_scale__ = MonthPartitionScale('dt')
    dt = Datetime()


def cli_args(**kwargs):
    return (
        'non.exists.table.module',
        dict(non_layout_args, **kwargs)
    )


@pytest.mark.parametrize('cli_args, expected_new_path', [
    (
        cli_args(new_name='foo2'),
        '//dummy/ods/test/foo2',
    ),
    (
        cli_args(new_layer='cdm', new_name='foo2'),
        '//dummy/cdm/test/foo2',
    ),
    (
        cli_args(new_group='bar'),
        '//dummy/ods/bar/foo',
    ),
])
def test_to_migration_entity(cli_args, expected_new_path):
    old_path = '//dummy/ods/test/foo'
    table_patch = mock.patch(
        'dmp_suite.cli.yt_custom.move_table.inspect_utils.get_object_by_path',
        return_value=TestTable
    )

    with table_patch:
        entity = move_table.to_migration_entity(cli_args)
        assert entity.old_paths == [old_path]
        assert entity.new_paths == [expected_new_path]
        assert YTMeta(entity.old_table_cls).target_path_wo_partition == old_path
        assert YTMeta(entity.new_table_cls).target_path_wo_partition == expected_new_path
        assert entity.new_table_cls.__layout__ is entity.new_layout
