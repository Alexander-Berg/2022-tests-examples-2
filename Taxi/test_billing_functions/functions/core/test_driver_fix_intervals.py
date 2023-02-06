import decimal

from dateutil import tz
import pytest

from taxi.billing.util import dates

from billing_functions import consts
import billing_functions.functions.core.driver_fix.intervals as df_intervals


def _parse_interval(interval: dict) -> df_intervals.RateInterval:
    return df_intervals.RateInterval(
        starts_at=_make_df_rate_interval_endpoint(interval['starts_at']),
        rate_per_minute=decimal.Decimal(interval['rate_per_minute']),
    )


def _make_df_rate_interval_endpoint(
        value: str,
) -> df_intervals.RateIntervalEndpoint:
    weekday, time = value.split(' ')
    hour, minute = time.split(':')
    return df_intervals.RateIntervalEndpoint(
        iso_week_day=consts.ISOWeekDay[weekday.lower()],
        hour=int(hour),
        minute=int(minute),
    )


@pytest.mark.parametrize(
    'start, end, rate_intervals, tz_id, shift_start,'
    'shift_end, expected_paid_intervals, expected_total_payment, ',
    [
        (
            '2019-11-01T00:00:00+00:00',
            '2019-11-30T00:00:00+00:00',
            {1: {'starts_at': 'Mon 01:00', 'rate_per_minute': '1'}},
            'Europe/Moscow',
            '2019-11-10T00:00:00+00:00',
            '2019-11-11T00:00:00+00:00',
            [
                {
                    'start': '2019-11-10T03:00:00',
                    'end': '2019-11-11T01:00:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2019-11-11T01:00:00',
                    'end': '2019-11-11T03:00:00',
                    'rate_interval': 1,
                },
            ],
            1440,
        ),
        pytest.param(
            '2019-11-01T00:00:00+00:00',
            '2019-11-30T00:00:00+00:00',
            {
                1: {'starts_at': 'Mon 01:00', 'rate_per_minute': '1'},
                2: {'starts_at': 'Tue 02:00', 'rate_per_minute': '2'},
                3: {'starts_at': 'Wed 03:00', 'rate_per_minute': '3'},
                4: {'starts_at': 'Thu 04:00', 'rate_per_minute': '4'},
                5: {'starts_at': 'Fri 05:00', 'rate_per_minute': '5'},
                6: {'starts_at': 'Sat 06:00', 'rate_per_minute': '6'},
                7: {'starts_at': 'Sun 07:00', 'rate_per_minute': '7'},
            },
            'Europe/Moscow',
            '2019-11-10T00:00:00+03:00',
            '2019-11-20T00:00:00+03:00',
            [
                {
                    'start': '2019-11-10T00:00:00',
                    'end': '2019-11-10T07:00:00',
                    'rate_interval': 6,
                },
                {
                    'start': '2019-11-10T07:00:00',
                    'end': '2019-11-11T01:00:00',
                    'rate_interval': 7,
                },
                {
                    'start': '2019-11-11T01:00:00',
                    'end': '2019-11-12T02:00:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2019-11-12T02:00:00',
                    'end': '2019-11-13T03:00:00',
                    'rate_interval': 2,
                },
                {
                    'start': '2019-11-13T03:00:00',
                    'end': '2019-11-14T04:00:00',
                    'rate_interval': 3,
                },
                {
                    'start': '2019-11-14T04:00:00',
                    'end': '2019-11-15T05:00:00',
                    'rate_interval': 4,
                },
                {
                    'start': '2019-11-15T05:00:00',
                    'end': '2019-11-16T06:00:00',
                    'rate_interval': 5,
                },
                {
                    'start': '2019-11-16T06:00:00',
                    'end': '2019-11-17T07:00:00',
                    'rate_interval': 6,
                },
                {
                    'start': '2019-11-17T07:00:00',
                    'end': '2019-11-18T01:00:00',
                    'rate_interval': 7,
                },
                {
                    'start': '2019-11-18T01:00:00',
                    'end': '2019-11-19T02:00:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2019-11-19T02:00:00',
                    'end': '2019-11-20T00:00:00',
                    'rate_interval': 2,
                },
            ],
            53280,
            id='Every weekday',
        ),
        pytest.param(
            '2019-11-02T00:00:00+00:00',
            '2019-11-03T00:00:00+00:00',
            {1: {'starts_at': 'Fri 03:01', 'rate_per_minute': '1'}},
            'Europe/Moscow',
            '2019-11-01T00:00:00+00:00',
            '2019-11-02T00:00:00+00:00',
            [],
            0,
            id='Shift just before rule',
        ),
        pytest.param(
            '2019-11-01T00:00:00+00:00',
            '2019-11-02T00:00:00+00:00',
            {1: {'starts_at': 'Fri 03:01', 'rate_per_minute': '1'}},
            'Europe/Moscow',
            '2019-11-02T00:00:00+00:00',
            '2019-11-03T00:00:00+00:00',
            [],
            0,
            id='Shift just after rule',
        ),
        pytest.param(
            '2019-11-01T00:00:00+00:00',
            '2019-11-02T00:00:00+00:00',
            {
                1: {'starts_at': 'Fri 04:00', 'rate_per_minute': '1'},
                2: {'starts_at': 'Fri 05:00', 'rate_per_minute': '2'},
            },
            'Europe/Moscow',
            '2019-11-01T04:00:00+03:00',
            '2019-11-01T05:00:00+03:00',
            [
                {
                    'start': '2019-11-01T04:00:00',
                    'end': '2019-11-01T05:00:00',
                    'rate_interval': 1,
                },
            ],
            60,
            id='Shift covers whole interval',
        ),
        pytest.param(
            '2019-11-01T04:00:00+03:00',
            '2019-11-10T00:00:00+03:00',
            {1: {'starts_at': 'Fri 04:01', 'rate_per_minute': '1'}},
            'Europe/Moscow',
            '2019-11-01T04:00:00+03:00',
            '2019-11-01T04:01:00+03:00',
            [
                {
                    'start': '2019-11-01T04:00:00',
                    'end': '2019-11-01T04:01:00',
                    'rate_interval': 1,
                },
            ],
            1,
            id='Shift is before first interval of the week',
        ),
        pytest.param(
            '2021-10-30T00:00:00+03:00',
            '2021-10-31T23:59:59+03:00',
            {1: {'starts_at': 'Sun 00:00', 'rate_per_minute': '1'}},
            'Asia/Jerusalem',
            '2021-10-31T00:00:00+03:00',
            '2021-10-31T03:00:00+03:00',
            [
                {
                    'start': '2021-10-31T00:00:00',
                    'end': '2021-10-31T02:00:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2021-10-31T01:00:00',
                    'end': '2021-10-31T02:00:00',
                    'rate_interval': 1,
                },
            ],
            180,
            id='Pass throw winter time change',
        ),
        pytest.param(
            '2021-10-30T00:00:00+03:00',
            '2021-10-31T23:59:59+03:00',
            {
                1: {'starts_at': 'Sun 00:00', 'rate_per_minute': '1'},
                3: {'starts_at': 'Sun 01:30', 'rate_per_minute': '3'},
            },
            'Asia/Jerusalem',
            '2021-10-30T21:00:00+00:00',
            '2021-10-31T00:00:00+00:00',
            [
                {
                    'start': '2021-10-31T00:00:00',
                    'end': '2021-10-31T01:30:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2021-10-31T01:30:00',
                    'end': '2021-10-31T02:00:00',
                    'rate_interval': 3,
                },
                {
                    'start': '2021-10-31T01:00:00',
                    'end': '2021-10-31T01:30:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2021-10-31T01:30:00',
                    'end': '2021-10-31T02:00:00',
                    'rate_interval': 3,
                },
            ],
            300,
            id='Calc hour with two paid intervals twice due to DST transition',
        ),
        pytest.param(
            '2021-10-30T00:00:00+03:00',
            '2021-10-31T23:59:59+03:00',
            {
                1: {'starts_at': 'Sun 00:00', 'rate_per_minute': '1'},
                3: {'starts_at': 'Sun 02:00', 'rate_per_minute': '3'},
            },
            'Asia/Jerusalem',
            '2021-10-30T21:00:00+00:00',
            '2021-10-31T01:00:00+00:00',
            [
                {
                    'start': '2021-10-31T00:00:00',
                    'end': '2021-10-31T02:00:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2021-10-31T01:00:00',
                    'end': '2021-10-31T02:00:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2021-10-31T02:00:00',
                    'end': '2021-10-31T03:00:00',
                    'rate_interval': 3,
                },
            ],
            360,
            id='DST transition at the end of paid interval',
        ),
        pytest.param(
            '2021-03-26T00:00:00+03:00',
            '2021-03-26T23:59:59+03:00',
            {1: {'starts_at': 'Fri 00:00', 'rate_per_minute': '1'}},
            'Asia/Jerusalem',
            '2021-03-25T22:00:00+00:00',
            '2021-03-26T01:00:00+00:00',
            [
                {
                    'start': '2021-03-26T00:00:00',
                    'end': '2021-03-26T02:00:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2021-03-26T03:00:00',
                    'end': '2021-03-26T04:00:00',
                    'rate_interval': 1,
                },
            ],
            180,
            id='Pass throw summer time change',
        ),
        pytest.param(
            '2021-03-26T00:00:00+03:00',
            '2021-03-26T23:59:59+03:00',
            {
                1: {'starts_at': 'Fri 00:00', 'rate_per_minute': '1'},
                3: {'starts_at': 'Fri 03:00', 'rate_per_minute': '3'},
            },
            'Asia/Jerusalem',
            '2021-03-25T22:00:00+00:00',
            '2021-03-26T01:00:00+00:00',
            [
                {
                    'start': '2021-03-26T00:00:00',
                    'end': '2021-03-26T02:00:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2021-03-26T03:00:00',
                    'end': '2021-03-26T04:00:00',
                    'rate_interval': 3,
                },
            ],
            300,
            id='Calc last hour in new time',
        ),
    ],
)
@pytest.mark.nofilldb()
@pytest.mark.dontfreeze()
def test_rate_schedule(
        start,
        end,
        rate_intervals,
        tz_id,
        shift_start,
        shift_end,
        expected_paid_intervals,
        expected_total_payment,
):
    start = dates.parse_datetime(start)
    end = dates.parse_datetime(end)
    rate_intervals = {
        id_: _parse_interval(interval)
        for id_, interval in rate_intervals.items()
    }
    tzinfo = tz.gettz(tz_id)
    calculator = df_intervals.Calculator(
        start, end, list(rate_intervals.values()), tzinfo,
    )
    shift_start = dates.parse_datetime(shift_start)
    shift_end = dates.parse_datetime(shift_end)
    paid_intervals = calculator.get_paid_intervals(shift_start, shift_end)

    expected_paid_intervals = [
        df_intervals.PaidInterval(
            start=dates.parse_naive_datetime(interval['start']),
            end=dates.parse_naive_datetime(interval['end']),
            rate_interval=rate_intervals[interval['rate_interval']],
        )
        for interval in expected_paid_intervals
    ]
    assert paid_intervals == expected_paid_intervals

    actual_payment = df_intervals.PaidInterval.get_total_payment_amount(
        paid_intervals,
    )
    assert actual_payment == expected_total_payment
