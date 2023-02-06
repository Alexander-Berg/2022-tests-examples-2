import datetime
import pytest

from taxi.core import db
from taxi.internal import blacklist
from taxi.internal import dbh


def _assert_doc_blacklisted(doc):
    assert doc['is_blacklisted']


def _assert_doc_is_not_blacklisted(doc):
    assert 'is_blacklisted' not in doc


@pytest.inline_callbacks
def test_add_existing_car_to_blacklist():
    plate = u'Z123NG177'
    yield blacklist.append_by_plate(plate, 'login', 'reason', 'otrs_ticket')
    bad_car = yield db.cars.find_one({'_id': plate})
    _assert_doc_blacklisted(bad_car)
    other_car = yield db.cars.find_one({'_id': u'\u0424789\u041c\u0414199'})
    _assert_doc_is_not_blacklisted(other_car)


@pytest.mark.filldb(cars='empty')
@pytest.inline_callbacks
def test_add_new_car_to_blacklist():
    assert (yield db.cars.count()) == 0
    yield blacklist.append_by_plate('w333qz', 'login', 'reason', 'otrs_ticket')
    all_cars = yield db.cars.find().run()
    assert len(all_cars) == 1
    assert 'W333QZ' == all_cars[0]['_id']
    _assert_doc_blacklisted(all_cars[0])


@pytest.inline_callbacks
def test_add_existing_driver_to_blacklist():
    yield blacklist.append_by_license('DD55', 'login', 'reason', 'otrs_ticket')
    first_driver = yield db.unique_drivers.find_one({'_id': 'AA'})
    _assert_doc_is_not_blacklisted(first_driver)
    second_driver = yield db.unique_drivers.find_one({'_id': 'FS'})
    _assert_doc_blacklisted(second_driver)

    yield blacklist.append_by_license('ZZZ777', 'login', 'reason', 'otrs_ticket')
    first_driver = yield db.unique_drivers.find_one({'_id': 'AA'})
    _assert_doc_is_not_blacklisted(first_driver)
    second_driver = yield db.unique_drivers.find_one({'_id': 'FS'})
    _assert_doc_blacklisted(second_driver)

    yield blacklist.append_by_license('RR4321', 'login', 'reason', 'otrs_ticket')
    first_driver = yield db.unique_drivers.find_one({'_id': 'AA'})
    _assert_doc_blacklisted(first_driver)
    second_driver = yield db.unique_drivers.find_one({'_id': 'FS'})
    _assert_doc_blacklisted(second_driver)


@pytest.mark.filldb(unique_drivers='empty')
@pytest.inline_callbacks
def test_add_new_driver_to_blacklist():
    assert (yield db.unique_drivers.count()) == 0
    yield blacklist.append_by_license('Z3QRR', 'login', 'reason', 'otrs_ticket')
    drivers = yield db.unique_drivers.find().run()
    assert len(drivers) == 1
    _assert_doc_blacklisted(drivers[0])
    assert [{'license': 'Z3QRR'}] == drivers[0]['licenses']
    assert [] == drivers[0]['profiles']
    obligatory_fields = set(['licenses', 'profiles', 'created', 'updated'])
    existing_fields = set(drivers[0].iterkeys())
    assert obligatory_fields.issubset(existing_fields)


@pytest.inline_callbacks
def test_remove_car_from_blacklist():
    plate = u'Z123NG177'
    yield blacklist.append_by_plate(plate, 'login', 'reason', 'otrs_ticket')
    yield dbh.cars.Doc.remove_from_blacklist_manually(
        car_numbers=[plate],
        login='login'
    )
    bad_car = yield db.cars.find_one({'_id': plate})
    _assert_doc_is_not_blacklisted(bad_car)


@pytest.inline_callbacks
def test_remove_existing_driver_from_blacklist():
    # it does not matter which license we use
    query = {'_id': 'FS'}
    user_with_two_licenses = yield db.unique_drivers.find_one(query)
    _assert_doc_is_not_blacklisted(user_with_two_licenses)

    yield blacklist.append_by_license('ZZZ777', 'login', 'reason', 'otrs_ticket')
    user_with_two_licenses = yield db.unique_drivers.find_one(query)
    _assert_doc_blacklisted(user_with_two_licenses)

    yield dbh.unique_drivers.Doc.remove_from_blacklist_manually(
        licenses=['DD55'],
        login='login'
    )
    user_with_two_licenses = yield db.unique_drivers.find_one(query)
    _assert_doc_is_not_blacklisted(user_with_two_licenses)


@pytest.mark.filldb(cars='empty', unique_drivers='empty')
@pytest.mark.now('2016-03-30 09:51:00+03')
@pytest.inline_callbacks
def test_blacklist_details():
    yield blacklist.append_by_plate(
        'z123456', 'valesini', 'I do not like him', '#567890'
    )
    cars = yield db.cars.find().run()
    assert len(cars) == 1
    assert 'Z123456' == cars[0]['_id']
    assert {
        'at': datetime.datetime.utcnow(),
        'login': 'valesini',
        'reason': 'I do not like him',
        'otrs_ticket': '#567890',
    } == cars[0]['blacklist_details']

    yield blacklist.append_by_license(
        'z123456', 'valesini', 'I do not like him', '#567890',
        datetime.date(2016, 5, 1),
    )
    drivers = yield db.unique_drivers.find().run()
    assert len(drivers) == 1
    assert [{'license': 'Z123456'}] == drivers[0]['licenses']
    assert {
        'at': datetime.datetime.utcnow(),
        'login': 'valesini',
        'reason': 'I do not like him',
        'otrs_ticket': '#567890',
        'till': datetime.datetime(2016, 5, 1, 21)
    } == drivers[0]['blacklist_details']
