from unittest import mock

import pytest
from frozendict import frozendict

from dmp_suite.cli.gp import move_table
from dmp_suite.greenplum import (
    GPTable,
    GPMeta,
    MonthPartitionScale,
    Datetime,
    String,
    Int,
)
from dmp_suite.greenplum.hnhm import HnhmEntity, HnhmLink, HnhmLinkElement
from dmp_suite.table import OdsLayout, DdsLayout
from test_dmp_suite.domain.common import test_domain

non_layout_args = frozendict(
    new_layer=None,
    new_name=None,
    new_group=None,
    new_prefix_key=None,
    new_domain=None,
)


class TestTable(GPTable):
    __layout__ = OdsLayout(source='test', name='foo')
    __partition_scale__ = MonthPartitionScale('dt')
    dt = Datetime()


class TestHnhmEntity(HnhmEntity):
    __layout__ = DdsLayout(name='test_entity', domain=test_domain)
    a = String()
    b = Int()

    __keys__ = [a]


class TestHnhmLink(HnhmLink):
    __layout__ = DdsLayout(name='test_link', domain=test_domain)

    device = HnhmLinkElement(entity=TestHnhmEntity())
    app_install = HnhmLinkElement(entity=TestHnhmEntity())

    __keys__ = [app_install]


def cli_args(**kwargs):
    return (
        'non.exists.table.module',
        dict(non_layout_args, **kwargs)
    )


@pytest.mark.parametrize('cli_args, expected_new_path', [
    (
        cli_args(new_name='foo2'),
        'dummy_pfxvalue_ods_test.foo2',
    ),
    (
        cli_args(new_layer='cdm', new_name='foo2'),
        'dummy_pfxvalue_cdm_test.foo2',
    ),
    (
        cli_args(new_group='bar'),
        'dummy_pfxvalue_ods_bar.foo',
    ),
])
def test_to_migration_entity(cli_args, expected_new_path):
    old_path = 'dummy_pfxvalue_ods_test.foo'

    table_patch = mock.patch(
        'dmp_suite.cli.gp.move_table.inspect_utils.get_object_by_path',
        return_value=TestTable
    )

    with table_patch:
        entity = move_table.to_migration_entity(cli_args)
        assert entity.old_paths == [old_path]
        assert entity.new_paths == [expected_new_path]
        assert GPMeta(entity.old_table_cls).table_full_name == old_path
        assert GPMeta(entity.new_table_cls).table_full_name == expected_new_path
        assert entity.new_table_cls.__layout__ is entity.new_layout


@pytest.mark.parametrize('table, expected_path_count', [
    (
        TestHnhmEntity,
        3,
    ),
    (
        TestHnhmLink,
        1,
    ),
])
def test_hnhm_to_migration_entity(table, expected_path_count):
    cli_table_args = cli_args(new_name='foo2')
    table_patch = mock.patch(
        'dmp_suite.cli.gp.move_table.inspect_utils.get_object_by_path',
        return_value=table
    )

    with table_patch:
        entity = move_table.to_migration_entity(cli_table_args)
        assert len(entity.old_paths) == expected_path_count
        assert len(entity.new_paths) == expected_path_count
        assert entity.new_table_cls.__layout__ is entity.new_layout
