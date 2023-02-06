import sys
sys.path.append('../')

import pytz

from datetime import datetime, timedelta

import helpers #pylint: disable=E0401

#pylint: disable=C0103


def test_DateTime():
    utcnow = datetime.utcnow()
    dt = helpers.DateTime()

    time_epsilon = timedelta(seconds=1)
    assert dt.utc - utcnow < time_epsilon

    dt = helpers.DateTime(utcnow)
    assert dt.utc == utcnow

    tz = pytz.timezone('Europe/Moscow')
    time_epsilon = tz.utcoffset(utcnow)
    assert dt.msk - utcnow == time_epsilon


def test_nearest_shift_start():
    now = datetime.utcnow()

    for msk_shift_start in xrange(24):
        shift_start = helpers.nearest_shift_start(msk_shift_start)
        assert shift_start.msk.hour == msk_shift_start
        assert shift_start.utc >= now
        assert shift_start.utc - now < timedelta(days=1)


def test_nearest_monday():
    now = datetime.utcnow()
    for msk_shift_start in xrange(24):
        monday = helpers.nearest_monday(msk_shift_start)
        assert monday.msk.weekday() == 0
        assert monday.utc >= now
        assert monday.utc - now < timedelta(days=7)


def test_has_gap_in_period():
    now = helpers.DateTime()

    # gap inside region
    gaps = [{
        'from': now + timedelta(days=1),
        'to': now + timedelta(days=2),
    }]
    start = now - timedelta(days=1)
    end = now + timedelta(days=8)
    assert helpers.has_gap_in_period(gaps, start, end)

    # region inside gap
    gaps = [{
        'from': now - timedelta(days=1),
        'to': now + timedelta(days=8),
    }]
    start = now + timedelta(days=1)
    end = now + timedelta(days=2)
    assert helpers.has_gap_in_period(gaps, start, end)

    # gap overlap region left
    gaps = [{
        'from': now - timedelta(days=1),
        'to': now + timedelta(days=2),
    }]
    start = now + timedelta(days=1)
    end = now + timedelta(days=8)
    assert helpers.has_gap_in_period(gaps, start, end)

    # gap overlap region right
    gaps = [{
        'from': now + timedelta(days=1),
        'to': now + timedelta(days=8),
    }]
    start = now - timedelta(days=1)
    end = now + timedelta(days=2)
    assert helpers.has_gap_in_period(gaps, start, end)

    # no gap in region
    gaps = [{
        'from': now + timedelta(days=7),
        'to': now + timedelta(days=8),
    }]
    start = now + timedelta(days=1)
    end = now + timedelta(days=2)
    assert not helpers.has_gap_in_period(gaps, start, end)
