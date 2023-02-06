import json

import pytest


"""
All tests are in protocol's suggest!
As at the curent time int-api's suggest is protocols's suggest
(just a proxy in fastcgi)
here we need only to test authorization and simple checks
"""


@pytest.fixture()
def mock_response(load_json):
    return load_json('response_persuggest_action_pin_drop.json')


TEST_PHONE = '+74951234001'
TEST_PERSONAL_PHONE_ID = 'p11111111111111111111110'


EN_HEADERS = {'Accept-Language': 'en'}
CC_EN_HEADERS = {'Accept-Language': 'en', 'User-Agent': 'call_center'}


@pytest.mark.parametrize(
    'user_identity, expected_code, personal_times_called',
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
    ],
)
def test_suggest_pindrop(
        taxi_integration,
        mockserver,
        blackbox_service,
        load_json,
        mock_response,
        user_identity,
        expected_code,
        personal_times_called,
):
    blackbox_service.set_token_info('test_token', '4003514353')

    @mockserver.json_handler('/personal/v1/phones/find')
    def mock_personal_phones_find(request):
        request_json = json.loads(request.get_data())
        assert request_json == {'value': TEST_PHONE}
        return {'id': TEST_PERSONAL_PHONE_ID, 'value': TEST_PHONE}

    @mockserver.json_handler('/persuggest/finalsuggest')
    def mock_persuggest(request):
        assert request.headers['X-Yataxi-Request-Source'] == 'suggest'
        assert request.headers['X-Yataxi-UserId'] == 'user_call_center'
        assert request.headers['X-Yandex-UID'] == '4003514353'
        assert request.headers['X-Request-Language'] == 'en'
        assert json.loads(request.get_data()) == load_json(
            'expected_request_action_pin_drop.json',
        )
        return mock_response

    request = load_json('request_action_pin_drop.json')
    request['user'].update(user_identity)
    response = taxi_integration.post(
        '/v1/suggest', request, headers=CC_EN_HEADERS,
    )
    assert response.status_code == expected_code, response.text

    if expected_code == 200:
        assert response.json() == load_json('response_action_pin_drop.json')

    assert mock_personal_phones_find.times_called == personal_times_called


@pytest.mark.parametrize(
    'source,yandex_uid_required,send_phone',
    [
        ('call_center', False, True),
        ('corp_cabinet', False, False),
        ('alice', True, True),
    ],
)
@pytest.mark.parametrize(
    'user_id_prefix,personal_phone_id,user_exists',
    [
        ('user_', TEST_PERSONAL_PHONE_ID, True),
        ('user_not_exists_', 'non_existent_personal', False),
    ],
)
def test_suggest_integration_auth(
        taxi_integration,
        mockserver,
        blackbox_service,
        load_json,
        user_id_prefix,
        personal_phone_id,
        user_exists,
        source,
        yandex_uid_required,
        send_phone,
        mock_response,
):
    blackbox_service.set_token_info('test_token', '4003514353')
    user_id = user_id_prefix + source

    @mockserver.json_handler('/persuggest/finalsuggest')
    def mock_persuggest(request):
        assert request.headers['X-Yataxi-Request-Source'] == 'suggest'
        assert request.headers['X-Yataxi-UserId'] == user_id
        request_json = json.loads(request.get_data())

        assert request_json['user_identity']['user_id'] == user_id

        if user_exists:
            assert (
                request_json['user_identity']['yandex_uuid']
                == '289146501a14f6cf5aca8a5885022cfc'
            )
        else:
            assert 'yandex_uuid' not in request_json['user_identity']

        return mock_response

    request = load_json('request_action_pin_drop.json')
    if source == 'call_center':
        headers = CC_EN_HEADERS
    else:
        request['sourceid'] = source
        headers = EN_HEADERS

    request['user']['id'] = user_id
    if send_phone:
        request['user']['personal_phone_id'] = personal_phone_id
    if yandex_uid_required:
        request['user']['yandex_uid'] = '4003514353'

    response = taxi_integration.post('/v1/suggest', request, headers=headers)
    assert response.status_code == 200

    assert response.json() == load_json('response_action_pin_drop.json')
    assert mock_persuggest.times_called == 1


def test_suggest_without_user_and_source_id(
        taxi_integration, mockserver, load_json, mock_response,
):
    user_id = 'user'

    @mockserver.json_handler('/persuggest/finalsuggest')
    def mock_persuggest(request):
        assert request.headers['X-Yataxi-Request-Source'] == 'suggest'
        assert request.headers['X-Yataxi-UserId'] == user_id
        request_json = json.loads(request.get_data())
        assert request_json['user_identity']['user_id'] == user_id
        return mock_response

    request = load_json('request_action_pin_drop.json')
    request.pop('user')
    request['id'] = user_id
    response = taxi_integration.post(
        '/v1/suggest', request, headers=EN_HEADERS,
    )
    assert response.status_code == 200, response.text

    assert response.json() == load_json('response_action_pin_drop.json')
    assert mock_persuggest.times_called == 1


@pytest.mark.parametrize(
    'user_id, phone, yandex_uid, source_id, headers, error_text',
    [
        # no yandex_uid in alice request
        (
            'user_alice',
            TEST_PHONE,
            None,
            'alice',
            EN_HEADERS,
            'for Alice should contain non empty \'yandex_uid\'',
        ),
        # no user_phone in call_center request
        (
            'user_call_center',
            None,
            None,
            None,
            CC_EN_HEADERS,
            'either personal_phone_id or phone should be passed',
        ),
        # empty user_phone in call_center request
        (
            'user_call_center',
            '',
            None,
            None,
            CC_EN_HEADERS,
            'either personal_phone_id or phone should be passed',
        ),
    ],
)
def test_suggest_errors(
        mockserver,
        taxi_integration,
        blackbox_service,
        load_json,
        user_id,
        phone,
        yandex_uid,
        source_id,
        headers,
        error_text,
):
    @mockserver.json_handler('/personal/v1/phones/find')
    def mock_personal_phones_find(request):
        request_json = json.loads(request.get_data())
        if request_json['value'] == TEST_PHONE:
            return {'id': TEST_PERSONAL_PHONE_ID, 'value': TEST_PHONE}
        else:
            return mockserver.make_response(status=404)

    request = load_json('request_action_pin_drop.json')
    request['user']['id'] = user_id
    request['user']['phone'] = phone
    request['user']['yandex_uid'] = yandex_uid
    if source_id:
        request['sourceid'] = source_id

    response = taxi_integration.post('/v1/suggest', request, headers=headers)

    assert response.status_code == 400
    assert response.json()['error']['text'] == error_text
    if phone:
        assert mock_personal_phones_find.times_called == 1


@pytest.mark.parametrize(
    'user_info, status_code, error_text',
    [
        [
            {
                'user': {
                    'id': 'user1',
                    'personal_phone_id': TEST_PERSONAL_PHONE_ID,
                },
            },
            200,
            None,
        ],
        [{'id': 'user1'}, 200, None],
        [{}, 400, 'Either \'user\' or \'id\' should be in request'],
        [
            {'user': {'id': 'user1'}, 'id': 'user1'},
            400,
            'Passing both user and id is not allowed',
        ],
        [{'id': ''}, 400, 'Empty user_id in request'],
        [
            {'user': {'personal_phone_id': TEST_PERSONAL_PHONE_ID}},
            400,
            'failed parsing suggest request: no id',
        ],
    ],
)
def test_suggest_user_id_source(
        taxi_integration,
        mockserver,
        load_json,
        mock_response,
        user_info,
        status_code,
        error_text,
):
    @mockserver.json_handler('/persuggest/finalsuggest')
    def mock_persuggest(request):
        assert request.headers['X-Yataxi-Request-Source'] == 'suggest'
        request_json = json.loads(request.get_data())
        assert request_json['user_identity']['user_id'] == 'user1'
        return mock_response

    request = load_json('request_action_pin_drop.json')
    request.pop('user')

    assert 'id' not in request
    assert 'user' not in request

    request.update(user_info)

    response = taxi_integration.post(
        '/v1/suggest', request, headers=EN_HEADERS,
    )
    assert response.status_code == status_code

    if response.status_code != 200:
        assert response.json()['error']['text'] == error_text
        assert mock_persuggest.times_called == 0
    else:
        assert response.json() == load_json('response_action_pin_drop.json')
        assert mock_persuggest.times_called == 1


@pytest.mark.parametrize(
    'update, headers, status_code, error_text, user_exists',
    [
        # Everything is fine
        (
            {
                'user': {
                    'id': 'user_alice',
                    'phone': TEST_PHONE,
                    'personal_phone_id': TEST_PERSONAL_PHONE_ID,
                    'yandex_uid': '4003514353',
                },
                'sourceid': 'alice',
            },
            EN_HEADERS,
            200,
            None,
            True,
        ),
        # Request source_id doesn't match user's
        (
            {
                'user': {
                    'id': 'user_alice',
                    'phone': TEST_PHONE,
                    'personal_phone_id': TEST_PERSONAL_PHONE_ID,
                    'yandex_uid': '4003514353',
                },
            },
            CC_EN_HEADERS,
            400,
            'user sourceid doesn\'t match request source_id',
            None,
        ),
        # User is not auhorized
        (
            {
                'user': {
                    'id': 'unauthorized',
                    'phone': TEST_PHONE,
                    'personal_phone_id': TEST_PERSONAL_PHONE_ID,
                },
            },
            CC_EN_HEADERS,
            200,
            None,
            False,
        ),
        # Phone id and user_id don't match
        (
            {
                'user': {
                    'id': 'user_call_center',
                    'personal_phone_id': 'nonexistent_ppi',
                },
            },
            CC_EN_HEADERS,
            400,
            'user personal_phone_id doesn\'t match request personal_phone_id',
            None,
        ),
        # Alice wrong 'yandex_uid'
        (
            {
                'user': {
                    'id': 'user_alice',
                    'phone': TEST_PHONE,
                    'personal_phone_id': TEST_PERSONAL_PHONE_ID,
                    'yandex_uid': '000000000',
                },
                'sourceid': 'alice',
            },
            EN_HEADERS,
            400,
            'user yandex_uid doesn\'t match request yandex_uid',
            None,
        ),
        # Alice wrong 'yandex_uid'
        (
            {
                'user': {
                    'id': 'user_alice',
                    'phone': TEST_PHONE,
                    'personal_phone_id': TEST_PERSONAL_PHONE_ID,
                },
                'sourceid': 'alice',
            },
            EN_HEADERS,
            400,
            'for Alice should contain non empty \'yandex_uid\'',
            None,
        ),
    ],
)
def test_input_errors(
        taxi_integration,
        mockserver,
        mock_response,
        load_json,
        update,
        headers,
        status_code,
        error_text,
        user_exists,
):
    @mockserver.json_handler('/persuggest/finalsuggest')
    def mock_persuggest(request):
        assert request.headers['X-Yataxi-Request-Source'] == 'suggest'
        request_json = json.loads(request.get_data())

        if user_exists:
            assert (
                request_json['user_identity']['yandex_uuid']
                == '289146501a14f6cf5aca8a5885022cfc'
            )
        else:
            assert 'yandex_uuid' not in request_json['user_identity']

        return mock_response

    request = load_json('request_action_pin_drop.json')
    request.update(update)

    response = taxi_integration.post('/v1/suggest', request, headers=headers)

    assert response.status_code == status_code

    if response.status_code != 200:
        assert response.json()['error']['text'] == error_text
        assert mock_persuggest.times_called == 0
    else:
        assert response.json() == load_json('response_action_pin_drop.json')
        assert mock_persuggest.times_called == 1


@pytest.mark.config(USER_API_USERS_ENDPOINTS={'users/get': True})
def test_no_phone_id(taxi_integration, mockserver, mock_response, load_json):
    @mockserver.json_handler('/persuggest/finalsuggest')
    def mock_persuggest(request):
        return mock_response

    @mockserver.json_handler('/user-api/users/get')
    def mock_user_get(request):
        return {'id': 'user_id'}

    request = load_json('request_action_pin_drop.json')
    request['id'] = 'user_id'
    request.pop('user')
    response = taxi_integration.post(
        '/v1/suggest', request, headers=EN_HEADERS,
    )

    assert response.status_code == 200
