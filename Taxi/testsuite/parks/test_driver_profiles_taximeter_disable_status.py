import json

import pytest


ENDPOINT_URL = '/driver-profiles/taximeter-disable-status'
DRIVER_UPDATED_TRIGGER_URL = (
    '/taximeter-xservice.taxi.yandex.net/' 'utils/driver-updated-trigger'
)


AUTHOR_YA_HEADERS = {
    'X-Ya-User-Ticket': '_!fake!_ya-11',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Real-Ip': '1.2.3.4',
}

AUTHOR_YA_UNREAL_HEADERS = {
    'X-Ya-User-Ticket': 'unreal_user_ticket',
    'X-Ya-User-Ticket-Provider': 'unreal_user_ticket_provider',
    'X-Real-Ip': '12.34.56.78',
}

OK_PUT_PARAM = {'disabled': True, 'disable_message': 'yeah boi'}


OK_REMOVE_PARAM = {'disabled': False, 'disable_message': ''}


BAD_REQUEST_PARAMS = [
    (
        {'disabled': False},
        {'error': {'text': 'disable_message must be present'}},
    ),
    (
        {'disable_message': 'hmmm'},
        {'error': {'text': 'disabled must be present'}},
    ),
]


NOT_FOUND_PARAMS = [
    (
        'not existed park id',
        'superDriver',
        {'error': {'text': 'driver not found'}},
    ),
    (
        '222333',
        'not existed driver id',
        {'error': {'text': 'driver not found'}},
    ),
]

CHANGE_LOG_PARAMS = [
    (
        {'disabled': False, 'disable_message': 'you gay'},
        {
            'Disabled': {'current': 'false', 'old': 'true'},
            'DisableMessage': {'current': 'you gay', 'old': 'some reason'},
        },
    ),
    (
        {'disabled': True, 'disable_message': ''},
        {'DisableMessage': {'current': '', 'old': 'some reason'}},
    ),
]


@pytest.fixture
def driver_updated_trigger(mockserver):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def mock_callback(request):
        return {}

    return mock_callback


@pytest.mark.config(TVM_USER_TICKET_USE_FAKE_CONTEXT=True)
@pytest.mark.redis_store(['sadd', '222333:Driver:Disabled', 'stuff driver'])
def test_put_ok(
        db,
        redis_store,
        taxi_parks,
        driver_updated_trigger,
        dispatcher_access_control,
):
    response = taxi_parks.put(
        ENDPOINT_URL,
        params={'park_id': '222333', 'id': 'superDriver'},
        data=json.dumps(OK_PUT_PARAM),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200
    assert len(redis_store.smembers('222333:Driver:Disabled')) == 2
    assert (
        redis_store.hget('Driver:DisableMessage' ':222333', 'superDriver')
        == b'yeah boi'
    )
    assert response.json() == OK_PUT_PARAM


@pytest.mark.config(TVM_USER_TICKET_USE_FAKE_CONTEXT=True)
@pytest.mark.redis_store(
    ['sadd', '222333:Driver:Disabled', 'superDriver'],
    ['hset', 'Driver:DisableMessage:222333', 'superDriver', 'some reason'],
)
def test_remove_ok(
        db,
        redis_store,
        taxi_parks,
        dispatcher_access_control,
        driver_updated_trigger,
):
    response = taxi_parks.put(
        ENDPOINT_URL,
        params={'park_id': '222333', 'id': 'superDriver'},
        data=json.dumps(OK_REMOVE_PARAM),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200
    assert len(redis_store.smembers('2223333:Driver:Disabled')) == 0
    assert (
        redis_store.hget('Driver:DisableMessage:222333', 'superDriver') is None
    )
    assert response.json() == OK_REMOVE_PARAM


@pytest.mark.parametrize('request_json, expected_response', BAD_REQUEST_PARAMS)
def test_bad_request(
        db,
        taxi_parks,
        request_json,
        expected_response,
        dispatcher_access_control,
        driver_updated_trigger,
):
    response = taxi_parks.put(
        ENDPOINT_URL,
        params={'park_id': '222333', 'id': 'superDriver'},
        data=json.dumps(request_json),
        headers=AUTHOR_YA_UNREAL_HEADERS,
    )

    assert response.status_code == 400
    assert response.json() == expected_response


@pytest.mark.parametrize('park, driver, error_text', NOT_FOUND_PARAMS)
def test_not_found(
        db,
        taxi_parks,
        park,
        driver,
        error_text,
        dispatcher_access_control,
        driver_updated_trigger,
):
    response = taxi_parks.put(
        ENDPOINT_URL,
        params={'park_id': park, 'id': driver},
        data=json.dumps(OK_PUT_PARAM),
        headers=AUTHOR_YA_UNREAL_HEADERS,
    )

    assert response.status_code == 404
    assert response.json() == error_text


@pytest.mark.config(TVM_USER_TICKET_USE_FAKE_CONTEXT=True)
@pytest.mark.redis_store(
    ['sadd', '222333:Driver:Disabled', 'superDriver'],
    ['hset', 'Driver:DisableMessage:222333', 'superDriver', 'some reason'],
)
@pytest.mark.parametrize('request_json, change_log', CHANGE_LOG_PARAMS)
def test_change_log(
        taxi_parks,
        dispatcher_access_control,
        driver_updated_trigger,
        sql_databases,
        request_json,
        change_log,
):
    response = taxi_parks.put(
        ENDPOINT_URL,
        params={'park_id': '222333', 'id': 'superDriver'},
        data=json.dumps(request_json),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200
    assert dispatcher_access_control.times_called == 1

    cursor = sql_databases.taximeter.conn.cursor()
    query = (
        'SELECT * FROM changes_0 WHERE object_id=\'superDriver\''
        ' ORDER BY date DESC'
    )
    cursor.execute(query)
    rows = cursor.fetchall()
    change = list(rows[0])
    assert change[0] == '222333'
    # skip id and date
    change[8] = json.loads(change[8])
    assert change[3:] == [
        'superDriver',
        'Taximeter disable status',
        '1',
        'Boss',
        len(change_log),
        change_log,
        '1.2.3.4',
    ]
