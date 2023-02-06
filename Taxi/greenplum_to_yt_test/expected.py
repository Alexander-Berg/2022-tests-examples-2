from datetime import timedelta, datetime

from dmp_suite import yt
from dmp_suite.ctl import CTL_LAST_LOAD_DATE
from dmp_suite.table import Sla, LayeredLayout


class YTExportBaseExpected(yt.ETLTable):
    __layout__ = yt.LayeredLayout('test', 'test')
    __location_cls__ = yt.YTLocation


class YTExportSnapshotExpected(YTExportBaseExpected):
    col_int = yt.Int()
    col_boolean = yt.Boolean()
    col_bigint = yt.Int()
    col_numeric = yt.Double()
    col_varchar = yt.String()
    col_text = yt.String()
    col_dt = yt.Date()
    col_dttm = yt.Datetime()
    col_int_array = yt.Any()
    col_varchar_array = yt.Any()
    col_json = yt.Any()


class YTExportSlaSnapshotExpected(YTExportSnapshotExpected):
    __sla__ = Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(hours=2))


class YTExportYearPartitionScaleExpected(YTExportSnapshotExpected):
    __partition_scale__ = yt.ShortYearPartitionScale('col_dttm')


class YTExportMonthPartitionScaleExpected(YTExportSnapshotExpected):
    __partition_scale__ = yt.ShortMonthPartitionScale('col_dttm')


class YTExportDayPartitionScaleExpected(YTExportSnapshotExpected):
    __partition_scale__ = yt.DayPartitionScale('col_dttm')


class YTExportWithKeyExpected(YTExportSnapshotExpected):
    col_int = yt.Int(sort_key=True, sort_position=0)
    col_dttm = yt.DatetimeMicroseconds()
    col_varchar = yt.String()


class YTExportCustomExpected(YTExportSnapshotExpected):
    col_int = yt.Int(sort_key=True, sort_position=3)
    col_dttm = yt.Datetime(sort_key=True, sort_position=2)
    col_varchar = yt.String(sort_key=True, sort_position=1)


class YTExportViewExpected(YTExportBaseExpected):
    blah = yt.Int()
    minor = yt.Datetime()


class YTExportExpectedWNewCol(YTExportSnapshotExpected):
    new_col = yt.String()


class YTExportExpectedStatic(YTExportSnapshotExpected):
    __dynamic__ = False
    __unique_keys__ = True
    col_int = yt.Int(sort_key=True, sort_position=0)
