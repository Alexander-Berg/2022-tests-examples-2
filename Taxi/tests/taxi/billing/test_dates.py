from dateutil import tz
import pytest

from taxi.billing.util import dates

ISR = tz.gettz('Israel')
MSK = tz.gettz('Europe/Moscow')


@pytest.mark.parametrize(
    'timepoint_str, tzinfo, expected',
    [
        ('2020-03-27T00:00:00+00:00', ISR, True),
        ('2020-10-24T23:00:00+00:00', ISR, True),
        ('2021-03-26T00:00:00+00:00', ISR, True),
        ('2021-10-30T23:00:00+00:00', ISR, True),
        ('2022-03-25T00:00:00+00:00', ISR, True),
        ('2022-10-29T23:00:00+00:00', ISR, True),
        ('2023-03-24T00:00:00+00:00', ISR, True),
        ('2023-10-28T23:00:00+00:00', ISR, True),
        ('2024-03-29T00:00:00+00:00', ISR, True),
        ('2024-10-26T23:00:00+00:00', ISR, True),
        ('2025-03-28T00:00:00+00:00', ISR, True),
        ('2025-10-25T23:00:00+00:00', ISR, True),
        ('2026-03-27T00:00:00+00:00', ISR, True),
        #
        ('2020-03-27T00:00:00.000001+00:00', ISR, False),
        ('2020-03-27T00:00:00+00:00', MSK, False),
    ],
)
@pytest.mark.dontfreeze
def test_is_dst_transition(timepoint_str, tzinfo, expected):
    timepoint = dates.parse_datetime(timepoint_str)
    assert dates.is_dst_transition(timepoint, tzinfo) == expected
