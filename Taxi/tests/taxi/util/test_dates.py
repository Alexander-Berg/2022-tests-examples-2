import datetime

import pytest
import pytz

from taxi.util import dates


@pytest.mark.parametrize(
    'duration_string, expected_timedelta',
    [
        ('0d', datetime.timedelta(seconds=0)),
        ('1d', datetime.timedelta(days=1)),
        ('2h', datetime.timedelta(hours=2)),
        ('3m', datetime.timedelta(minutes=3)),
        ('4s', datetime.timedelta(seconds=4)),
        ('5d10h', datetime.timedelta(days=5, hours=10)),
        ('2h3m', datetime.timedelta(hours=2, minutes=3)),
        ('2d5s', datetime.timedelta(days=2, seconds=5)),
        ('3h4m5s', datetime.timedelta(hours=3, minutes=4, seconds=5)),
        (
            '4d5h6m7s',
            datetime.timedelta(days=4, hours=5, minutes=6, seconds=7),
        ),
    ],
)
async def test_parse_duration_string(duration_string, expected_timedelta):
    assert dates.parse_duration_string(duration_string) == expected_timedelta


@pytest.mark.parametrize(
    'expected, utc_offset',
    [
        pytest.param(
            datetime.datetime(2019, 8, 1, 0, 0),
            None,
            marks=[pytest.mark.now('2019-09-11T12:08:12')],
            id='without UTC offset',
        ),
        pytest.param(
            datetime.datetime(2019, 8, 1, 0, 0),
            '+1100',
            marks=[pytest.mark.now('2019-09-11T12:08:12')],
            id='with UTC offset',
        ),
        pytest.param(
            datetime.datetime(2019, 9, 1, 0, 0, 0),
            '+1100',
            marks=[pytest.mark.now('2019-09-30T23:08:12')],
            id='one month shift forward because of timezone',
        ),
        pytest.param(
            datetime.datetime(2019, 7, 1, 0, 0, 0),
            '-1100',
            marks=[pytest.mark.now('2019-09-01T02:08:12')],
            id='one month shift backward because of timezone',
        ),
    ],
)
async def test_last_month_start(expected, utc_offset):
    assert dates.last_month_start(utc_offset) == expected


@pytest.mark.parametrize(
    'expected, utc_offset',
    [
        pytest.param(
            datetime.datetime(2019, 8, 31, 23, 59, 59, 999999),
            None,
            marks=[pytest.mark.now('2019-09-11T12:08:12')],
            id='without UTC offset',
        ),
        pytest.param(
            datetime.datetime(2019, 8, 31, 23, 59, 59, 999999),
            '+1100',
            marks=[pytest.mark.now('2019-09-11T12:08:12')],
            id='with UTC offset',
        ),
        pytest.param(
            datetime.datetime(2019, 9, 30, 23, 59, 59, 999999),
            '+1100',
            marks=[pytest.mark.now('2019-09-30T23:08:12')],
            id='one month shift forward because of timezone',
        ),
        pytest.param(
            datetime.datetime(2019, 7, 31, 23, 59, 59, 999999),
            '-1100',
            marks=[pytest.mark.now('2019-09-01T02:08:12')],
            id='one month shift backward because of timezone',
        ),
    ],
)
async def test_last_month_end(expected, utc_offset):
    assert dates.last_month_end(utc_offset) == expected


@pytest.mark.parametrize(
    'timestring,timezone,expected',
    [
        pytest.param(
            '2020-10-10T13:10:10+0000',
            None,
            datetime.datetime(2020, 10, 10, 13, 10, 10, tzinfo=pytz.utc),
            id='with timezone utc',
        ),
        pytest.param(
            '2020-10-10T13:10:10+0300',
            None,
            datetime.datetime(2020, 10, 10, 10, 10, 10, tzinfo=pytz.utc),
            id='with timezone +3',
        ),
        pytest.param(
            '2020-10-10T13:10:10',
            'Europe/Moscow',
            datetime.datetime(2020, 10, 10, 10, 10, 10, tzinfo=pytz.utc),
            id='Europe/Moscow timezone explicitly specified',
        ),
    ],
)
async def test_parse_timestring_aware(timestring, timezone, expected):
    args = [timestring, timezone] if timezone else [timestring]
    assert dates.parse_timestring_aware(*args) == expected


AWARE_DT = '2000-01-01 00:00:00+00:00'
NOT_AWARE_DT = '2000-01-01 00:00:00'

CASES = [
    pytest.param('2000-01-01T00:00:00', NOT_AWARE_DT, id='na_0'),
    pytest.param('2000-01-01T00:00:00.0', NOT_AWARE_DT, id='na_1'),
    pytest.param('2000-01-01T00:00:00.00', NOT_AWARE_DT, id='na_2'),
    pytest.param('2000-01-01T00:00:00.000', NOT_AWARE_DT, id='na_3'),
    pytest.param('2000-01-01T00:00:00.0000', NOT_AWARE_DT, id='na_4'),
    pytest.param('2000-01-01T00:00:00.00000', NOT_AWARE_DT, id='na_5'),
    pytest.param('2000-01-01T00:00:00.000000', NOT_AWARE_DT, id='na_6'),
    pytest.param('2000-01-01T00:00:00Z', AWARE_DT, id='z_0'),
    pytest.param('2000-01-01T00:00:00.0Z', AWARE_DT, id='z_1'),
    pytest.param('2000-01-01T00:00:00.00Z', AWARE_DT, id='z_2'),
    pytest.param('2000-01-01T00:00:00.000Z', AWARE_DT, id='z_3'),
    pytest.param('2000-01-01T00:00:00.0000Z', AWARE_DT, id='z_4'),
    pytest.param('2000-01-01T00:00:00.00000Z', AWARE_DT, id='z_5'),
    pytest.param('2000-01-01T00:00:00.000000Z', AWARE_DT, id='z_6'),
    pytest.param('2000-01-01T00:00:00+00:00', AWARE_DT, id='fp_0'),
    pytest.param('2000-01-01T00:00:00.0+00:00', AWARE_DT, id='fp_1'),
    pytest.param('2000-01-01T00:00:00.00+00:00', AWARE_DT, id='fp_2'),
    pytest.param('2000-01-01T00:00:00.000+00:00', AWARE_DT, id='fp_3'),
    pytest.param('2000-01-01T00:00:00.0000+00:00', AWARE_DT, id='fp_4'),
    pytest.param('2000-01-01T00:00:00.00000+00:00', AWARE_DT, id='fp_5'),
    pytest.param('2000-01-01T00:00:00.000000+00:00', AWARE_DT, id='fp_6'),
    pytest.param('2000-01-01T00:00:00+0000', AWARE_DT, id='ib_0'),
    pytest.param('2000-01-01T00:00:00.0+0000', AWARE_DT, id='ib_1'),
    pytest.param('2000-01-01T00:00:00.00+0000', AWARE_DT, id='ib_2'),
    pytest.param('2000-01-01T00:00:00.000+0000', AWARE_DT, id='ib_3'),
    pytest.param('2000-01-01T00:00:00.0000+0000', AWARE_DT, id='ib_4'),
    pytest.param('2000-01-01T00:00:00.00000+0000', AWARE_DT, id='ib_5'),
    pytest.param('2000-01-01T00:00:00.000000+0000', AWARE_DT, id='ib_6'),
    pytest.param('2000-01-01T00:00:00-00:00', AWARE_DT, id='fm_0'),
    pytest.param('2000-01-01T00:00:00.0-00:00', AWARE_DT, id='fm_1'),
    pytest.param('2000-01-01T00:00:00.00-00:00', AWARE_DT, id='fm_2'),
    pytest.param('2000-01-01T00:00:00.000-00:00', AWARE_DT, id='fm_3'),
    pytest.param('2000-01-01T00:00:00.0000-00:00', AWARE_DT, id='fm_4'),
    pytest.param('2000-01-01T00:00:00.00000-00:00', AWARE_DT, id='fm_5'),
    pytest.param('2000-01-01T00:00:00.000000-00:00', AWARE_DT, id='fm_6'),
    pytest.param(
        '2123-04-15T12:34:56.7890-06:30',
        '2123-04-15 12:34:56.789000-06:30',
        id='random',
    ),
]


@pytest.mark.parametrize('tst_str, expected_res', CASES)
def test_parse_isoformat(tst_str, expected_res):
    assert str(dates.parse_isoformat(tst_str)) == expected_res


@pytest.mark.parametrize(
    'tst_str, fraction, ib_fraction',
    [
        pytest.param(
            AWARE_DT,
            '2000-01-01T00:00:00.000000+00:00',
            '2000-01-01T00:00:00.000000+0000',
            id='aware',
        ),
        pytest.param(
            NOT_AWARE_DT,
            '2000-01-01T00:00:00.000000+00:00',
            '2000-01-01T00:00:00.000000+0000',
            id='not_aware',
        ),
        pytest.param(
            '2123-04-15T12:34:56.7890-06:30',
            '2123-04-15T12:34:56.789000-06:30',
            '2123-04-15T12:34:56.789000-0630',
            id='random',
        ),
    ],
)
def test_fraction(tst_str, fraction, ib_fraction):
    stamp = dates.parse_isoformat(tst_str)
    assert dates.timestring_fraction(stamp) == fraction
    assert dates.timestring_iso_basic_fraction(stamp) == ib_fraction
