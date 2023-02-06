import datetime
import pytest

from taxi.core import db
from taxi.internal import dbh
from taxi.internal import mph


@pytest.mark.filldb(orders='bulk_mph_check', mph_results='bulk_mph_check')
@pytest.inline_callbacks
def test_bulk_checks(patch):
    orders = yield db.orders.find({}).run()
    orders = map(dbh.orders.Doc, orders)

    thresholds = mph.Cache()
    yield thresholds.load()

    assert thresholds.find('not_exists', datetime.datetime.utcnow()) is None
    assert thresholds.find(
        'zone_exists',
        datetime.datetime.utcnow() - datetime.timedelta(seconds=501)
    )['test_key'] == 1.5
    assert thresholds.find(
        'zone_exists',
        datetime.datetime.utcnow() - datetime.timedelta(seconds=500)
    )['test_key'] == 1.0
    assert thresholds.find(
        'zone_exists',
        datetime.datetime.utcnow() - datetime.timedelta(seconds=100)
    )['test_key'] == 1.0
    assert thresholds.find(
        'zone_exists',
        datetime.datetime.utcnow() + datetime.timedelta(seconds=50000)
    ) is None

    tariff_settings = yield dbh.tariff_settings.Doc.find_many(
        {}, fields=[
            dbh.tariff_settings.Doc.tz, dbh.tariff_settings.Doc.home_zone
        ]
    )
    tariff_settings = {
        doc.home_zone: doc for doc in tariff_settings
    }

    @patch('taxi.internal.mph._get_weighted_threshold')
    def _test_key(mph_doc, thresholds, tz):
        assert tz == 'Europe/Moscow'
        assert isinstance(mph_doc, dbh.mph_results.Doc)
        return thresholds['test_key']

    results, orders, _ = yield mph.bulk_check_thresholds(
        orders, thresholds, tariff_settings
    )
    assert results
    assert 4 not in results
    assert abs(results[1] - 1.0) < 0.01
    assert results[2] == 0.8
    assert abs(results[3] - 1.0) < 0.01


@pytest.mark.filldb(orders='bulk_mph_check', mph_results='bulk_mph_check')
@pytest.mark.parametrize('order_id, expected_result', [
    (1, 1.0), (2, 0.8), (3, 1.0), (4, None)
])
@pytest.inline_callbacks
def test_single_order_check(patch, order_id, expected_result):
    order = yield dbh.orders.Doc.find_one_by_id(order_id)

    @patch('taxi.internal.mph._get_weighted_threshold')
    def _test_key(mph_doc, thresholds, tz):
        assert tz == 'Europe/Moscow'
        assert isinstance(mph_doc, dbh.mph_results.Doc)
        return thresholds['test_key']

    result = yield mph.check_single_order(
        order.pk,
        order.request.due,
        order.nearest_zone,
    )
    if expected_result is None:
        assert result is None
    else:
        assert abs(result - expected_result) < 0.01


_NOW = datetime.datetime(2017, 6, 7, 4, 45, 0)


@pytest.mark.parametrize('mph_doc,thresholds,expected', [
    ({
        'value': 50,
        'updated': _NOW,
        'wall_total_seconds': 7200
    }, None, None),
    ({
        'value': 50,
        'updated': _NOW,
        'wall_total_seconds': 7200
    }, {'3_4': 100}, None),
    ({
         'value': 50,
         'updated': _NOW,
         'wall_total_seconds': 44 * 60
     }, {'3_4': 100}, 100),
    ({
         'value': 50,
         'updated': _NOW,
         'wall_total_seconds': (45 + 17) * 60
     }, {'3_4': 100, '3_3': 50}, (100. * 45. + 17. * 50.) / (45. + 17.)),
    ({
         'value': 50,
         'updated': _NOW,
         'wall_total_seconds': (45 + 60 + 17) * 60
     }, {'3_4': 100, '3_3': 50, '3_2': 25},
     (100. * 45. + 60. * 50. + 17. * 25.) / (45. + 60. + 17.))
])
def test_get_weighted_threshold(mph_doc, thresholds, expected):
    mph_doc = dbh.mph_results.Doc(mph_doc)
    actual = mph._get_weighted_threshold(mph_doc, thresholds, 'UTC')
    if expected is None:
        assert actual is None
    else:
        assert abs(actual - expected) < 1


@pytest.mark.filldb(order_proc='calc_on_order_time')
@pytest.inline_callbacks
def test_calc_on_order_time():
    proc = yield dbh.order_proc.Doc.find_one_by_id(
        '0ece815749aa47ce802479a0962d45b5'
    )
    intervals = mph._load_intervals(
        '1956790819_e87c186760164085bf3963ef17764387', [proc]
    )
    assert intervals
    assert int(mph._calc_on_order_time(intervals)) / 60 == 78
