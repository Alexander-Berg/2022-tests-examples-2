import datetime

import pytest


@pytest.fixture(name='mock_user_api')
def _mock_user_api(mockserver):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return {
            'id': 'user',
            'gcm_token': '1234567',
            'application': 'test_app',
        }

    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve_bulk')
    def _phones_retrieve_bulk(request):
        return {'items': [{}]}


@pytest.fixture(name='mock_xiva_v2_send')
def _mock_xiva_v2_send(mockserver):
    def _mock(code, headers=None):
        if headers is None:
            headers = {'TransitID': 'id'}

        if code == 200:
            message = 'Ok'
        else:
            message = 'Internal error'

        @mockserver.json_handler('/xiva/v2/send')
        def _mock_xiva(request):
            return mockserver.make_response(message, code, headers=headers)

    return _mock


async def _send_push(
        taxi_ucommunications,
        headers=None,
        expected_code=200,
        expected_body=None,
):
    if headers is None:
        headers = {'X-Idempotency-Token': '12345'}
    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={'user': 'user', 'data': {}, 'intent': 'taxi_in_the_way'},
        headers=headers,
    )
    assert response.status_code == expected_code
    if expected_body is not None:
        assert response.json() == expected_body


async def _send_sms(taxi_ucommunications):
    return await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )


@pytest.mark.now('2020-01-31T00:00:00Z')
async def test_disabled(
        taxi_ucommunications, mockserver, mock_personal, mongodb,
):
    @mockserver.json_handler('/yasms/sendsms')
    def mock_yams(request):
        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    assert mongodb.communications_request_idempotency_tokens.count() == 0

    response = await _send_sms(taxi_ucommunications)
    assert response.status_code == 200
    assert mock_yams.times_called == 1
    assert mongodb.communications_request_idempotency_tokens.count() == 0


@pytest.mark.now('2020-01-31T00:00:00Z')
async def test_simple(
        taxi_ucommunications, mockserver, mock_personal, mongodb, load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents_request_idempotency.json')

    @mockserver.json_handler('/yasms/sendsms')
    def mock_yams(request):
        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    assert mongodb.communications_request_idempotency_tokens.count() == 0

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'idempotency',
        },
    )
    assert response.status_code == 200
    assert mock_yams.times_called == 1
    assert mongodb.communications_request_idempotency_tokens.count() == 1
    doc = mongodb.communications_request_idempotency_tokens.find_one()
    assert doc['request_type'] == 'handler-user_sms_send-post:idempotency'
    assert doc['status'] == 'success'
    assert doc['delete_after'] == datetime.datetime(2020, 1, 31, 0, 1)


@pytest.mark.filldb(communications_request_idempotency_tokens='already_done')
@pytest.mark.now('2020-01-31T00:00:00Z')
async def test_request_already_done(
        taxi_ucommunications, mockserver, mock_personal, mongodb, load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents_request_idempotency_already_done.json')

    @mockserver.json_handler('/yasms/sendsms')
    def mock_yams(request):
        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    assert mongodb.communications_request_idempotency_tokens.count() == 1

    doc_before = mongodb.communications_request_idempotency_tokens.find_one()
    assert doc_before['delete_after'] == datetime.datetime(2020, 1, 31, 0, 2)

    response = await _send_sms(taxi_ucommunications)
    assert response.status_code == 200
    assert mock_yams.times_called == 0

    assert mongodb.communications_request_idempotency_tokens.count() == 1
    doc_after = mongodb.communications_request_idempotency_tokens.find_one()
    assert doc_after['delete_after'] == datetime.datetime(2020, 1, 31, 0, 5)


@pytest.mark.filldb(
    communications_request_idempotency_tokens='previous_failed',
)
@pytest.mark.now('2020-01-31T00:00:00Z')
async def test_previous_request_failed(
        taxi_ucommunications, mockserver, mock_personal, mongodb, load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents_request_idempotency_request_failed.json')

    @mockserver.json_handler('/yasms/sendsms')
    def mock_yams(request):
        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    assert mongodb.communications_request_idempotency_tokens.count() == 1
    doc_before = mongodb.communications_request_idempotency_tokens.find_one()
    assert doc_before['status'] == 'failed'

    response = await _send_sms(taxi_ucommunications)
    assert response.status_code == 200
    assert mock_yams.times_called == 1
    assert mongodb.communications_request_idempotency_tokens.count() == 1
    doc_after = mongodb.communications_request_idempotency_tokens.find_one()
    assert doc_after['status'] == 'success'


@pytest.mark.filldb(
    communications_request_idempotency_tokens='previous_frozen',
)
@pytest.mark.now('2020-01-31T00:00:00Z')
async def test_previous_request_expired(
        taxi_ucommunications, mockserver, mock_personal, mongodb, load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents_request_idempotency_request_failed.json')

    @mockserver.json_handler('/yasms/sendsms')
    def mock_yams(request):
        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    assert mongodb.communications_request_idempotency_tokens.count() == 1
    doc_before = mongodb.communications_request_idempotency_tokens.find_one()
    assert doc_before['status'] == 'pending'

    response = await _send_sms(taxi_ucommunications)
    assert response.status_code == 200
    assert mock_yams.times_called == 1
    assert mongodb.communications_request_idempotency_tokens.count() == 1
    doc_after = mongodb.communications_request_idempotency_tokens.find_one()
    assert doc_after['status'] == 'success'


@pytest.mark.filldb(
    communications_request_idempotency_tokens='pending_not_expired',
)
@pytest.mark.now('2020-01-31T00:00:00Z')
async def test_previous_pending_not_expired(
        taxi_ucommunications, mockserver, mock_personal, mongodb, load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents_request_idempotency_request_failed.json')

    @mockserver.json_handler('/yasms/sendsms')
    def mock_yams(request):
        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    assert mongodb.communications_request_idempotency_tokens.count() == 1
    doc_before = mongodb.communications_request_idempotency_tokens.find_one()

    response = await _send_sms(taxi_ucommunications)
    assert response.status_code == 409
    assert mock_yams.times_called == 0
    assert mongodb.communications_request_idempotency_tokens.count() == 1

    doc_after = mongodb.communications_request_idempotency_tokens.find_one()
    doc_after.pop('delete_after')
    doc_before.pop('delete_after')
    assert doc_after == doc_before


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_PUSH_IDEMPOTENCY={
        'rules': [
            {
                'applications': ['test_app'],
                'intents': ['taxi_another_intent'],
                'settings': {'enabled': True, 'token_ttl': 5000},
            },
        ],
    },
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
async def test_push_disabled(
        taxi_ucommunications, mongodb, mock_user_api, mock_xiva_v2_send,
):
    mock_xiva_v2_send(code=200)
    mongodb.communications_request_idempotency_tokens.remove()

    await _send_push(taxi_ucommunications)

    assert mongodb.communications_request_idempotency_tokens.count() == 0


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_PUSH_IDEMPOTENCY={
        'rules': [
            {
                'applications': ['test_app'],
                'intents': ['taxi_in_the_way'],
                'settings': {'enabled': True, 'token_ttl': 5000},
            },
        ],
    },
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
async def test_push_simple(
        taxi_ucommunications, mongodb, mock_user_api, mock_xiva_v2_send,
):
    mock_xiva_v2_send(code=200)
    mongodb.communications_request_idempotency_tokens.remove()

    await _send_push(taxi_ucommunications)

    assert mongodb.communications_request_idempotency_tokens.count() == 1
    doc_after = mongodb.communications_request_idempotency_tokens.find_one()
    assert doc_after['status'] == 'success'
    assert (
        doc_after['delete_after'] - doc_after['created']
    ) == datetime.timedelta(seconds=5)


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_PUSH_IDEMPOTENCY={
        'rules': [
            {
                'applications': ['app1'],
                'intents': ['intent1'],
                'settings': {'enabled': True, 'token_ttl': 7000},
            },
            {
                'applications': ['test_app'],
                'intents': ['intent1'],
                'settings': {'enabled': True, 'token_ttl': 6000},
            },
            {
                'applications': ['test_app'],
                'intents': ['*'],
                'settings': {'enabled': True, 'token_ttl': 5000},
            },
        ],
    },
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
async def test_any_intent(
        taxi_ucommunications, mongodb, mock_user_api, mock_xiva_v2_send,
):
    mock_xiva_v2_send(code=200)
    mongodb.communications_request_idempotency_tokens.remove()

    await _send_push(taxi_ucommunications)

    assert mongodb.communications_request_idempotency_tokens.count() == 1
    doc_after = mongodb.communications_request_idempotency_tokens.find_one()
    assert doc_after['status'] == 'success'
    assert (
        doc_after['delete_after'] - doc_after['created']
    ) == datetime.timedelta(seconds=5)


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_PUSH_IDEMPOTENCY={
        'rules': [
            {
                'applications': ['*'],
                'intents': ['another_intent'],
                'settings': {'enabled': True, 'token_ttl': 5000},
            },
        ],
    },
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
async def test_any_app_another_intent(
        taxi_ucommunications, mongodb, mock_user_api, mock_xiva_v2_send,
):
    mock_xiva_v2_send(code=200)
    mongodb.communications_request_idempotency_tokens.remove()

    await _send_push(taxi_ucommunications)
    assert mongodb.communications_request_idempotency_tokens.count() == 0


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_PUSH_IDEMPOTENCY={
        'rules': [
            {
                'applications': ['*'],
                'intents': ['*'],
                'settings': {'enabled': True, 'token_ttl': 5000},
            },
        ],
    },
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
async def test_any_app_and_intent(
        taxi_ucommunications, mongodb, mock_user_api, mock_xiva_v2_send,
):
    mock_xiva_v2_send(code=200)
    mongodb.communications_request_idempotency_tokens.remove()

    await _send_push(taxi_ucommunications)

    assert mongodb.communications_request_idempotency_tokens.count() == 1
    doc_after = mongodb.communications_request_idempotency_tokens.find_one()
    assert doc_after['status'] == 'success'
    assert (
        doc_after['delete_after'] - doc_after['created']
    ) == datetime.timedelta(seconds=5)


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_PUSH_IDEMPOTENCY={
        'rules': [
            {
                'applications': ['test_app'],
                'intents': ['taxi_in_the_way'],
                'settings': {'enabled': False, 'token_ttl': 5000},
            },
        ],
    },
    COMMUNICATIONS_USER_NOTIFICATION_USE_TOKEN_IF_EXISTS=True,
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
@pytest.mark.parametrize(
    'is_app_in_config',
    (
        True,
        pytest.param(
            False,
            marks=pytest.mark.config(
                COMMUNICATIONS_USER_NOTIFICATION_PUSH_IDEMPOTENCY={
                    'rules': [],
                },
            ),
        ),
    ),
)
@pytest.mark.parametrize('do_send_token', (True, False))
async def test_use_push_token_if_exists(
        taxi_ucommunications,
        mongodb,
        mock_user_api,
        mock_xiva_v2_send,
        is_app_in_config,
        do_send_token,
):
    mock_xiva_v2_send(code=200)
    mongodb.communications_request_idempotency_tokens.remove()

    await _send_push(
        taxi_ucommunications, headers=None if do_send_token else {},
    )

    assert mongodb.communications_request_idempotency_tokens.count() == (
        1 if do_send_token else 0
    )
    if not do_send_token:
        return
    doc_after = mongodb.communications_request_idempotency_tokens.find_one()
    assert doc_after['status'] == 'success'
    if is_app_in_config:
        expected_delta = datetime.timedelta(seconds=5)
    else:
        expected_delta = datetime.timedelta(seconds=4.5)
    assert doc_after['delete_after'] - doc_after['created'] == expected_delta


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_PUSH_IDEMPOTENCY={
        'rules': [
            {
                'applications': ['test_app'],
                'intents': ['taxi_in_the_way'],
                'settings': {'enabled': True},
            },
        ],
    },
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    UCOMMUNICATIONS_CLIENT_QOS={
        '__default__': {'attempts': 2, 'timeout-ms': 1500},
    },
)
async def test_push_default_ttl(
        taxi_ucommunications, mongodb, mock_user_api, mock_xiva_v2_send,
):
    mock_xiva_v2_send(code=200)
    mongodb.communications_request_idempotency_tokens.remove()

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={
            'user': 'user',
            'data': {},
            'confirm': True,
            'intent': 'taxi_in_the_way',
        },
        headers={'X-Idempotency-Token': '12345'},
    )
    assert response.status_code == 200

    assert mongodb.communications_request_idempotency_tokens.count() == 1
    doc_after = mongodb.communications_request_idempotency_tokens.find_one()
    assert doc_after['status'] == 'success'
    assert (
        doc_after['delete_after'] - doc_after['created']
    ) == datetime.timedelta(seconds=3)


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_PUSH_IDEMPOTENCY={
        'rules': [
            {
                'applications': ['test_app'],
                'intents': ['taxi_in_the_way'],
                'settings': {'enabled': True, 'token_ttl': 5000},
            },
        ],
    },
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
@pytest.mark.parametrize('xiva_code,response_code', [(500, 502), (400, 400)])
async def test_xiva_failed(
        taxi_ucommunications,
        mongodb,
        xiva_code,
        response_code,
        mock_user_api,
        mock_xiva_v2_send,
):
    mock_xiva_v2_send(code=xiva_code, headers={})
    mongodb.communications_request_idempotency_tokens.remove()
    assert mongodb.communications_request_idempotency_tokens.count() == 0

    await _send_push(taxi_ucommunications, expected_code=response_code)
    assert mongodb.communications_request_idempotency_tokens.count() == 1
    doc_after = mongodb.communications_request_idempotency_tokens.find_one()
    assert doc_after['status'] == 'failed'


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_PUSH_IDEMPOTENCY={
        'rules': [
            {
                'applications': ['test_app'],
                'intents': ['taxi_in_the_way'],
                'settings': {'enabled': True, 'token_ttl': 5000},
            },
        ],
    },
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
@pytest.mark.filldb(
    communications_request_idempotency_tokens='user_notification_conflict',
)
@pytest.mark.now('2020-01-31T00:00:00Z')
async def test_notifiction_conflict(
        taxi_ucommunications, mongodb, mock_user_api, mock_xiva_v2_send,
):
    mock_xiva_v2_send(code=200)
    assert mongodb.communications_request_idempotency_tokens.count() == 1

    expected_body = {'code': '409', 'message': 'Request already in progress'}
    await _send_push(
        taxi_ucommunications, expected_code=409, expected_body=expected_body,
    )


@pytest.mark.config(
    UCOMMUNICATIONS_CLIENT_QOS={
        '/driver/sms/send': {'attempts': 3, 'timeout-ms': 1500},
        '/general/sms/send': {'attempts': 1, 'timeout-ms': 2000},
        '/user/notification/push': {'attempts': 2, 'timeout-ms': 2500},
        '/user/sms/send': {'attempts': 1, 'timeout-ms': 2000},
        '__default__': {'attempts': 2, 'timeout-ms': 1500},
    },
)
@pytest.mark.now('2020-01-31T00:00:00Z')
async def test_default_ttl(
        taxi_ucommunications,
        mockserver,
        mock_personal,
        mongodb,
        mock_xiva_v2_send,
        load_json,
):
    @mockserver.json_handler('/yasms/sendsms')
    def _mock_yams(request):
        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    mock_xiva_v2_send(code=200)

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'idempotency_default_ttl',
        },
    )
    assert response.status_code == 200
    doc = mongodb.communications_request_idempotency_tokens.find_one(
        {'request_type': 'handler-user_sms_send-post:idempotency_default_ttl'},
    )
    ttl = doc['delete_after'] - doc['created']
    assert ttl == datetime.timedelta(seconds=2)

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_driver_profiles_driver_profiles_retrieve(request):
        return load_json('driver_profiles_by_phone.json')

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'idempotency_default_ttl',
        },
    )
    assert response.status_code == 200
    doc = mongodb.communications_request_idempotency_tokens.find_one(
        {
            'request_type': (
                'handler-driver_sms_send-post:idempotency_default_ttl'
            ),
        },
    )
    ttl = doc['delete_after'] - doc['created']
    assert ttl == datetime.timedelta(milliseconds=4500)

    response = await taxi_ucommunications.post(
        'general/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'idempotency_default_ttl',
        },
    )
    assert response.status_code == 200
    doc = mongodb.communications_request_idempotency_tokens.find_one(
        {
            'request_type': (
                'handler-general_sms_send-post:idempotency_default_ttl'
            ),
        },
    )
    ttl = doc['delete_after'] - doc['created']
    assert ttl == datetime.timedelta(seconds=2)


async def test_send_idepotency_fallback(
        taxi_ucommunications,
        mock_yasms,
        statistics,
        mongodb,
        load_json,
        mockserver,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents_request_idempotency.json')

    assert mongodb.communications_request_idempotency_tokens.count() == 0

    test_payload = {
        'park_id': 'PARK_ID',
        'driver_id': 'DRIVER_ID',
        'text': 'Добрый день!',
        'intent': 'idempotency',
    }

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json=test_payload,
        headers={'X-Idempotency-Token': '11111'},
    )
    assert response.status_code == 200
    assert mongodb.communications_request_idempotency_tokens.count() == 1

    mongodb.communications_request_idempotency_tokens.remove()
    statistics.fallbacks = [
        'idempotency_handler-driver_sms_send-post_disabled',
    ]
    await taxi_ucommunications.invalidate_caches()
    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json=test_payload,
        headers={'X-Idempotency-Token': '22222'},
    )
    assert response.status_code == 200
    assert mongodb.communications_request_idempotency_tokens.count() == 0


async def test_idepotency_mongo_error_counter(
        taxi_ucommunications,
        mock_yasms,
        testpoint,
        statistics,
        load_json,
        mockserver,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents_request_idempotency.json')

    mongo_error_simulation = False

    @testpoint('simulate__token_checker_with_fallback__mongo_error')
    def _simulate__token_checker_with_fallback__mongo_error(data):
        return {'inject_failure': mongo_error_simulation}

    test_payload = {
        'park_id': 'PARK_ID',
        'driver_id': 'DRIVER_ID',
        'text': 'Добрый день!',
        'intent': 'idempotency',
    }
    test_metric = 'mongo.idempotency.handler-driver_sms_send-post'

    async with statistics.capture(taxi_ucommunications) as capture:
        await taxi_ucommunications.post(
            'driver/sms/send',
            json=test_payload,
            headers={'X-Idempotency-Token': '11111'},
        )
    assert capture.statistics[f'{test_metric}.success'] == 1
    assert f'{test_metric}.error' not in capture.statistics

    mongo_error_simulation = True
    async with statistics.capture(taxi_ucommunications) as capture:
        await taxi_ucommunications.post(
            'driver/sms/send',
            json=test_payload,
            headers={'X-Idempotency-Token': '22222'},
        )
    assert f'{test_metric}.success' not in capture.statistics
    assert capture.statistics[f'{test_metric}.error'] == 1
