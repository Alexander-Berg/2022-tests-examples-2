import base64
import copy
import datetime
import hashlib
import hmac
import json

import bson
import pytest

from taxi_tests import utils


CC_HEADERS = {'User-Agent': 'call_center'}


def make_afs_is_spammer_response_builder(add_sec_to_block_time):
    def response_builder(now):
        if add_sec_to_block_time is None:
            return {'is_spammer': False}
        blocked_until = now + datetime.timedelta(seconds=add_sec_to_block_time)
        return {
            'is_spammer': True,
            'blocked_until': utils.timestring(blocked_until),
        }

    return response_builder


PERSONAL_PHONES_DB = [
    {'id': f'p0000000000000000000000{d}', 'value': f'+7915111111{d}'}
    for d in range(10)
]


PERSONAL_PHONES_DB.append(
    {'id': 'p00000000000000000000100', 'value': '+79151111100'},
)


def find_personal_db_record(field, value):
    return next(
        (record for record in PERSONAL_PHONES_DB if record[field] == value),
        None,
    )


def process_personal_request(request, field):
    request_json = json.loads(request.get_data())
    assert field in request_json

    return find_personal_db_record(field, request_json[field])


@pytest.fixture()
def services_mocks(mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_personal_phones_retrieve(request):
        return process_personal_request(
            request, 'id',
        ) or mockserver.make_response({}, 404)

    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_personal_phones_store(request):
        return process_personal_request(
            request, 'value',
        ) or mockserver.make_response({}, 400)

    return []


@pytest.mark.parametrize(
    'phone,personal_phone_id,dont_ask_name,name,discount_card,user_id,'
    'expected_code,expected_response',
    [
        (
            '+79151111111',
            'p00000000000000000000001',
            None,
            None,
            None,
            'e4707fc6e79e4562b4f0af20a8e87111',
            200,
            {
                'dont_ask_name': False,
                'experiments': [
                    'call_center_experiment_1',
                    'call_center_experiment_2',
                ],
            },
        ),
        (
            '+79151111112',
            'p00000000000000000000002',
            None,
            None,
            None,
            None,
            200,
            {
                'dont_ask_name': False,
                'experiments': [
                    'call_center_experiment_1',
                    'call_center_experiment_2',
                ],
            },
        ),
        (
            '+79151111110',
            'p00000000000000000000000',
            None,
            None,
            None,
            None,
            200,
            {
                'dont_ask_name': False,
                'experiments': [
                    'call_center_experiment_1',
                    'call_center_experiment_2',
                ],
            },
        ),
        (
            '+79151111114',
            'p00000000000000000000004',
            None,
            None,
            None,
            'e4707fc6e79e4562b4f0af20a8e87114',
            200,
            {
                'dont_ask_name': False,
                'experiments': [
                    'call_center_experiment_1',
                    'call_center_experiment_2',
                ],
            },
        ),
        (
            '+79151111114',
            'p00000000000000000000004',
            None,
            'Вася',
            '033',
            'e4707fc6e79e4562b4f0af20a8e87114',
            200,
            {
                'dont_ask_name': False,
                'experiments': [
                    'call_center_experiment_1',
                    'call_center_experiment_2',
                ],
                'name': 'Вася',
            },
        ),
        (
            '+79151111114',
            'p00000000000000000000004',
            True,
            None,
            '033',
            'e4707fc6e79e4562b4f0af20a8e87114',
            200,
            {
                'dont_ask_name': True,
                'experiments': [
                    'call_center_experiment_1',
                    'call_center_experiment_2',
                ],
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'personal_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=True,
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=False,
            ),
        ),
    ],
)
@pytest.mark.experiments3(filename='experiments3_profile.json')
@pytest.mark.now('2018-07-20T10:15:00+0000')
def test_profile(
        taxi_integration,
        mockserver,
        db,
        services_mocks,
        phone,
        personal_phone_id,
        dont_ask_name,
        name,
        discount_card,
        user_id,
        expected_code,
        expected_response,
        personal_enabled,
):
    request_body = {
        'user': {'phone': phone, 'personal_phone_id': personal_phone_id},
    }
    if dont_ask_name is not None:
        request_body['dont_ask_name'] = dont_ask_name
    if name is not None:
        request_body['name'] = name
    if discount_card is not None:
        request_body['discount_card'] = discount_card

    response = taxi_integration.post(
        'v1/profile', json=request_body, headers=CC_HEADERS,
    )
    assert response.status_code == expected_code

    phone_doc = db.user_phones.find_one(
        {'phone': phone, 'personal_phone_id': personal_phone_id},
    )

    user_doc = db.users.find_one({'phone_id': phone_doc['_id']})

    if user_id is None:
        user_id = user_doc['_id']
    expected_response['user_id'] = user_id

    if dont_ask_name is not None:
        assert user_doc['dont_ask_name'] == dont_ask_name
    if name is not None:
        assert user_doc['given_name'] == name

    expected_response_full = copy.deepcopy(expected_response)
    if personal_enabled:
        expected_response_full['personal_phone_id'] = personal_phone_id

    data = response.json()
    assert data == expected_response_full


@pytest.mark.parametrize(
    'expected_error_text',
    [
        pytest.param(
            'either personal_phone_id or phone should be passed',
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=True,
            ),
        ),
        pytest.param(
            'failed to parse user phone from request',
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=False,
            ),
        ),
    ],
)
@pytest.mark.now('2018-04-24T10:15:00+0000')
def test_errors(taxi_integration, expected_error_text):
    response = taxi_integration.post(
        'v1/profile', json={'user': {}}, headers=CC_HEADERS,
    )
    assert response.status_code == 400

    data = response.json()
    assert data == {'error': {'text': expected_error_text}}


@pytest.mark.parametrize(
    'phone,personal_phone_id,source_id,application,yandex_uid',
    [
        (
            '+79151111100',
            'p00000000000000000000100',
            'alice',
            'alice',
            '480301451',
        ),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=False,
            ),
        ),
    ],
)
@pytest.mark.now('2018-07-20T10:15:00+0000')
def test_alice(
        taxi_integration,
        mockserver,
        db,
        services_mocks,
        phone,
        personal_phone_id,
        source_id,
        application,
        yandex_uid,
):
    user_phone = db.user_phones.find_one({'phone': phone})
    assert user_phone is None

    request_body = {
        'user': {
            'phone': phone,
            'personal_phone_id': personal_phone_id,
            'yandex_uid': yandex_uid,
        },
        'sourceid': source_id,
    }

    # create user

    response = taxi_integration.post('v1/profile', json=request_body)
    assert response.status_code == 200, response

    user_phone = db.user_phones.find_one({'phone': phone})
    assert user_phone['phone'] == phone
    assert user_phone['personal_phone_id'] == personal_phone_id
    assert user_phone['phone_hash'] is not None
    assert user_phone['phone_salt'] is not None
    assert (
        user_phone['phone_hash']
        == hmac.new(
            base64.b64decode(user_phone['phone_salt']) + b'secdist_salt',
            user_phone['phone'].encode(),
            hashlib.sha256,
        ).hexdigest()
    )

    data = response.json()
    response_user_id = data['user_id']

    user_doc = db.users.find_one({'_id': response_user_id})
    assert user_doc['sourceid'] == source_id
    assert user_doc['application'] == application
    assert user_doc['yandex_uid'] == yandex_uid

    # use existing user

    response = taxi_integration.post('v1/profile', json=request_body)
    assert response.status_code == 200, response

    data = response.json()
    assert response_user_id == data['user_id']

    # wrong request params (no user.yandex_uid)

    request_body = {
        'user': {'phone': phone, 'personal_phone_id': personal_phone_id},
        'sourceid': source_id,
    }

    response = taxi_integration.post('v1/profile', json=request_body)
    assert response.status_code == 400, response
    data = response.json()
    assert data == {
        'error': {'text': 'for alice should contain non empty \'yandex_uid\''},
    }


@pytest.mark.parametrize('initially_has_plus', (False, True))
@pytest.mark.parametrize('alice_update_using_user_api', (False, True))
@pytest.mark.parametrize(
    'user_exps,blackbox_has_plus,alice_check_plus_in_passport,resulting_plus',
    [
        (['ya_plus'], True, True, True),
        (['ya_plus'], False, True, False),
        (['ya_plus'], True, False, False),
        ({}, True, True, False),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=False,
            ),
        ),
    ],
)
def test_alice_plus(
        taxi_integration,
        mockserver,
        user_experiments,
        db,
        config,
        services_mocks,
        initially_has_plus,
        user_exps,
        blackbox_has_plus,
        resulting_plus,
        alice_check_plus_in_passport,
        alice_update_using_user_api,
):
    config_values = {
        'ALICE_CHECK_PLUS_IN_PASSPORT': alice_check_plus_in_passport,
        'ALICE_UPDATE_PLUS_USING_USER_API': alice_update_using_user_api,
    }
    config.set_values(config_values)
    user_id = 'a5507fc6e79e4562b4f0af20a8e87111'
    user_experiments.set_value(user_exps)
    if initially_has_plus:
        db.users.update(
            {'_id': user_id}, {'$set': {'has_ya_plus': initially_has_plus}},
        )

    @mockserver.json_handler('/user-api/users/update-ya-plus')
    def _mock_user_api_update_ya_plus(request):
        assert request.json == {
            'user_id': user_id,
            'has_ya_plus': resulting_plus,
        }
        db.users.update(
            {'_id': user_id},
            {'$set': {'has_ya_plus': request.json['has_ya_plus']}},
        )

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        desired_query = {
            'method=check_has_plus',
            'format=json',
            'phone_number=79151111111',
        }
        query = set(request.query_string.decode().split('&'))
        assert query == desired_query, response.query_string
        return {'has_plus': blackbox_has_plus}

    response = taxi_integration.post(
        'v1/profile',
        json={
            'user': {
                'phone': '+79151111111',
                'personal_phone_id': 'p00000000000000000000001',
                'yandex_uid': '480301451',
            },
            'sourceid': 'alice',
        },
    )
    assert response.status_code == 200, response.text
    has_plus = db.users.find_one({'_id': user_id}).get('has_ya_plus', False)
    assert has_plus == resulting_plus, response.json()
    if alice_update_using_user_api and initially_has_plus != resulting_plus:
        assert _mock_user_api_update_ya_plus.times_called == 1
    else:
        assert _mock_user_api_update_ya_plus.times_called == 0


@pytest.mark.config(
    INTEGRATION_SUPPORTED_APPLICATIONS=['valid_app'],
    APPLICATION_DETECTION_RULES_NEW={
        'rules': [
            {'match': 'valid_app', '@app_name': 'valid_app', '@app_ver1': '2'},
            {'@app_name': 'foolish', '@app_ver1': '2'},
        ],
    },
)
@pytest.mark.parametrize(
    'sourceid,application,code',
    [
        ('corp_cabinet', 'corpweb', 200),
        ('alice', 'alice', 200),
        ('svo_order', 'call_center', 200),
        (None, 'valid_app', 200),
        (None, 'bad_app', 400),
        ('uber', 'uber', 400),
        ('wrong', 'wrong', 400),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=False,
            ),
        ),
    ],
)
@pytest.mark.now('2018-07-20T10:15:00+0000')
def test_sourceid_and_application(
        taxi_integration,
        db,
        mockserver,
        services_mocks,
        sourceid,
        application,
        code,
):
    """
    Check allowable values of sourceid in request for int-api
    """

    db.users.remove()
    db.user_phones.remove()

    request_body = {
        'user': {
            'phone': '+79151111100',
            'personal_phone_id': 'p00000000000000000000100',
        },
        'sourceid': sourceid,
    }
    if sourceid == 'alice':
        request_body['user'].update({'yandex_uid': '480301451'})

    headers = {}
    if sourceid is None:
        headers = {'User-Agent': application}
    response = taxi_integration.post(
        'v1/profile', json=request_body, headers=headers,
    )
    assert response.status_code == code, response
    data = response.json()

    if code == 200:
        assert data is not None
        response_user_id = data['user_id']
        user_doc = db.users.find_one({'_id': response_user_id})
        assert user_doc['sourceid'] == sourceid or application
        assert user_doc['application'] == application
    elif code == 400:
        text = 'source_id invalid'
        if sourceid is None:
            text = 'Invalid application'
        assert data == {'error': {'text': text}}
    else:
        assert False


@pytest.mark.filldb(orders='has_debt')
@pytest.mark.parametrize(
    'personal_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=True,
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=False,
            ),
        ),
    ],
)
def test_has_debt(
        taxi_integration, db, mockserver, services_mocks, personal_enabled,
):
    """
    Check user has debt
    """

    personal_phone_id = 'p00000000000000000000001'

    request_body = {
        'user': {
            'phone': '+79151111111',
            'personal_phone_id': personal_phone_id,
            'yandex_uid': '480301451',
        },
        'sourceid': 'alice',
    }

    response = taxi_integration.post('v1/profile', json=request_body)
    assert response.status_code == 200, response
    data = response.json()

    expected_response = {
        'dont_ask_name': False,
        'experiments': [
            'call_center_experiment_1',
            'call_center_experiment_2',
        ],
        'has_debt': True,
        'user_id': 'a5507fc6e79e4562b4f0af20a8e87111',
    }

    if personal_enabled:
        expected_response['personal_phone_id'] = personal_phone_id

    assert data == expected_response


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'timeout': 100, 'retries': 1},
        'profile': {'use_afs': True, 'timeout': 200, 'retries': 2},
    },
)
@pytest.mark.now('2018-11-20T11:00:00+0300')
@pytest.mark.parametrize(
    'afs_resp_builder,time_offset, response_code',
    [
        (make_afs_is_spammer_response_builder, 0, 403),
        (make_afs_is_spammer_response_builder, -1, 403),
        (make_afs_is_spammer_response_builder, 60 * 60 * 4, 403),
        (make_afs_is_spammer_response_builder, None, 200),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=False,
            ),
        ),
    ],
)
def test_afs_is_spammer_checking(
        taxi_integration,
        mockserver,
        services_mocks,
        afs_resp_builder,
        time_offset,
        now,
        response_code,
):
    @mockserver.json_handler('/antifraud/client/user/is_spammer/profile')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': 'e4707fc6e79e4562b4f0af20a8e87113',
            'user_phone_id': '59246c5b6195542e9b084113',
            'user_source_id': 'call_center',
        }
        return afs_resp_builder(time_offset)(now)

    req = {
        'user': {
            'phone': '+79151111113',
            'personal_phone_id': 'p00000000000000000000003',
        },
    }
    response = taxi_integration.post(
        'v1/profile', json=req, headers=CC_HEADERS,
    )
    assert response.status_code == response_code
    if response_code != 200:
        data = response.json()
        assert 'blocked' in data
        assert 'type' in data


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=False,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'timeout': 100, 'retries': 1},
        'profile': {'use_afs': True, 'timeout': 200, 'retries': 2},
    },
)
@pytest.mark.now('2018-11-20T11:00:00+0300')
@pytest.mark.parametrize(
    'afs_resp_builder,time_offset',
    [
        (make_afs_is_spammer_response_builder, 0),
        (make_afs_is_spammer_response_builder, -1),
        (make_afs_is_spammer_response_builder, 60 * 60 * 4),
        (make_afs_is_spammer_response_builder, None),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=False,
            ),
        ),
    ],
)
def test_afs_is_spammer_disabled_in_client(
        taxi_integration,
        mockserver,
        services_mocks,
        afs_resp_builder,
        time_offset,
        now,
):
    @mockserver.json_handler('/antifraud/client/user/is_spammer/profile')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': 'e4707fc6e79e4562b4f0af20a8e87113',
            'user_phone_id': '59246c5b6195542e9b084113',
            'user_source_id': 'call_center',
        }
        return afs_resp_builder(time_offset)(now)

    req = {
        'user': {
            'phone': '+79151111113',
            'personal_phone_id': 'p00000000000000000000003',
        },
    }
    response = taxi_integration.post(
        'v1/profile', json=req, headers=CC_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'timeout': 100, 'retries': 1},
        'profile': {'use_afs': True, 'timeout': 200, 'retries': 2},
    },
)
@pytest.mark.parametrize('response_code', [500, 400, 403])
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=False,
            ),
        ),
    ],
)
def test_antifraud_affected(
        taxi_integration, mockserver, services_mocks, response_code,
):
    @mockserver.handler('/antifraud/client/user/is_spammer/profile')
    def mock_detect_invalid(request):
        return mockserver.make_response(
            '{"code":' + str(response_code) + '}', response_code,
        )

    req = {
        'user': {
            'phone': '+79151111113',
            'personal_phone_id': 'p00000000000000000000003',
        },
    }
    response = taxi_integration.post(
        'v1/profile', json=req, headers=CC_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.config(
    USER_API_USERS_ENDPOINTS={'users/integration/create': True},
)
@pytest.mark.parametrize(
    'personal_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=True,
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=False,
            ),
        ),
    ],
)
@pytest.mark.now('2018-07-20T10:15:00+0000')
def test_profile_user_api_get(
        taxi_integration, db, mockserver, services_mocks, personal_enabled,
):
    @mockserver.json_handler('/user-api/users/integration/create')
    def _mock_user_api_create_user(request):
        assert request.json == {
            'phone_id': '59246c5b6195542e9b084114',
            'sourceid': 'call_center',
            'application': 'call_center',
            'given_name': 'given-name',
        }
        db.users.find_and_modify(
            {'_id': 'e4707fc6e79e4562b4f0af20a8e87114'},
            {'$set': {'given_name': 'given-name'}},
        )
        return {
            'id': 'e4707fc6e79e4562b4f0af20a8e87114',
            'application': 'call_center',
            'sourceid': 'call_center',
            'phone_id': '59246c5b6195542e9b084114',
            'authorized': True,
            'given_name': 'given-name',
        }

    phone, personal_phone_id = '+79151111114', 'p00000000000000000000004'

    response = taxi_integration.post(
        'v1/profile',
        json={
            'user': {'phone': phone, 'personal_phone_id': personal_phone_id},
            'name': 'given-name',
            'discount_card': '044',
        },
        headers=CC_HEADERS,
    )
    assert response.status_code == 200

    expected_response = {
        'user_id': 'e4707fc6e79e4562b4f0af20a8e87114',
        'dont_ask_name': False,
        'name': 'given-name',
        'experiments': [
            'call_center_experiment_1',
            'call_center_experiment_2',
        ],
    }
    if personal_enabled:
        expected_response['personal_phone_id'] = personal_phone_id

    assert response.json() == expected_response
    assert _mock_user_api_create_user.wait_call()

    user_doc = db.users.find_one({'_id': 'e4707fc6e79e4562b4f0af20a8e87114'})
    phone_doc = db.user_phones.find_one({'_id': user_doc['phone_id']})

    assert user_doc.get('dont_ask_name') is None
    assert user_doc['given_name'] == 'given-name'
    assert phone_doc['phone'] == phone
    assert phone_doc['personal_phone_id'] == personal_phone_id


@pytest.mark.config(
    USER_API_USERS_ENDPOINTS={'users/integration/create': True},
)
@pytest.mark.now('2018-07-20T10:15:00+0000')
def test_profile_user_api_create(
        taxi_integration, db, mockserver, services_mocks,
):
    @mockserver.json_handler('/user-api/users/integration/create')
    def _mock_user_api_create_user(request):
        assert request.json == {
            'phone_id': '59246c5b6195542e9b084112',
            'sourceid': 'call_center',
            'application': 'call_center',
            'dont_ask_name': True,
        }
        db.users.insert(
            {
                '_id': '1234567890',
                'phone_id': bson.ObjectId('59246c5b6195542e9b084112'),
                'sourceid': 'call_center',
                'application': 'call_center',
                'dont_ask_name': True,
                'authorized': True,
            },
        )
        return {
            'id': '1234567890',
            'application': 'call_center',
            'sourceid': 'call_center',
            'phone_id': '59246c5b6195542e9b084112',
            'authorized': True,
            'dont_ask_name': True,
        }

    phone, personal_phone_id = '+79151111112', 'p00000000000000000000002'

    response = taxi_integration.post(
        'v1/profile',
        json={
            'user': {'phone': phone, 'personal_phone_id': personal_phone_id},
            'dont_ask_name': True,
            'discount_card': '044',
        },
        headers=CC_HEADERS,
    )
    assert response.status_code == 200

    phone_doc = db.user_phones.find_one({'phone': phone})
    user_doc = db.users.find_one({'phone_id': phone_doc['_id']})

    assert user_doc['_id'] == '1234567890'
    assert user_doc['dont_ask_name']
    assert user_doc.get('given_name') is None

    assert response.json() == {
        'user_id': user_doc['_id'],
        'dont_ask_name': True,
        'experiments': [
            'call_center_experiment_1',
            'call_center_experiment_2',
        ],
        'personal_phone_id': personal_phone_id,
    }
    assert _mock_user_api_create_user.wait_call()


@pytest.mark.parametrize(
    'sourceid,exp_enabled,had_suggest_field,should_suggest,zalogin_resp_code',
    [
        ('alice', True, True, True, 200),
        ('alice', True, True, False, 200),
        ('corp_cabinet', True, False, None, -1),
        ('alice', True, False, False, 500),
        ('alice', False, False, None, -1),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=False,
            ),
        ),
    ],
)
def test_alice_suggest_portal_signin(
        taxi_integration,
        mockserver,
        experiments3,
        services_mocks,
        sourceid,
        exp_enabled,
        had_suggest_field,
        should_suggest,
        zalogin_resp_code,
):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': exp_enabled},
        name='suggest_portal_signin',
        consumers=['integration/profile'],
        clauses=[],
        default_value={},
    )
    taxi_integration.tests_control(invalidate_caches=True)

    @mockserver.handler('/zalogin/v1/internal/suggest-portal-signin')
    def _mock_zalogin_suggest_portal_signin(request):
        assert (
            request.headers['X-YaTaxi-PhoneId'] == '59246c5b6195542e9b084111'
        )
        assert request.headers['X-Yandex-UID'] == '480301451'
        assert isinstance(should_suggest, bool)
        if zalogin_resp_code != 200:
            return mockserver.make_response(status=500)
        return mockserver.make_response(
            json.dumps({'suggest_portal_signin': should_suggest}),
        )

    response = taxi_integration.post(
        'v1/profile',
        json={
            'user': {
                'phone': '+79151111111',
                'personal_phone_id': 'p00000000000000000000001',
                'yandex_uid': '480301451',
            },
            'sourceid': sourceid,
        },
    )

    data = response.json()
    assert response.status_code == 200
    assert ('suggest_portal_signin' in data) == had_suggest_field

    if 'suggest_portal_signin' in data:
        assert data['suggest_portal_signin'] == should_suggest


TEST_PHONE = '+79151111114'
TEST_PERSONAL_PHONE_ID = 'p00000000000000000000004'

NEW_PHONE = '+79151111100'
NEW_PERSONAL_PHONE_ID = 'p00000000000000000000100'


@pytest.mark.parametrize(
    'phone_data, expected_code, personal_times_called',
    [
        pytest.param({'phone': TEST_PHONE}, 200, 1, id='only_phone'),
        pytest.param(
            {'personal_phone_id': TEST_PERSONAL_PHONE_ID},
            200,
            0,
            id='only_personal_phone_id',
        ),
        pytest.param(
            {'phone': TEST_PHONE, 'personal_phone_id': TEST_PERSONAL_PHONE_ID},
            200,
            0,
            id='both',
        ),
        pytest.param({}, 400, 0, id='none'),
        pytest.param(
            {'phone': NEW_PHONE},
            200,
            1,
            id='phone_doc_does_not_exist_for_phone',
        ),
        pytest.param(
            {'personal_phone_id': 'p00000000000000000000100'},
            200,
            0,
            id='phone_doc_does_not_exist_for_personal',
        ),
        pytest.param({'phone': '+7915'}, 400, 0, id='phone_bad_format'),
    ],
)
@pytest.mark.parametrize(
    'personal_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=True,
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=False,
            ),
        ),
    ],
)
def test_personal(
        taxi_integration,
        mockserver,
        db,
        services_mocks,
        phone_data,
        expected_code,
        personal_times_called,
        personal_enabled,
):
    """
    Test checks whether personal client should be called based on user_identity
    passed with request. If personal_phone_id is missing it should be retrieved
    via personal service.
    """

    @mockserver.json_handler('/personal/v1/phones/store')
    def mock_personal_store(request):
        request_json = json.loads(request.get_data())
        assert 'value' in request_json
        if request_json['value'] == TEST_PHONE:
            return {'id': TEST_PERSONAL_PHONE_ID, 'value': TEST_PHONE}
        elif request_json['value'] == NEW_PHONE:
            return {'id': NEW_PERSONAL_PHONE_ID, 'value': NEW_PHONE}
        else:
            return mockserver.make_response({}, 400)

    request_body = {'user': phone_data}

    response = taxi_integration.post(
        'v1/profile', json=request_body, headers=CC_HEADERS,
    )

    # differences in the old behaviour
    # which is based on using a raw phone number
    if not personal_enabled:
        # personal/phones/store always gets called during GetOrCreatePhoneDoc
        personal_times_called = 1

        if 'phone' not in phone_data:
            expected_code = 400

    assert response.status_code == expected_code
    if expected_code == 200:
        assert mock_personal_store.times_called == personal_times_called

        phone_doc = db.user_phones.find_one(phone_data)
        assert phone_doc is not None


@pytest.mark.config(
    INTEGRATION_SUPPORTED_APPLICATIONS=['agent_007'],
    CREATE_INTEGRATION_USERS_WITHOUT_SOURCE_ID_APPS=['agent_007'],
    INTEGRATION_API_PERSONAL_IN_PROFILE_ENABLED=True,
    APPLICATION_DETECTION_RULES_NEW={'rules': [{'@app_name': 'agent_007'}]},
)
@pytest.mark.now('2018-07-20T10:15:00+0000')
def test_no_source_id(taxi_integration, db, mockserver, services_mocks):
    db.users.remove()
    db.user_phones.remove()

    application = 'agent_007'

    request_body = {'user': {'phone': '+79151111100'}}

    headers = {'User-Agent': application}
    response = taxi_integration.post(
        'v1/profile', json=request_body, headers=headers,
    )
    assert response.status_code == 200, response
    data = response.json()

    assert data is not None
    response_user_id = data['user_id']
    user_doc = db.users.find_one({'_id': response_user_id})
    assert user_doc.get('sourceid') is None
    assert user_doc['application'] == 'agent_007'


@pytest.mark.parametrize(
    'phone', [pytest.param('+79151111100'), pytest.param('+79151111110')],
)
@pytest.mark.config(USER_API_USE_USER_PHONES_CREATION=True)
@pytest.mark.experiments3(filename='experiments3_profile.json')
@pytest.mark.now('2020-02-03T20:00:00.00+0000')
def test_audience_category(
        taxi_integration, db, mockserver, services_mocks, phone,
):
    @mockserver.handler('/user-api/user_phones')
    def mock_detect_invalid(request):
        response = {
            'is_new_number': True,
            'created': '2019-11-21T14:15:31.787+0000',
            'updated': '2020-02-03T13:29:14.14+0000',
            'stat': {
                'big_first_discounts': 0,
                'complete': 50,
                'complete_card': 3,
                'complete_apple': 0,
                'complete_google': 0,
                'total': 50,
                'fake': 0,
            },
            'is_loyal': False,
            'is_yandex_staff': True,
            'is_taxi_staff': True,
            'bound_uid': '4034765244',
            'last_order': {'city_id': 'Москва', 'nearest_zone': 'moscow'},
            'last_payment_method': {'type': 'cash'},
            'id': '5dd69c0358204bb4a0a225b8',
            'phone': '+79151111100',
            'type': 'yandex',
            'personal_phone_id': 'p00000000000000000000100',
        }

        data = request.json
        if data['personal_phone_id'] == 'p00000000000000000000100':
            return mockserver.make_response(json.dumps(response), status=200)
        if data['personal_phone_id'] == 'p00000000000000000000000':
            response.pop('is_new_number')
            return mockserver.make_response(json.dumps(response), status=200)
        return mockserver.make_response(status=400)

    db.user_phones.remove()

    request_body = {'user': {'phone': phone}}

    response = taxi_integration.post(
        'v1/profile', json=request_body, headers=CC_HEADERS,
    )

    assert response.status_code == 200
    data = response.json()
    if phone == '+79151111100':
        assert 'audience_category' in data
        assert data['audience_category'] == 'newbie'
    if phone == '+79151111110':
        assert 'audience_category' not in data
