from datetime import datetime, timedelta

from dmp_suite.ctl import CTL_LAST_LOAD_DATE

from dmp_suite import greenplum as gp
from dmp_suite.table import Sla, LayeredLayout


class GPExportExpected(gp.GPEtlTable):
    __location_cls__ = gp.ExternalGPLocation
    __layout__ = gp.ExternalGPLayout('test', 'test')

    col_int = gp.BigInt()
    col_boolean = gp.Boolean()
    col_bigint = gp.BigInt()
    col_uint = gp.BigInt()
    col_numeric = gp.Numeric()
    col_varchar = gp.String()
    col_text = gp.String()
    col_dt = gp.Date()
    col_dttm = gp.Datetime()
    col_dttm_ms = gp.Datetime()
    col_int_array = gp.Json()
    col_varchar_array = gp.Json()
    col_json = gp.Json()


class GPExportExpectedFullExpected(GPExportExpected):
    __indexes__ = ['Test_indexes']
    __storage_parameters__ = gp.StorageParameters(
        orientation=gp.Orientation.COLUMN
    )


class GPExportSlaSnapshotExpected(GPExportExpected):
    __sla__ = Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(hours=2))


class GPExportYearPartitionExpected(GPExportExpected):
    __partition_scale__ = gp.YearPartitionScale('col_dttm', start='2020-01-01')


class GPExportMonthPartitionExpected(GPExportExpected):
    __partition_scale__ = gp.MonthPartitionScale('col_dttm', start='2020-03-01')


class GPExportDayPartitionExpected(GPExportExpected):
    __partition_scale__ = gp.DayPartitionScale('col_dttm', start='2020-03-01', end='2020-05-01')


class GPExportDayPartitionTtlExpected(GPExportExpected):
    __partition_scale__ = gp.DayPartitionScale('col_dttm', partition_ttl_day_cnt=90)


class GPExportDayTablespaceTtlExpected(GPExportExpected):
    __partition_scale__ = gp.DayPartitionScale('col_dttm', tablespace_ttl_day_cnt=365)


class GPExportDayPartitionTablespaceTtlExpected(GPExportExpected):
    __partition_scale__ = gp.DayPartitionScale('col_dttm', partition_ttl_day_cnt=90, tablespace_ttl_day_cnt=365)


class GPExportWithKeyExpected(GPExportExpected):
    col_int = gp.BigInt(key=True)


class GPExportArrayExpected(GPExportExpected):
    col_int_array = gp.Array(gp.Int)
    col_varchar_array = gp.Array(gp.String)


class GPExportExpectedWDistribution(GPExportExpected):
    __distributed_by__ = gp.Distribution('col_int')


class GPExportExpectedManyDistributions(GPExportExpected):
    __distributed_by__ = gp.Distribution('col_int', 'col_bigint')


class GPExportExpectedWoDistributions(GPExportExpected):
    __distributed_by__ = gp.Distribution()


class GPExportExpectedExcluded(gp.GPEtlTable):
    __location_cls__ = gp.ExternalGPLocation
    __layout__ = gp.ExternalGPLayout('test', 'test')

    col_int = gp.BigInt()
    col_boolean = gp.Boolean()
    col_bigint = gp.BigInt()
    col_uint = gp.BigInt()
    col_numeric = gp.Numeric()
    col_varchar = gp.String()
    col_text = gp.String()
    col_dt = gp.Date()


class GPExportExpectedNewColOnGP(GPExportExpected):
    new_col_on_GP = gp.String()


class GPExportExpectedTypeV3Test(gp.GPEtlTable):
    """
    Базовая таблица для проверки конвертации
    новых type_v3 типов из таблицы YT в GP.
    """
    __location_cls__ = gp.ExternalGPLocation
    __layout__ = gp.ExternalGPLayout('test', 'test')

    col_int = gp.BigInt(key=True)
    col_decimal = gp.Numeric()
    col_date = gp.Date()
    col_datetime = gp.Datetime()
    col_timestamp = gp.Datetime()
