import datetime

from taxi_fleet.utils import l10n


def test_localize_date():
    # Basically only 2 cases. Added third, just for a good measure
    date = datetime.date(2000, 1, 1)
    date_no_shift = l10n.localize_date(date, 0)
    assert date_no_shift == date
    date_plus3 = l10n.localize_date(date, 3)
    assert date_plus3 == date
    date_minus3 = l10n.localize_date(date, -3)
    assert date_minus3 == datetime.date(1999, 12, 31)


def test_localize_datetime():
    datetime_ = datetime.datetime(2000, 1, 1)
    datetime_plus_3 = l10n.localize_datetime(datetime_, 3)
    assert datetime_plus_3 == datetime.datetime(
        2000, 1, 1, 3, tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
    )
