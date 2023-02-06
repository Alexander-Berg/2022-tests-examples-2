from datetime import timedelta, datetime

from dmp_suite.ctl import CTL_LAST_LOAD_DATE
from dmp_suite.greenplum import Int, String, Numeric, Datetime, Array, GPTable
from dmp_suite.export.greenplum_to_yt.decorators import greenplum_to_yt_table
from dmp_suite import greenplum as gp, yt
from dmp_suite.table import Sla, LayeredLayout
from dmp_suite.greenplum.view import View
from test_dmp_suite.greenplum import utils
from test_dmp_suite.greenplum.utils import GreenplumTestTable, external_gp_layout


class GPSourceTable(GPTable):
    __layout__ = utils.TestLayout('test')
    id = Int()
    created_at = Datetime()
    value = String()
    value_2 = Numeric()
    value_arr = Array(String)


@greenplum_to_yt_table(
    GPSourceTable,
    layout=yt.LayeredLayout('test', 'test'),
    location_cls=yt.YTLocation,
    dynamic=True,
    field_kwargs={
        'id': dict(sort_key=True, sort_position=0)
    }
)
class GPToYTTable:
    pass


@greenplum_to_yt_table(
    GPSourceTable,
    layout=yt.LayeredLayout('test', 'test'),
    location_cls=yt.YTLocation,
    dynamic=True,
    field_kwargs={
     'id': dict(sort_key=True, sort_position=0)
    },
    exclude_fields=('value_arr',)
)
class GPToYTTableExcluded:
    pass


class GPExportSnaphotTest(GreenplumTestTable):
    _etl_processed_dttm = gp.Datetime()
    __distributed_by__ = gp.Distribution('col_int')
    __layout__ = external_gp_layout()

    col_int = gp.Int()
    col_boolean = gp.Boolean()
    col_bigint = gp.BigInt()
    col_numeric = gp.Numeric()
    col_varchar = gp.String()
    col_text = gp.String()
    col_dt = gp.Date()
    col_dttm = gp.Datetime()
    col_int_array = gp.Array(gp.Int)
    col_varchar_array = gp.Array(gp.String)
    col_json = gp.Json()


class GPExportSlaSnapshotTest(GPExportSnaphotTest):
    __sla__ = Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(hours=1))


class GPExportYearPartitionScaleTest(GPExportSnaphotTest):
    __partition_scale__ = gp.YearPartitionScale('col_dttm', start='2020-01-01')


class GPExportMonthPartitionScaleTest(GPExportSnaphotTest):
    __partition_scale__ = gp.MonthPartitionScale('col_dttm', start='2020-03-01')


class GPExportDayPartitionScaleTest(GPExportSnaphotTest):
    __partition_scale__ = gp.DayPartitionScale('col_dttm', start='2020-03-01')


class GPExportWithKeyTest(GPExportSnaphotTest):
    col_int = gp.Int(key=True)


class GPViewTest(View):
    __layout__ = external_gp_layout()
    __query__ = 'select a as blah, b as minor from test_table'

    blah = gp.Int()
    minor = gp.Datetime()


class GPCommonTest(GPTable):
    __distributed_by__ = gp.Distribution('col_int')
    __layout__ = utils.TestLayout(name="test_export")
    __partition_scale__ = gp.MonthPartitionScale('col_dttm', start='2020-01-01', end='2022-01-01')

    col_int = gp.Int()
    col_bigint = gp.BigInt()
    col_smallint = gp.SmallInt()
    col_boolean = gp.Boolean()
    col_numeric = gp.Numeric()
    col_double = gp.Double()
    col_varchar = gp.String()
    col_text = gp.String()
    col_dt = gp.Date()
    col_dttm = gp.Datetime()
    col_json = gp.Json()
    col_point = gp.Point()
    col_uuid = gp.Uuid()
    col_array_int = gp.Array(gp.Int)
    col_array_str = gp.Array(gp.String)
    col_array_dt = gp.Array(gp.Date)
    col_array_dttm = gp.Array(gp.Datetime)
    col_array_bool = gp.Array(gp.Boolean)


class YTCommonTest(yt.YTTable):
    __layout__ = yt.LayeredLayout('test', 'test', prefix_key='test')

    col_int = yt.Int()
    col_boolean = yt.Boolean()
    col_bigint = yt.Int()
    col_smallint = yt.Int()
    col_numeric = yt.Double()
    col_double = yt.Double()
    col_varchar = yt.String()
    col_text = yt.String()
    col_dt = yt.Date()
    col_dttm = yt.Datetime()
    col_json = yt.Any()
    col_point = yt.Any()
    col_uuid = yt.String()
    col_array_int = yt.Any()
    col_array_str = yt.Any()
    col_array_dt = yt.Any()
    col_array_dttm = yt.Any()
    col_array_bool = yt.Any()


class YTCommonDynamicTest(YTCommonTest):
    __dynamic__ = True
    __unique_keys__ = True
    col_int = yt.Int(sort_key=True)


class GPCommonTestPartTest(GPCommonTest):
    __distributed_by__ = gp.Distribution('col_int')
    __partition_scale__ = gp.MonthPartitionScale('col_dttm', start='2020-01-01', end='2022-01-01')


class YTCommonDynamicPartTest(YTCommonDynamicTest):
    __partition_scale__ = yt.MonthPartitionScale('col_dt')
    __layout__ = yt.LayeredLayout('test', 'test_part')


# Export meta test table style
class YTExportBase(yt.ETLTable):
    __layout__ = yt.DeprecatedLayeredYtLayout('test', 'test')
    __location_cls__ = yt.YTLocation


@greenplum_to_yt_table(
    copy_from_table=GPExportSnaphotTest,
)
class YTSnaphotTest(YTExportBase):
    __layout__ = yt.LayeredLayout('test', 'test')
    __location_cls__ = yt.YTLocation


@greenplum_to_yt_table(
    copy_from_table=GPExportSnaphotTest,
)
class YTSnaphotCustomTest(YTExportBase):
    col_varchar = yt.String(sort_key=True, sort_position=1)
    col_dttm = yt.Datetime(sort_key=True, sort_position=2)
    col_int = yt.Int(sort_key=True, sort_position=3)


@greenplum_to_yt_table(
    copy_from_table=GPExportWithKeyTest,
    location_cls=yt.YTLocation,
)
class YTWithKeyTest(YTExportBase):
    col_int = yt.Int(sort_key=True, sort_position=0)
    col_dttm = yt.DatetimeMicroseconds()


@greenplum_to_yt_table(
    copy_from_table=GPExportYearPartitionScaleTest,
    location_cls=yt.YTLocation,
)
class YTYearPartitionScaleTest(YTExportBase):
    __partition_scale__ = yt.ShortYearPartitionScale('col_dttm')
    col_dttm = yt.Datetime()


@greenplum_to_yt_table(
    copy_from_table=GPViewTest,
    location_cls=yt.YTLocation,
)
class YTFromViewTest(YTExportBase):
    blah = yt.Int()
    minor = yt.Datetime()


@greenplum_to_yt_table(
    copy_from_table=GPViewTest,
    location_cls=yt.YTLocation,
)
class YTFromViewTest(YTExportBase):
    blah = yt.Int()
    minor = yt.Datetime()


@greenplum_to_yt_table(
    copy_from_table=GPExportSnaphotTest,
    location_cls=yt.YTLocation,
)
class YTStaticTest(YTExportBase):
    __dynamic__ = False
    __unique_keys__ = True
    col_int = yt.Int(sort_key=True, sort_position=0)


class GPNativeDatesTest(gp.GPTable):
    """
    Базовая таблица для проверки передачи дата-времени
    с GP на YT при использовании (нативных) типов даты
    и времени YT.
    """

    __distributed_by__ = gp.Distribution('col_int')
    __layout__ = utils.TestLayout('test_gpsql_to_yt_native_dates')

    col_int = gp.Int()
    col_dt = gp.Date(key=True)
    col_dttm = gp.Datetime()


@greenplum_to_yt_table(
    layout=yt.NotLayeredYtLayout('test', 'gpsql_to_yt_native_dates'),
    location_cls=yt.NotLayeredYtLocation,
    copy_from_table=GPNativeDatesTest,
    field_kwargs={
        'col_dt': {'type': yt.NativeDate},
        'col_dttm': {'type': yt.NativeDatetime},
    },
    keys={
        'col_dt': dict(sort_key=True, sort_position=1),
    },
)
class YTNativeDateTest(yt.YTTable):
    """
    Таблица используется для проверки конвертации типов
    даты-времени в GP в (нативные) типы даты-времени на
    YT, при явном их указании.
    """
    pass


class GPDecimalTest(gp.GPTable):
    """
    Базовая таблица для проверки передачи Numeric значений
    с GP в Decimal YT при использовании (нативных) типов даты
    и времени YT.
    """

    __distributed_by__ = gp.Distribution('col_int')
    __layout__ = utils.TestLayout('test_gpsql_to_yt_decimal')

    col_int = gp.Int()
    col_decimal = gp.Numeric(key=True)


@greenplum_to_yt_table(
    layout=yt.NotLayeredYtLayout('test', 'gpsql_to_yt_decimal'),
    location_cls=yt.NotLayeredYtLocation,
    copy_from_table=GPDecimalTest,
    field_kwargs={
        'col_decimal': {'type': (lambda **x: yt.Decimal(5, 3, **x))},
    },
    keys={
        'col_decimal': dict(sort_key=True, sort_position=0),
    },
)
class YTDecimalTest(yt.YTTable):
    """
    Таблица используется для проверки конвертации типа
    Numeric из GP в Decimal YT, при явном его указании.
    """
    pass
