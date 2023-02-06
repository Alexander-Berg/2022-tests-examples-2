import datetime
import pytest

from taxi.internal import dbh
from taxiadmin import promotion_controllers


@pytest.mark.filldb(_fill=False)
def test_serialization_circle():
    """Test that if we serialize and derserialize object,
    we get the same exact one
    """
    doc = {
        '_id': 'id',
        dbh.promotions.Doc.begin_time: datetime.datetime(1901, 1, 1),
        dbh.promotions.Doc.end_time: datetime.datetime(2001, 2, 2),
        dbh.promotions.Doc.updated: datetime.datetime(
            3000, 3, 3, 3, 3, 3, microsecond=12685
        ),
        dbh.promotions.Doc.cities: ['Moscow', 'Novgorod'],
        dbh.promotions.Doc.zones: ['moscow', 'novgorod'],
        dbh.promotions.Doc.config: {'key': 'value'}
    }
    controller = promotion_controllers._BasePromotionController()
    result = controller.deserialize(controller.serialize(doc))
    assert '_id' not in result
    result['_id'] = 'id'
    assert result == doc


@pytest.mark.filldb(_fill=False)
def test_serialization_works():
    doc = {
        '_id': 'id',
        dbh.promotions.Doc.begin_time: datetime.datetime(1901, 1, 1),
        dbh.promotions.Doc.end_time: datetime.datetime(2001, 2, 2),
        dbh.promotions.Doc.updated: datetime.datetime(
            3000, 3, 3, 3, 3, 3, microsecond=12685
        ),
        dbh.promotions.Doc.cities: ['Moscow', 'Novgorod'],
        dbh.promotions.Doc.zones: ['moscow', 'novgorod'],
        dbh.promotions.Doc.config: {'key': 'value'}
    }
    controller = promotion_controllers._BasePromotionController()
    result = controller.serialize(doc)
    assert {
        '_id',
        dbh.promotions.Doc.begin_time,
        dbh.promotions.Doc.end_time,
        dbh.promotions.Doc.config,
        dbh.promotions.Doc.cities,
        dbh.promotions.Doc.zones,
        dbh.promotions.Doc.updated,
    } == set(result.keys())
