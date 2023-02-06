import hashlib
import json
import urllib

import pytest


@pytest.mark.parametrize(
    'user_id, docs_count, list_response, token',
    [
        ('user_1', 1, '[]', 'token'),  # same hash
        ('user_1', 1, '[]', 'new_token'),  # another hash
        (
            'user_2',
            2,
            '[{"id": "user_2", "session": "old_yandex_uuid"}]',
            'token',
        ),  # unsubscribe existing user
        ('user_2', 2, '[]', 'token'),  # new taxi user
    ],
)
async def test_user_subscription_task(
        taxi_ucommunications,
        mockserver,
        stq_runner,
        mongodb,
        user_id,
        docs_count,
        list_response,
        token,
):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return {'id': 'user_id'}

    @mockserver.json_handler('/xiva/v2/unsubscribe/app')
    def _unsubscribe_app(request):
        assert request.args['user'] != request.args['uuid']
        return mockserver.make_response('OK', 200)

    @mockserver.json_handler('/xiva/v2/list')
    def _xiva_list(request):
        response = json.dumps(list_response)
        if response:
            assert request.args == {'service': 'taxi', 'user': user_id}
        return mockserver.make_response(
            list_response, 200, headers={'TransitID': 'id'},
        )

    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe_app(request, *args, **kwargs):
        if not list_response:
            assert False
        assert request.args == {
            'user': user_id,
            'uuid': user_id,
            'platform': 'ios',
            'app_name': 'ru.yandex.taxi.inhouse',
            'service': 'taxi',
        }
        body = f'push_token={token}'
        assert request.get_data() == str.encode(body)
        return mockserver.make_response('OK', 200)

    await stq_runner.user_notification_subscription.call(
        task_id='sample_task',
        kwargs={
            'user_id': user_id,
            'application': 'iphone',
            'token': token,
            'token_type': 'apns',
            'build_type': 'inhouse-distr',
            'push_tokens_hash': {
                'apns_token_hash': hashlib.md5(token.encode()).hexdigest(),
                'gcm_token_hash': hashlib.md5(''.encode()).hexdigest(),
                'hms_token_hash': hashlib.md5(''.encode()).hexdigest(),
            },
        },
    )
    assert mongodb.user_notification_subscription.count() == docs_count


@pytest.mark.parametrize(
    'user_id, list_response, token, task_id, inserted, modified, '
    'expected_task_id',
    [
        ('user_0', '[]', 'token', 'task_0', 1, 0, 'task_0'),  # new taxi user
        ('user_1', '[]', 'token', 'task_1', 0, 1, 'task_1'),  # same hash
        (
            'user_1',
            '[]',
            'new_token',
            'task_2',
            0,
            1,
            'task_2',
        ),  # another hash
        (
            'user_2',
            '[{"id": "user_2", "session": "old_yandex_uuid"}]',
            'token',
            'task_3',
            1,
            0,
            'task_3',
        ),  # unsubscribe existing user
    ],
)
@pytest.mark.filldb(user_notification_subscription='with_task_id')
async def test_user_subscription_task_check_task_id(
        taxi_ucommunications,
        mockserver,
        stq_runner,
        mongodb,
        testpoint,
        user_id,
        list_response,
        token,
        task_id,
        inserted,
        modified,
        expected_task_id,
):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return {'id': 'user_id'}

    @mockserver.json_handler('/xiva/v2/unsubscribe/app')
    def _unsubscribe_app(request):
        assert request.args['user'] != request.args['uuid']
        return mockserver.make_response('OK', 200)

    @mockserver.json_handler('/xiva/v2/list')
    def _xiva_list(request):
        response = json.dumps(list_response)
        if response:
            assert request.args == {'service': 'taxi', 'user': user_id}
        return mockserver.make_response(
            list_response, 200, headers={'TransitID': 'id'},
        )

    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe_app(request, *args, **kwargs):
        if not list_response:
            assert False
        assert request.args == {
            'user': user_id,
            'uuid': user_id,
            'platform': 'ios',
            'app_name': 'ru.yandex.taxi.inhouse',
            'service': 'taxi',
        }
        body = f'push_token={token}'
        assert request.get_data() == str.encode(body)
        return mockserver.make_response('OK', 200)

    @testpoint('subscription-mongo-write-result')
    def subscription_mongo_wr(data):
        assert data == {'inserted': inserted, 'modified': modified}

    assert mongodb.user_notification_subscription.count() == 1

    await stq_runner.user_notification_subscription.call(
        task_id=task_id,
        kwargs={
            'user_id': user_id,
            'application': 'iphone',
            'build_type': 'inhouse-distr',
            'token': token,
            'token_type': 'apns',
        },
    )

    await subscription_mongo_wr.wait_call()

    doc_after = mongodb.user_notification_subscription.find_one(
        {'user_id': user_id},
    )
    assert doc_after['task_id'] == expected_task_id


async def test_user_subscription_task_xiva_unsubscribe_error(
        taxi_ucommunications, mockserver, stq_runner,
):
    @mockserver.json_handler('/xiva/v2/unsubscribe/app')
    def _unsubscribe_app(request):
        return mockserver.make_response('Internal Error', 500)

    @mockserver.json_handler('/xiva/v2/list')
    def _xiva_list(request):
        return mockserver.make_response(
            '[{"id": "user_id", "session": "old_yandex_uuid"}]',
            200,
            headers={'TransitID': 'id'},
        )

    await stq_runner.user_notification_subscription.call(
        task_id='sample_task',
        kwargs={
            'user_id': 'user_id',
            'application': 'iphone',
            'build_type': 'inhouse-distr',
            'token': 'token',
            'token_type': 'apns',
        },
        expect_fail=True,
    )


async def test_user_subscription_task_xiva_list_error(
        taxi_ucommunications, mockserver, stq_runner,
):
    @mockserver.json_handler('/xiva/v2/list')
    def _xiva_list(request):
        return mockserver.make_response(
            'Internal Error', 500, headers={'TransitID': 'id'},
        )

    await stq_runner.user_notification_subscription.call(
        task_id='sample_task',
        kwargs={
            'user_id': 'user_id',
            'application': 'iphone',
            'build_type': 'inhouse-distr',
            'token': 'token',
            'token_type': 'apns',
        },
        expect_fail=True,
    )


@pytest.mark.parametrize(
    'subscribe_response, subscribe_code, expect_task_fail',
    [
        # fail
        ('Internal Error', 500, True),
        ('Bad gateway', 502, True),
        ('some unknown 400 error', 400, True),
        # not fail
        ('Bad device', 405, False),
        # specific subscription errors, not RecoverableError:
        (
            'application ru.yandex.taxi.develop for platform apns is not '
            'registered',
            400,
            False,
        ),
        ('invalid argument user', 400, False),
        ('invalid pushtoken', 400, False),
        ('invalid characters in argument "uuid"', 400, False),
    ],
)
async def test_user_subscription_task_xiva_errors(
        taxi_ucommunications,
        mockserver,
        stq_runner,
        subscribe_response,
        subscribe_code,
        expect_task_fail,
):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return {'id': 'user_id'}

    @mockserver.json_handler('/xiva/v2/unsubscribe/app')
    def _unsubscribe_app(request):
        assert request.args['user'] != request.args['uuid']
        return mockserver.make_response('OK', 200)

    @mockserver.json_handler('/xiva/v2/list')
    def _xiva_list(request):
        return mockserver.make_response('[]', 200, headers={'TransitID': 'id'})

    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe_app(request, *args, **kwargs):
        return mockserver.make_response(subscribe_response, subscribe_code)

    await stq_runner.user_notification_subscription.call(
        task_id='sample_task',
        kwargs={
            'user_id': 'user_id',
            'application': 'iphone',
            'token': 'token',
            'token_type': 'apns',
            'build_type': 'inhouse-distr',
            'push_tokens_hash': {
                'apns_token_hash': hashlib.md5('token'.encode()).hexdigest(),
                'gcm_token_hash': hashlib.md5(''.encode()).hexdigest(),
                'hms_token_hash': hashlib.md5(''.encode()).hexdigest(),
            },
        },
        expect_fail=expect_task_fail,
    )


async def test_push_settings(
        taxi_ucommunications, mockserver, stq_runner, mongodb,
):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe_app(request, *args, **kwargs):
        filter_ = json.dumps(
            {
                'rules': [
                    {'if': {'$has_tags': ['T1']}, 'do': 'skip'},
                    {'if': {'$has_tags': ['T2']}, 'do': 'skip'},
                ],
            },
            separators=(',' ':'),
        )
        filter_ = urllib.parse.quote(filter_)
        body = f'push_token=token&filter={filter_}'
        assert request.get_data() == str.encode(body)
        return mockserver.make_response('OK', 200)

    await stq_runner.user_notification_subscription.call(
        task_id='sample_task',
        kwargs={
            'user_id': 'user_1',
            'application': 'iphone',
            'token': 'token',
            'token_type': 'apns',
            'build_type': 'inhouse-distr',
            'push_tokens_hash': {
                'apns_token_hash': hashlib.md5('token'.encode()).hexdigest(),
                'gcm_token_hash': hashlib.md5(''.encode()).hexdigest(),
                'hms_token_hash': hashlib.md5(''.encode()).hexdigest(),
            },
            'push_settings': {
                'enabled_by_system': True,
                'excluded_tags': ['T1', 'T2'],
                'included_tags': [],
            },
        },
    )


@pytest.mark.parametrize(
    'enabled_by_system, xiva_times_called', [(True, 1), (False, 2)],
)
async def test_changed_enabled_by_system(
        taxi_ucommunications,
        mockserver,
        stq_runner,
        mongodb,
        enabled_by_system,
        xiva_times_called,
):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe_app(request, *args, **kwargs):
        return mockserver.make_response('OK', 200)

    await stq_runner.user_notification_subscription.call(
        task_id='sample_task',
        kwargs={
            'user_id': 'user_1',
            'application': 'iphone',
            'token': 'token',
            'token_type': 'apns',
            'build_type': 'inhouse-distr',
            'push_tokens_hash': {
                'apns_token_hash': hashlib.md5('token'.encode()).hexdigest(),
                'gcm_token_hash': hashlib.md5(''.encode()).hexdigest(),
                'hms_token_hash': hashlib.md5(''.encode()).hexdigest(),
            },
            'push_settings': {
                'enabled_by_system': True,
                'excluded_tags': ['T1', 'T2'],
                'included_tags': [],
            },
        },
    )

    await stq_runner.user_notification_subscription.call(
        task_id='sample_task_2',
        kwargs={
            'user_id': 'user_1',
            'application': 'iphone',
            'token': 'token',
            'token_type': 'apns',
            'build_type': 'inhouse-distr',
            'push_tokens_hash': {
                'apns_token_hash': hashlib.md5('token'.encode()).hexdigest(),
                'gcm_token_hash': hashlib.md5(''.encode()).hexdigest(),
                'hms_token_hash': hashlib.md5(''.encode()).hexdigest(),
            },
            'push_settings': {
                'enabled_by_system': enabled_by_system,
                'excluded_tags': ['T1', 'T2'],
                'included_tags': [],
            },
        },
    )

    assert _subscribe_app.times_called == xiva_times_called


@pytest.mark.parametrize(
    'included_tags, xiva_times_called', [([], 1), (['T3'], 2)],
)
async def test_changed_included_tags(
        taxi_ucommunications,
        mockserver,
        stq_runner,
        mongodb,
        included_tags,
        xiva_times_called,
):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe_app(request, *args, **kwargs):
        return mockserver.make_response('OK', 200)

    await stq_runner.user_notification_subscription.call(
        task_id='sample_task',
        kwargs={
            'user_id': 'user_1',
            'application': 'iphone',
            'token': 'token',
            'token_type': 'apns',
            'build_type': 'inhouse-distr',
            'push_tokens_hash': {
                'apns_token_hash': hashlib.md5('token'.encode()).hexdigest(),
                'gcm_token_hash': hashlib.md5(''.encode()).hexdigest(),
                'hms_token_hash': hashlib.md5(''.encode()).hexdigest(),
            },
            'push_settings': {
                'enabled_by_system': True,
                'excluded_tags': ['T1', 'T2'],
                'included_tags': [],
            },
        },
    )

    await stq_runner.user_notification_subscription.call(
        task_id='sample_task_2',
        kwargs={
            'user_id': 'user_1',
            'application': 'iphone',
            'token': 'token',
            'token_type': 'apns',
            'build_type': 'inhouse-distr',
            'push_tokens_hash': {
                'apns_token_hash': hashlib.md5('token'.encode()).hexdigest(),
                'gcm_token_hash': hashlib.md5(''.encode()).hexdigest(),
                'hms_token_hash': hashlib.md5(''.encode()).hexdigest(),
            },
            'push_settings': {
                'enabled_by_system': True,
                'excluded_tags': ['T1', 'T2'],
                'included_tags': included_tags,
            },
        },
    )

    assert _subscribe_app.times_called == xiva_times_called


async def test_subscribe_zuser(taxi_ucommunications, mockserver, stq_runner):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe_app(request, *args, **kwargs):
        assert request.args == {
            'user': 'zuser_id',
            'uuid': 'zuser_id',
            'platform': 'ios',
            'app_name': 'ru.yandex.taxi.inhouse',
            'service': 'taxi',
        }
        body = 'push_token=token'
        assert request.get_data() == str.encode(body)
        return mockserver.make_response('OK', 200)

    await stq_runner.user_notification_subscription.call(
        task_id='sample_task',
        kwargs={
            'user_id': 'zuser_id',
            'application': 'iphone',
            'token': 'token',
            'token_type': 'apns',
            'build_type': 'inhouse-distr',
            'push_tokens_hash': {
                'apns_token_hash': hashlib.md5('token'.encode()).hexdigest(),
                'gcm_token_hash': hashlib.md5(''.encode()).hexdigest(),
                'hms_token_hash': hashlib.md5(''.encode()).hexdigest(),
            },
        },
    )


@pytest.mark.parametrize(
    'user_api_response',
    [{'id': 'user_id', 'zuser_id': 'zuser_id'}, {'id': 'user_id'}],
)
async def test_unsubscribe_zuser(
        taxi_ucommunications, mockserver, stq_runner, user_api_response,
):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return user_api_response

    @mockserver.json_handler('/xiva/v2/unsubscribe/app')
    def _unsubscribe_app(request):
        assert request.args['user'] == 'zuser_id'
        assert request.args['uuid'] == 'zuser_id'
        return mockserver.make_response('OK', 200)

    @mockserver.json_handler('/xiva/v2/list')
    def _xiva_list(request):
        return mockserver.make_response('[]', 200, headers={'TransitID': 'id'})

    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe_app(request, *args, **kwargs):
        assert request.args == {
            'user': 'user_id',
            'uuid': 'user_id',
            'platform': 'ios',
            'app_name': 'ru.yandex.taxi.inhouse',
            'service': 'taxi',
        }
        return mockserver.make_response('OK', 200)

    await stq_runner.user_notification_subscription.call(
        task_id='sample_task',
        kwargs={
            'user_id': 'user_id',
            'application': 'iphone',
            'token': 'token',
            'token_type': 'apns',
            'build_type': 'inhouse-distr',
        },
    )
    assert _unsubscribe_app.times_called == int(
        'zuser_id' in user_api_response,
    )
    assert _subscribe_app.times_called == 1


async def test_new_webpush_subscription(
        taxi_ucommunications, mockserver, stq_runner, testpoint,
):
    @testpoint('subscription-mongo-write-result')
    def update_subscription(data):
        assert data == {'inserted': 1, 'modified': 0}

    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return {'id': 'user_id'}

    @mockserver.json_handler('/xiva/v2/subscribe/webpush')
    def _subscribe_webpush(request):
        assert request.args['user'] == 'user_id'
        assert request.args['service'] == 'taxi'
        assert request.args['session'] == 'user_id'
        assert request.args['client'] == 'web_turboapp_taxi'
        return mockserver.make_response('OK', 200)

    await stq_runner.user_notification_subscription.call(
        task_id='sample_task',
        kwargs={
            'token': '',
            'user_id': 'user_id',
            'application': 'web_turboapp_taxi',
            'web_push_subscription': {
                'endpoint': 'https://fcm.googleapis.com/fcm/send/id',
                'expirationTime': None,
                'keys': {
                    'auth': '9pvIVgPVrXiT2gYizpdS-g222',
                    'p256dh': 'BNFGBgNt0dLv4AOJr0ocZfX9U120PyGbfiHZ9smoTTG',
                },
            },
        },
    )
    assert _subscribe_webpush.times_called == 1
    await update_subscription.wait_call()


@pytest.mark.filldb(user_notification_subscription='webpush')
async def test_same_webpush_subscription(
        taxi_ucommunications, stq_runner, testpoint,
):
    @testpoint('subscription-mongo-write-result')
    def update_subscription(data):
        assert data == {'inserted': 0, 'modified': 0}

    await stq_runner.user_notification_subscription.call(
        task_id='sample_task',
        kwargs={
            'token': '',
            'user_id': 'user_id',
            'application': 'web_turboapp_taxi',
            'web_push_subscription': {
                'endpoint': 'https://fcm.googleapis.com/fcm/send/id',
                'expirationTime': None,
                'keys': {
                    'auth': '9pvIVgPVrXiT2gYizpdS-g222',
                    'p256dh': 'BNFGBgNt0dLv4AOJr0ocZfX9U120PyGbfiHZ9smoTTG',
                },
            },
        },
    )

    await update_subscription.wait_call()


@pytest.mark.filldb(user_notification_subscription='webpush')
async def test_update_webpush_subscription(
        taxi_ucommunications, stq_runner, mockserver, testpoint,
):
    @testpoint('subscription-mongo-write-result')
    def update_subscription(data):
        assert data == {'inserted': 0, 'modified': 1}

    @mockserver.json_handler('/xiva/v2/subscribe/webpush')
    def _subscribe_webpush(request):
        assert request.args['user'] == 'user_id'
        assert request.args['service'] == 'taxi'
        assert request.args['session'] == 'user_id'
        assert request.args['client'] == 'web_turboapp_taxi'
        return mockserver.make_response('OK', 200)

    await stq_runner.user_notification_subscription.call(
        task_id='sample_task',
        kwargs={
            'token': '',
            'user_id': 'user_id',
            'application': 'web_turboapp_taxi',
            'web_push_subscription': {
                'endpoint': 'new_endpoint',
                'expirationTime': None,
                'keys': {
                    'auth': '9pvIVgPVrXiT2gYizpdS-g222',
                    'p256dh': 'BNFGBgNt0dLv4AOJr0ocZfX9U120PyGbfiHZ9smoTTG',
                },
            },
        },
    )

    await update_subscription.wait_call()


async def test_write_push_enabled_by_system(
        taxi_ucommunications, mockserver, stq_runner, mongodb, testpoint,
):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return {'id': 'user_0'}

    @mockserver.json_handler('/xiva/v2/unsubscribe/app')
    def _unsubscribe_app(request):
        assert request.args['user'] != request.args['uuid']
        return 'OK'

    @mockserver.json_handler('/xiva/v2/list')
    def _xiva_list(request):
        return []

    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe_app(request, *args, **kwargs):
        return mockserver.make_response('OK', 200)

    @testpoint('subscription-mongo-write-result')
    def subscription_mongo_wr(data):
        assert data == {'inserted': 1, 'modified': 0}

    await stq_runner.user_notification_subscription.call(
        task_id='task_id',
        kwargs={
            'user_id': 'user_0',
            'application': 'iphone',
            'build_type': 'inhouse-distr',
            'token': 'token',
            'token_type': 'apns',
            'push_settings': {
                'enabled_by_system': False,
                'excluded_tags': [],
                'included_tags': [],
            },
        },
    )

    await subscription_mongo_wr.wait_call()

    user_doc = mongodb.user_notification_subscription.find_one(
        {'user_id': 'user_0'},
    )
    assert user_doc['enabled_by_system'] is False
