from datetime import datetime, timedelta

from dmp_suite.ctl import CTL_LAST_SYNC_DATE

from dmp_suite import yt
from dmp_suite.table import Sla


class YTExportTest(yt.NotLayeredYtTable):
    __layout__ = yt.NotLayeredYtLayout('folder', 'table', prefix_key='test')
    etl_updated = yt.Datetime()

    col_int = yt.Int()
    col_boolean = yt.Boolean()
    col_bigint = yt.Int()
    col_uint = yt.UInt()
    col_numeric = yt.Double()
    col_varchar = yt.String()
    col_text = yt.String()
    col_dt = yt.Date()
    col_dttm = yt.Datetime()
    col_dttm_ms = yt.DatetimeMicroseconds()
    col_int_array = yt.Any()
    col_varchar_array = yt.Any()
    col_json = yt.Any()


class YTExportSlaSnapshotTest(YTExportTest):
    __sla__ = Sla(CTL_LAST_SYNC_DATE, warn_lag=timedelta(hours=1))


class YTExportYearPartitionTest(YTExportTest):
    __partition_scale__ = yt.YearPartitionScale('col_dttm')


class YTExportShortYearPartitionTest(YTExportTest):
    __partition_scale__ = yt.ShortYearPartitionScale('col_dttm')


class YTExportMonthPartitionTest(YTExportTest):
    __partition_scale__ = yt.MonthPartitionScale('col_dttm')


class YTExportShortMonthPartitionTest(YTExportTest):
    __partition_scale__ = yt.ShortMonthPartitionScale('col_dttm')


class YTExportDayPartitionTest(YTExportTest):
    __partition_scale__ = yt.DayPartitionScale('col_dttm')


class YTExportTestWithKey(YTExportTest):
    col_int = yt.Int(sort_key=True, sort_position=0)


class YTExportTypeV3Test(yt.NotLayeredYtTable):
    """
    Базовая таблица для проверки конвертации
    новых type_v3 типов из таблицы YT в GP.
    """
    __layout__ = yt.NotLayeredYtLayout('folder', 'table', prefix_key='test')

    col_int = yt.Int(sort_key=True)
    col_decimal = yt.Decimal(5, 3)
    col_date = yt.NativeDate()
    col_datetime = yt.NativeDatetime()
    col_timestamp = yt.NativeTimestamp()
