import inspect
import os

import pytest

import sources_root
from dmp_suite import yt
from dmp_suite import table as base_table
from dmp_suite.replication.meta.dmp_integration import (
    errors, extractors, rule_facade, table, yt_target_proxy,
)
from dmp_suite.yt import table as yt_table

YAMLS_PATH = os.path.join(
    sources_root.SOURCES_ROOT,
    'dmp_suite/test_dmp_suite/replication/replication_yaml',
)


class ReplicationTargetProxyTest(yt_target_proxy.BaseReplicationTargetProxy):
    def __init__(
            self,
            rule_path: str,
            destination_name: str,
            *,
            check_path_convention: bool = True,
    ):
        source_name, rule_filename = os.path.split(rule_path)
        rule_path = os.path.join(YAMLS_PATH, source_name, rule_filename)
        rule = rule_facade.construct_from_rule_yaml(
            rule_path, destination_name,
        )
        super().__init__(rule, destination_name, check_path_convention=check_path_convention)


@pytest.mark.parametrize('path, partitioned, check_convention, expected', [
    ('', True, True, errors.InvalidPathError),
    ('/', True, True, errors.InvalidPathError),
    ('///', True, True, errors.InvalidPathError),
    ('raw/eda!/order', True, True, errors.InvalidPathError),
    ('raw/eda//order', True, True, errors.InvalidPathError),

    # conventional paths with partitions
    ('raw/eda/order', True, True, ('raw', 'eda', 'order')),
    ('raw/eda/order2', True, True, ('raw', 'eda', 'order2')),
    ('/raw/eda/order/', True, True, ('raw', 'eda', 'order')),
    ('etl/raw_history/eda/order', True, True, ('etl/raw_history', 'eda', 'order')),
    ('raw/eda/order/order', True, True, errors.InvalidPathError),
    ('raw/eda/bigfood/order', True, True, errors.InvalidPathError),
    ('raw/eda/bigfood/april/order/order', True, True, errors.InvalidPathError),

    # conventional paths without partitions
    ('raw/eda/order/order', False, True, ('raw', 'eda', 'order')),
    ('etl/raw_history/eda/order/order', False, True, ('etl/raw_history', 'eda', 'order')),
    ('raw/eda/bigfood/april/order', False, True, errors.InvalidPathError),
    ('raw/eda/bigfood/april/order/order', False, True, errors.InvalidPathError),
    ('raw/eda/order', False, True, errors.InvalidPathError),

    # non-conventional paths with partitions
    ('raw/eda/order', True, False, ('raw', 'eda', 'order')),
    ('raw/eda/order2', True, False, ('raw', 'eda', 'order2')),
    ('/raw/eda/order/', True, False, ('raw', 'eda', 'order')),
    ('raw/eda/bigfood/april/order/order', True, False, ('raw', 'eda/bigfood/april/order', 'order')),
    ('raw/eda/bigfood/order', True, False, ('raw', 'eda/bigfood', 'order')),
    ('raw/eda/order/order', True, False, ('raw', 'eda/order', 'order')),
    ('raw/eda/order/order2/', True, False, ('raw', 'eda/order', 'order2')),
    ('etl/raw_history/eda/order', True, False, ('etl/raw_history', 'eda', 'order')),
    ('etl/raw_history/eda/bigfood/order2/order2', True, False, ('etl/raw_history', 'eda/bigfood/order2', 'order2')),
    ('raw/eda//order', True, False, errors.InvalidPathError),
    ('raw/order', True, False, errors.InvalidPathError),

    # non-conventional paths without partitions
    ('raw/eda/order/order', False, False, ('raw', 'eda', 'order')),
    ('raw/eda/bigfood/april/order/order', False, False, ('raw', 'eda/bigfood/april', 'order')),
    ('etl/raw_history/eda/order/order', False, False, ('etl/raw_history', 'eda', 'order')),
    ('etl/raw_history/eda/order2/order2', False, False, ('etl/raw_history', 'eda', 'order2')),
    ('raw/eda/order', False, False, errors.InvalidPathError),
    ('etl/raw_history/eda/order/order2', False, False, errors.InvalidPathError),
])
def test_path_parsing(path, partitioned, check_convention, expected):
    if inspect.isclass(expected) and issubclass(expected, Exception):
        with pytest.raises(expected):
            yt_target_proxy.parse_path(
                path=path,
                partitioned=partitioned,
                check_path_convention=check_convention,
            )
    else:
        assert yt_target_proxy.parse_path(
            path=path,
            partitioned=partitioned,
            check_path_convention=check_convention,
        ) == expected

        layer, group, name = expected

        class DummyTable(yt_table.YTTable):
            __location_cls__ = yt_table.YTLocation
            __layout__ = yt_table.DeprecatedLayeredYtLayout(
                prefix_key='eda_new',
                layer=layer,
                group=group,
                name=name,
            )
            id = yt_table.Int(sort_key=True, sort_position=0, comment='id')
            utc_created_dttm = yt_table.Datetime(comment='Дата создания в UTC')

        if partitioned:
            DummyTable.__partition_scale__ = yt.YearPartitionScale('utc_created_dttm')

        meta = yt.YTMeta(DummyTable)
        assert meta.rel_path_wo_partition == path.strip('/')


def test_error_on_non_yt_destination():
    with pytest.raises(errors.DestinationTypeNotSupportedError):
        class DummyTable(table.ReplicationTable):
            __replication_target__ = ReplicationTargetProxyTest(
                'test_source/test_rule_w_ext_destination.yaml',
                'test_rule_w_ext_destinations_raw_ext',
            )


class ReplicationStaticTable(table.ReplicationTable):
    __replication_target__ = ReplicationTargetProxyTest(
        'test_source/test_rule_w_yt_static_destination.yaml',
        'test_rule_w_yt_static_destination_raw',
    )


class ReplicationDynamicTable(table.ReplicationTable):
    __replication_target__ = ReplicationTargetProxyTest(
        'test_source/test_rule_w_yt_destination.yaml',
        'test_rule_w_yt_destination_raw',
    )


class ReplicationAutoRawTable(table.ReplicationTable):
    __replication_target__ = ReplicationTargetProxyTest(
        'test_source/test_rule_autoraw.yaml',
        'test_rule_autoraw_destination',
    )


def test_table_with_inconvenient_path():
    class DummyTable(table.ReplicationTable):
        __replication_target__ = ReplicationTargetProxyTest(
            'test_source/test_rule_inconvenient_path.yaml',
            'test_rule_inconvenient_path_destination',
            check_path_convention=False,
        )

    assert DummyTable.__layout__ == yt_table.DeprecatedLayeredYtLayout(
        prefix_key='eda_new',
        layer='test_layer',
        group='test_group/nested_folder/one_more_folder',
        name='dynamic',
    )

    class DummyTable(table.ReplicationTable):
        __replication_target__ = ReplicationTargetProxyTest(
            'test_source/test_rule_inconvenient_path.yaml',
            'test_rule_inconvenient_path_no_patition_destination',
            check_path_convention=False,
        )

    assert DummyTable.__layout__ == yt_table.DeprecatedLayeredYtLayout(
        prefix_key='eda_new',
        layer='test_layer',
        group='test_group/nested_folder/more',
        name='dynamic',
    )

    class DummyTable(table.ReplicationTable):
        __replication_target__ = ReplicationTargetProxyTest(
            'test_source/test_rule_inconvenient_path.yaml',
            'test_rule_inconvenient_path_raw_hist_destination',
            check_path_convention=False,
        )

    assert DummyTable.__layout__ == yt_table.DeprecatedLayeredYtLayout(
        prefix_key='eda_new',
        layer='etl/raw_history',
        group='test_group/nested_folder/one_more_folder',
        name='dynamic',
    )

    class DummyTable(table.ReplicationTable):
        __replication_target__ = ReplicationTargetProxyTest(
            'test_source/test_rule_inconvenient_path.yaml',
            'test_rule_inconvenient_path_raw_hist_no_partition_destination',
            check_path_convention=False,
        )

    assert DummyTable.__layout__ == yt_table.DeprecatedLayeredYtLayout(
        prefix_key='eda_new',
        layer='etl/raw_history',
        group='test_group/nested_folder/another_folder',
        name='dynamic',
    )
    assert DummyTable.__partition_scale__ is None


def test_table_with_invalid_path():
    with pytest.raises(errors.InvalidPathError):
        class DummuTable(table.ReplicationTable):
            __replication_target__ = ReplicationTargetProxyTest(
                'test_source/test_rule_invalid_path.yaml',
                'test_rule_invalid_path_destination',
            )


def test_autoraw_table_creation():
    assert_tables_are_equal(ReplicationAutoRawTable, ReplicationDynamicTable)
    assert_tables_are_equal(ReplicationAutoRawTable, DmpDynamicTable)


def test_autoraw_extractors_creation():
    repl_legacy_extractors = extractors.from_replication_table(
        ReplicationDynamicTable,
    )
    autoraw_extractors = extractors.from_replication_table(
        ReplicationAutoRawTable,
    )
    assert repl_legacy_extractors.keys() == autoraw_extractors.keys()
    for name in repl_legacy_extractors:
        legacy_extractor = repl_legacy_extractors[name]
        autoraw_extractor = autoraw_extractors[name]
        assert (
                inspect.signature(legacy_extractor)
                == inspect.signature(autoraw_extractor)
        )


class ReplicationShardTable(table.ReplicationTable):
    __replication_target__ = ReplicationTargetProxyTest(
        'test_source/test_rule_shard.yaml',
        'test_rule_shard_destination',
    )


class ReplicationNoShardTable(table.ReplicationTable):
    __replication_target__ = ReplicationTargetProxyTest(
        'test_source/test_rule_no_shard.yaml',
        'test_rule_no_shard_destination',
    )

@pytest.mark.parametrize(
    'cls, shards_num',
    (
        (ReplicationShardTable, 8),
        (ReplicationAutoRawTable, 1),
        (ReplicationNoShardTable, 1),
    )
)
def test_shard_information(cls, shards_num):
    assert cls.__replication_target__.rule_facade.rule.queue_data.shards_num == shards_num


class DmpStaticTable(yt_table.YTTable):
    """Тестовая статическая YT таблица"""

    __location_cls__ = yt_table.YTLocation
    __layout__ = yt_table.DeprecatedLayeredYtLayout(
        prefix_key='eda_new',
        layer='test_layer',
        group='test_group',
        name='static',
    )

    __compression_level__ = 'normal'
    __unique_keys__ = True
    __partition_scale__ = None
    __dynamic__ = False
    __atomicity__ = yt.Atomicity.FULL
    __tablet_cell_bundle__ = yt.TabletCellBundle.INHERIT

    id = yt_table.Int(sort_key=True, sort_position=0, comment='id')
    doc = yt_table.Any(comment='Все поля записи на источнике')


class DmpDynamicTable(yt_table.YTTable):
    """Тестовая динамическая YT таблица"""

    __layout__ = yt_table.DeprecatedLayeredYtLayout(
        prefix_key='eda_new',
        layer='test_layer',
        group='test_group',
        name='dynamic',
    )

    __compression_level__ = 'normal'
    __unique_keys__ = True
    __partition_scale__ = yt_table.ShortYearPartitionScale('utc_created_dttm')
    __dynamic__ = True
    __atomicity__ = yt.Atomicity.FULL
    __tablet_cell_bundle__ = yt.TabletCellBundle.INHERIT
    __enable_dynamic_store_read__ = True

    id = yt_table.Int(sort_key=True, sort_position=0, comment='id')
    id2 = yt_table.Int(sort_key=True, sort_position=1, comment='id2')
    utc_created_dttm = yt_table.Datetime(comment='Дата создания в UTC')
    doc = yt_table.Any(comment='Все поля записи на источнике')
    etl_updated = yt_table.Datetime(comment='Время загрузки/изменения записи')


def test_is_subclass():
    assert issubclass(table.ReplicationTable, yt_table.YTTable)


def test_all_yt_table_attributes_are_covered():
    class Dummy:
        pass

    ignored_attrs = (
        set(dir(Dummy))
        .union({'__annotations__', '__sla__'})
        .union(set(dir(base_table.TableMeta)))
        .difference({'__doc__'})
    )

    dmp_attrs = set(dir(yt_table.YTTable)) - ignored_attrs
    replication_attrs = set(dir(ReplicationStaticTable)) - ignored_attrs

    not_covered_attrs = dmp_attrs - replication_attrs

    assert not not_covered_attrs

    for attr_name in dmp_attrs:
        dmp_attr = getattr(yt_table.YTTable, attr_name)

        try:
            replication_attr = getattr(ReplicationStaticTable, attr_name)
        except errors.NotSupportedError:
            continue

        if callable(dmp_attr):
            assert callable(replication_attr)
            assert (
                    inspect.signature(dmp_attr)
                    == inspect.signature(replication_attr)
            )
            continue

        raw_replication_attr = type.__getattribute__(
            ReplicationStaticTable, attr_name,
        )
        assert isinstance(raw_replication_attr, table.ProxyAttribute), f'Failed on {attr_name}'


def assert_tables_are_equal(first, second):
    assert first.__layout__ == second.__layout__
    assert first.__location_cls__ == second.__location_cls__
    assert first.__compression_level__ == second.__compression_level__
    assert first.__unique_keys__ == second.__unique_keys__
    assert first.__dynamic__ == second.__dynamic__
    assert first.__doc__ == second.__doc__
    assert first.__partition_scale__ == second.__partition_scale__
    assert first.__enable_dynamic_store_read__ == second.__enable_dynamic_store_read__

    first_instance = first()
    second_instance = second()

    assert first_instance.field_names() == second_instance.field_names()
    assert list(first_instance.fields()) == list(second_instance.fields())


@pytest.mark.parametrize(
    'first_table,second_table',
    [
        (DmpStaticTable, ReplicationStaticTable),
        (DmpDynamicTable, ReplicationDynamicTable),
    ],
)
def test_tables(first_table, second_table):
    assert_tables_are_equal(first_table, second_table)
