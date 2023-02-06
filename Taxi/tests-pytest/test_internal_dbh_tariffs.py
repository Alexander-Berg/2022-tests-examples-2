import datetime

import pytest

from taxi.internal import dbh


@pytest.mark.filldb(tariffs='for_parks')
@pytest.mark.parametrize('due,park_id,expected_tariff_id', [
    # Should return MRT for moscow, because park is not specified
    (datetime.datetime(2016, 4, 8), None, 'moscow_low_price_mrt'),

    # Should return MRT for moscow, because no tariff for park
    (datetime.datetime(2016, 4, 8), 'park', 'moscow_low_price_mrt'),

    # Should return MRT for moscow, because park is not specified
    (datetime.datetime(2016, 5, 8), None, 'moscow_high_price'),

    # Should return parks tariff
    (datetime.datetime(2016, 5, 8), 'park', 'moscow_high_price_park'),

    # Should return MRT for moscow, because park is not specified
    (datetime.datetime(2020, 4, 8), None, 'moscow_low_price_mrt'),

    # Should return parks tariff
    (datetime.datetime(2020, 4, 8), 'park', 'moscow_low_price_park'),
])
@pytest.inline_callbacks
def test_find_tariffs_for_parks(due, park_id, expected_tariff_id):
    t = yield dbh.tariffs.Doc.find_active('moscow', due, park_id)
    assert t._id == expected_tariff_id


@pytest.inline_callbacks
def test_find_active_tariff():
    t = yield dbh.tariffs.Doc.find_active(
        'mytishchi', datetime.datetime.fromtimestamp(1150000000.000)
    )
    assert t._id == 'mytishchi'

    t = yield dbh.tariffs.Doc.find_active(
        'moscow', datetime.datetime.fromtimestamp(1150000000.000)
    )
    assert t._id == 'moscow'

    t = yield dbh.tariffs.Doc.find_active(
        'moscow', datetime.datetime.fromtimestamp(1250000000.000)
    )
    assert t._id == 'moscow2'

    with pytest.raises(dbh.tariffs.NotFound):
        # too early
        yield dbh.tariffs.Doc.find_active(
            'mytishchi', datetime.datetime.fromtimestamp(1000000000.000)
        )

    with pytest.raises(dbh.tariffs.NotFound):
        # too late
        yield dbh.tariffs.Doc.find_active(
            'mytishchi', datetime.datetime.fromtimestamp(1500000000.000)
        )

    with pytest.raises(dbh.tariffs.NotFound):
        # wrong homezone
        yield dbh.tariffs.Doc.find_active(
            'mks', datetime.datetime.fromtimestamp(1150000000.000)
        )

    t = yield dbh.tariffs.Doc.find_active('moscow')
    assert t._id == 'moscow2'

    with pytest.raises(dbh.tariffs.NotFound):
        # too late
        yield dbh.tariffs.Doc.find_active('mytishchi')
