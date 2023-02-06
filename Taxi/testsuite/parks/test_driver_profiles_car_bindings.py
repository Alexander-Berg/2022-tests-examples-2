import datetime
import json

import pytest

from . import error
from .test_cars import AUTHOR_DRIVER_HEADERS
from .test_cars import AUTHOR_FLEET_API_HEADERS
from .test_cars import AUTHOR_YA_HEADERS
from .test_cars import CHANGE_LOG_AUTHOR_PARAMS


ENDPOINT_URL = '/driver-profiles/car-bindings'
MOCK_URL = '/taximeter-xservice.taxi.yandex.net/utils/driver-updated-trigger'
PARK_ID = '1488'
OLD_CAR_ID = 'old_car_id'
NEW_CAR_ID = 'new_car_id'
OLD_MODIFIED_DATE = datetime.datetime(2018, 10, 1)  # see db_dbdrivers
NEW_MODIFIED_DATE = datetime.datetime(2018, 11, 1)
STR_NEW_MODIFIED_DATE = NEW_MODIFIED_DATE.strftime('%Y-%m-%dT%H:%M:%S+0000')


def get_driver(db, driver_id):
    return db.dbdrivers.find_one({'driver_id': driver_id})


def parse_date(date):
    return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S+0000')


def check_message(message, old_driver, new_driver):
    # I need to parse ObjectId('...') to compare id so i prefer
    # not to compare them because no one really need them
    del message['new_driver']['_id']
    del message['old_driver']['_id']
    del old_driver['_id']
    del new_driver['_id']
    message['old_driver']['modified_date'] = parse_date(
        message['old_driver']['modified_date'],
    )
    message['new_driver']['modified_date'] = parse_date(
        message['new_driver']['modified_date'],
    )

    assert message['old_driver']['modified_date'] == OLD_MODIFIED_DATE
    # i write current time in modified_date of new driver
    assert message['new_driver']['modified_date'] == NEW_MODIFIED_DATE
    # but dont compare modified_date with time stored in mongo
    # since i can not parametrize mongo current time
    del message['new_driver']['modified_date']
    del new_driver['modified_date']

    assert message['old_driver'] == old_driver
    assert message['new_driver'] == new_driver


@pytest.mark.now(STR_NEW_MODIFIED_DATE)
@pytest.mark.parametrize(
    'author_headers',
    [AUTHOR_YA_HEADERS, AUTHOR_DRIVER_HEADERS, AUTHOR_FLEET_API_HEADERS],
)
@pytest.mark.parametrize(
    'driver_profile_id',
    ['driver_to_change_vehicle', 'driver_for_new_car1', 'driver_for_new_car2'],
)
def test_put_ok(
        db,
        mockserver,
        taxi_parks,
        dispatcher_access_control,
        driver_profile_id,
        author_headers,
):
    old_driver = get_driver(db, driver_profile_id)

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        # driver should be in db when trigger called
        new_driver = get_driver(db, driver_profile_id)
        new_driver.pop('updated_ts')
        assert new_driver['car_id'] == NEW_CAR_ID
        check_message(json.loads(request.data), old_driver, new_driver)
        return '{}'

    response = taxi_parks.put(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': driver_profile_id,
            'car_id': NEW_CAR_ID,
        },
        headers=author_headers,
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 201, response.text
    assert response.json() == {}


def test_put_not_modified(
        db, mockserver, taxi_parks, dispatcher_access_control,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return '{}'

    response = taxi_parks.put(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'driver_to_change_vehicle',
            'car_id': OLD_CAR_ID,
        },
        headers=AUTHOR_YA_HEADERS,
    )

    assert mock_callback.times_called == 0
    assert response.status_code == 200, response.text
    new_driver = get_driver(db, 'driver_to_change_vehicle')
    assert new_driver['car_id'] == OLD_CAR_ID
    assert 'updated_ts' not in new_driver
    assert response.json() == {}


def test_put_no_such_driver(
        db, mockserver, taxi_parks, dispatcher_access_control,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return '{}'

    response = taxi_parks.put(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'no_such_driver',
            'car_id': OLD_CAR_ID,
        },
        headers=AUTHOR_YA_HEADERS,
    )

    assert mock_callback.times_called == 0
    assert response.status_code == 400, response.text
    new_driver = get_driver(db, 'driver_to_change_vehicle')
    assert new_driver['car_id'] == OLD_CAR_ID
    assert new_driver['modified_date'] == OLD_MODIFIED_DATE
    assert response.json() == error.make_error_response('no such driver')


@pytest.mark.now(STR_NEW_MODIFIED_DATE)
def test_delete_ok(db, mockserver, taxi_parks, dispatcher_access_control):
    old_driver = get_driver(db, 'driver_to_change_vehicle')

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        # driver should be in db when trigger called
        new_driver = get_driver(db, 'driver_to_change_vehicle')
        new_driver.pop('updated_ts')
        assert new_driver['car_id'] is None
        check_message(json.loads(request.data), old_driver, new_driver)
        return '{}'

    old_driver = get_driver(db, 'driver_to_change_vehicle')
    response = taxi_parks.delete(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'driver_to_change_vehicle',
            'car_id': OLD_CAR_ID,
        },
        headers=AUTHOR_YA_HEADERS,
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 200, response.text
    assert response.json() == {}


def test_delete_not_found(
        db, mockserver, taxi_parks, dispatcher_access_control,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return '{}'

    response = taxi_parks.delete(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'driver_to_change_vehicle',
            'car_id': NEW_CAR_ID,
        },
        headers=AUTHOR_YA_HEADERS,
    )

    assert mock_callback.times_called == 0
    assert response.status_code == 404, response.text
    new_driver = get_driver(db, 'driver_to_change_vehicle')
    assert new_driver['car_id'] == OLD_CAR_ID
    assert new_driver['modified_date'] == OLD_MODIFIED_DATE
    assert response.json() == error.make_error_response('no such binding')


def test_put_no_car_at_all(db, taxi_parks, dispatcher_access_control):
    response = taxi_parks.put(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'driver_to_change_vehicle',
            'car_id': 'net_takogo',
        },
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response('no such car')


def test_put_no_car_in_cache(
        db, taxi_parks, mockserver, testpoint, dispatcher_access_control,
):
    @testpoint('stale_cache')
    def _stale_cache(data):
        return {'cars': True}

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return '{}'

    response = taxi_parks.put(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'driver_to_change_vehicle',
            'car_id': NEW_CAR_ID,
        },
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 201, response.text
    assert response.json() == {}


def test_no_such_car_delete(
        db, redis_store, taxi_parks, dispatcher_access_control,
):
    response = taxi_parks.delete(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'driver_to_change_vehicle',
            'car_id': 'net_takogo',
        },
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 404, response.text
    assert response.json() == error.make_error_response('no such binding')


CHANGE_LOG_PUT_PARAMS = [
    (
        'driver_to_change_vehicle',
        {
            'Car': {'current': 'BMW i8', 'old': 'Audi A6'},
            'CarId': {'current': 'new_car_id', 'old': 'old_car_id'},
        },
    ),
    (
        'driver_for_new_car1',
        {
            'Car': {'current': 'BMW i8', 'old': ''},
            'CarId': {'current': 'new_car_id', 'old': ''},
        },
    ),
]


@pytest.mark.now(STR_NEW_MODIFIED_DATE)
@pytest.mark.parametrize(
    'author_headers, user_id, display_name, client_ip',
    CHANGE_LOG_AUTHOR_PARAMS,
)
@pytest.mark.parametrize(
    'driver_profile_id, expected_change_log', CHANGE_LOG_PUT_PARAMS,
)
def test_put_change_log(
        db,
        mockserver,
        taxi_parks,
        sql_databases,
        dispatcher_access_control,
        author_headers,
        user_id,
        display_name,
        client_ip,
        driver_profile_id,
        expected_change_log,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_taximeter_callback(request):
        # driver should be in db when trigger called
        new_driver = get_driver(db, driver_profile_id)
        new_driver.pop('updated_ts')
        assert new_driver['car_id'] == NEW_CAR_ID
        check_message(json.loads(request.data), old_driver, new_driver)
        return '{}'

    old_driver = get_driver(db, driver_profile_id)

    response = taxi_parks.put(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': driver_profile_id,
            'car_id': NEW_CAR_ID,
        },
        headers=author_headers,
    )

    assert mock_taximeter_callback.times_called == 1
    assert response.status_code == 201, response.text
    assert response.json() == {}

    cursor = sql_databases.taximeter.conn.cursor()
    query = (
        'SELECT * FROM changes_0'
        ' WHERE object_id=\'{}\''
        ' ORDER BY date DESC LIMIT(1)'.format(driver_profile_id)
    )

    cursor.execute(query)
    rows = cursor.fetchall()
    assert len(rows) == 1
    change = list(rows[0])
    assert change[0] == '1488'
    # skip id and date
    change[8] = json.loads(change[8])
    assert change[3:] == [
        driver_profile_id,
        'MongoDB.Docs.Driver.DriverDoc',
        user_id,
        display_name,
        len(expected_change_log),
        expected_change_log,
        client_ip,
    ]


@pytest.mark.now(STR_NEW_MODIFIED_DATE)
@pytest.mark.parametrize(
    'author_headers, user_id, display_name, client_ip',
    CHANGE_LOG_AUTHOR_PARAMS,
)
def test_delete_change_log(
        db,
        mockserver,
        taxi_parks,
        sql_databases,
        dispatcher_access_control,
        author_headers,
        user_id,
        display_name,
        client_ip,
):

    old_driver = get_driver(db, 'driver_to_change_vehicle')

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        # driver should be in db when trigger called
        new_driver = get_driver(db, 'driver_to_change_vehicle')
        new_driver.pop('updated_ts')
        assert new_driver['car_id'] is None
        check_message(json.loads(request.data), old_driver, new_driver)
        return '{}'

    EXPECTED_RESPONSE = {
        'Car': {'current': '', 'old': 'Audi A6'},
        'CarId': {'current': '', 'old': 'old_car_id'},
    }

    response = taxi_parks.delete(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'driver_to_change_vehicle',
            'car_id': OLD_CAR_ID,
        },
        headers=author_headers,
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 200, response.text
    assert response.json() == {}

    cursor = sql_databases.taximeter.conn.cursor()
    query = (
        'SELECT * FROM changes_0'
        ' WHERE object_id=\'driver_to_change_vehicle\''
        ' ORDER BY date DESC LIMIT(1)'
    )
    cursor.execute(query)
    rows = cursor.fetchall()
    assert len(rows) == 1
    change = list(rows[0])
    assert change[0] == '1488'
    # skip id and date
    change[8] = json.loads(change[8])
    assert change[3:] == [
        'driver_to_change_vehicle',
        'MongoDB.Docs.Driver.DriverDoc',
        user_id,
        display_name,
        len(EXPECTED_RESPONSE),
        EXPECTED_RESPONSE,
        client_ip,
    ]


@pytest.mark.now(STR_NEW_MODIFIED_DATE)
def test_no_author(
        db, mockserver, taxi_parks, sql_databases, dispatcher_access_control,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        # driver should be in db when trigger called
        new_driver = get_driver(db, 'driver_to_change_vehicle')
        new_driver.pop('updated_ts')
        return '{}'

    response_delete = taxi_parks.delete(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'driver_to_change_vehicle',
            'car_id': OLD_CAR_ID,
        },
    )

    assert mock_callback.times_called == 0
    assert response_delete.status_code == 400
    assert response_delete.json() == error.make_error_response(
        'An author must be provided',
    )

    response_put = taxi_parks.put(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'driver_to_change_vehicle',
            'car_id': NEW_CAR_ID,
        },
    )

    assert mock_callback.times_called == 0
    assert response_put.status_code == 400
    assert response_delete.json() == error.make_error_response(
        'An author must be provided',
    )


@pytest.mark.now(STR_NEW_MODIFIED_DATE)
@pytest.mark.parametrize(
    'incorrect_author_headers',
    [
        {**AUTHOR_YA_HEADERS, **AUTHOR_DRIVER_HEADERS},
        {**AUTHOR_YA_HEADERS, **AUTHOR_FLEET_API_HEADERS},
        {**AUTHOR_DRIVER_HEADERS, **AUTHOR_FLEET_API_HEADERS},
        {
            **AUTHOR_YA_HEADERS,
            **AUTHOR_DRIVER_HEADERS,
            **AUTHOR_FLEET_API_HEADERS,
        },
    ],
)
def test_incorrect_author(
        db,
        mockserver,
        taxi_parks,
        sql_databases,
        dispatcher_access_control,
        incorrect_author_headers,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        # driver should be in db when trigger called
        return '{}'

    response_delete = taxi_parks.delete(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'driver_to_change_vehicle',
            'car_id': OLD_CAR_ID,
        },
        headers=incorrect_author_headers,
    )

    assert mock_callback.times_called == 0
    assert response_delete.status_code == 400
    assert response_delete.json() == error.make_error_response(
        'Exactly one author must be provided',
    )

    response_put = taxi_parks.put(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'driver_to_change_vehicle',
            'car_id': NEW_CAR_ID,
        },
        headers=incorrect_author_headers,
    )

    assert mock_callback.times_called == 0
    assert response_put.status_code == 400
    assert response_delete.json() == error.make_error_response(
        'Exactly one author must be provided',
    )


def test_courier_put_created(
        taxi_parks, mockserver, dispatcher_access_control,
):
    @mockserver.json_handler(MOCK_URL)
    def trigger_callback(request):
        request.get_data()
        return {}

    response = taxi_parks.put(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'courier_123_without_car',
            'car_id': 'fake_car_1',
        },
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 201, response.text
    assert response.json() == {}
    assert trigger_callback.times_called >= 1


@pytest.mark.parametrize('is_stale_cache', [False, True])
def test_courier_put_ok(taxi_parks, testpoint, mockserver, is_stale_cache):
    @testpoint('stale_cache')
    def _stale_cache(data):
        return {'cars': is_stale_cache, 'driver_profiles': is_stale_cache}

    @mockserver.json_handler(MOCK_URL)
    def trigger_callback(request):
        request.get_data()
        return {}

    response = taxi_parks.put(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'courier_abc_with_fake_car_1',
            'car_id': 'fake_car_1',
        },
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text
    assert response.json() == {}
    assert trigger_callback.times_called == 0


DRIVER_BINDING_ERROR = 'driver cannot be bound to fake car'
COURIER_BINDING_ERROR = 'courier cannot be bound to real car'
CONSTANT_BINDING_ERROR = 'courier car binding cannot be changed'
COURIER_PUT_BAD_PARAMS = [
    ('driver_to_change_vehicle', 'fake_car_1', DRIVER_BINDING_ERROR),
    ('courier_123_without_car', 'new_car_id', COURIER_BINDING_ERROR),
    ('courier_abc_with_fake_car_1', 'new_car_id', CONSTANT_BINDING_ERROR),
    ('courier_abc_with_fake_car_1', 'fake_car_2', CONSTANT_BINDING_ERROR),
]


@pytest.mark.parametrize('driver_id, car_id, message', COURIER_PUT_BAD_PARAMS)
def test_courier_put_bad(
        taxi_parks,
        db,
        mockserver,
        dispatcher_access_control,
        driver_id,
        car_id,
        message,
):
    @mockserver.json_handler(MOCK_URL)
    def trigger_callback(request):
        request.get_data()
        return {}

    response = taxi_parks.put(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': driver_id,
            'car_id': car_id,
        },
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(message)
    assert trigger_callback.times_called == 0


def test_courier_delete_bad(taxi_parks, db, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def trigger_callback(request):
        request.get_data()
        return {}

    response = taxi_parks.delete(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'courier_abc_with_fake_car_1',
            'car_id': 'fake_car_1',
        },
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(CONSTANT_BINDING_ERROR)
    assert trigger_callback.times_called == 0


def test_cannot_change_removed_driver(db, mockserver, taxi_parks):
    expected_response = error.make_error_response('cannot edit removed driver')

    response = taxi_parks.put(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'removed_driver',
            'car_id': 'some_car_id',
        },
        headers=AUTHOR_YA_HEADERS,
    )
    assert response.status_code == 400, response.text
    assert response.json() == expected_response

    response = taxi_parks.delete(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': 'removed_driver',
            'car_id': 'some_car_id',
        },
        headers=AUTHOR_YA_HEADERS,
    )
    assert response.status_code == 400, response.text
    assert response.json() == expected_response
