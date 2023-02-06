import datetime
import pytest

from taxi.internal import dbh
from taxi.internal.subvention_kit import single_driver_stats


@pytest.mark.filldb(_fill=False)
def test_count_rides():
    from_ = datetime.datetime(2017, 05, 12, 02, 45)
    to = from_ + datetime.timedelta(days=7)
    tss = [
        to - datetime.timedelta(days=x) for x in xrange(0, 8)
    ]
    docs = [
        dbh.unique_driver_zone_stats.Doc({
            dbh.unique_driver_zone_stats.Doc.midnight_datetime: ts,
            dbh.unique_driver_zone_stats.Doc.num_orders: 1,
            dbh.unique_driver_zone_stats.Doc.num_sticker_orders: 0,
            dbh.unique_driver_zone_stats.Doc.num_lightbox_orders: 0,
            dbh.unique_driver_zone_stats.Doc.num_full_branding_orders: 0,
        }) for ts in tss]
    stats = single_driver_stats._count_rides(docs, from_, to)
    assert dict(stats[0]) == {
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 5,
        6: 6,
        7: 7
    }
