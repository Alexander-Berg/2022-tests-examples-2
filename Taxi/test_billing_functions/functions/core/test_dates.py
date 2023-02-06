from dateutil import tz
import pytest

from taxi.billing.util import dates as util

from billing_functions.functions.core import dates


ISR = tz.gettz('Israel')


@pytest.mark.parametrize(
    'shift_end,timezone,expected',
    (
        (
            '2020-05-07T21:00:00+00:00',
            'Europe/Moscow',
            '2020-05-07T00:00:00+03:00',
        ),
        (
            '2020-05-07T00:00:00+00:00',
            'Europe/Moscow',
            '2020-05-07T00:00:00+03:00',
        ),
        (
            '2020-05-07T11:11:00+03:00',
            'Europe/Moscow',
            '2020-05-07T00:00:00+03:00',
        ),
    ),
)
async def test_calculate_start_of_last_shift_day(
        shift_end, timezone, expected,
):
    actual = dates.calc_start_of_last_shift_day(
        util.parse_datetime(shift_end), timezone,
    )
    assert actual == util.parse_datetime(expected)


@pytest.mark.parametrize(
    'since_str, till_str, tzinfo, expected_str',
    [
        pytest.param(
            '2021-09-30T00:00:00+03:00',
            '2021-10-01T00:00:00+03:00',
            ISR,
            None,
            id='no_dst_transition',
        ),
        pytest.param(
            '2021-10-31T00:00:01+03:00',
            '2021-11-01T00:00:00+03:00',
            ISR,
            '2021-10-30T23:00:00+00:00',
            id='transition_to_winter_time',
        ),
        pytest.param(
            '2021-10-30T21:01:01+00:00',
            '2021-10-31T00:00:00+00:00',
            ISR,
            '2021-10-30T23:00:00+00:00',
            id='transition_to_winter_time_utc',
        ),
        pytest.param(
            '2021-03-26T01:01:01+03:00',
            '2021-03-27T00:00:00+03:00',
            ISR,
            '2021-03-26T00:00:00+00:00',
            id='transition_to_summer_time',
        ),
        pytest.param(
            '2021-10-30T23:00:00+00:00',
            '2021-11-01T00:00:00+03:00',
            ISR,
            '2021-10-30T23:00:00+00:00',
            id='transition_is_since',
        ),
        pytest.param(
            '2021-10-30T20:00:00+00:00',
            '2021-10-30T23:00:00+00:00',
            ISR,
            None,
            id='transition_is_till',
        ),
        pytest.param(
            '2021-10-30T20:00:00+00:00',
            '2021-10-30T20:00:00+00:00',
            ISR,
            None,
            id='transition_is_till',
        ),
    ],
)
@pytest.mark.dontfreeze
def test_find_dst_transition(since_str, till_str, tzinfo, expected_str):
    since = util.parse_datetime(since_str)
    till = util.parse_datetime(till_str)
    expected = util.parse_datetime(expected_str) if expected_str else None

    actual = dates.find_dst_transition(since, till, tzinfo)
    assert actual == expected


@pytest.mark.dontfreeze
def test_find_dst_transition_not_implemented():
    with pytest.raises(NotImplementedError):
        dates.find_dst_transition(
            util.parse_datetime('2021-03-27T00:00:00+00:00'),
            util.parse_datetime('2021-03-26T00:00:00+00:00'),
            ISR,
        )

    with pytest.raises(NotImplementedError):
        dates.find_dst_transition(
            util.parse_datetime('2021-01-26T00:00:00+00:00'),
            util.parse_datetime('2021-03-26T00:00:00+00:00'),
            ISR,
        )
