from datetime import timedelta, date

import pytest
import metrika.pylib.utils as mutil


def test_str_to_bool():
    with pytest.raises(ValueError):
        mutil.str_to_bool("")

    with pytest.raises(ValueError):
        mutil.str_to_bool("this is bad value")

    for value in mutil.TRUE_VALUES:
        assert mutil.str_to_bool(value) is True

    for value in mutil.FALSE_VALUES:
        assert mutil.str_to_bool(value) is False


def test_timedelta_to_str():
    assert mutil.timedelta_to_str(timedelta(seconds=0)) == ''
    assert mutil.timedelta_to_str(timedelta(seconds=0), short=False) == ''

    assert mutil.timedelta_to_str(timedelta(seconds=1)) == '1s'
    assert mutil.timedelta_to_str(timedelta(seconds=1), short=False) == '1 second'
    assert mutil.timedelta_to_str(timedelta(seconds=2), short=False) == '2 seconds'

    assert mutil.timedelta_to_str(timedelta(seconds=61)) == '1m'
    assert mutil.timedelta_to_str(timedelta(seconds=61), short=False) == '1 minute,1 second'
    assert mutil.timedelta_to_str(timedelta(seconds=123), short=False) == '2 minutes,3 seconds'

    assert mutil.timedelta_to_str(timedelta(seconds=61*60)) == '1h'
    assert mutil.timedelta_to_str(timedelta(seconds=61*60), short=False) == '1 hour,1 minute'

    assert mutil.timedelta_to_str(timedelta(seconds=61*60*24)) == '1d'
    assert mutil.timedelta_to_str(timedelta(seconds=61*65*24), short=False) == '1 day,2 hours,26 minutes'


def test_get_format_from_name():
    with pytest.raises(TypeError):
        mutil.get_format_from_name(None)

    with pytest.raises(TypeError):
        mutil.get_format_from_name(25)

    with pytest.raises(ValueError):
        mutil.get_format_from_name('')

    with pytest.raises(ValueError):
        mutil.get_format_from_name('.yaml')

    with pytest.raises(ValueError):
        mutil.get_format_from_name('name.')

    with pytest.raises(ValueError):
        mutil.get_format_from_name('name')

    with pytest.raises(ValueError):
        mutil.get_format_from_name('super.invalid')

    assert mutil.get_format_from_name('name.yaml') == 'yaml'
    assert mutil.get_format_from_name('name.yml') == 'yaml'
    assert mutil.get_format_from_name('name.xml') == 'xml'
    assert mutil.get_format_from_name('name.txt') == 'plaintext'


@pytest.mark.parametrize("orig_date,today,next_date", [
    (date(1975, 4, 12), date(2020, 3, 2), date(2020, 4, 12)),
    (date(2000, 3, 2), date(2020, 3, 2), date(2020, 3, 2)),
    (date(2000, 2, 29), date(2020, 2, 28), date(2020, 2, 29)),
    (date(2000, 2, 29), date(2020, 3, 1), date(2021, 3, 1)),
    (date(2000, 2, 29), date(2020, 3, 2), date(2021, 3, 1)),
    (date(2000, 2, 29), date(2021, 2, 28), date(2021, 3, 1)),
    (date(2000, 2, 29), date(2021, 3, 1), date(2021, 3, 1)),
    (date(2000, 2, 29), date(2021, 3, 2), date(2022, 3, 1)),
    (date(2001, 3, 1), date(2020, 2, 28), date(2020, 3, 1)),
])
def test_get_next_date_after_today(monkeypatch, orig_date, today, next_date):
    monkeypatch.setattr(mutil, "TODAY", today)
    assert mutil.get_next_date_after_today(orig_date) == next_date
