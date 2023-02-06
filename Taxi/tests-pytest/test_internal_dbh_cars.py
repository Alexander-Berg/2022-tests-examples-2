import datetime

import pytest

from taxi.internal import dbh


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('raw_doc,expected_model', [
    ({'model': 'camry', 'raw_model': 'CAmRY'}, 'camry'),
    ({'raw_model': 'CAmRY'}, 'CAmRY'),
    ({}, None),
])
def test_any_model_property(raw_doc, expected_model):
    doc = dbh.cars.Doc(raw_doc)
    assert doc.any_model == expected_model


@pytest.inline_callbacks
def _check_history(car_numbers, expected_history):
    blacklist_history_docs = yield dbh.blacklist_history.Doc.find_many(
        {
            dbh.blacklist_history.Doc.car_number: {'$in': car_numbers}
        }
    )
    blacklist_history = [dict(blacklist_history_doc)
                         for blacklist_history_doc in blacklist_history_docs]
    for item in blacklist_history:
        item.pop('_id')
        item['details'].pop('till', None)
    assert blacklist_history == expected_history


@pytest.mark.now('2018-01-01T00:00:00')
@pytest.mark.parametrize('car_numbers,expected_history', [
    (
        ['TEST_NUMBER_2'],
        [
            {
                'car_number': 'TEST_NUMBER_2',
                'created': datetime.datetime(2018, 1, 1),
                'blacklisted': True,
                'details': {
                    'login': 'test_login',
                    'at': datetime.datetime(2018, 1, 1),
                    'otrs_ticket': 'test_ticket',
                    'reason': 'test_reason'
                }
            }
        ]
    )
])
@pytest.inline_callbacks
def test_add_to_blacklist(car_numbers, expected_history):
    now = datetime.datetime.utcnow()
    yield dbh.cars.Doc.add_to_blacklist(
        car_numbers, 'test_login', 'test_reason', 'test_ticket', now)
    cars = yield dbh.cars.Doc.find_many(
        {
            '_id': {'$in': car_numbers}
        }
    )
    assert cars
    for car in cars:
        assert car.blacklisted
    yield _check_history(car_numbers, expected_history)


@pytest.mark.now('2018-01-01T00:00:00')
@pytest.mark.parametrize('car_numbers,expected_history', [
    (
        ['TEST_NUMBER_1'],
        [
            {
                'car_number': 'TEST_NUMBER_1',
                'created': datetime.datetime(2018, 1, 1),
                'blacklisted': False,
                'details': {
                    'at': datetime.datetime(2018, 1, 1),
                    'login': 'test_login',
                    'otrs_ticket': 'test_ticket',
                    'reason': 'test_reason'
                }
            }
        ]
    )
])
@pytest.inline_callbacks
def test_remove_from_blacklist(car_numbers, expected_history):
    yield dbh.cars.Doc.remove_from_blacklist_manually(
        car_numbers, 'test_login', 'test_reason', 'test_ticket')
    cars = yield dbh.cars.Doc.find_many(
        {
            '_id': {'$in': car_numbers}
        }
    )
    assert cars
    for car in cars:
        assert not car.blacklisted
    yield _check_history(car_numbers, expected_history)
