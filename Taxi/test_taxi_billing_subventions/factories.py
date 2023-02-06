import datetime as dt
import decimal
from typing import List
from typing import Sequence

from taxi.billing.util import dates

from taxi_billing_subventions.common import intervals
from taxi_billing_subventions.common import models


def make_df_rate_interval_endpoint(
        value,
) -> models.DriverFixRateIntervalEndpoint:
    weekday: str
    time: str
    weekday, time = value.split(' ')
    hour, minute = time.split(':')
    return models.DriverFixRateIntervalEndpoint(
        iso_week_day=models.ISOWeekDay[weekday.lower()],
        hour=int(hour),
        minute=int(minute),
    )


def make_driver_fix_rate_interval(value: str) -> models.DriverFixRateInterval:
    endpoint_str, _, rate_str = value.rpartition(', ')
    return models.DriverFixRateInterval(
        starts_at=make_df_rate_interval_endpoint(endpoint_str),
        rate_per_minute=decimal.Decimal(rate_str),
    )


def make_driver_fix_rate_intervals(
        str_values: Sequence[str],
) -> List[models.DriverFixRateInterval]:
    return [
        make_driver_fix_rate_interval(str_value) for str_value in str_values
    ]


def make_datetime_interval(
        start_end: Sequence[str],
) -> intervals.Interval[dt.datetime]:
    start, end = start_end
    return intervals.closed_open(
        dates.parse_datetime(start), dates.parse_datetime(end),
    )


def make_unfit_reason(attrs: dict):
    return models.rule.MatchReason.build_unfit(
        attrs['sub_kind'], attrs['code'], attrs['details'],
    )


def make_grouped_thresholds(attrs: dict):
    default_value = attrs['default']
    custom = attrs['custom']
    grouped_thresholds = dict.fromkeys(
        [(weekday, hour) for weekday in range(1, 8) for hour in range(0, 24)],
        default_value,
    )
    for (weekday, hour), income in custom:
        grouped_thresholds[(weekday, hour)] = income
    return grouped_thresholds


def make_driver_entity(attrs: dict):
    return models.Entity(
        external_id=attrs['external_id'], kind=models.EntityKind.DRIVER.value,
    )


def make_time(value: str):
    return dt.datetime.strptime(value, '%H:%M:%S%z').timetz()
