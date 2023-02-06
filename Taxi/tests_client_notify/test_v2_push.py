import copy

import pytest

from tests_client_notify import helpers

X_IDEMPOTENCY_TOKEN = 'token'


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'taximeter': {
            'description': 'yandex pro',
            'xiva_service': 'taximeter',
        },
    },
    CLIENT_NOTIFY_INTENTS={
        'taximeter': {'MessageNew': {'description': 'new mesage in chat'}},
    },
    CLIENT_NOTIFY_PAYLOAD_REPACK={
        'repack_rules': [
            {
                'enabled': True,
                'conditions': {'services': ['taximeter'], 'intents': []},
                'payload_repack': {
                    'payload': {
                        'id#notification_id': None,
                        'action': 'intent',
                        'collapse_key': 'collapse_key',
                        'data': {
                            'message#xget': '/root/notification/text',
                            'name#xget': '/root/notification/title',
                        },
                        'ttl': 59,
                        'my_obj_key1': {
                            'inner_key': 'inner_val',
                            'my_obj_key2': {'inner_key2': 'inner_val2'},
                        },
                        'my_str_key': 'str',
                        'my_int_key': 666,
                        'my_double_key': 13.14,
                        'my_array_key': [1, 2, 3],
                        'my_test_key#xget': '/root/notification/title',
                    },
                    'repack': {
                        'apns': {
                            'aps': {
                                'sound#xget': '/root/notification/sound',
                                'mutable-content': 1,
                            },
                            'collapse-id#xget': '/root/collapse_key',
                            'repack_payload': ['*'],
                        },
                        'other': {'repack_payload': ['*']},
                    },
                },
            },
        ],
    },
)
async def test_ok(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        nonlocal notification_body
        data = request.json
        notification_body = copy.deepcopy(data)

        assert data['payload']['id']
        data['payload'].pop('id')

        assert data == {
            'payload': {
                'collapse_key': 'collapse_key',
                'action': 'intent',
                'ttl': 59,
                'data': {
                    'message': (
                        'Пассажир добавил или изменил промежуточную точку'
                    ),
                    'name': 'Платформа',
                },
                'my_str_key': 'str',
                'my_obj_key1': {
                    'inner_key': 'inner_val',
                    'my_obj_key2': {'inner_key2': 'inner_val2'},
                },
                'my_int_key': 666,
                'my_double_key': 13.14,
                'my_array_key': [1, 2, 3],
                'my_test_key': 'Платформа',
            },
            'repack': {
                'apns': {
                    'collapse-id': 'Alert:5b4203a47e8a4361b3a5505fc2967f62',
                    'repack_payload': ['*'],
                    'aps': {'sound': 'default', 'mutable-content': 1},
                },
                'other': {'repack_payload': ['*']},
            },
        }

        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    notification_body = None
    response = await taxi_client_notify.post(
        'v2/push',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'taximeter',
            'message_id': 'service_message_id',
            'client_id': 'dbid-uuid',
            'intent': 'MessageNew',
            'ttl': 60,
            'collapse_key': 'Alert:5b4203a47e8a4361b3a5505fc2967f62',
            'notification': {
                'text': 'Пассажир добавил или изменил промежуточную точку',
                'title': 'Платформа',
                'sound': 'default',
            },
            'data': {'flags': ['high_priority']},
            'return_notification_body': True,
        },
    )
    assert response.status_code == 200
    assert response.json()['notification_body'] == notification_body


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'taximeter': {
            'description': 'yandex pro',
            'xiva_service': 'taximeter',
        },
    },
    CLIENT_NOTIFY_INTENTS={
        'taximeter': {'MessageNew': {'description': 'new mesage in chat'}},
    },
    CLIENT_NOTIFY_PAYLOAD_REPACK={'repack_rules': []},
)
async def test_400_no_rule(taxi_client_notify, mockserver):
    response = await taxi_client_notify.post(
        'v2/push',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'taximeter',
            'message_id': 'service_message_id',
            'client_id': 'dbid-uuid',
            'intent': 'MessageNew',
            'ttl': 60,
            'collapse_key': 'Alert:5b4203a47e8a4361b3a5505fc2967f62',
            'notification': {
                'text': 'Пассажир добавил или изменил промежуточную точку',
                'title': 'Платформа',
                'sound': 'default',
            },
            'data': {'flags': ['high_priority']},
        },
    )
    assert response.status_code == 400


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'taximeter': {
            'description': 'yandex pro',
            'xiva_service': 'taximeter',
        },
    },
    CLIENT_NOTIFY_INTENTS={
        'taximeter': {'MessageNew': {'description': 'new mesage in chat'}},
    },
    CLIENT_NOTIFY_PAYLOAD_REPACK={
        'repack_rules': [
            {
                'enabled': True,
                'conditions': {'services': ['taximeter'], 'intents': []},
                'payload_repack': {'payload': {'data': {'message#xget': 5}}},
            },
        ],
    },
)
async def test_agl_error(taxi_client_notify, testpoint):
    @testpoint('parse-fail')
    def parse_fail(data):
        assert data['rule_number'] == 0

    response = await taxi_client_notify.post(
        'v2/push',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'taximeter',
            'message_id': 'service_message_id',
            'client_id': 'dbid-uuid',
            'intent': 'MessageNew',
            'ttl': 60,
            'collapse_key': 'Alert:5b4203a47e8a4361b3a5505fc2967f62',
            'notification': {
                'text': 'Пассажир добавил или изменил промежуточную точку',
                'title': 'Платформа',
                'sound': 'default',
            },
            'data': {'flags': ['high_priority']},
        },
    )
    assert response.status_code == 400
    await parse_fail.wait_call()


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'taximeter': {
            'description': 'yandex pro',
            'xiva_service': 'taximeter',
        },
    },
    CLIENT_NOTIFY_INTENTS={
        'taximeter': {'MessageNew': {'description': 'new mesage in chat'}},
    },
    CLIENT_NOTIFY_PAYLOAD_REPACK={
        'repack_rules': [
            {
                'enabled': True,
                'conditions': {'services': ['taxi'], 'intents': []},
                'payload_repack': {},
            },
            {
                'enabled': True,
                'conditions': {'services': ['taximeter'], 'intents': []},
                'payload_repack': {},
            },
            {
                'enabled': True,
                'conditions': {'services': ['taximeter'], 'intents': []},
                'payload_repack': {},
            },
        ],
    },
)
async def test_duplicate_rule(taxi_client_notify, testpoint):
    @testpoint('duplicate-rule')
    def duplicate_rule(data):
        assert data['rule_number'] == 2

    await taxi_client_notify.enable_testpoints()
    await duplicate_rule.wait_call()


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'magnit': {'description': 'Магнит', 'provider': 'magnit'},
    },
    CLIENT_NOTIFY_INTENTS={
        'magnit': {'new_order': {'description': 'new order'}},
    },
    CLIENT_NOTIFY_PAYLOAD_REPACK={
        'repack_rules': [
            {
                'enabled': True,
                'conditions': {'services': ['magnit'], 'intents': []},
                'payload_repack': {
                    'message_body#xget': '/root/notification/text',
                    'message_title#xget': '/root/notification/title',
                    'topic_name#xget': '/root/client_id',
                    'deep_link#xget': {
                        'path': '/root/notification/link',
                        'default-value': None,
                    },
                },
            },
        ],
    },
)
async def test_magnit(taxi_client_notify, mockserver):
    @mockserver.json_handler('/magnit-notifications/v1/message')
    def _send(request):
        data = request.json
        assert data == {
            'message_body': 'Body',
            'message_title': 'Title',
            'topic_name': 'eater-uuid',
        }

        return mockserver.make_response('{}', 201)

    response = await taxi_client_notify.post(
        'v2/push',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'magnit',
            'message_id': 'service_message_id',
            'client_id': 'eater-uuid',
            'intent': 'new_order',
            'notification': {'text': 'Body', 'title': 'Title'},
            'data': {},
        },
    )
    assert response.status_code == 200


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'magnit': {'description': 'Магнит', 'provider': 'magnit'},
    },
    CLIENT_NOTIFY_INTENTS={
        'magnit': {'new_order': {'description': 'new order'}},
    },
    CLIENT_NOTIFY_PAYLOAD_REPACK={
        'repack_rules': [
            {
                'enabled': True,
                'conditions': {'services': ['magnit'], 'intents': []},
                'payload_repack': {
                    'message_body#xget': '/root/notification/text',
                    'message_title#xget': '/root/notification/title',
                    'topic_name#xget': '/root/client_id',
                    'deep_link#xget': {
                        'path': '/root/notification/link',
                        'default-value': None,
                    },
                    'order_cost#xget': '/root/data/cost',
                },
            },
        ],
    },
)
@helpers.TRANSLATIONS
async def test_push_v2_localization(taxi_client_notify, mockserver):
    @mockserver.json_handler('/magnit-notifications/v1/message')
    def _send(request):
        data = request.json
        assert data == {
            'message_body': 'Добрый день!',
            'message_title': 'Yandex.Go',
            'topic_name': 'eater-uuid',
            'order_cost': '100 руб.',
        }

        return mockserver.make_response('{}', 201)

    response = await taxi_client_notify.post(
        'v2/push',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'magnit',
            'message_id': 'service_message_id',
            'client_id': 'eater-uuid',
            'locale': 'ru',
            'intent': 'new_order',
            'notification': {
                'text': {'key': 'hello_key', 'keyset': 'notify'},
                'title': 'Yandex.Go',
            },
            'data': {
                'cost': {
                    'key': 'key1',
                    'keyset': 'notify',
                    'params': {'cost': 100},
                },
            },
        },
    )
    assert response.status_code == 200
    assert response.json()['notification_id'] is not None


async def test_no_locale(taxi_client_notify):
    response = await taxi_client_notify.post(
        'v2/push',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'eda_courier',
            'message_id': 'service_message_id',
            'client_id': 'id',
            'intent': 'order_new',
            'notification': {
                'text': {'key': 'hello_key', 'keyset': 'notify'},
                'title': 'Yandex.Go',
            },
            'data': {},
        },
    )
    assert response.status_code == 400


@helpers.TRANSLATIONS
@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'taximeter': {
            'description': 'test',
            'xiva_service': 'taximeter',
            'localization': {'locale_source': 'contractor'},
        },
    },
    CLIENT_NOTIFY_INTENTS={'taximeter': {'test': {'description': 'test'}}},
    CLIENT_NOTIFY_PAYLOAD_REPACK={
        'repack_rules': [
            {
                'enabled': True,
                'conditions': {'services': ['taximeter'], 'intents': []},
                'payload_repack': {
                    'payload': {
                        'text#xget': '/root/notification/text',
                        'cost#xget': '/root/data/cost',
                    },
                },
            },
        ],
    },
)
@pytest.mark.parametrize(
    'locale,text,cost',
    [('ru', 'Добрый день!', '100 руб.'), ('en', 'Hello!', '100 dollars.')],
    ids=['ru', 'en'],
)
async def test_locale_source_contractor(
        taxi_client_notify, mockserver, locale, text, cost,
):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        assert request.json['payload']['text'] == text
        assert request.json['payload']['cost'] == cost
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_driver_profiles_driver_app_profiles_retrieve(request):
        return {
            'profiles': [
                {'data': {'locale': locale}, 'park_driver_profile_id': 'a-b'},
            ],
        }

    response = await taxi_client_notify.post(
        'v2/push',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'taximeter',
            'client_id': 'a-b',
            'intent': 'test',
            'notification': {'text': {'key': 'hello_key', 'keyset': 'notify'}},
            'data': {
                'cost': {
                    'key': 'key1',
                    'keyset': 'notify',
                    'params': {'cost': 100},
                },
            },
        },
    )
    assert response.status_code == 200


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'taximeter': {
            'description': 'yandex pro',
            'xiva_service': 'taximeter',
        },
    },
    CLIENT_NOTIFY_INTENTS={
        'taximeter': {'MessageNew': {'description': 'new mesage in chat'}},
    },
    CLIENT_NOTIFY_PAYLOAD_REPACK={
        'repack_rules': [
            {
                'enabled': True,
                'conditions': {'services': ['taximeter'], 'intents': []},
                'payload_repack': {'payload': {}},
            },
        ],
    },
)
async def test_session_id(taxi_client_notify, mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        assert request.json['subscriptions'] == [{'session': ['session_id']}]

        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    response = await taxi_client_notify.post(
        'v2/push',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'taximeter',
            'message_id': 'service_message_id',
            'client_id': 'dbid-uuid',
            'session_id': 'session_id',
            'intent': 'MessageNew',
            'ttl': 60,
            'data': {'flags': ['high_priority']},
            'return_notification_body': True,
        },
    )
    assert response.status_code == 200
