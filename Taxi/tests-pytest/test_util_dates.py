import datetime

import pytest

from taxi.util import dates


@pytest.mark.filldb(_fill=None)
@pytest.mark.parametrize('now_time,threshold,expected_time', [
    ((13, 0, 0), 5, (13, 5, 0)),
    ((13, 0, 0), 2, (13, 2, 0)),
    ((13, 0, 0), 1, (13, 1, 0)),
    ((13, 2, 30), 5, (13, 5, 0)),
    ((13, 4, 59), 5, (13, 5, 0)),
    ((13, 0, 59), 1, (13, 1, 0)),
    ((13, 1, 0), 2, (13, 2, 0)),
])
def test_round_time(now_time, threshold, expected_time):
    now = datetime.datetime(2015, 1, 1, *now_time)
    expected = datetime.datetime(2015, 1, 1, *expected_time)
    assert dates.round_time(now, threshold) == expected


@pytest.mark.parametrize('datetime_obj,timezone,time_string', [
    (datetime.datetime(2016, 12, 1, 16, 0), 'Asia/Almaty',
     '2016-12-01T22:00:00+0600'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Asia/Almaty',
     '2016-12-05T22:00:00+0600'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Asia/Barnaul',
     '2016-12-01T23:00:00+0700'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Asia/Barnaul',
     '2016-12-05T23:00:00+0700'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Asia/Irkutsk',
     '2016-12-02T00:00:00+0800'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Asia/Irkutsk',
     '2016-12-06T00:00:00+0800'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Asia/Krasnoyarsk',
     '2016-12-01T23:00:00+0700'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Asia/Krasnoyarsk',
     '2016-12-05T23:00:00+0700'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Asia/Novosibirsk',
     '2016-12-01T23:00:00+0700'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Asia/Novosibirsk',
     '2016-12-05T23:00:00+0700'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Asia/Omsk',
     '2016-12-01T22:00:00+0600'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Asia/Omsk',
     '2016-12-05T22:00:00+0600'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Asia/Tbilisi',
     '2016-12-01T20:00:00+0400'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Asia/Tbilisi',
     '2016-12-05T20:00:00+0400'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Asia/Tomsk',
     '2016-12-01T23:00:00+0700'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Asia/Tomsk',
     '2016-12-05T23:00:00+0700'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Asia/Vladivostok',
     '2016-12-02T02:00:00+1000'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Asia/Vladivostok',
     '2016-12-06T02:00:00+1000'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Asia/Yakutsk',
     '2016-12-02T01:00:00+0900'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Asia/Yakutsk',
     '2016-12-06T01:00:00+0900'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Asia/Yekaterinburg',
     '2016-12-01T21:00:00+0500'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Asia/Yekaterinburg',
     '2016-12-05T21:00:00+0500'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Asia/Yerevan',
     '2016-12-01T20:00:00+0400'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Asia/Yerevan',
     '2016-12-05T20:00:00+0400'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Europe/Kaliningrad',
     '2016-12-01T18:00:00+0200'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Europe/Kaliningrad',
     '2016-12-05T18:00:00+0200'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Europe/Kiev',
     '2016-12-01T18:00:00+0200'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Europe/Kiev',
     '2016-12-05T18:00:00+0200'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Europe/Minsk',
     '2016-12-01T19:00:00+0300'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Europe/Minsk',
     '2016-12-05T19:00:00+0300'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Europe/Moscow',
     '2016-12-01T19:00:00+0300'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Europe/Moscow',
     '2016-12-05T19:00:00+0300'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Europe/Samara',
     '2016-12-01T20:00:00+0400'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Europe/Samara',
     '2016-12-05T20:00:00+0400'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Europe/Volgograd',
     '2016-12-01T19:00:00+0300'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Europe/Volgograd',
     '2016-12-05T19:00:00+0300'),
    (datetime.datetime(2016, 12, 1, 16, 0), 'Europe/Saratov',
     '2016-12-01T19:00:00+0300'),
    (datetime.datetime(2016, 12, 5, 16, 0), 'Europe/Saratov',
     '2016-12-05T20:00:00+0400'),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_pytz(datetime_obj, timezone, time_string):
    assert dates.timestring(datetime_obj, timezone) == time_string
    assert dates.parse_timestring(time_string) == datetime_obj
