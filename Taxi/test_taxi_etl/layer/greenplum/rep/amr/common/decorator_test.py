import pytest
import mock
import dmp_suite.greenplum as gp
import connection.greenplum as gp_con
from test_dmp_suite.greenplum import utils

from taxi_etl.layer.greenplum.rep.amr.common.table import (
    agg_tariff_zone_cur_tariff_class_metric_table, agg_tariff_zone_cur_tariff_class_metric_view
)
from taxi_etl.layer.greenplum.rep.amr.common.source import TimeType, Scales
from . import tables


@pytest.mark.parametrize(
    "time_type,scale,table_expected", [
        (TimeType.LCL, Scales.DAY, tables.TableLclDaily),
        (TimeType.MSK, Scales.MONTH, tables.TableMskMonthly),
    ]
)
def test_agg_tariff_zone_cur_tariff_class_metric_table(time_type, scale, table_expected):
    @agg_tariff_zone_cur_tariff_class_metric_table(
        time_type=time_type,
        scale=scale,
        fields=tables.Fields,
    )
    class TableDecorated(gp.GPTable):
        __layout__ = utils.TestLayout('table_decorated')

    meta_decorated = gp.GPMeta(TableDecorated)
    meta_expected = gp.GPMeta(table_expected)

    assert TableDecorated.__doc__ == table_expected.__doc__
    assert meta_decorated.distribution.keys == meta_expected.distribution.keys

    assert meta_decorated.partition_scale.__class__ == meta_expected.partition_scale.__class__
    assert meta_decorated.partition_scale.partition_key == meta_expected.partition_scale.partition_key
    assert meta_decorated.partition_scale._start == meta_expected.partition_scale._start
    assert meta_decorated.partition_scale._end == meta_expected.partition_scale._end

    assert meta_decorated.field_names() == meta_expected.field_names()


@mock.patch('dmp_suite.greenplum.view.settings', mock.MagicMock(return_value={'select': ['developer_mlu'], 'all': ['etl']}))
@pytest.mark.slow('gp')
def test_agg_tariff_zone_cur_tariff_class_metric_view():

    @agg_tariff_zone_cur_tariff_class_metric_table(TimeType.LCL, Scales.DAY, tables.Fields)
    class TableDaily(gp.GPTable):
        __layout__ = utils.TestLayout('table_daily')

    @agg_tariff_zone_cur_tariff_class_metric_table(TimeType.LCL, Scales.WEEK, tables.Fields)
    class TableWeekly(gp.GPTable):
        __layout__ = utils.TestLayout('table_weekly')

    @agg_tariff_zone_cur_tariff_class_metric_table(TimeType.LCL, Scales.MONTH, tables.Fields)
    class TableMonthly(gp.GPTable):
        __layout__ = utils.TestLayout('table_monthly')

    @agg_tariff_zone_cur_tariff_class_metric_view(
        time_type=TimeType.LCL,
        fields=tables.Fields,
        tables={
            Scales.DAY: TableDaily,
            Scales.WEEK: TableWeekly,
            Scales.MONTH: TableMonthly,
        }
    )
    class ViewDecorated(gp.GPTable):
        __layout__ = utils.TestLayout('view_lcl')

    class ViewExpected(tables.ViewLcl):
        __doc__ = tables.ViewLcl.__doc__
        __layout__ = utils.TestLayout('view_lcl')
        __query__ = tables.SQL_TEMPLATE
        __tables__ = {
            'table_daily': TableDaily,
            'table_weekly': TableWeekly,
            'table_monthly': TableMonthly,
        }

    with gp_con._get_default_connection() as connection, connection.cursor() as cur:
        decorated_sql = ViewDecorated().get_sql(with_drop_statement=False).as_string(cur)
        expected_sql = ViewExpected().get_sql(with_drop_statement=False).as_string(cur)

    assert decorated_sql == expected_sql

    meta_decorated = gp.GPMeta(ViewDecorated)
    meta_expected = gp.GPMeta(ViewExpected)

    assert ViewDecorated.__doc__ == ViewExpected.__doc__
    assert meta_decorated.field_names() == meta_expected.field_names()
