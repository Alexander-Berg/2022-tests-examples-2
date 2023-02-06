# coding=utf-8
from __future__ import unicode_literals

import datetime
import pytest

from taxi.core import db, async
from taxi.internal import permit_whitelist
from taxi.util import helpers


@pytest.mark.now('2018-02-05')
@pytest.mark.parametrize('car_numbers,till,expected_history', [
    (['AB001', 'АВ002'], datetime.datetime(2018, 3, 5), [
        {
            'car_number': 'АВ001',
            'login': 'test_login',
            'created': datetime.datetime(2018, 2, 5),
            'whitelisted': True,
        },
        {
            'car_number': 'АВ001',
            'login': 'test_login',
            'created': datetime.datetime(2018, 2, 5),
            'whitelisted': True,
            'till': datetime.datetime(2018, 3, 5),
            'is_last': True
        },
        {
            'car_number': 'АВ002',
            'login': 'test_login',
            'created': datetime.datetime(2018, 2, 5),
            'whitelisted': True,
            'till': datetime.datetime(2018, 3, 5),
            'is_last': True,
        }
    ]),
    (['AB003'], None, [
        {
            'car_number': 'АВ003',
            'login': 'test_login',
            'created': datetime.datetime(2018, 2, 5),
            'whitelisted': True,
            'is_last': True,
        }
    ])
])
@pytest.inline_callbacks
def test_add_to_whitelist(car_numbers, till, expected_history):
    yield permit_whitelist.add_to_whitelist(
        car_numbers=car_numbers,
        login='test_login',
        till=till
    )
    car_numbers = [helpers.clean_number(car_number)
                   for car_number in car_numbers]
    whitelist_after = (yield db.static.find_one({
        '_id': permit_whitelist.PERMIT_WHITELIST_STATIC_DOC_ID
    }))[permit_whitelist.CAR_NUMBERS_FIELD]
    for car_number in car_numbers:
        assert car_number in whitelist_after
    history_docs = yield db.whitelist_history.find({
        'car_number': {'$in': car_numbers}
    }).run()
    for doc in history_docs:
        doc.pop('_id')
    assert sorted(history_docs) == sorted(expected_history)


@pytest.mark.now('2018-02-05')
@pytest.mark.parametrize('car_numbers,expected_history', [
    (['AB004', 'АВ005'], [
        {
            'car_number': 'АВ004',
            'login': 'test_login',
            'created': datetime.datetime(2018, 2, 5),
            'whitelisted': True,
        },
        {
            'car_number': 'АВ004',
            'login': 'test_login',
            'created': datetime.datetime(2018, 2, 5),
            'whitelisted': False,
            'is_last': True,
        },
        {
            'car_number': 'АВ005',
            'login': 'test_login',
            'created': datetime.datetime(2018, 2, 5),
            'whitelisted': False,
            'is_last': True,
        }
    ])
])
@pytest.inline_callbacks
def test_remove_from_whitelist(car_numbers, expected_history):
    whitelist_before = (yield db.static.find_one({
        '_id': permit_whitelist.PERMIT_WHITELIST_STATIC_DOC_ID
    }))[permit_whitelist.CAR_NUMBERS_FIELD]
    clean_numbers = [helpers.clean_number(car_number)
                   for car_number in car_numbers]
    for clean_number in clean_numbers:
        assert clean_number in whitelist_before
    yield permit_whitelist.remove_from_whitelist(
        car_numbers=car_numbers,
        login='test_login',
    )
    whitelist_after = (yield db.static.find_one({
        '_id': permit_whitelist.PERMIT_WHITELIST_STATIC_DOC_ID
    }))[permit_whitelist.CAR_NUMBERS_FIELD]
    for clean_number in clean_numbers:
        assert clean_number not in whitelist_after
    history_docs = yield db.whitelist_history.find({
        'car_number': {'$in': clean_numbers}
    }).run()
    for doc in history_docs:
        doc.pop('_id')
    assert sorted(history_docs) == sorted(expected_history)


@pytest.mark.now('2018-02-06')
@pytest.inline_callbacks
def test_remove_expired():
    expected = ['АВ007', 'АВ008']
    count = yield permit_whitelist.remove_expired(
        login='test_robot_login',
        now=datetime.datetime.utcnow()
    )
    assert count == 2
    whitelist_after = (yield db.static.find_one({
        '_id': permit_whitelist.PERMIT_WHITELIST_STATIC_DOC_ID
    }))[permit_whitelist.CAR_NUMBERS_FIELD]
    for car_number in expected:
        assert car_number not in whitelist_after
    history_docs = yield db.whitelist_history.find({
        'car_number': {'$in': expected}
    }).run()
    added_docs = [doc for doc in history_docs
                  if doc['login'] == 'test_robot_login']
    assert len(added_docs) == 2


@pytest.inline_callbacks
def test_get_whitelist_details(patch):
    @patch('taxi.internal.driver_manager._set_color')
    @async.inline_callbacks
    def _set_color(raw_color, car_doc):
        yield
        if raw_color == u'Красный':
            car_doc['color_code'] = 'red'
        elif raw_color == u'Серый':
            car_doc['color_code'] = 'gray'
        car_doc['color'] = raw_color

    @patch('taxi.internal.driver_manager._set_brand_model')
    @async.inline_callbacks
    def _set_brand_model(brand, model, car_doc):
        yield
        car_doc['model'] = model

    expected = [
        {
            'added': datetime.datetime(2018, 1, 1),
            'car_number': 'АВ006',
            'till': datetime.datetime(2018, 3, 6),
            'model': 'Toyota Verso',
            'age': 2014,
            'permit': '12345',
            'color': 'Красный',
            'login': 'test_login'
        },
        {
            'added': datetime.datetime(2018, 1, 2),
            'car_number': 'АВ007',
            'till': datetime.datetime(2018, 1, 31),
            'model': 'Lexus LS',
            'age': 2016,
            'color': 'Серый',
            'login': 'test_login'
        }
    ]
    result = yield permit_whitelist.get_whitelist_details(
        skip=2, limit=2, pattern='ab00')
    assert result['total'] == 5
    assert sorted(result['items']) == sorted(expected)
