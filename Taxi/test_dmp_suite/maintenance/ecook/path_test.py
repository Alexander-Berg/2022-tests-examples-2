import pytest
from mock import patch

import dmp_suite.maintenance.ecook.paths as paths
from dmp_suite.datetime_utils import period
from test_dmp_suite.maintenance.ecook.table import MonthFooTable, DayFooTable, FooTable
from test_dmp_suite.maintenance.ecook.utils import use_settings_mock, WITH_DEFAULT_SETTINGS
from test_dmp_suite.maintenance.ecook.table import GPHeapTable, GPMonthPartitionTable, \
    GPListPartitionTable, GPListAndMonthPartitionTable
from dmp_suite.inspect_utils import find_tables
from dmp_suite.greenplum.hnhm import HnhmBaseTemplate, HnhmEntity
from dmp_suite.greenplum.meta import GPMeta


@patch('dmp_suite.maintenance.ecook.paths.settings', use_settings_mock(WITH_DEFAULT_SETTINGS))
def test_paths_by_yt_table():
    with pytest.raises(ValueError):
        paths.by_table(MonthFooTable)()

    result = paths.by_table(
        MonthFooTable,
        period('2019-01-30', '2019-02-15')
    )()
    expected = [
        ('//source/bar/month_foo/2019-01-01', '//dummy/bar/month_foo/2019-01-01'),
        ('//source/bar/month_foo/2019-02-01', '//dummy/bar/month_foo/2019-02-01'),
    ]
    assert expected == result

    result = paths.by_table(
        MonthFooTable,
        period('2019-02-03', '2019-02-15')
    )()
    expected = [(
        '//source/bar/month_foo/2019-02-01', '//dummy/bar/month_foo/2019-02-01'
    )]
    assert expected == result

    result = paths.by_table(
        MonthFooTable,
        period('2019-02-03 10:00:00', '2019-02-03 16:10:00')
    )()
    expected = [(
        '//source/bar/month_foo/2019-02-01', '//dummy/bar/month_foo/2019-02-01'
    )]
    assert expected == result

    result = paths.by_table(
        DayFooTable,
        period('2019-01-31', '2019-02-01')
    )()
    expected = [
        ('//source/bar/day_foo/2019-01-31', '//dummy/bar/day_foo/2019-01-31'),
        ('//source/bar/day_foo/2019-02-01', '//dummy/bar/day_foo/2019-02-01'),
    ]
    assert expected == result

    result = paths.by_table(
        DayFooTable,
        period('2019-02-03 10:00:00', '2019-02-03 16:10:00')
    )()
    expected = [
        ('//source/bar/day_foo/2019-02-03', '//dummy/bar/day_foo/2019-02-03')
    ]
    assert expected == result

    result = paths.by_table(FooTable)()
    expected = [('//source/bar/group/foo/foo', '//dummy/bar/group/foo/foo')]
    assert expected == result

    result = paths.by_table(
        FooTable,
        period('2019-02-03 10:00:00', '2019-02-03 16:10:00')
    )()
    expected = [('//source/bar/group/foo/foo', '//dummy/bar/group/foo/foo')]
    assert expected == result


@patch('dmp_suite.maintenance.ecook.paths.settings', use_settings_mock(WITH_DEFAULT_SETTINGS))
def test_folder_by_yt_table():
    result = paths.folder_by_table(MonthFooTable)()
    expected = [
        ('//source/bar/month_foo', '//dummy/bar/month_foo'),
    ]
    assert expected == result

    result = paths.folder_by_table(FooTable)()
    # by folder, because FooTable is not partitioned.
    expected = [(
        '//source/bar/group/foo/foo', '//dummy/bar/group/foo/foo'
    )]
    assert expected == result


def _get_expected_hnhm():
    hnhm_tables = find_tables(
        module='test_dmp_suite.maintenance.ecook.table',
        table_base_classes=(HnhmEntity,),
    )
    result = []
    for hnhm_table in hnhm_tables:
        result.extend(
            [
                (
                    (
                        {
                            'meta': t,
                            'name': GPMeta(t, prefix_manager=lambda x: '').table_full_name,
                            'partition': {
                                'end_dttm': '2019-02-01 00:00:00',
                                'start_dttm': '2019-01-31 00:00:00'
                            } if hnhm_table.__partition_scale__ is not None else None,
                            'subpartition': None,
                            'schema_name_prefix': GPMeta(t).prefix
                        }
                    ),
                    GPMeta(t).table_full_name,
                ) for t in hnhm_table().get_classes()
            ]
        )
    return result


def _get_hnhm_table_from_paths_result(result):
    return [i for i in result
            if isinstance(i[0], dict) and issubclass(i[0].get('meta'), HnhmBaseTemplate)]


@patch('dmp_suite.maintenance.ecook.paths.settings', use_settings_mock(WITH_DEFAULT_SETTINGS))
def test_paths_from_module():
    with pytest.raises(ValueError):
        paths.tables_from_module('test_dmp_suite.maintenance.ecook')()

    with pytest.raises(ValueError):
        paths.tables_from_module('test_dmp_suite.maintenance.ecook.table')()

    result = paths.tables_from_module(
        'test_dmp_suite.maintenance.ecook.table',
        period('2019-01-31', '2019-02-01'),
    )()

    result_hnhm = _get_hnhm_table_from_paths_result(result)
    expected_hnhm = _get_expected_hnhm()
    for items in [expected_hnhm, result_hnhm]:
        for item in items:
            item[0]['meta'] = list(item[0]['meta']().fields())

    expected = [
        ('//source/bar/day_foo/2019-01-31', '//dummy/bar/day_foo/2019-01-31'),
        ('//source/bar/day_foo/2019-02-01', '//dummy/bar/day_foo/2019-02-01'),
        ('//source/bar/group/foo/foo', '//dummy/bar/group/foo/foo'),
        ('//source/bar/month_foo/2019-01-01', '//dummy/bar/month_foo/2019-01-01'),
        ('//source/bar/month_foo/2019-02-01', '//dummy/bar/month_foo/2019-02-01'),
        (
            {
                'meta': GPHeapTable,
                'name': GPMeta(GPHeapTable, prefix_manager=lambda x: '').table_full_name,
                'partition': None,
                'subpartition': None,
                'schema_name_prefix': GPMeta(GPHeapTable).prefix
            },
            GPMeta(GPHeapTable).table_full_name,
        ),
        (
            {
                'meta': GPMonthPartitionTable,
                'name': GPMeta(GPMonthPartitionTable, prefix_manager=lambda x: '').table_full_name,
                'partition': {
                    'end_dttm': '2019-02-01 00:00:00',
                    'start_dttm': '2019-01-31 00:00:00'
                },
                'subpartition': None,
                'schema_name_prefix': GPMeta(GPMonthPartitionTable).prefix
            },
            GPMeta(GPMonthPartitionTable).table_full_name,
        ),
        (
            {
                'meta': GPListPartitionTable,
                'name': GPMeta(GPListPartitionTable, prefix_manager=lambda x: '').table_full_name,
                'partition': None,
                'subpartition': None,
                'schema_name_prefix': GPMeta(GPListPartitionTable).prefix
            },
            GPMeta(GPListPartitionTable).table_full_name,
        ),
        (
            {
                'meta': GPListAndMonthPartitionTable,
                'name': GPMeta(GPListAndMonthPartitionTable, prefix_manager=lambda x: '').table_full_name,
                'partition': None,
                'subpartition': {
                    'end_dttm': '2019-02-01 00:00:00',
                    'start_dttm': '2019-01-31 00:00:00'
                },
                'schema_name_prefix': GPMeta(GPListAndMonthPartitionTable).prefix
            },
            GPMeta(GPListAndMonthPartitionTable).table_full_name,
        )
    ] + expected_hnhm
    result.sort(key=lambda x: x[1], reverse=False)
    expected.sort(key=lambda x: x[1], reverse=False)
    assert expected == result


@patch('dmp_suite.maintenance.ecook.paths.settings', use_settings_mock(WITH_DEFAULT_SETTINGS))
def test_paths_from_module_only_yt_table():
    result = paths.tables_from_module(
        'test_dmp_suite.maintenance.ecook.table',
        period('2019-01-31', '2019-02-01'),
        without_gp_table=True
    )()
    expected = [
        ('//source/bar/day_foo/2019-01-31', '//dummy/bar/day_foo/2019-01-31'),
        ('//source/bar/day_foo/2019-02-01', '//dummy/bar/day_foo/2019-02-01'),
        ('//source/bar/group/foo/foo', '//dummy/bar/group/foo/foo'),
        ('//source/bar/month_foo/2019-01-01', '//dummy/bar/month_foo/2019-01-01'),
        ('//source/bar/month_foo/2019-02-01', '//dummy/bar/month_foo/2019-02-01')
    ]
    result.sort(key=lambda x: x[1], reverse=False)
    expected.sort(key=lambda x: x[1], reverse=False)
    assert expected == result


@patch('dmp_suite.maintenance.ecook.paths.settings', use_settings_mock(WITH_DEFAULT_SETTINGS))
def test_paths_from_module_only_gp_table():
    result = paths.tables_from_module(
        'test_dmp_suite.maintenance.ecook.table',
        period('2019-01-31', '2019-02-01'),
        without_yt_table=True
    )()

    result_hnhm = _get_hnhm_table_from_paths_result(result)
    expected_hnhm = _get_expected_hnhm()
    for items in [expected_hnhm, result_hnhm]:
        for item in items:
            item[0]['meta'] = list(item[0]['meta']().fields())

    expected = [
        (
            {
                'meta': GPHeapTable,
                'name': GPMeta(GPHeapTable, prefix_manager=lambda x: '').table_full_name,
                'partition': None,
                'subpartition': None,
                'schema_name_prefix': GPMeta(GPHeapTable).prefix
            },
            GPMeta(GPHeapTable).table_full_name,
        ),
        (
            {
                'meta': GPMonthPartitionTable,
                'name': GPMeta(GPMonthPartitionTable, prefix_manager=lambda x: '').table_full_name,
                'partition': {
                    'end_dttm': '2019-02-01 00:00:00',
                    'start_dttm': '2019-01-31 00:00:00'
                },
                'subpartition': None,
                'schema_name_prefix': GPMeta(GPMonthPartitionTable).prefix
            },
            GPMeta(GPMonthPartitionTable).table_full_name,
        ),
        (
            {
                'meta': GPListPartitionTable,
                'name': GPMeta(GPListPartitionTable, prefix_manager=lambda x: '').table_full_name,
                'partition': None,
                'subpartition': None,
                'schema_name_prefix': GPMeta(GPListPartitionTable).prefix
            },
            GPMeta(GPListPartitionTable).table_full_name,
        ),
        (
            {
                'meta': GPListAndMonthPartitionTable,
                'name': GPMeta(GPListAndMonthPartitionTable, prefix_manager=lambda x: '').table_full_name,
                'partition': None,
                'subpartition': {
                    'end_dttm': '2019-02-01 00:00:00',
                    'start_dttm': '2019-01-31 00:00:00'
                },
                'schema_name_prefix': GPMeta(GPListAndMonthPartitionTable).prefix
            },
            GPMeta(GPListAndMonthPartitionTable).table_full_name,
        )
    ] + expected_hnhm
    result.sort(key=lambda x: x[1], reverse=False)
    expected.sort(key=lambda x: x[1], reverse=False)
    assert expected == result


@patch('dmp_suite.maintenance.ecook.paths.settings', use_settings_mock(WITH_DEFAULT_SETTINGS))
def test_yt_path():
    result = paths.yt_paths('foo/foo', prefix_key='test')()
    expected = [('//source/foo/foo', '//dummy/foo/foo')]
    assert expected == result

    with pytest.raises(ValueError):
        paths.yt_paths('//home/foo')()

    result = paths.yt_paths('//home/foo', 'foo/foo', prefix_key='test')()
    expected = [('//home/foo', '//dummy/foo/foo')]
    assert expected == result

    result = paths.yt_paths('//home/foo', '//foo/foo', prefix_key='test')()
    expected = [('//home/foo', '//foo/foo')]
    assert expected == result

    result = paths.yt_paths('foo/foo', 'bar/bar', prefix_key='test')()
    expected = [('//source/foo/foo', '//dummy/bar/bar')]
    assert expected == result


@patch('dmp_suite.maintenance.ecook.paths.settings', use_settings_mock(WITH_DEFAULT_SETTINGS))
@pytest.mark.parametrize(
    'table, source_name, target_name', [
        (MonthFooTable, '//source/bar/month_foo', '//dummy/bar/month_foo'),
        (FooTable, '//source/bar/group/foo/foo', '//dummy/bar/group/foo/foo'),
    ]
)
def test_all_ctl_by_table_for_yt(table, source_name, target_name):
    expected = [
        (
            source_name,
            paths.CtlTarget('yt', target_name, param)
        )
        for param in (
            paths.CTL_LAST_LOAD_DATE_MICROSECONDS,
            paths.CTL_LAST_DDS_LOAD_DATE_MICROSECONDS,
            paths.CTL_LAST_SYNC_DATE,
            paths.CTL_LAST_LOAD_ID,
         )
    ]

    assert paths.all_ctl_by_table(table)() == expected


@patch('dmp_suite.maintenance.ecook.paths.settings', use_settings_mock(WITH_DEFAULT_SETTINGS))
def test_all_ctl_by_table_for_gp():
    from dmp_suite.greenplum import GPTable, Int
    from dmp_suite.table import SummaryLayout

    class GpTestTable(GPTable):
        __layout__ = SummaryLayout('test_table')
        id = Int(key=True)

    expected = [
        (
            'pfxvalue_summary.test_table',
            paths.CtlTarget('gp', 'dummy_pfxvalue_summary.test_table', param)
        )
        for param in (
            paths.CTL_LAST_LOAD_DATE_MICROSECONDS,
            paths.CTL_LAST_DDS_LOAD_DATE_MICROSECONDS,
            paths.CTL_LAST_SYNC_DATE,
            paths.CTL_LAST_LOAD_ID,
         )
    ]

    assert paths.all_ctl_by_table(GpTestTable)() == expected


@patch('dmp_suite.maintenance.ecook.paths.settings', use_settings_mock(WITH_DEFAULT_SETTINGS))
def test_all_ctl_by_table_for_hnhm():
    from dmp_suite.greenplum import hnhm, Int
    from dmp_suite.table import ChangeType, DdsLayout

    class HnhmTestEntity(hnhm.HnhmEntity):
        __layout__ = DdsLayout('hnhm_test_entity')

        eid = Int(change_type=ChangeType.IGNORE)

        __keys__ = [eid]

    param = paths.CTL_LAST_LOAD_DATE_MICROSECONDS
    expected = [
        (
            'pfxvalue_dds.a__hnhm_test_entity__eid__key',
            paths.CtlTarget('gp', 'dummy_pfxvalue_dds.a__hnhm_test_entity__eid__key', param)
        ),
        (
            'pfxvalue_dds.h__hnhm_test_entity',
            paths.CtlTarget('gp', 'dummy_pfxvalue_dds.h__hnhm_test_entity', param)
        ),
    ]

    assert paths.all_ctl_by_table(HnhmTestEntity)() == expected
