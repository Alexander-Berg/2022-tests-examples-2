from datetime import timedelta
from functools import partial

import mock
import pytest

from dmp_suite import greenplum as gp
from dmp_suite import yt
from dmp_suite.ctl import CTL_LAST_LOAD_DATE
from dmp_suite.export.yt_to_greenplum import yt_to_greenplum_table
from dmp_suite.greenplum.connection import _as_sql
from dmp_suite.table import Sla
from .expected import (
    GPExportExpected, GPExportDayPartitionExpected, GPExportMonthPartitionExpected, GPExportYearPartitionExpected,
    GPExportDayPartitionTtlExpected, GPExportDayTablespaceTtlExpected, GPExportDayPartitionTablespaceTtlExpected,
    GPExportWithKeyExpected, GPExportArrayExpected, GPExportExpectedFullExpected, GPExportExpectedManyDistributions,
    GPExportExpectedWoDistributions, GPExportExpectedWDistribution, GPExportExpectedExcluded,
    GPExportExpectedNewColOnGP,
    GPExportSlaSnapshotExpected, GPExportExpectedTypeV3Test
)
from .tables import (
    YTExportTest, YTExportYearPartitionTest,
    YTExportTestWithKey, YTExportMonthPartitionTest, YTExportDayPartitionTest,
    YTExportShortYearPartitionTest, YTExportShortMonthPartitionTest, YTExportSlaSnapshotTest,
    YTExportTypeV3Test,
)


def test_fields_validation():
    with pytest.raises(ValueError):
        @yt_to_greenplum_table(
            copy_from_table=YTExportTest,
            field_kwargs={'not_exist_for_field_kwargs': {'type': gp.String}},
        )
        class DummyTable:
            pass

    with pytest.raises(ValueError):
        @yt_to_greenplum_table(
            copy_from_table=YTExportTest,
            keys={'not_exist_for_key': {'key': True}},
        )
        class DummyTable:
            pass

    with pytest.raises(ValueError):
        @yt_to_greenplum_table(
            copy_from_table=YTExportTest,
            exclude_fields=('not_excludable',),
        )
        class DummyTable:
            pass


@pytest.mark.parametrize(
    'kwargs',
    [
        dict(partition_start="xxx"),
        dict(partition_end="xxx"),
        dict(partition_ttl_day_cnt=1),
        dict(tablespace_ttl_day_cnt=2),
    ]
)
def test_partition_scale_raises(kwargs):
    with pytest.raises(ValueError):
        @yt_to_greenplum_table(
            copy_from_table=YTExportTest,
            partition_scale=gp.YearPartitionScale('dummy_test', start='2020-01-01'),
            **kwargs,
        )
        class DummyTable:
            pass


def test_array_raises():
    with pytest.raises(ValueError):
        @yt_to_greenplum_table(
            copy_from_table=YTExportTest,
            field_kwargs={'col_int': {'type': gp.Array}},
        )
        class DummyTable:
            pass

    # test no exception raised: fully specified gp.Array
    @yt_to_greenplum_table(
        copy_from_table=YTExportTest,
        field_kwargs={'col_int': {'type': gp.Array, 'inner_data_type': gp.Int}},
    )
    class DummyTable:
        pass

    # test no exception raised: partial
    @yt_to_greenplum_table(
        copy_from_table=YTExportTest,
        field_kwargs={'col_int': {'type': partial(gp.Array, gp.Int)}},
    )
    class DummyTable:
        pass


def test_attributes_inheritance():
    class EmptyYTTable(yt.YTTable):
        pass

    class SomeGPTable(gp.GPTable):
        test_integer_field = gp.Int(comment='me comment')

    class GPEtlTable(gp.GPEtlTable):
        pass

    @yt_to_greenplum_table(
        copy_from_table=EmptyYTTable,
    )
    class DummyTable(SomeGPTable):
        pass

    assert hasattr(DummyTable, "test_integer_field")
    assert getattr(getattr(DummyTable, "test_integer_field"), "comment") == "me comment"

    @yt_to_greenplum_table(
        copy_from_table=EmptyYTTable,
    )
    class DummyTable(GPEtlTable):
        pass

    assert hasattr(DummyTable, "_etl_processed_dttm")

    # makes a GPEtlTable from no table class
    @yt_to_greenplum_table(
        copy_from_table=EmptyYTTable,
    )
    class DummyTable:
        pass

    assert hasattr(DummyTable, "_etl_processed_dttm")


class YTTableWithSlaTest(YTExportTest):
    __sla__ = Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(hours=2))


class GPTableWithSlaTest(gp.GPTable):
    __sla__ = Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(hours=2))


class EmptyTable:
    pass


@pytest.mark.parametrize(
    "user_table,yt_table,gp_export_table,kwargs", [
        # Sla
        (EmptyTable, YTExportSlaSnapshotTest, GPExportExpected, {}),  # SLA не появляется из ниоткуда
        (EmptyTable, YTTableWithSlaTest, GPExportExpected, {}),  # SLA не копируется с YT-таблицы
        # SLA можно брать от GP-таблицы, к которой применен декоратор
        (GPTableWithSlaTest, YTExportTest, GPExportSlaSnapshotExpected, {}),
        (
            EmptyTable,
            YTExportTest,
            GPExportSlaSnapshotExpected,
            {
                'sla': Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(hours=2))
            }
        ),
        (EmptyTable, YTExportTest, GPExportExpected, {}),
        (
            EmptyTable,
            YTExportTest,
            GPExportExpected,
            {},
        ),
        (
            EmptyTable,
            YTExportTestWithKey,
            GPExportWithKeyExpected,
            dict(field_kwargs=dict(col_int=dict(key=True))),
        ),
        (
            EmptyTable,
            YTExportTestWithKey,
            GPExportWithKeyExpected,
            dict(keys=dict(col_int=dict())),
        ),
        (
            EmptyTable,
            YTExportTest,
            GPExportArrayExpected,
            dict(
                field_kwargs=dict(
                    col_int_array=dict(type=gp.Array, inner_data_type=gp.Int),
                    col_varchar_array=dict(type=gp.Array, inner_data_type=gp.String),
                )
            ),
        ),
        (
            EmptyTable,
            YTExportYearPartitionTest,
            GPExportYearPartitionExpected,
            dict(partition_start='2020-01-01'),
        ),
        (
            EmptyTable,
            YTExportShortYearPartitionTest,
            GPExportYearPartitionExpected,
            dict(partition_start='2020-01-01'),
        ),
        (
            EmptyTable,
            YTExportMonthPartitionTest,
            GPExportMonthPartitionExpected,
            dict(partition_start='2020-03-01'),
        ),
        (
            EmptyTable,
            YTExportShortMonthPartitionTest,
            GPExportMonthPartitionExpected,
            dict(partition_start='2020-03-01'),
        ),
        (
            EmptyTable,
            YTExportDayPartitionTest,
            GPExportDayPartitionExpected,
            dict(partition_start='2020-03-01', partition_end='2020-05-01'),
        ),
        (
            EmptyTable,
            YTExportDayPartitionTest,
            GPExportDayPartitionTtlExpected,
            dict(partition_ttl_day_cnt=90),
        ),
        (
            EmptyTable,
            YTExportDayPartitionTest,
            GPExportDayTablespaceTtlExpected,
            dict(tablespace_ttl_day_cnt=365),
        ),
        (
            EmptyTable,
            YTExportDayPartitionTest,
            GPExportDayPartitionTablespaceTtlExpected,
            dict(partition_ttl_day_cnt=90, tablespace_ttl_day_cnt=365),
        ),
        (
            EmptyTable,
            YTExportDayPartitionTest,
            GPExportExpected,
            dict(inherit_partition_scale=False),
        ),
        (
            EmptyTable,
            YTExportTest,
            GPExportExpectedFullExpected,
            dict(
                indexes=['Test_indexes'],
                storage_parameters=gp.StorageParameters(orientation=gp.Orientation.COLUMN),
            ),
        ),
        (
            EmptyTable,
            YTExportTest,
            GPExportExpectedManyDistributions,
            dict(distributed_by=('col_int', 'col_bigint')),
        ),
        (
            EmptyTable,
            YTExportTest,
            GPExportExpectedWDistribution,
            dict(distributed_by='col_int'),
        ),
        (
            EmptyTable,
            YTExportTest,
            GPExportExpectedWoDistributions,
            dict(distributed_by=None),
        ),
        (
            EmptyTable,
            YTExportTest,
            GPExportExpectedExcluded,
            dict(exclude_fields=('col_dttm', 'col_dttm_ms', 'col_int_array', 'col_varchar_array', 'col_json')),
        ),
        (
            EmptyTable,
            YTExportTypeV3Test,
            GPExportExpectedTypeV3Test,
            dict(keys=dict(col_int={})),
        ),
    ]
)
def test_export_meta(user_table, yt_table, gp_export_table, kwargs):
    distributed_by = kwargs.pop('distributed_by', None)

    deco = yt_to_greenplum_table(
        copy_from_table=yt_table,
        distributed_by=distributed_by,
        layout=gp.ExternalGPLayout('test', 'test'),
        location_cls=gp.ExternalGPLocation,
        **kwargs
    )

    table = deco(user_table)

    meta_expected = gp.GPMeta(gp_export_table)
    meta = gp.GPMeta(table)

    # test sql distribution
    _as_sql(meta.distribution.sql_desc)

    assert meta.distribution.keys == meta_expected.distribution.keys

    assert meta.location.full() == meta_expected.location.full()
    assert meta.indexes == meta_expected.indexes
    assert meta.storage_parameters.orientation == meta_expected.storage_parameters.orientation
    assert meta.storage_parameters.column_compression == meta_expected.storage_parameters.column_compression

    assert meta.table.get_sla() == meta_expected.table.get_sla()

    assert meta.partition_scale.__class__ == meta_expected.partition_scale.__class__
    if meta.partition_scale:
        assert meta.partition_scale.partition_key == meta_expected.partition_scale.partition_key
        assert meta.partition_scale._start == meta_expected.partition_scale._start
        assert meta.partition_scale._end == meta_expected.partition_scale._end

    with mock.patch('dmp_suite.greenplum.table.SQLDesc', mock.MagicMock()):
        for name in meta.field_names():
            field = meta.get_field(name)
            field_expected = meta_expected.get_field(name)
            assert field == field_expected


@pytest.mark.parametrize(
    "yt_table,field_kwargs", [
        (YTExportTestWithKey, {}),
    ]
)
def test_export_meta_wo_key(yt_table, field_kwargs):
    with pytest.raises(ValueError):
        @yt_to_greenplum_table(
            copy_from_table=yt_table,
            layout=gp.ExternalGPLayout('test', 'test'),
            location_cls=gp.ExternalGPLocation,
            distributed_by='col_int',
            field_kwargs=field_kwargs,
        )
        class Table:
            pass


def test_carry_gptable_attributes():
    @yt_to_greenplum_table(
        copy_from_table=YTExportTest,
        layout=gp.ExternalGPLayout('test', 'test'),
        location_cls=gp.ExternalGPLocation,
    )
    class Table(gp.GPEtlTable):
        new_col_on_GP = gp.String()

    meta_expected = gp.GPMeta(GPExportExpectedNewColOnGP)
    meta = gp.GPMeta(Table)

    with mock.patch('dmp_suite.greenplum.table.SQLDesc', mock.MagicMock()):
        for name in set(meta.field_names() + meta_expected.field_names()):
            field = meta.get_field(name)
            field_expected = meta_expected.get_field(name)
            assert field == field_expected, f'Failed for {name}'


def test_additional_attrs():
    additional_attrs = {'attr_1': True}

    @yt_to_greenplum_table(
        copy_from_table=YTExportTest,
        layout=gp.ExternalGPLayout('test', 'test'),
        location_cls=gp.ExternalGPLocation,
        additional_attrs=additional_attrs,
    )
    class Table:
        pass
    assert getattr(Table, 'attr_1') == additional_attrs.get('attr_1')


def test_keys_field_kwargs_update():
    @yt_to_greenplum_table(
        copy_from_table=YTExportTestWithKey,
        keys={'col_int': {'key': True}},
        field_kwargs={'col_int': {'type': gp.String}},
    )
    class Table1:
        pass

    @yt_to_greenplum_table(
        copy_from_table=YTExportTestWithKey,
        keys={'col_int': {'key': True, 'type': gp.String}},
    )
    class Table2:
        pass

    _result_field_1: gp.GPField = getattr(Table1, 'col_int')
    assert type(_result_field_1) is gp.String
    assert _result_field_1.key

    _result_field_2: gp.GPField = getattr(Table2, 'col_int')
    assert type(_result_field_2) is gp.String
    assert _result_field_2.key
