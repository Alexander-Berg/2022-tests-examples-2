# encoding=utf-8
import json

import pytest

from . import error
from . import utils


"""
Все тесты в test_driver_profiles_profile.py проверяют как PUT,
так и соответствующий ему PATCH. Тч здесь остается проверить
только специфичные для PATCH сценарии.
"""

ENDPOINT_URL = '/driver-profiles/profile-patch'
INTERNAL_ENDPOINT_URL = '/internal/driver-profiles/profile-patch'

AUTHOR_YA_HEADERS = {
    'X-Ya-User-Ticket': '_!fake!_ya-11',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Real-Ip': '1.2.3.4',
}
PLATFORM_HEADERS = {'X-Ya-Service-Name': 'mock'}

ENDPOINT_URLS_WITH_AUTHOR = [
    # endpoint_url, headers,
    # dac_times_called, author_id, author_name, author_ip
    (ENDPOINT_URL, AUTHOR_YA_HEADERS, 1, '1', 'Boss', '1.2.3.4'),
    (INTERNAL_ENDPOINT_URL, PLATFORM_HEADERS, 0, 'mock', 'Platform', ''),
]
ENDPOINT_URLS = [x[:2] for x in ENDPOINT_URLS_WITH_AUTHOR]

DRIVER_UPDATED_TRIGGER_URL = (
    '/taximeter-xservice.taxi.yandex.net/' 'utils/driver-updated-trigger'
)


BAD_PARAMS = [
    (
        {'driver_profile': {'unset': 'some_field'}},
        'driver_profile.unset must be an array',
    ),
    ({'accounts': []}, 'accounts are not allowed in patch request'),
    # test required field errors
    (
        {'driver_profile': {'set': {'work_rule_id': ''}}},
        (
            'driver_profile.set.work_rule_id '
            'must be an utf-8 string without BOM with '
            'length >= 1 and <= 500'
        ),
    ),
    (
        {
            'driver_profile': {
                'set': {'work_rule_id': 'asd'},
                'unset': ['work_rule_id'],
            },
        },
        (
            'driver_profile.unset can not contain `work_rule_id` '
            'when set contains it'
        ),
    ),
    # test optional fields
    (
        {
            'driver_profile': {
                'set': {'check_message': 'asd'},
                'unset': ['check_message'],
            },
        },
        (
            'driver_profile.unset can not contain `check_message`'
            ' when set contains it'
        ),
    ),
]


@pytest.mark.parametrize('endpoint_url, headers', ENDPOINT_URLS)
@pytest.mark.parametrize('request_body, error_message', BAD_PARAMS)
def test_bad(taxi_parks, endpoint_url, headers, request_body, error_message):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '0'},
        data=json.dumps(request_body),
        headers=headers,
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(error_message)


def get_driver(db, park_id, driver_id):
    return db.dbdrivers.find_one({'park_id': park_id, 'driver_id': driver_id})


@pytest.fixture
def driver_updated_trigger(mockserver):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def mock_callback(request):
        return {}

    return mock_callback


OK_PARAMS = [
    # no changes
    ({'driver_profile': {}}, {'driver_profile': {}}, [], {}, {}),
    # change required
    (
        {'driver_profile': {'set': {'work_rule_id': 'other_rule_id'}}},
        {'driver_profile': {'work_rule_id': 'other_rule_id'}},
        ['rule_id'],
        {'rule_id': 'other_rule_id'},
        {'RuleId': {'old': 'rule_zero', 'current': 'other_rule_id'}},
    ),
    # add optional
    (
        {'driver_profile': {'set': {'comment': '678'}}},
        {'driver_profile': {'comment': '678'}},
        ['comment'],
        {'comment': '678'},
        {'Comment': {'old': '', 'current': '678'}},
    ),
    # change optional
    (
        {'driver_profile': {'set': {'check_message': 'Petrov'}}},
        {'driver_profile': {'check_message': 'Petrov'}},
        ['check_message'],
        {'check_message': 'Petrov'},
        {'CheckMessage': {'old': 'qwe', 'current': 'Petrov'}},
    ),
    # remove optional which is absent
    (
        {'driver_profile': {'unset': ['comment']}},
        {'driver_profile': {}},
        [],
        {},
        {},
    ),
    # remove optional
    (
        {'driver_profile': {'unset': ['check_message']}},
        {'driver_profile': {}},
        ['check_message'],
        {},
        {'CheckMessage': {'old': 'qwe', 'current': ''}},
    ),
]


@pytest.mark.sql('taximeter', 'SELECT 1')
@pytest.mark.parametrize(
    'endpoint_url, headers, '
    'dac_times_called, author_id, author_name, author_ip',
    ENDPOINT_URLS_WITH_AUTHOR,
)
@pytest.mark.parametrize(
    'request_body, expected_response, '
    'affected_db_fields, expected_db_fields,'
    'expected_change_log',
    OK_PARAMS,
)
def test_patch_ok(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        db,
        mockserver,
        sql_databases,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_identifications_bulk_store,
        personal_phones_bulk_store,
        personal_tins_bulk_store,
        endpoint_url,
        headers,
        dac_times_called,
        author_id,
        author_name,
        author_ip,
        request_body,
        expected_response,
        affected_db_fields,
        expected_db_fields,
        expected_change_log,
        driver_work_rules,
):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def driver_updated_trigger(request):
        request.get_data()  # to save request
        return '{}'

    driver_in_mongo_before = utils.datetime_to_str(get_driver(db, '123', '0'))

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '0'},
        data=json.dumps(request_body),
        headers=headers,
    )

    assert response.status_code == 200, response.text

    # check mocks call times
    assert dispatcher_access_control.times_called == dac_times_called
    assert driver_updated_trigger.times_called == 1

    assert personal_driver_licenses_bulk_store.times_called == 0
    assert personal_emails_bulk_store.times_called == 0
    assert personal_identifications_bulk_store.times_called == 0
    assert personal_phones_bulk_store.times_called == 0
    assert personal_tins_bulk_store.times_called == 0

    # check stored driver
    driver_in_mongo = utils.datetime_to_str(get_driver(db, '123', '0'))
    assert driver_in_mongo.pop('updated_ts') != driver_in_mongo_before.pop(
        'updated_ts',
    )
    assert driver_in_mongo.pop('modified_date') != driver_in_mongo_before.pop(
        'modified_date',
    )
    expected_in_mongo = utils.replace(
        utils.remove(driver_in_mongo_before, affected_db_fields),
        expected_db_fields,
    )
    assert driver_in_mongo == expected_in_mongo

    # check response
    expected_response['driver_profile']['id'] = '0'
    expected_response['driver_profile']['park_id'] = '123'
    response_to_check = response.json()
    assert response_to_check == expected_response

    # check driver_updated_message
    trigger_request_data = driver_updated_trigger.next_call()['request']
    assert trigger_request_data.method == 'POST'
    trigger_request = json.loads(trigger_request_data.get_data())
    assert trigger_request['old_driver'].pop('_id', None) is not None
    assert trigger_request['old_driver'].pop('updated_ts', None) is not None
    assert trigger_request['old_driver'].pop('modified_date', None) is not None
    assert trigger_request['old_driver'].pop('created_date', None) is not None
    assert trigger_request['new_driver'].pop('_id', None) is not None
    assert trigger_request['new_driver'].pop('updated_ts', None) is not None
    assert trigger_request['new_driver'].pop('modified_date', None) is not None
    assert trigger_request['new_driver'].pop('created_date', None) is not None
    assert driver_in_mongo_before.pop('_id', None) is not None
    assert driver_in_mongo.pop('_id', None) is not None
    assert driver_in_mongo_before.pop('created_date', None) is not None
    assert driver_in_mongo.pop('created_date', None) is not None
    assert trigger_request == {
        'old_driver': driver_in_mongo_before,
        'new_driver': driver_in_mongo,
    }

    # check change_log
    if len(expected_change_log) > 0:
        cursor = sql_databases.taximeter.conn.cursor()
        query = (
            'SELECT * FROM changes_0 WHERE object_id=\'{}\' '
            'ORDER BY date DESC'
        ).format('0')

        query = 'SELECT * FROM changes_0'

        cursor.execute(query)
        rows = cursor.fetchall()
        assert len(rows) == 1
        change = list(rows[0])
        assert change[0] == '123'
        # skip id and date
        change[8] = json.loads(change[8])
        assert change[3:] == [
            '0',
            'MongoDB.Docs.Driver.DriverDoc',
            author_id,
            author_name,
            len(expected_change_log),
            expected_change_log,
            author_ip,
        ]
    else:
        cursor = sql_databases.taximeter.conn.cursor()
        query = (
            'SELECT * FROM changes_0 WHERE object_id=\'{}\' '
            'ORDER BY date DESC'
        ).format('0')

        cursor.execute(query)
        rows = cursor.fetchall()
        assert len(rows) == 0


DAMAGED_PARK_PARAMS = [
    ('driver_1', {'comment': 'коммент'}),
    ('driver_1', {'comment': 'коммент', 'work_status': 'working'}),
    ('driver_1', {'comment': 'коммент', 'work_status': 'fired'}),
    ('driver_2', {'comment': 'коммент'}),
    ('driver_2', {'comment': 'коммент', 'work_status': 'fired'}),
    ('driver_2', {'comment': 'коммент', 'work_status': 'not_working'}),
]


@pytest.mark.parametrize('endpoint_url, headers', ENDPOINT_URLS)
@pytest.mark.parametrize('driver_id, patch', DAMAGED_PARK_PARAMS)
def test_damaged_park(
        taxi_parks,
        mockserver,
        dispatcher_access_control,
        endpoint_url,
        headers,
        driver_id,
        patch,
):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def driver_updated_trigger(request):
        request.get_data()
        return {}

    park_id = 'damaged_park'
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': park_id, 'id': driver_id},
        data=json.dumps({'driver_profile': {'set': patch}}),
        headers=headers,
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'driver_profile': {'id': driver_id, 'park_id': park_id, **patch},
    }


DUPLICATE_PHONE_PARAMS = [
    # driver_1 (fired)
    ('driver_1', 'fired', True),
    ('driver_1', 'working', True),
    # driver_2 (working)
    ('driver_2', 'not_working', True),
    ('driver_2', 'working', True),
    # courier_1 (fired)
    ('courier_1', 'fired', True),
    ('courier_1', 'not_working', True),
    ('courier_1', 'working', False),
]


@pytest.mark.parametrize('endpoint_url, headers', ENDPOINT_URLS)
@pytest.mark.parametrize('driver_id, status, is_valid', DUPLICATE_PHONE_PARAMS)
@pytest.mark.filldb(dbdrivers='couriers')
def test_duplicate_phone(
        taxi_parks,
        mockserver,
        dispatcher_access_control,
        endpoint_url,
        headers,
        driver_id,
        status,
        is_valid,
):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def driver_updated_trigger(request):
        request.get_data()
        return {}

    park_id = 'couriers_park'
    patch = {'work_status': status}
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': park_id, 'id': driver_id},
        data=json.dumps({'driver_profile': {'set': patch}}),
        headers=headers,
    )

    if is_valid:
        assert response.status_code == 200, response.text
        assert response.json() == {
            'driver_profile': {'id': driver_id, 'park_id': park_id, **patch},
        }
    else:
        assert response.status_code == 400, response.text
        assert response.json() == error.make_error_response(
            'duplicate_phone', 'duplicate_phone',
        )


@pytest.mark.sql('taximeter', 'SELECT 1')
@pytest.mark.parametrize(
    'endpoint_url, headers, '
    'dac_times_called, author_id, author_name, author_ip',
    ENDPOINT_URLS_WITH_AUTHOR,
)
@pytest.mark.parametrize(
    'park_id, request_body, expected_response, '
    'affected_db_fields, expected_db_fields,'
    'expected_change_log',
    [
        (
            'only_signalq_park1',
            {'driver_profile': {'set': {'signalq_details': {'unit': 'East'}}}},
            {'driver_profile': {'signalq_details': {'unit': 'East'}}},
            ['signalq_details'],
            {'signalq_details': {'unit': 'East'}},
            {
                'signalq_details': {
                    'old': '{"employee_number":"1523","unit":"West"}',
                    'current': '{"unit":"East"}',
                },
            },
        ),
        (
            'taxi_signalq_park1',
            {
                'driver_profile': {
                    'set': {
                        'work_status': 'working',
                        'signalq_details': {
                            'unit': 'East',
                            'subunit': 'Middle',
                            'employee_number': '5155',
                        },
                    },
                },
            },
            {
                'driver_profile': {
                    'signalq_details': {
                        'unit': 'East',
                        'subunit': 'Middle',
                        'employee_number': '5155',
                    },
                    'work_status': 'working',
                },
            },
            ['signalq_details', 'work_status'],
            {
                'work_status': 'working',
                'signalq_details': {
                    'unit': 'East',
                    'subunit': 'Middle',
                    'employee_number': '5155',
                },
            },
            {
                'signalq_details': {
                    'old': '{"employee_number":"124","subunit":"Cost"}',
                    'current': (
                        '{"employee_number":"5155","subunit":"Middle",'
                        '"unit":"East"}'
                    ),
                },
                'WorkStatus': {'old': 'NotWorking', 'current': 'Working'},
            },
        ),
        (
            'taxi_signalq_park1',
            {'driver_profile': {'unset': ['signalq_details']}},
            {'driver_profile': {}},
            ['signalq_details'],
            {'signalq_details': {}},
            {
                'signalq_details': {
                    'old': '{"employee_number":"124","subunit":"Cost"}',
                    'current': '',
                },
            },
        ),
        (
            'only_signalq_park1',
            {
                'driver_profile': {
                    'set': {
                        'signalq_details': {
                            'unit': 'East',
                            'employee_number': '1242',
                        },
                    },
                },
            },
            {
                'error': {
                    'code': 'duplicate_employee_number',
                    'text': 'duplicate_employee_number',
                },
            },
            None,
            None,
            None,
        ),
    ],
)
def test_patch_with_signalq_details(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        db,
        mockserver,
        sql_databases,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_identifications_bulk_store,
        personal_phones_bulk_store,
        personal_tins_bulk_store,
        endpoint_url,
        headers,
        dac_times_called,
        author_id,
        author_name,
        author_ip,
        park_id,
        request_body,
        expected_response,
        affected_db_fields,
        expected_db_fields,
        expected_change_log,
        driver_work_rules,
):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def driver_updated_trigger(request):
        request.get_data()  # to save request
        return '{}'

    driver_in_mongo_before = utils.datetime_to_str(
        get_driver(db, park_id, '0'),
    )

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': park_id, 'id': '0'},
        data=json.dumps(request_body),
        headers=headers,
    )

    if expected_response.get('error') is not None:
        assert response.status_code == 400, response.text
        assert response.json() == expected_response
        return

    assert response.status_code == 200, response.text

    # check mocks call times
    assert dispatcher_access_control.times_called == dac_times_called
    assert driver_updated_trigger.times_called == (
        1 if park_id != 'only_signalq_park1' else 0
    )

    assert personal_driver_licenses_bulk_store.times_called == 0
    assert personal_emails_bulk_store.times_called == 0
    assert personal_identifications_bulk_store.times_called == 0
    assert personal_phones_bulk_store.times_called == 0
    assert personal_tins_bulk_store.times_called == 0

    # check stored driver
    driver_in_mongo = utils.datetime_to_str(get_driver(db, park_id, '0'))
    assert driver_in_mongo.pop('updated_ts') != driver_in_mongo_before.pop(
        'updated_ts',
    )
    assert driver_in_mongo.pop('modified_date') != driver_in_mongo_before.pop(
        'modified_date',
    )
    expected_in_mongo = utils.replace(
        utils.remove(driver_in_mongo_before, affected_db_fields),
        expected_db_fields,
    )
    assert driver_in_mongo == expected_in_mongo

    # check response
    expected_response['driver_profile']['id'] = '0'
    expected_response['driver_profile']['park_id'] = park_id
    response_to_check = response.json()
    assert response_to_check == expected_response

    if park_id != 'only_signalq_park1':
        # check driver_updated_message
        trigger_request_data = driver_updated_trigger.next_call()['request']
        assert trigger_request_data.method == 'POST'
        trigger_request = json.loads(trigger_request_data.get_data())
        assert trigger_request['old_driver'].pop('_id', None) is not None
        assert (
            trigger_request['old_driver'].pop('updated_ts', None) is not None
        )
        assert (
            trigger_request['old_driver'].pop('modified_date', None)
            is not None
        )
        assert (
            trigger_request['old_driver'].pop('created_date', None) is not None
        )
        assert trigger_request['new_driver'].pop('_id', None) is not None
        assert (
            trigger_request['new_driver'].pop('updated_ts', None) is not None
        )
        assert (
            trigger_request['new_driver'].pop('modified_date', None)
            is not None
        )
        assert (
            trigger_request['new_driver'].pop('created_date', None) is not None
        )
        assert driver_in_mongo_before.pop('_id', None) is not None
        assert driver_in_mongo.pop('_id', None) is not None
        assert driver_in_mongo_before.pop('created_date', None) is not None
        assert driver_in_mongo.pop('created_date', None) is not None
        assert trigger_request == {
            'old_driver': driver_in_mongo_before,
            'new_driver': driver_in_mongo,
        }

    # check change_log
    if len(expected_change_log) > 0:
        cursor = sql_databases.taximeter.conn.cursor()
        query = (
            'SELECT * FROM changes_0 WHERE object_id=\'{}\' '
            'ORDER BY date DESC'
        ).format('0')

        query = 'SELECT * FROM changes_0'

        cursor.execute(query)
        rows = cursor.fetchall()
        assert len(rows) == 1
        change = list(rows[0])
        assert change[0] == park_id
        # skip id and date
        change[8] = json.loads(change[8])
        assert change[3:] == [
            '0',
            'MongoDB.Docs.Driver.DriverDoc',
            author_id,
            author_name,
            len(expected_change_log),
            expected_change_log,
            author_ip,
        ]
    else:
        cursor = sql_databases.taximeter.conn.cursor()
        query = (
            'SELECT * FROM changes_0 WHERE object_id=\'{}\' '
            'ORDER BY date DESC'
        ).format('0')

        cursor.execute(query)
        rows = cursor.fetchall()
        assert len(rows) == 0


@pytest.mark.parametrize(
    'hire_date, projection, code, expected',
    [
        (
            '2199-12-31',
            {'error': ['text']},
            400,
            error.make_error_response('invalid_hire_date'),
        ),
        (
            '1800-02-01',
            {'error': ['text']},
            400,
            error.make_error_response('invalid_hire_date'),
        ),
        (
            '1700-01-01',
            {'error': ['text']},
            400,
            error.make_error_response('invalid_hire_date'),
        ),
        (
            '2015-02-01',
            {'error': ['text']},
            400,
            error.make_error_response('invalid_hire_date'),
        ),
        (
            '1899-12-31',
            {'error': ['text']},
            400,
            error.make_error_response('invalid_hire_date'),
        ),
        (
            '1900-01-01',
            {'driver_profile': 'hire_date'},
            200,
            {'driver_profile': {'hire_date': '1900-01-01T00:00:00+0000'}},
        ),
        (
            '2011-01-01',
            {'error': ['text']},
            400,
            error.make_error_response('invalid_hire_date'),
        ),
        (
            '2010-12-31',
            {'driver_profile': 'hire_date'},
            200,
            {'driver_profile': {'hire_date': '2010-12-31T00:00:00+0000'}},
        ),
        (
            '2000-02-01',
            {'driver_profile': 'hire_date'},
            200,
            {'driver_profile': {'hire_date': '2000-02-01T00:00:00+0000'}},
        ),
        (
            '2000-12-31',
            {'driver_profile': 'hire_date'},
            200,
            {'driver_profile': {'hire_date': '2000-12-31T00:00:00+0000'}},
        ),
    ],
)
@pytest.mark.parametrize('endpoint_url, headers', ENDPOINT_URLS)
@pytest.mark.now('2000-01-01T00:00:00+0000')
def test_valid_hire_date(
        taxi_parks,
        dispatcher_access_control,
        mockserver,
        endpoint_url,
        headers,
        hire_date,
        projection,
        code,
        expected,
):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def driver_updated_trigger(request):
        return {}

    request_body = {'driver_profile': {'set': {'hire_date': hire_date}}}
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '0'},
        data=json.dumps(request_body),
        headers=headers,
    )

    assert response.status_code == code, response.text
    assert utils.projection(response.json(), projection) == expected
