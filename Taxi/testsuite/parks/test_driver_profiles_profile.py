import copy
import json

import pytest

from . import error
from . import utils

NOW = '2021-10-04T12:00:00+00:00'
PARK_ID = '123'
DRIVER_ID = '0'

PUT_ENDPOINT_URL = '/driver-profiles/profile'
PATCH_ENDPOINT_URL = '/driver-profiles/profile-patch'
ENDPOINT_URLS = [PUT_ENDPOINT_URL, PATCH_ENDPOINT_URL]

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

ALL_FIELDS = {
    'work_status',
    'work_rule_id',
    'providers',
    'hire_date',
    'fire_date',
    'hiring_source',
    'comment',
    'check_message',
    'payment_service_id',
    'license_experience',
}


def get_driver(db, park_id, license):
    return db.dbdrivers.find_one({'park_id': park_id, 'license': license})


def get_driver_by_id(db, park_id, id):
    return db.dbdrivers.find_one({'park_id': park_id, 'driver_id': id})


def make_patch_request_if_need(request, endpoint):
    if endpoint == PATCH_ENDPOINT_URL:
        to_set = copy.deepcopy(request['driver_profile'])
        set_fields = {key for key in to_set}
        unset_fields = ALL_FIELDS - set_fields
        return {'driver_profile': {'set': to_set, 'unset': list(unset_fields)}}
    else:
        return request


def make_patch_response_if_need(response, endpoint):
    if endpoint == PATCH_ENDPOINT_URL:
        return utils.remove(response, 'accounts')
    else:
        return response


def make_expected_patch_bson(bson, endpoint):
    if endpoint == PATCH_ENDPOINT_URL:
        return utils.remove(bson, 'balance_limit')
    else:
        return bson


PROFILE = {
    'accounts': [{'balance_limit': '100.0000', 'type': 'current'}],
    'driver_profile': {
        'work_status': 'not_working',
        'work_rule_id': 'other_rule_id',
        'providers': ['park'],
        'hire_date': '2017-11-20',
        'fire_date': '2017-11-20',
        'hiring_source': 'selfreg',
        'comment': 'Some new words',
        'check_message': 'more words',
        'payment_service_id': '999999',
        'license_experience': {'total_since': '2017-12-27'},
    },
}

MONGO_DRIVER1 = {
    'park_id': PARK_ID,
    'driver_id': DRIVER_ID,
    'first_name': 'Andrew',
    'middle_name': 'Al',
    'last_name': 'Mir',
    'phone_pd_ids': [],
    'email': 'asd@asd.ru',
    'address': 'Мск',
    'deaf': True,
    'license_country': 'rus',
    'license_series': '123',
    'license_number': '123',
    'license': '123123',
    'license_normalized': '123123',
    'license_driver_birth_date': '1939-09-01T00:00:00+0000',
    'license_expire_date': '2028-11-20T00:00:00+0000',
    'license_issue_date': '2018-11-20T00:00:00+0000',
    'work_status': 'not_working',
    'rule_id': 'other_rule_id',
    'providers': ['park'],
    'balance_limit': 100,
    'hire_date': '2017-11-20T00:00:00+0000',
    'fire_date': '2017-11-20T00:00:00+0000',
    'license_experience': {
        'total': '2017-12-27T00:00:00+0000',
        'another_category': True,
    },
    'hiring_source': 'selfreg',
    'car_id': '12345',
    'comment': 'Some new words',
    'check_message': 'more words',
    'password': '999999',
    'orders_provider': {
        'taxi': True,
        'taxi_walking_courier': False,
        'lavka': False,
        'eda': False,
        'cargo': False,
        'retail': False,
    },
}


@pytest.fixture
def driver_updated_trigger(mockserver):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def mock_callback(request):
        return {}

    return mock_callback


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_put_ok(
        db,
        dispatcher_access_control,
        driver_updated_trigger,
        driver_balance_limit_updated_trigger,
        taxi_parks,
        endpoint_url,
        driver_work_rules,
        contractor_profiles_manager,
):
    driver_balance_limit_updated_trigger.save_old_balance_limit(
        PARK_ID, DRIVER_ID,
    )
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': PARK_ID, 'id': DRIVER_ID},
        data=json.dumps(make_patch_request_if_need(PROFILE, endpoint_url)),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text
    driver_balance_limit_updated_trigger.check(PARK_ID, DRIVER_ID)

    driver_in_mongo = utils.datetime_to_str(get_driver(db, PARK_ID, '123123'))
    assert driver_in_mongo.pop('_id') is not None
    assert driver_in_mongo.pop('updated_ts') is not None
    assert driver_in_mongo.pop('created_date') is not None
    assert driver_in_mongo.pop('modified_date') is not None

    assert make_expected_patch_bson(
        driver_in_mongo, endpoint_url,
    ) == make_expected_patch_bson(MONGO_DRIVER1, endpoint_url)

    expected_response = copy.deepcopy(PROFILE)
    expected_response['driver_profile']['id'] = DRIVER_ID
    expected_response['driver_profile']['park_id'] = PARK_ID
    expected_response['accounts'][0]['id'] = '0'
    # we don't want to change return values format right now
    expected_response = utils.replace(
        expected_response,
        {
            'driver_profile': {
                'hire_date': '2017-11-20T00:00:00+0000',
                'fire_date': '2017-11-20T00:00:00+0000',
            },
        },
    )
    response_to_check = response.json()
    assert response_to_check == make_patch_response_if_need(
        expected_response, endpoint_url,
    )


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.now('2019-11-20T00:00:00+0000')
@pytest.mark.parametrize(
    'remove, projection, expected, mongo_projection, expected_mongo',
    [
        (
            {'driver_profile': 'fire_date'},
            {'driver_profile': 'fire_date'},
            {},
            'fire_date',
            {},
        ),
        (
            {'driver_profile': 'license_experience'},
            {'driver_profile': 'license_experience'},
            {},
            'license_experience',
            {'license_experience': {'another_category': True}},
        ),
    ],
)
def test_unset(
        db,
        dispatcher_access_control,
        driver_updated_trigger,
        driver_balance_limit_updated_trigger,
        taxi_parks,
        endpoint_url,
        remove,
        projection,
        expected,
        mongo_projection,
        expected_mongo,
        driver_work_rules,
        contractor_profiles_manager,
):
    driver_balance_limit_updated_trigger.save_old_balance_limit(
        PARK_ID, DRIVER_ID,
    )
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': PARK_ID, 'id': DRIVER_ID},
        data=json.dumps(
            make_patch_request_if_need(
                utils.remove(PROFILE, remove), endpoint_url,
            ),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text
    driver_balance_limit_updated_trigger.check(PARK_ID, DRIVER_ID)

    driver_in_mongo = utils.datetime_to_str(get_driver(db, PARK_ID, '123123'))
    assert utils.projection(response.json(), projection) == expected
    assert (
        utils.projection(driver_in_mongo, mongo_projection) == expected_mongo
    )


@pytest.mark.parametrize(
    'replacement, error_message',
    [
        (
            {'driver_profile': {'payment_service_id': '999998'}},
            'duplicate_payment_service_id',
        ),
        (
            {'driver_profile': {'hiring_source': 'asd'}},
            'invalid_hiring_source',
        ),
    ],
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_invalid_request_with_unreal_headers(
        taxi_parks,
        driver_work_rules,
        driver_updated_trigger,
        endpoint_url,
        replacement,
        error_message,
        contractor_profiles_manager,
):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': PARK_ID, 'id': DRIVER_ID},
        data=json.dumps(
            make_patch_request_if_need(
                utils.replace(PROFILE, replacement), endpoint_url,
            ),
        ),
        headers=AUTHOR_YA_UNREAL_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        error_message, error_message,
    )


@pytest.mark.parametrize(
    'replacement, error_message',
    [
        (
            {'driver_profile': {'payment_service_id': '999998'}},
            'X-Ya-User-Ticket and X-Ya-User-Ticket-Provider must be provided',
        ),
        (
            {'driver_profile': {'hiring_source': 'asd'}},
            'X-Ya-User-Ticket and X-Ya-User-Ticket-Provider must be provided',
        ),
    ],
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_invalid_request_with_empty_headers(
        taxi_parks,
        driver_work_rules,
        endpoint_url,
        driver_updated_trigger,
        replacement,
        error_message,
        contractor_profiles_manager,
):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': PARK_ID, 'id': DRIVER_ID},
        data=json.dumps(make_patch_request_if_need(PROFILE, endpoint_url)),
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(error_message)


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.config(TVM_USER_TICKET_USE_FAKE_CONTEXT=True)
def test_no_such_driver(
        taxi_parks, dispatcher_access_control, endpoint_url, driver_work_rules,
):
    driver_work_rules.set_work_rules_response(WORK_RULES_ALL)

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': PARK_ID, 'id': 'no_such'},
        data=json.dumps(
            make_patch_request_if_need(
                utils.replace(
                    PROFILE,
                    {'driver_profile': {'payment_service_id': '500100'}},
                ),
                endpoint_url,
            ),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        'no_such_driver', 'no_such_driver',
    )


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.config(TVM_USER_TICKET_USE_FAKE_CONTEXT=True)
def test_incompatible_work_rule(
        taxi_parks,
        endpoint_url,
        driver_work_rules,
        contractor_profiles_manager,
        driver_updated_trigger,
):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': PARK_ID, 'id': '6'},
        data=json.dumps(
            make_patch_request_if_need(
                utils.replace(
                    PROFILE,
                    {
                        'driver_profile': {
                            'payment_service_id': '12939123',
                            'work_rule_id': 'incompatible_new_rule_id',
                        },
                    },
                ),
                endpoint_url,
            ),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert driver_work_rules.comp_list_times_called == 1
    assert driver_work_rules.list_times_called == 1
    assert driver_work_rules.status_code == 200

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        'incompatible_work_rule', 'incompatible_work_rule',
    )


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.config(TVM_USER_TICKET_USE_FAKE_CONTEXT=True)
def test_driver_work_rules_bad_request(
        taxi_parks,
        db,
        driver_work_rules,
        driver_updated_trigger,
        driver_balance_limit_updated_trigger,
        dispatcher_access_control,
        endpoint_url,
        mockserver,
        contractor_profiles_manager,
):
    @mockserver.json_handler(
        '/driver_work_rules/v1/work-rules/compatible/list',
    )
    def mock_dwr_callback(request):
        return mockserver.make_response(json.dumps(WORK_RULES_ALL), 200)

    driver_balance_limit_updated_trigger.save_old_balance_limit(
        PARK_ID, DRIVER_ID,
    )
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': PARK_ID, 'id': DRIVER_ID},
        data=json.dumps(
            make_patch_request_if_need(
                utils.replace(
                    PROFILE,
                    {
                        'driver_profile': {
                            'payment_service_id': '91239139',
                            'work_rule_id': 'incompatible_new_rule_id',
                        },
                    },
                ),
                endpoint_url,
            ),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert mock_dwr_callback.times_called == 1

    assert response.status_code == 200, response.text
    driver_balance_limit_updated_trigger.check(PARK_ID, DRIVER_ID)
    assert (
        response.json()['driver_profile']['work_rule_id']
        == 'incompatible_new_rule_id'
    )

    driver_in_mongo = utils.datetime_to_str(get_driver(db, PARK_ID, '123123'))
    driver_in_mongo['rule_id'] == 'incompatible_new_rule_id'


CHANGES_PROFILE = {
    'accounts': [{'balance_limit': '50.5', 'type': 'current'}],
    'driver_profile': {
        'work_status': 'working',
        'work_rule_id': 'rule_zero',
        'providers': ['yandex', 'park'],
        'hire_date': '2018-11-20',
        'fire_date': '2018-11-20',
        'comment': 'ads',
        'check_message': 'qwe',
        'payment_service_id': '999997',
    },
}


@pytest.mark.config(TVM_USER_TICKET_USE_FAKE_CONTEXT=True)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'to_set, to_unset, expected',
    [
        (
            {'driver_profile': {'hiring_source': 'selfreg'}},
            {},
            {'HiringSource': {'current': 'selfreg', 'old': ''}},
        ),
        (
            {'driver_profile': {'hire_date': '2017-11-20'}},
            {},
            {
                'HireDate': {
                    'current': '2017-11-20T00:00:00+0000',
                    'old': '2018-11-20T00:00:00+0000',
                },
            },
        ),
        (
            {
                'driver_profile': {
                    'license_experience': {'total_since': '2017-12-27'},
                },
            },
            {},
            {
                'license_experience': {
                    'current': '{"total":"2017-12-27T00:00:00+0000"}',
                    'old': '',
                },
            },
        ),
    ],
)
@pytest.mark.sql('taximeter', 'SELECT 1')
def test_change_log(
        taxi_parks,
        dispatcher_access_control,
        driver_updated_trigger,
        endpoint_url,
        sql_databases,
        to_set,
        to_unset,
        expected,
        driver_work_rules,
        contractor_profiles_manager,
):
    profile = utils.remove(utils.replace(CHANGES_PROFILE, to_set), to_unset)

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': PARK_ID, 'id': '4'},
        data=json.dumps(make_patch_request_if_need(profile, endpoint_url)),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200
    assert dispatcher_access_control.times_called == 1

    cursor = sql_databases.taximeter.conn.cursor()
    query = 'SELECT * FROM changes_0 WHERE object_id=\'4\' ORDER BY date DESC'
    cursor.execute(query)
    rows = cursor.fetchall()
    assert len(rows) == 1
    change = list(rows[0])
    assert change[0] == '123'
    # skip id and date
    change[8] = json.loads(change[8])
    assert change[3:] == [
        '4',
        'MongoDB.Docs.Driver.DriverDoc',
        '1',
        'Boss',
        len(expected),
        expected,
        '1.2.3.4',
    ]


TEST_PAYMENT_SERVICE_ID_PROFILE = {
    'accounts': [{'balance_limit': '100.0000', 'type': 'current'}],
    'driver_profile': {
        'work_status': 'not_working',
        'work_rule_id': 'other_rule_id',
        'hire_date': '2017-11-20',
        'fire_date': '2017-11-20',
        'providers': ['park'],
        'hiring_source': 'selfreg',
        'comment': 'Some new words',
        'check_message': 'more words',
    },
}


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'id, modified_driver, expected, mongo_expected',
    [
        # update existing
        (
            DRIVER_ID,
            utils.replace(
                TEST_PAYMENT_SERVICE_ID_PROFILE,
                {'driver_profile': {'payment_service_id': '999987'}},
            ),
            {'driver_profile': {'payment_service_id': '999987'}},
            {'password': '999987'},
        ),
        # remove existing
        (DRIVER_ID, TEST_PAYMENT_SERVICE_ID_PROFILE, {}, {}),
        (
            DRIVER_ID,
            utils.replace(
                TEST_PAYMENT_SERVICE_ID_PROFILE,
                {'driver_profile': {'payment_service_id': ''}},
            ),
            {},
            {},
        ),
        # update previously absent
        (
            '6',
            utils.replace(
                TEST_PAYMENT_SERVICE_ID_PROFILE,
                {'driver_profile': {'payment_service_id': '999987'}},
            ),
            {'driver_profile': {'payment_service_id': '999987'}},
            {'password': '999987'},
        ),
        # remove absent
        ('6', TEST_PAYMENT_SERVICE_ID_PROFILE, {}, {}),
        (
            '6',
            utils.replace(
                TEST_PAYMENT_SERVICE_ID_PROFILE,
                {'driver_profile': {'payment_service_id': ''}},
            ),
            {},
            {},
        ),
    ],
)
def test_put_payment_service_id(
        db,
        dispatcher_access_control,
        driver_updated_trigger,
        driver_balance_limit_updated_trigger,
        taxi_parks,
        endpoint_url,
        id,
        modified_driver,
        expected,
        mongo_expected,
        driver_work_rules,
        contractor_profiles_manager,
):
    driver_balance_limit_updated_trigger.save_old_balance_limit(PARK_ID, id)
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': PARK_ID, 'id': id},
        data=json.dumps(
            make_patch_request_if_need(modified_driver, endpoint_url),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text
    driver_balance_limit_updated_trigger.check(PARK_ID, id)

    driver_in_mongo = get_driver_by_id(db, PARK_ID, id)
    assert utils.projection(driver_in_mongo, 'password') == mongo_expected
    assert (
        utils.projection(
            response.json(), {'driver_profile': 'payment_service_id'},
        )
        == expected
    )


WORK_RULE_ZERO = {
    'commission_for_subvention_percent': '1.2345',
    'commission_for_workshift_percent': '5.4321',
    'id': 'rule_zero',
    'is_commission_for_orders_cancelled_by_client_' 'enabled': True,
    'is_commission_if_platform_commission_is_null_' 'enabled': True,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': True,
    'is_enabled': True,
    'is_workshift_enabled': False,
    'name': 'Штатный',
    'subtype': 'selfreg',
    'type': 'park',
}
WORK_RULE_INCOMPATIBLE = {
    'commission_for_subvention_percent': '1.2345',
    'commission_for_workshift_percent': '5.4321',
    'id': 'incompatible_new_rule_id',
    'is_commission_for_orders_cancelled_by_client_' 'enabled': True,
    'is_commission_if_platform_commission_is_null_' 'enabled': True,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': True,
    'is_enabled': True,
    'is_workshift_enabled': False,
    'name': 'Штатный',
    'subtype': 'selfreg',
    'type': 'park',
}
WORK_RULE_OTHER = {
    'commission_for_subvention_percent': '1.2345',
    'commission_for_workshift_percent': '5.4321',
    'id': 'other_rule_id',
    'is_commission_for_orders_cancelled_by_client_' 'enabled': True,
    'is_commission_if_platform_commission_is_null_' 'enabled': True,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': True,
    'is_enabled': True,
    'is_workshift_enabled': False,
    'name': 'Штатный',
    'subtype': 'selfreg',
    'type': 'park',
}

WORK_RULES_ALL = {
    'work_rules': [WORK_RULE_ZERO, WORK_RULE_INCOMPATIBLE, WORK_RULE_OTHER],
}


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_work_rules_check(
        db,
        dispatcher_access_control,
        driver_updated_trigger,
        taxi_parks,
        endpoint_url,
        driver_work_rules,
        contractor_profiles_manager,
):
    request_driver = utils.replace(
        PROFILE, {'driver_profile': {'work_rule_id': 'null'}},
    )

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': PARK_ID, 'id': DRIVER_ID},
        data=json.dumps(
            make_patch_request_if_need(request_driver, endpoint_url),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'error': {
            'code': 'invalid_work_rule_id',
            'text': 'invalid_work_rule_id',
        },
    }


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_cannot_change_removed_driver(
        db, mockserver, taxi_parks, endpoint_url,
):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': 'removed_driver'},
        json=make_patch_request_if_need(PROFILE, endpoint_url),
        headers=AUTHOR_YA_HEADERS,
    )
    assert response.status_code == 400, response.text
    code = 'cannot_edit_removed_driver'
    assert response.json() == error.make_error_response(code, code)


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_cannot_change_readonly_driver(
        db, mockserver, taxi_parks, endpoint_url,
):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': 'readonly_driver'},
        json=make_patch_request_if_need(PROFILE, endpoint_url),
        headers=AUTHOR_YA_HEADERS,
    )
    assert response.status_code == 400, response.text
    code = 'cannot_edit_readonly_driver'
    assert response.json() == error.make_error_response(code, code)


PROFILE_WITH_SIGNALQ = utils.replace(
    PROFILE, {'driver_profile': {'signalq_details': {'unit': 'West'}}},
)
PROFILE_WITH_SIGNALQ['driver_profile'].pop('work_rule_id')
MONGO_DRIVER_WITH_SIGNALQ = utils.replace(
    MONGO_DRIVER1,
    {
        'park_id': 'taxi_signalq_park1',
        'license': '123123252',
        'license_series': '123',
        'license_number': '123252',
        'license_normalized': '123123252',
        'signalq_details': {'unit': 'West'},
    },
)
MONGO_DRIVER_WITH_SIGNALQ.pop('rule_id')


@pytest.mark.parametrize(
    'park_id, is_signalq, make_not_taxi_working',
    [
        ('taxi_signalq_park1', True, False),
        ('only_signalq_park1', True, True),
        (PARK_ID, False, False),
    ],
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_put_with_signalq_details(
        db,
        dispatcher_access_control,
        driver_updated_trigger,
        driver_balance_limit_updated_trigger,
        taxi_parks,
        park_id,
        is_signalq,
        make_not_taxi_working,
        endpoint_url,
        driver_work_rules,
        contractor_profiles_manager,
):
    request_body = PROFILE_WITH_SIGNALQ
    if make_not_taxi_working:
        request_body = utils.replace(
            request_body, {'driver_profile': {'work_status': 'working'}},
        )

    driver_balance_limit_updated_trigger.save_old_balance_limit(
        park_id, DRIVER_ID,
    )
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': park_id, 'id': DRIVER_ID},
        data=json.dumps(
            make_patch_request_if_need(request_body, endpoint_url),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    if make_not_taxi_working:
        assert response.status_code == 400, response.text
        assert response.json() == {
            'error': {
                'code': 'forbidden_signalq_working_status',
                'text': 'forbidden_signalq_working_status',
            },
        }
        return

    if not is_signalq:
        assert response.status_code == 400, response.text
        assert response.json() == {
            'error': {
                'code': 'unexpected_signalq_details',
                'text': 'unexpected_signalq_details',
            },
        }
        return

    assert response.status_code == 200, response.text
    driver_balance_limit_updated_trigger.check(park_id, DRIVER_ID)

    driver_in_mongo = utils.datetime_to_str(
        get_driver(db, park_id, '123123252'),
    )
    assert driver_in_mongo.pop('_id') is not None
    assert driver_in_mongo.pop('updated_ts') is not None
    assert driver_in_mongo.pop('created_date') is not None
    assert driver_in_mongo.pop('modified_date') is not None

    assert make_expected_patch_bson(
        driver_in_mongo, endpoint_url,
    ) == make_expected_patch_bson(MONGO_DRIVER_WITH_SIGNALQ, endpoint_url)

    expected_response = copy.deepcopy(PROFILE_WITH_SIGNALQ)
    expected_response['driver_profile']['id'] = DRIVER_ID
    expected_response['driver_profile']['park_id'] = park_id
    expected_response['accounts'][0]['id'] = '0'
    # we don't want to change return values format right now
    expected_response = utils.replace(
        expected_response,
        {
            'driver_profile': {
                'hire_date': '2017-11-20T00:00:00+0000',
                'fire_date': '2017-11-20T00:00:00+0000',
            },
        },
    )
    response_to_check = response.json()
    assert response_to_check == make_patch_response_if_need(
        expected_response, endpoint_url,
    )


@pytest.mark.parametrize('trigger_enabled', [True, False])
def test_enable_balance_limit_updated_trigger_config(
        taxi_config,
        mockserver,
        dispatcher_access_control,
        driver_updated_trigger,
        driver_balance_limit_updated_trigger,
        taxi_parks,
        driver_work_rules,
        contractor_profiles_manager,
        trigger_enabled,
):
    taxi_config.set(PARKS_ENABLE_BALANCE_LIMIT_UPDATED_TRIGGER=trigger_enabled)

    response = taxi_parks.put(
        PUT_ENDPOINT_URL,
        params={'park_id': PARK_ID, 'id': DRIVER_ID},
        data=json.dumps(PROFILE),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text
    assert driver_balance_limit_updated_trigger.has_calls == trigger_enabled


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ('park_id', 'driver_id'),
    [
        (PARK_ID, '1'),  # driver with balance_limit
        (PARK_ID, '2'),  # driver without balance_limit
    ],
)
@pytest.mark.parametrize(
    'new_balance_limit',
    [15.0, 15.44445, 0.0, 15.0001, 14.9999, 15.00005, 14.999999],
)
def test_balance_limit_updated_trigger(
        db,
        mockserver,
        dispatcher_access_control,
        driver_updated_trigger,
        driver_balance_limit_updated_trigger,
        taxi_parks,
        driver_work_rules,
        contractor_profiles_manager,
        park_id,
        driver_id,
        new_balance_limit,
):

    request_body = copy.deepcopy(PROFILE)
    request_body['accounts'][0]['balance_limit'] = str(new_balance_limit)

    driver_balance_limit_updated_trigger.save_old_balance_limit(
        park_id, driver_id,
    )
    response = taxi_parks.put(
        PUT_ENDPOINT_URL,
        params={'park_id': park_id, 'id': driver_id},
        data=json.dumps(request_body),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text
    driver_balance_limit_updated_trigger.check(park_id, driver_id, NOW)


def test_balance_limit_updated_trigger_fail(
        mockserver,
        dispatcher_access_control,
        driver_updated_trigger,
        driver_balance_limit_updated_trigger,
        taxi_parks,
        driver_work_rules,
        contractor_profiles_manager,
):
    driver_balance_limit_updated_trigger.save_old_balance_limit(
        PARK_ID, DRIVER_ID,
    )
    driver_balance_limit_updated_trigger.return_error = True
    response = taxi_parks.put(
        PUT_ENDPOINT_URL,
        params={'park_id': PARK_ID, 'id': DRIVER_ID},
        data=json.dumps(PROFILE),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text
    driver_balance_limit_updated_trigger.check(PARK_ID, DRIVER_ID)
