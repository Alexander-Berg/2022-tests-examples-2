# encoding=utf-8
import json

import pytest

from . import error
from . import utils


"""
Все тесты в test_driver_profiles_personal.py проверяют как PUT,
так и соответствующий ему PATCH. Тч здесь остается проверить
только специфичные для PATCH сценарии.
"""

ENDPOINT_URL = '/driver-profiles/personal-patch'
INTERNAL_ENDPOINT_URL = '/internal/driver-profiles/personal-patch'

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

PARK_ID = '123'
DRIVER_ID = '0'
COURIER_ID = '1'


BAD_PARAMS = [
    (
        {'driver_profile': {'unset': 'some_field'}},
        'driver_profile.unset must be an array',
    ),
    # test required field errors
    (
        {'driver_profile': {'set': {'last_name': ''}}},
        (
            'driver_profile.set.last_name'
            ' must be an utf-8 string without BOM with '
            'length >= 1 and <= 500'
        ),
    ),
    (
        {
            'driver_profile': {
                'set': {'last_name': 'asd'},
                'unset': ['last_name'],
            },
        },
        (
            'driver_profile.unset can not contain `last_name` '
            'when set contains it'
        ),
    ),
    (
        {'driver_profile': {'unset': ['last_name']}},
        (
            'driver_profile.unset required field `last_name`'
            ' can not be deleted'
        ),
    ),
    (
        {'driver_profile': {'unset': ['first_name']}},
        (
            'driver_profile.unset required field `first_name`'
            ' can not be deleted'
        ),
    ),
    (
        {'driver_profile': {'unset': ['driver_license']}},
        (
            'driver_profile.unset required field `driver_license`'
            ' can not be deleted'
        ),
    ),
    # test optional fields
    (
        {
            'driver_profile': {
                'set': {'tax_identification_number': 'asd'},
                'unset': ['tax_identification_number'],
            },
        },
        (
            'driver_profile.unset can not contain '
            '`tax_identification_number` when set contains it'
        ),
    ),
]


@pytest.mark.parametrize('endpoint_url, headers', ENDPOINT_URLS)
@pytest.mark.parametrize('request_body, error_message', BAD_PARAMS)
def test_bad(
        taxi_parks,
        contractor_profiles_manager,
        endpoint_url,
        headers,
        request_body,
        error_message,
):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': PARK_ID, 'id': DRIVER_ID},
        data=json.dumps(request_body),
        headers=headers,
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(error_message)


def get_driver(db, driver_id):
    return db.dbdrivers.find_one({'park_id': PARK_ID, 'driver_id': driver_id})


@pytest.fixture
def driver_updated_trigger(mockserver):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def mock_callback(request):
        return {}

    return mock_callback


OK_PARAMS = [
    # no changes
    (
        DRIVER_ID,
        {'driver_profile': {}},
        {'driver_profile': {}},
        [],
        {},
        {},
        {
            'driver_licenses': 0,
            'emails': 0,
            'identifications': 0,
            'phones': 0,
            'tins': 0,
        },
    ),
    # change required
    (
        DRIVER_ID,
        {'driver_profile': {'set': {'last_name': 'Petrov'}}},
        {'driver_profile': {'last_name': 'Petrov'}},
        ['last_name'],
        {'last_name': 'Petrov'},
        {'LastName': {'old': 'Mir', 'current': 'Petrov'}},
        {
            'driver_licenses': 0,
            'emails': 0,
            'identifications': 0,
            'phones': 0,
            'tins': 0,
        },
    ),
    (
        DRIVER_ID,
        {
            'driver_profile': {
                'set': {
                    'driver_license': {
                        'country': 'fra',
                        'number': '12345EE',
                        'birth_date': '1939-09-01',
                        'expiration_date': '2028-11-20',
                        'issue_date': '2018-11-20',
                    },
                },
            },
        },
        {
            'driver_profile': {
                'driver_license': {
                    'country': 'fra',
                    'number': '12345EE',
                    'normalized_number': '12345EE',
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
            },
        },
        [
            'license_country',
            'license_series',
            'license_number',
            'license',
            'license_normalized',
            'license_driver_birth_date',
            'license_expire_date',
            'license_issue_date',
            'driver_license_pd_id',
        ],
        {
            'license_country': 'fra',
            'license_number': '12345EE',
            'license': '12345EE',
            'license_normalized': '12345EE',
            'license_driver_birth_date': '1939-09-01T00:00:00+0000',
            'license_expire_date': '2028-11-20T00:00:00+0000',
            'license_issue_date': '2018-11-20T00:00:00+0000',
            'driver_license_pd_id': 'id_12345EE',
        },
        {
            'License': {'current': '12345EE', 'old': '123123'},
            'LicenseCountryId': {'current': 'fra', 'old': 'rus'},
            'LicenseDriverBirthDate': {
                'current': '1939-09-01T00:00:00+0000',
                'old': '1949-09-01T00:00:00+0000',
            },
            'LicenseExpireDate': {
                'current': '2028-11-20T00:00:00+0000',
                'old': '2038-11-20T00:00:00+0000',
            },
            'LicenseIssueDate': {
                'current': '2018-11-20T00:00:00+0000',
                'old': '2008-11-20T00:00:00+0000',
            },
            'LicenseNormalized': {'current': '12345EE', 'old': '123123'},
            'LicenseNumber': {'current': '12345EE', 'old': '123'},
            'LicenseSeries': {'current': '', 'old': '123'},
            'driver_license_pd_id': {'current': 'id_12345EE', 'old': ''},
        },
        {
            'driver_licenses': 1,
            'emails': 0,
            'identifications': 0,
            'phones': 0,
            'tins': 0,
        },
    ),
    # add optional
    (
        DRIVER_ID,
        {'driver_profile': {'set': {'tax_identification_number': '678'}}},
        {'driver_profile': {'tax_identification_number': '678'}},
        ['tax_identification_number_pd_id'],
        {'tax_identification_number_pd_id': 'id_678'},
        {'tax_identification_number_pd_id': {'old': '', 'current': 'id_678'}},
        {
            'driver_licenses': 0,
            'emails': 0,
            'identifications': 0,
            'phones': 0,
            'tins': 1,
        },
    ),
    # change optional
    (
        DRIVER_ID,
        {'driver_profile': {'set': {'middle_name': 'Petrov'}}},
        {'driver_profile': {'middle_name': 'Petrov'}},
        ['middle_name'],
        {'middle_name': 'Petrov'},
        {'MiddleName': {'old': 'Al', 'current': 'Petrov'}},
        {
            'driver_licenses': 0,
            'emails': 0,
            'identifications': 0,
            'phones': 0,
            'tins': 0,
        },
    ),
    # remove optional which is absent
    (
        DRIVER_ID,
        {'driver_profile': {'unset': ['bank_accounts']}},
        {'driver_profile': {}},
        [],
        {},
        {},
        {
            'driver_licenses': 0,
            'emails': 0,
            'identifications': 0,
            'phones': 0,
            'tins': 0,
        },
    ),
    # remove optional
    (
        DRIVER_ID,
        {'driver_profile': {'unset': ['deaf']}},
        {'driver_profile': {}},
        ['deaf'],
        {},
        {'Deaf': {'old': 'False', 'current': ''}},
        {
            'driver_licenses': 0,
            'emails': 0,
            'identifications': 0,
            'phones': 0,
            'tins': 0,
        },
    ),
    # change required, add optional, remove optional
    (
        DRIVER_ID,
        {
            'driver_profile': {
                'set': {
                    'last_name': 'Petrov',
                    'tax_identification_number': '678',
                },
                'unset': ['email'],
            },
        },
        {
            'driver_profile': {
                'last_name': 'Petrov',
                'tax_identification_number': '678',
            },
        },
        ['last_name', 'tax_identification_number_pd_id', 'email'],
        {'last_name': 'Petrov', 'tax_identification_number_pd_id': 'id_678'},
        {
            'LastName': {'old': 'Mir', 'current': 'Petrov'},
            'tax_identification_number_pd_id': {
                'old': '',
                'current': 'id_678',
            },
            'Email': {'old': 'asd@asd.ru', 'current': ''},
        },
        {
            'driver_licenses': 0,
            'emails': 0,
            'identifications': 0,
            'phones': 0,
            'tins': 1,
        },
    ),
    # courier license unchangeable
    (
        COURIER_ID,
        {
            'driver_profile': {
                'set': {
                    'driver_license': {
                        'country': 'fra',
                        'number': '12345EE',
                        'birth_date': '1939-09-01',
                        'expiration_date': '2028-11-20',
                        'issue_date': '2018-11-20',
                    },
                },
            },
        },
        {
            'driver_profile': {
                'driver_license': {
                    'country': 'rus',
                    'number': 'COURIERabcd',
                    'normalized_number': 'COURIERabcd',
                    'birth_date': '1994-01-01T07:15:00+0000',
                    'expiration_date': '2024-11-20T00:00:00+0000',
                    'issue_date': '2014-11-20T00:00:00+0000',
                },
            },
        },
        [
            'license_country',
            'license_series',
            'license_number',
            'license',
            'license_normalized',
            'license_driver_birth_date',
            'license_expire_date',
            'license_issue_date',
            'driver_license_pd_id',
        ],
        {
            'license_country': 'rus',
            'license_number': 'COURIERabcd',
            'license': 'COURIERabcd',
            'license_normalized': 'COURIERabcd',
            'license_driver_birth_date': '1994-01-01T07:15:00+0000',
            'license_expire_date': '2024-11-20T00:00:00+0000',
            'license_issue_date': '2014-11-20T00:00:00+0000',
            'driver_license_pd_id': 'id_COURIERabcd',
        },
        {},
        {
            'driver_licenses': 1,
            'emails': 0,
            'identifications': 0,
            'phones': 0,
            'tins': 0,
        },
    ),
    # change permit_num
    (
        DRIVER_ID,
        {
            'driver_profile': {
                'set': {'permit_number': 'SUPER_TAXI_DRIVER_LICENSE_2'},
            },
        },
        {'driver_profile': {'permit_number': 'SUPER_TAXI_DRIVER_LICENSE_2'}},
        ['permit_number'],
        {'permit_number': 'SUPER_TAXI_DRIVER_LICENSE_2'},
        {
            'permit_number': {
                'old': 'SUPER_TAXI_DRIVER_LICENSE_1',
                'current': 'SUPER_TAXI_DRIVER_LICENSE_2',
            },
        },
        {
            'driver_licenses': 0,
            'emails': 0,
            'identifications': 0,
            'phones': 0,
            'tins': 0,
        },
    ),
]


@pytest.mark.sql('taximeter', 'SELECT 1')
@pytest.mark.parametrize(
    'endpoint_url, headers, '
    'dac_times_called, author_id, author_name, author_ip',
    ENDPOINT_URLS_WITH_AUTHOR,
)
@pytest.mark.parametrize(
    'driver_id, request_body, expected_response, '
    'affected_db_fields, expected_db_fields,'
    'expected_change_log, mock_call_times',
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
        driver_id,
        request_body,
        expected_response,
        affected_db_fields,
        expected_db_fields,
        expected_change_log,
        mock_call_times,
):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def driver_updated_trigger(request):
        request.get_data()  # to save request
        return '{}'

    driver_in_mongo_before = utils.datetime_to_str(get_driver(db, driver_id))

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': PARK_ID, 'id': driver_id},
        data=json.dumps(request_body),
        headers=headers,
    )

    assert response.status_code == 200, response.text

    # check mocks call times
    assert dispatcher_access_control.times_called == dac_times_called
    assert driver_updated_trigger.times_called == 1

    assert personal_driver_licenses_bulk_store.times_called == (
        mock_call_times['driver_licenses']
    )
    assert personal_emails_bulk_store.times_called == mock_call_times['emails']
    assert personal_identifications_bulk_store.times_called == (
        mock_call_times['identifications']
    )
    assert personal_phones_bulk_store.times_called == mock_call_times['phones']
    assert personal_tins_bulk_store.times_called == mock_call_times['tins']

    # check stored driver
    driver_in_mongo = utils.datetime_to_str(get_driver(db, driver_id))
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
    expected_response['driver_profile']['id'] = driver_id
    expected_response['driver_profile']['park_id'] = PARK_ID
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
        ).format(driver_id)

        query = 'SELECT * FROM changes_0'

        cursor.execute(query)
        rows = cursor.fetchall()
        assert len(rows) == 1
        change = list(rows[0])
        assert change[0] == PARK_ID
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
        ).format(driver_id)

        cursor.execute(query)
        rows = cursor.fetchall()
        assert len(rows) == 0


OK_PARAMS = [
    (
        DRIVER_ID,
        {
            'driver_profile': {
                'set': {
                    'driver_license': {
                        'country': 'fra',
                        'number': '12345EE',
                        'birth_date': '1939-09-01',
                        'expiration_date': '2028-11-20',
                        'issue_date': '2018-11-20',
                    },
                },
            },
        },
        {
            'driver_profile': {
                'driver_license': {
                    'country': 'fra',
                    'number': '12345EE',
                    'normalized_number': '12345EE',
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'hiring_details': {
                    'hiring_date': '2018-11-20T00:00:00+0000',
                    'hiring_type': 'commercial',
                },
            },
        },
        [
            'license_country',
            'license_series',
            'license_number',
            'license',
            'license_normalized',
            'license_driver_birth_date',
            'license_expire_date',
            'license_issue_date',
            'driver_license_pd_id',
            'hiring_details',
        ],
        {
            'license_country': 'fra',
            'license_number': '12345EE',
            'license': '12345EE',
            'license_normalized': '12345EE',
            'license_driver_birth_date': '1939-09-01T00:00:00+0000',
            'license_expire_date': '2028-11-20T00:00:00+0000',
            'license_issue_date': '2018-11-20T00:00:00+0000',
            'driver_license_pd_id': 'id_12345EE',
            'hiring_details': {
                'hiring_date': '2018-11-20T00:00:00+0000',
                'hiring_type': 'commercial',
            },
        },
        {
            'License': {'current': '12345EE', 'old': '123123'},
            'LicenseCountryId': {'current': 'fra', 'old': 'rus'},
            'LicenseDriverBirthDate': {
                'current': '1939-09-01T00:00:00+0000',
                'old': '1949-09-01T00:00:00+0000',
            },
            'LicenseExpireDate': {
                'current': '2028-11-20T00:00:00+0000',
                'old': '2038-11-20T00:00:00+0000',
            },
            'LicenseIssueDate': {
                'current': '2018-11-20T00:00:00+0000',
                'old': '2008-11-20T00:00:00+0000',
            },
            'LicenseNormalized': {'current': '12345EE', 'old': '123123'},
            'LicenseNumber': {'current': '12345EE', 'old': '123'},
            'LicenseSeries': {'current': '', 'old': '123'},
            'driver_license_pd_id': {'current': 'id_12345EE', 'old': ''},
            'HiringDetails': {
                'current': (
                    '{"hiring_date":"2018-11-20T00:00:00+0000",'
                    '"hiring_type":"commercial"}'
                ),
                'old': '',
            },
        },
        {'driver_licenses': 1},
    ),
]


@pytest.mark.sql('taximeter', 'SELECT 1')
@pytest.mark.parametrize(
    'endpoint_url, headers, '
    'dac_times_called, author_id, author_name, author_ip',
    ENDPOINT_URLS_WITH_AUTHOR[:1],
)
@pytest.mark.parametrize(
    'driver_id, request_body, expected_response, '
    'affected_db_fields, expected_db_fields,'
    'expected_change_log, mock_call_times',
    OK_PARAMS,
)
def test_hiring_details_ok(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        db,
        mockserver,
        sql_databases,
        personal_driver_licenses_bulk_store,
        endpoint_url,
        headers,
        dac_times_called,
        author_id,
        author_name,
        author_ip,
        driver_id,
        request_body,
        expected_response,
        affected_db_fields,
        expected_db_fields,
        expected_change_log,
        mock_call_times,
):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def driver_updated_trigger(request):
        request.get_data()  # to save request
        return '{}'

    @mockserver.json_handler(
        '/contractor_profiles_manager/v1/' 'hiring-type-restriction/retrieve',
    )
    def mock_cpm_callback(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'is_restricted': True,
                    'available_hiring_type': 'commercial',
                    'hiring_date': '2018-11-20T00:00:00+0000',
                    'is_warning_expected': True,
                },
            ),
            200,
        )

    driver_in_mongo_before = utils.datetime_to_str(get_driver(db, driver_id))

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': PARK_ID, 'id': driver_id},
        data=json.dumps(request_body),
        headers=headers,
    )

    assert response.status_code == 200, response.text

    # check mocks call times
    assert dispatcher_access_control.times_called == dac_times_called
    assert driver_updated_trigger.times_called == 1

    assert personal_driver_licenses_bulk_store.times_called == (
        mock_call_times['driver_licenses']
    )

    # check stored driver
    driver_in_mongo = utils.datetime_to_str(get_driver(db, driver_id))
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
    expected_response['driver_profile']['id'] = driver_id
    expected_response['driver_profile']['park_id'] = PARK_ID
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
        ).format(driver_id)

        query = 'SELECT * FROM changes_0'

        cursor.execute(query)
        rows = cursor.fetchall()
        assert len(rows) == 1
        change = list(rows[0])
        assert change[0] == PARK_ID
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
        ).format(driver_id)

        cursor.execute(query)
        rows = cursor.fetchall()
        assert len(rows) == 0


DUPLICATE_PHONE_PARAMS = [
    # driver_1 (+7001, fired)
    ('driver_1', '+7001', True),
    ('driver_1', '+7002', False),
    ('driver_1', '+7003', True),
    ('driver_1', '+7004', True),
    # driver_2 (+7002, working)
    ('driver_2', '+7001', False),
    ('driver_2', '+7002', True),
    ('driver_2', '+7003', False),
    ('driver_2', '+7004', True),
    # courier_1 (+7002, fired)
    ('courier_1', '+7001', True),
    ('courier_1', '+7002', True),
    ('courier_1', '+7003', False),
    ('courier_1', '+7004', True),
    # courier_2 (+7003, working)
    ('courier_2', '+7001', True),
    ('courier_2', '+7002', False),
    ('courier_2', '+7003', True),
    ('courier_2', '+7004', True),
]


@pytest.mark.filldb(dbdrivers='couriers')
@pytest.mark.parametrize('endpoint_url, headers', ENDPOINT_URLS)
@pytest.mark.parametrize('driver_id, phone, is_valid', DUPLICATE_PHONE_PARAMS)
def test_duplicate_phone(
        taxi_parks,
        mockserver,
        contractor_profiles_manager,
        dispatcher_access_control,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        endpoint_url,
        headers,
        driver_id,
        phone,
        is_valid,
):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def driver_updated_trigger(request):
        request.get_data()
        return {}

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': 'couriers_park', 'id': driver_id},
        data=json.dumps({'driver_profile': {'set': {'phones': [phone]}}}),
        headers=headers,
    )

    if is_valid:
        assert response.status_code == 200, response.text
        assert response.json() == {
            'driver_profile': {
                'id': driver_id,
                'park_id': 'couriers_park',
                'phones': [phone],
            },
        }
    else:
        assert response.status_code == 400, response.text
        assert response.json() == error.make_error_response(
            'duplicate_phone', 'duplicate_phone',
        )


@pytest.mark.sql('taximeter', 'SELECT 1')
@pytest.mark.parametrize('endpoint_url, headers', ENDPOINT_URLS)
def test_patch_new_pd_phones(
        taxi_parks,
        contractor_profiles_manager,
        dispatcher_access_control,
        db,
        mockserver,
        sql_databases,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        endpoint_url,
        headers,
):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def driver_updated_trigger(request):
        return '{}'

    @mockserver.json_handler('/personal/v1/phones/bulk_find')
    def bulk_find(request):
        return {'items': []}

    driver_in_mongo_before = utils.datetime_to_str(get_driver(db, '0'))

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '0'},
        json={'driver_profile': {'set': {'phones': ['+7500100']}}},
        headers=headers,
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'driver_profile': {
            'id': '0',
            'park_id': '123',
            'phones': ['+7500100'],
        },
    }

    assert bulk_find.times_called == 1
    assert personal_phones_bulk_store.times_called == 1

    # check stored driver
    driver_in_mongo = utils.datetime_to_str(get_driver(db, '0'))
    assert driver_in_mongo.pop('updated_ts') != driver_in_mongo_before.pop(
        'updated_ts',
    )
    assert driver_in_mongo.pop('modified_date') != driver_in_mongo_before.pop(
        'modified_date',
    )
    driver_in_mongo_before.pop('phone_pd_ids')

    assert driver_in_mongo.pop('phone_pd_ids') == ['id_+7500100']

    assert driver_in_mongo == driver_in_mongo_before
