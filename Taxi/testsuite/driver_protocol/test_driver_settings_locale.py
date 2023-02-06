import datetime

import bson.timestamp
import pytest


def test_check_invalid_session(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'test_session', 'driver')

    response = taxi_driver_protocol.post('driver/settings/locale')
    assert response.status_code == 401

    response = taxi_driver_protocol.post('driver/settings/locale?db=1488')
    assert response.status_code == 401

    response = taxi_driver_protocol.post(
        'driver/settings/locale?db=1488&session=unknown_session',
    )
    assert response.status_code == 401


def test_invalid_parameters(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('1488', 'test_session', 'driver')

    response = taxi_driver_protocol.post(
        'driver/settings/locale?db=1488&session=test_session',
    )
    assert response.status_code == 400


def test_unsupported_locale(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('1488', 'test_session', 'driver')

    def post_locale(locale):
        return taxi_driver_protocol.post(
            'driver/settings/locale?db=1488&session=test_session',
            data={'locale': locale},
        )

    # locale is not present both in config and country settings
    response = post_locale('strange_locale')
    assert response.status_code == 400

    # locale is present in config but not in country settings
    response = post_locale('az')
    assert response.status_code == 400

    # locale is present in country settings but not in config
    response = post_locale('et')
    assert response.status_code == 400


def test_supported_locale_saves_in_database(
        db, taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'test_session', 'driver')

    def load_driver_under_test():
        return db.dbdrivers.find_one(
            {'driver_id': 'driver', 'park_id': '1488'},
        )

    assert 'locale' not in load_driver_under_test()

    response = taxi_driver_protocol.post(
        'driver/settings/locale?db=1488&session=test_session',
        data={'locale': 'ru'},
    )

    assert response.status_code == 200
    assert load_driver_under_test()['locale'] == 'ru'


def check_updated(updated_field):
    assert isinstance(updated_field, datetime.datetime)
    delta = datetime.datetime.utcnow() - updated_field
    assert datetime.timedelta() <= delta < datetime.timedelta(minutes=1)


def check_updated_ts(updated_field):
    assert isinstance(updated_field, bson.timestamp.Timestamp)
    check_updated(datetime.datetime.utcfromtimestamp(updated_field.time))
    assert updated_field.inc > 0


def test_update_updated_ts(
        db, taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'test_session', 'driver')

    db.dbdrivers.update(
        {'driver_id': 'driver', 'park_id': '1488'},
        {
            '$set': {
                'updated_ts': bson.timestamp.Timestamp(11111, 5),
                'modified_date': datetime.datetime(year=2019, month=1, day=1),
            },
        },
    )

    def load_driver_under_test():
        return db.dbdrivers.find_one(
            {'driver_id': 'driver', 'park_id': '1488'},
        )

    driver_doc = load_driver_under_test()
    assert driver_doc['updated_ts'] == bson.timestamp.Timestamp(11111, 5)
    assert driver_doc['modified_date'] == datetime.datetime(
        year=2019, month=1, day=1,
    )

    response = taxi_driver_protocol.post(
        'driver/settings/locale?db=1488&session=test_session',
        data={'locale': 'ru'},
    )

    assert response.status_code == 200

    # Check modified_date and updated_ts
    driver_doc = load_driver_under_test()
    check_updated(driver_doc['modified_date'])
    check_updated_ts(driver_doc['updated_ts'])


@pytest.mark.config(COUNTRIES_DATA_SOURCE='database')
def test_supported_locale_save_in_database_with_countries_data_source_database(
        db, taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'test_session', 'driver')

    def load_driver_under_test():
        return db.dbdrivers.find_one(
            {'driver_id': 'driver', 'park_id': '1488'},
        )

    assert 'locale' not in load_driver_under_test()

    response = taxi_driver_protocol.post(
        'driver/settings/locale?db=1488&session=test_session',
        data={'locale': 'ru'},
    )

    assert response.status_code == 200
    assert load_driver_under_test().get('locale') == 'ru'
