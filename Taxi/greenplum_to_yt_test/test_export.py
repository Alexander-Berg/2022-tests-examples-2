from datetime import timedelta
from decimal import Decimal

import mock
import pytest

from connection import greenplum as gp
from connection.yt import get_yt_client
from dmp_suite import yt
from dmp_suite.ctl import CTL_LAST_LOAD_DATE
from dmp_suite.exceptions import DWHError
from dmp_suite.export.greenplum_to_yt.decorators import greenplum_to_yt_table
from dmp_suite.export.greenplum_to_yt.greenplum_to_yt import gp_to_yt_source
from dmp_suite.greenplum import GPMeta
from dmp_suite.table import Sla
from dmp_suite.task.execution import run_task
from dmp_suite.yt.dyntable_operation.dynamic_table_loaders import PostgreSqlDynamicIncrementLoader
from dmp_suite.yt.operation import read_yt_table
from dmp_suite.yt.task.etl.transform import replace_by_snapshot
from .expected import (
    YTExportSnapshotExpected,
    YTExportYearPartitionScaleExpected,
    YTExportMonthPartitionScaleExpected,
    YTExportDayPartitionScaleExpected,
    YTExportCustomExpected,
    YTExportWithKeyExpected,
    YTExportViewExpected,
    YTExportExpectedWNewCol,
    YTExportExpectedStatic,
    YTExportSlaSnapshotExpected,
)
from .tables import (
    GPSourceTable,
    GPToYTTable,
    GPToYTTableExcluded,
    GPExportSnaphotTest,
    GPExportMonthPartitionScaleTest,
    GPExportYearPartitionScaleTest,
    GPExportDayPartitionScaleTest,
    GPExportWithKeyTest,
    GPViewTest,
    YTSnaphotTest,
    YTSnaphotCustomTest,
    YTWithKeyTest,
    YTYearPartitionScaleTest,
    YTFromViewTest,
    YTStaticTest,
    GPExportSlaSnapshotTest,
    GPNativeDatesTest,
    YTNativeDateTest,
    GPDecimalTest,
    YTDecimalTest,
)
from .test_gp_to_yt import _prepare_gp_table


TEST_DATA = [
    dict(id=0, created_at='2018-12-01 09:30:00.000000', value='abcdefg', value_2=11.0, value_arr=['a', 'b', 'c']),
    dict(id=0, created_at='2019-06-01 09:30:00.000000', value='abc', value_2=1.0, value_arr=['a', 'b', 'c']),
    dict(id=1, created_at='2020-01-01 08:00:00.000000', value='bcd', value_2=1.0, value_arr=['a', 'b', 'c']),
    dict(id=2, created_at='2020-01-01 09:00:00.000000', value='cde', value_2=2.0, value_arr=['a', 'b', 'c']),
    dict(id=3, created_at='2020-01-13 09:00:00.000000', value='efg', value_2=2.0, value_arr=['a', 'b', 'c']),
    dict(id=4, created_at=None, value=None, value_2=0.0, value_arr=['a', 'b', 'c']),
    dict(id=5, created_at='2020-02-03 05:00:00.000000', value='gjk', value_2=2.0, value_arr=['a', 'b', 'c']),
    dict(id=0, created_at='9999-12-31 23:59:59.000000', value='verylongperiod', value_2=42.0, value_arr=['a', 'b', 'c'])
]


def select_rows(meta):
    sql = 'id, created_at, value, value_2, value_arr from [{}] '.format(meta.target_path())
    return get_yt_client().select_rows(sql)


def select_rows_excluded(meta):
    sql = 'id, created_at, value, value_2 from [{}] '.format(meta.target_path())
    return get_yt_client().select_rows(sql)


@pytest.mark.slow('gp')
@mock.patch(
    "dmp_suite.yt.dyntable_operation.dynamic_table_loaders.get_ctl",
    mock.MagicMock(),
)
def test_export():
    gp_meta = GPMeta(GPSourceTable)

    with gp.connection.transaction():
        gp.connection.create_table(GPSourceTable)
        gp.connection.insert(GPSourceTable, TEST_DATA)

    PostgreSqlDynamicIncrementLoader(
        'greenplum.connections.ritchie',
        GPToYTTable,
        update_fields=['created_at'],
        source_table=gp_meta.table_full_name,
        update_from='2019-02-01 08:00:00.000000',
        update_to='2020-02-03 06:00:00.000000',
    ).load()

    actual = list(select_rows(yt.YTMeta(GPToYTTable)))

    expected = [
        dict(id=0, created_at='2019-06-01 09:30:00', value='abc', value_2=1.0, value_arr=['a', 'b', 'c']),
        dict(id=1, created_at='2020-01-01 08:00:00', value='bcd', value_2=1.0, value_arr=['a', 'b', 'c']),
        dict(id=2, created_at='2020-01-01 09:00:00', value='cde', value_2=2.0, value_arr=['a', 'b', 'c']),
        dict(id=3, created_at='2020-01-13 09:00:00', value='efg', value_2=2.0, value_arr=['a', 'b', 'c']),
        dict(id=5, created_at='2020-02-03 05:00:00', value='gjk', value_2=2.0, value_arr=['a', 'b', 'c']),
    ]

    assert expected == actual


@pytest.mark.slow('gp')
@mock.patch(
    "dmp_suite.yt.dyntable_operation.dynamic_table_loaders.get_ctl",
    mock.MagicMock(),
)
def test_export_exclude():
    gp_meta = GPMeta(GPSourceTable)

    with gp.connection.transaction():
        gp.connection.create_table(GPSourceTable)
        gp.connection.insert(GPSourceTable, TEST_DATA)

    PostgreSqlDynamicIncrementLoader(
        'greenplum.connections.ritchie',
        GPToYTTableExcluded,
        update_fields=['created_at'],
        source_table=gp_meta.table_full_name,
        update_from='2019-02-01 08:00:00.000000',
        update_to='2020-02-03 06:00:00.000000',
    ).load()

    actual = list(select_rows_excluded(yt.YTMeta(GPToYTTable)))

    expected = [
        dict(id=0, created_at='2019-06-01 09:30:00', value='abc', value_2=1.0),
        dict(id=1, created_at='2020-01-01 08:00:00', value='bcd', value_2=1.0),
        dict(id=2, created_at='2020-01-01 09:00:00', value='cde', value_2=2.0),
        dict(id=3, created_at='2020-01-13 09:00:00', value='efg', value_2=2.0),
        dict(id=5, created_at='2020-02-03 05:00:00', value='gjk', value_2=2.0),
    ]

    assert expected == actual


# Export meta
def compare_meta(yt_table, yt_expected_table):
    meta_expected = yt.YTMeta(yt_expected_table)
    meta = yt.YTMeta(yt_table)

    assert meta.location.folder() == meta_expected.location.folder()
    assert meta.partition_scale == meta_expected.partition_scale
    assert meta.table.get_sla() == meta_expected.table.get_sla()

    for name in meta.field_names():
        field = meta.get_field(name)
        expected_field = meta_expected.get_field(name)
        assert field == expected_field, f'Fail on {name}'


class EmptyTable(yt.ETLTable):
    pass


class YTTableWithSLa(yt.ETLTable):
    __sla__ = Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(hours=2))


@pytest.mark.parametrize(
    "user_table,gp_table,yt_export_table,kwargs", [
        (EmptyTable, GPExportSnaphotTest, YTExportSnapshotExpected, {}),
        # Sla:
        (EmptyTable, GPExportSlaSnapshotTest, YTExportSnapshotExpected, {}),
        (YTTableWithSLa, GPExportSnaphotTest, YTExportSlaSnapshotExpected, {}),
        (
            EmptyTable,
            GPExportSnaphotTest,
            YTExportSlaSnapshotExpected,
            {
                'sla': Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(hours=2))
            }
        ),
        (
            EmptyTable,
            GPExportSnaphotTest,
            YTExportCustomExpected,
            {
                'field_kwargs': {
                    'col_int': dict(sort_key=True, sort_position=3),
                    'col_dttm': dict(sort_key=True, sort_position=2),
                    'col_varchar': dict(sort_key=True, sort_position=1),
                }
            }
        ),
        (
            EmptyTable,
            GPExportSnaphotTest,
            YTExportCustomExpected,
            {
                'keys': {
                    'col_int': dict(sort_position=3),
                    'col_dttm': dict(sort_position=2),
                    'col_varchar': dict(sort_position=1),
                }
            }
        ),
        (
            EmptyTable,
            GPExportWithKeyTest,
            YTExportWithKeyExpected,
            {
                'keys': {'col_int': dict(sort_key=True, sort_position=0)},
                'field_kwargs': {
                    'col_dttm': {'type': yt.DatetimeMicroseconds},
                }
            }
        ),

        (EmptyTable, GPExportYearPartitionScaleTest, YTExportYearPartitionScaleExpected, {}),
        (EmptyTable, GPExportMonthPartitionScaleTest, YTExportMonthPartitionScaleExpected, {}),
        (EmptyTable, GPExportDayPartitionScaleTest, YTExportDayPartitionScaleExpected, {}),

        (EmptyTable, GPViewTest, YTExportViewExpected, {}),
        (
            EmptyTable,
            GPExportWithKeyTest,
            YTExportSnapshotExpected,
            {
                'field_kwargs': {
                    'col_int': dict(sort_key=False),
                }
            }
        ),
    ]
)
def test_export_meta(user_table, gp_table, yt_export_table, kwargs):
    deco = greenplum_to_yt_table(
        copy_from_table=gp_table,
        layout=yt.LayeredLayout('test', 'test'),
        location_cls=yt.YTLocation,
        **kwargs,
    )

    table = deco(user_table)

    compare_meta(yt_table=table, yt_expected_table=yt_export_table)


@pytest.mark.parametrize(
    "gp_table,yt_export_table", [
        (YTSnaphotTest, YTExportSnapshotExpected),
        (YTSnaphotCustomTest, YTExportCustomExpected),
        (YTWithKeyTest, YTExportWithKeyExpected),

        (YTYearPartitionScaleTest, YTExportYearPartitionScaleExpected),

        (YTFromViewTest, YTExportViewExpected),
        (YTStaticTest, YTExportExpectedStatic),
    ]
)
def test_export_meta_table_style(gp_table, yt_export_table):
    compare_meta(yt_table=gp_table, yt_expected_table=yt_export_table)


@pytest.mark.parametrize(
    "gp_table,kwargs", [
        (GPExportWithKeyTest, {}),
        (GPExportWithKeyTest, {'keys': {'col_int': dict()}}),
        (GPExportWithKeyTest, {'field_kwargs': {'col_int': dict(sort_key=True)}}),
    ]
)
def test_export_meta_wo_key(gp_table, kwargs):
    with pytest.raises(RuntimeError):
        @greenplum_to_yt_table(
            copy_from_table=gp_table,
            layout=yt.NotLayeredYtLayout('test', 'test'),
            **kwargs,
        )
        class Table:
            pass


def test_additional_attrs():
    additional_attrs = {'attr_1': True}

    @greenplum_to_yt_table(
        copy_from_table=GPExportSnaphotTest,
        layout=yt.LayeredLayout('test', 'test'),
        location_cls=yt.YTLocation,
        additional_attrs=additional_attrs
    )
    class Table:
        pass

    assert Table.attr_1 == additional_attrs.get('attr_1')


def test_export_meta_w_new_col():
    @greenplum_to_yt_table(
        copy_from_table=GPExportSnaphotTest,
        layout=yt.LayeredLayout('test', 'test'),
        location_cls=yt.YTLocation,
        field_kwargs={
            'new_col': {'type': yt.String}
        }
    )
    class Table(YTExportSnapshotExpected):
        new_col = yt.String()

    meta_expected = yt.YTMeta(YTExportExpectedWNewCol)
    meta = yt.YTMeta(Table)

    for name in meta.field_names():
        assert meta.get_field(name) == meta_expected.get_field(name)


def test_export_meta_partition_scale_twice():
    with pytest.raises(DWHError):
        @greenplum_to_yt_table(
            copy_from_table=GPExportSnaphotTest,
            layout=yt.LayeredLayout('test', 'test'),
            location_cls=yt.YTLocation,
            partition_scale=yt.MonthPartitionScale("utc_created_dttm"),
            **{},
        )
        class Table(yt.ETLTable):
            __partition_scale__ = yt.MonthPartitionScale("utc_created_dttm")
            utc_created_dttm = yt.Datetime()


@pytest.mark.slow('gp')
@pytest.mark.parametrize(
    'small_table',
    [
        False,
        True,
    ]
)
def test_gp_to_yt_native_dates(small_table):
    """
    Тест проверяет, что значения дат Greenplum успешно конвертируются
    в (нативные) даты YT при использовании `gp_to_yt_source` для обоих
    значений аргумента `small_table`. Т.к. `gp_to_yt_source` использует
    GPTransfer для передачи данных между GP и YT, то проверяется также
    и его поведение.
    """

    data = [
        {'col_int': 1, 'col_dt': "2010-10-10", 'col_dttm': "2010-10-10T12:13:14"},
        {'col_int': 2, 'col_dt': "2010-10-11", 'col_dttm': "2010-10-11T12:13:14"},
        {'col_int': 3, 'col_dt': "2010-10-12", 'col_dttm': "2010-10-12T12:13:14"},
        {'col_int': 4, 'col_dt': "2010-10-13", 'col_dttm': "2010-10-13T12:13:14"},
    ]

    with _prepare_gp_table(GPNativeDatesTest, data):

        task = replace_by_snapshot(
            "test_gp_to_yt_native_dates",
            source=gp_to_yt_source(
                GPNativeDatesTest,
                small_table=small_table,
            ),
            target_table=YTNativeDateTest,
        )
        run_task(task)

        yt_data = read_yt_table(yt.resolve_meta(YTNativeDateTest).target_path())

        assert [
            {'col_int': 1, 'col_dt': 14_892, 'col_dttm': 1_286_712_794},
            {'col_int': 2, 'col_dt': 14_893, 'col_dttm': 1_286_799_194},
            {'col_int': 3, 'col_dt': 14_894, 'col_dttm': 1_286_885_594},
            {'col_int': 4, 'col_dt': 14_895, 'col_dttm': 1_286_971_994},
        ] == list(yt_data)



@pytest.mark.slow('gp')
def test_gp_to_yt_native_dates():
    """
    Тест проверяет, что значения Numeric успешно конвертируются
    в Decimal тип YT при использовании `gp_to_yt_source`. Так как
    `gp_to_yt_source` использует GPTransfer для передачи данных
    между GP и YT, то проверяется также и его поведение.
    """

    # Внимание:
    # На данный момент прямая передача Numeric в Decimal не
    # поддержана в GPTransfer, поэтому и тестируется только
    # режим передачи через tsv.

    data = [
        {'col_int': 1, 'col_decimal': '12.345'},
        {'col_int': 2, 'col_decimal': '0.94'},
        {'col_int': 3, 'col_decimal': '1.5'},
    ]

    with _prepare_gp_table(GPDecimalTest, data):

        task = replace_by_snapshot(
            "test_gp_to_yt_native_dates",
            source=gp_to_yt_source(
                GPDecimalTest,
                small_table=False,
            ),
            target_table=YTDecimalTest,
        )
        run_task(task)

        yt_data = read_yt_table(yt.resolve_meta(YTDecimalTest).target_path())
        yt_data = [
            {
                'col_int': r['col_int'],
                'col_decimal': YTDecimalTest.col_decimal.deserializer(r['col_decimal']),
            }
            for r in yt_data
        ]

        assert [
            {'col_int': 2, 'col_decimal': Decimal('0.94')},
            {'col_int': 3, 'col_decimal': Decimal('1.5')},
            {'col_int': 1, 'col_decimal': Decimal('12.345')},
        ] == list(yt_data)
