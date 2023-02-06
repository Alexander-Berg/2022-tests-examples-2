# -*- coding: utf-8 -*-

import datetime

import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import dbh
from taxi.internal import promotions_manager


@pytest.mark.filldb(_fill=False)
@pytest.mark.now('2015-06-23 19:00:00+03')
@pytest.mark.parametrize('begin_date,end_date,is_active', [
    ('2015-01-01', '2015-01-05', False),
    ('2015-01-01', '2015-12-31', True),
    ('2015-12-01', '2015-12-31', False),
])
def test_promotion_is_active(begin_date, end_date, is_active):
    begin_time = datetime.datetime.strptime(begin_date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    handler = promotions_manager.BasePromotionHandler(
        begin_time, end_time, [], [], begin_time
    )
    assert is_active == handler.is_active()


@pytest.mark.parametrize('price,performer_class,request_class,expected_promo', [
    (4000000, ['econom'], ['econom'], []),
    (4000000, ['business'], ['business'], []),
    (
        2000000, ['business'], ['econom'],
        ['higher_class_car_business', 'higher_class_car'],
    ),
    (1000000, ['business'], ['econom'], []),
    (
        4000000, ['vip'], ['econom'],
        ['higher_class_car_vip', 'higher_class_car'],
    ),
    (3000000, ['vip'], ['econom'], []),
    (4000000, ['vip'], ['business', 'vip'], []),
    (
            4000000, ['vip'], ['business'],
            ['higher_class_car_vip', 'higher_class_car'],
    ),
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_higher_class_calculation(
        price, performer_class, request_class, expected_promo,
        patch):

    driver_docs = [
        {
            'car': {
                'allowed_classes': performer_class,
                'price': price,
            },
            '_id': '905254_141590',
        },
    ]

    db.cities.save({
        '_id': 'msk',
        'classification_rules': [
            ('business', 'add', '1000000', 5),
            ('vip', 'delete', '2000000', 5),
        ],
    })

    @patch('taxi.internal.driver_manager.get_driver_by_clid_uuid')
    @async.inline_callbacks
    def get_driver_by_clid_uuid(driver_id, projection_fields, consumer_name):
        yield
        for doc in driver_docs:
            if driver_id == doc['_id']:
                result = dbh.drivers.Doc(doc)
        async.return_value(result)

    @patch('random.random')
    def random():
        return 0.0  # Because there is some logic about probabilities.

    promo_handler = yield promotions_manager.HigherClassCarPromoHandler(
        datetime.datetime.min, datetime.datetime.max,
        [], datetime.datetime.utcnow(), None
    )
    proc = dbh.order_proc.Doc({
        'candidates': [{
            'driver_id': '905254_141590',
            'car_number': '55'
        }]
    })
    performer = proc.indexed_candidates[0]
    assert performer.car_number == '55'
    soon_proc = dbh.order_proc.Doc(order={
        '_type': 'soon',
        'city': 'msk',
        'request': {
            'class': request_class,
        },
    })
    granted_promotions = yield promo_handler.on_driver_assigned(
        soon_proc, performer, None
    )
    assert granted_promotions == expected_promo

    urgent_proc = dbh.order_proc.Doc(order={
        '_id': 'orderid',
        'city': 'msk',
        '_type': 'urgent',
        'request': {
            'class': request_class,
        },
    })
    granted_promotions = yield promo_handler.on_driver_assigned(
        urgent_proc, performer, None
    )
    assert granted_promotions == expected_promo


@pytest.inline_callbacks
def test_list_promotions():
    promos = yield promotions_manager.list_supported_promotions()
    assert (
        {promo['_id'] for promo in promos} ==
        {promotions_manager.HigherClassCarPromoHandler.PROMOTION_NAME}
    )


@pytest.inline_callbacks
def test_update_promo_settings():
    promo = (yield promotions_manager.list_supported_promotions())[0]

    # normal case
    promo['cities'] = 'Saratov'
    yield promotions_manager.update_promotion_settings(promo['_id'], promo)
    assert (yield db.promotions.find_one(promo['_id']))['cities'] == 'Saratov'

    # not found
    with pytest.raises(promotions_manager.NotFound):
        yield promotions_manager.update_promotion_settings('lalala', promo)

    # race
    promo['updated'] = datetime.datetime.utcnow()
    with pytest.raises(promotions_manager.RaceCondition):
        yield promotions_manager.update_promotion_settings(promo['_id'], promo)
