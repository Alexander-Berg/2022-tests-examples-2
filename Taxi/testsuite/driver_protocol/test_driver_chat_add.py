import json

import pytest


@pytest.fixture
def client_notify(mockserver):
    class Handlers:
        @mockserver.json_handler('/client_notify/v2/push')
        def mock_client_notify(request):
            return {'notification_id': '123123'}

    return Handlers()


def test_not_authorized(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post('driver/chat/add')
    assert response.status_code == 401

    response = taxi_driver_protocol.post('driver/chat/add?db=1488')
    assert response.status_code == 401

    response = taxi_driver_protocol.post(
        'driver/chat/add?db=abc&session=qwerty',
    )
    assert response.status_code == 401

    response = taxi_driver_protocol.get(
        'driver/chat/add?db=1488&session=qwerty',
    )
    assert response.status_code != 401


def test_simple(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        'driver/chat/add?db=1488&session=qwerty', 'channel=&msg=&tag=',
    )
    assert response.status_code == 200


def test_not_valid_channel(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('1', '2', '3')
    driver_authorizer_service.set_session('777', 'qwerty', 'driver')

    response = taxi_driver_protocol.get(
        'driver/chat/add?db=777&session=qwerty',
    )
    assert response.status_code == 200
    assert not response.text

    response = taxi_driver_protocol.post(
        'driver/chat/add?db=1&session=2', 'channel=Index&msg=Chop is dish',
    )
    assert response.status_code == 404

    response = taxi_driver_protocol.post(
        'driver/chat/add?db=777&session=qwerty', 'channel=&msg=Chop is dish',
    )
    assert response.status_code == 500


@pytest.mark.parametrize(
    'get_chat_response',
    ['NotFound', 'NoOrder', 'NoParticipant', 'InvalidDriver', 'EmptyDriver'],
)
def test_external_chat_get_order_chat_info(
        taxi_driver_protocol,
        mockserver,
        get_chat_response,
        load_json,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/chat/1.0/chat/$$taxichat:123')
    def mock_chat(request):
        if get_chat_response == 'NotFound':
            return mockserver.make_response('Not found', 404)
        return load_json(get_chat_response + '.json')

    response = taxi_driver_protocol.post(
        'driver/chat/add?db=1488&session=qwerty',
        'channel=$$taxichat:123&msg=Я обожаю внешние чаты',
    )
    if get_chat_response == 'NotFound':
        assert response.status_code == 404
    else:
        assert response.status_code == 400


@pytest.mark.redis_store(
    ['hset', 'Order:SetCar:Items:1488', 'order', json.dumps({'id': 'ID'})],
)
@pytest.mark.parametrize('chat_update_code', [400, 404, 409, 451, 500])
def test_external_chat_bad_update_code(
        taxi_driver_protocol,
        client_notify,
        mockserver,
        chat_update_code,
        load_json,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/chat/1.0/chat/$$taxichat:123')
    def mock_chat(request):
        return load_json('OrderChatInfoOk.json')

    @mockserver.json_handler('/chat/1.0/chat/$$taxichat:123/add_update')
    def mock_add_update(request):
        return mockserver.make_response('Бла-бла-бла', chat_update_code)

    def expected_code(chat_update_code):
        if chat_update_code in [400, 404]:
            return chat_update_code
        return 500

    response = taxi_driver_protocol.get(
        'driver/chat/add?db=1488&session=qwerty',
        params={'channel': '$$taxichat:123', 'msg': 'Я обожаю внешние чаты'},
    )
    assert response.status_code == expected_code(chat_update_code)

    if chat_update_code == 409:
        client_notify.mock_client_notify.wait_call()


@pytest.mark.config(CLIENTDRIVER_CHAT_PHONE_SHOULD_FILTER=True)
@pytest.mark.redis_store(
    [
        'set',
        'Order:ChatInfo:$$taxichat:123',
        json.dumps(
            {
                'ChatId': '$$taxichat:123',
                'OrderId': '1234567890',
                'DriverId': 'driver',
                'DbId': '1488',
                'NewestMessageId': '3',
            },
        ),
    ],
)
def test_external_chat_ok(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/chat/1.0/chat/$$taxichat:123/add_update')
    def mock_add_update(request):
        return mockserver.make_response(json.dumps({'message_id': '8'}), 201)

    response = taxi_driver_protocol.get(
        'driver/chat/add?db=1488&session=qwerty',
        params={'channel': '$$taxichat:123', 'msg': 'Я обожаю внешние чаты'},
    )
    assert response.status_code == 200
    assert response.json()['msg_id'] == '8'


@pytest.mark.config(
    CLIENTDRIVER_CHAT_PHONE_SHOULD_FILTER=True,
    CLIENTDRIVER_CHAT_PHONE_SUBSTITUTION_TANKER_KEY='phone_msg_key',
    CLIENTDRIVER_CHAT_PHONE_MESSAGE_REGEXP='((\\d\\D{0,10}){10})',
)
@pytest.mark.redis_store(
    [
        'set',
        'Order:ChatInfo:$$taxichat:123',
        json.dumps(
            {
                'ChatId': '$$taxichat:123',
                'OrderId': '1234567890',
                'DriverId': 'driver',
                'DbId': '1488',
                'NewestMessageId': '3',
            },
        ),
    ],
)
@pytest.mark.translations(
    client_messages={'phone_msg_key': {'ru': 'Call Ya.Taxi'}},
)
@pytest.mark.parametrize(
    'message',
    [
        ('Call me +92341253',),
        ('Позвоните мне +7(495)324-23-42',),
        ('+7и000в 000и00 вы00',),
        ('0df0vv0c0cccccccccc0ff0dd0gg0vhh0ccc0hh0',),
        ('8__000+_+0₽;₽00~+_+00_++₽00',),
    ],
)
def test_external_chat_message_filter(
        taxi_driver_protocol, mockserver, driver_authorizer_service, message,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/chat/1.0/chat/$$taxichat:123/add_update')
    def mock_add_update(request):
        return mockserver.make_response(json.dumps({'message_id': '8'}), 201)

    response = taxi_driver_protocol.get(
        'driver/chat/add?db=1488&session=qwerty',
        params={'channel': '$$taxichat:123', 'msg': message},
    )
    assert response.status_code == 200


@pytest.mark.config(
    CLIENTDRIVER_CHAT_PHONE_SHOULD_FILTER=True,
    CLIENTDRIVER_CHAT_PHONE_SUBSTITUTION_TANKER_KEY='phone_msg_key',
    CLIENTDRIVER_CHAT_PHONE_MESSAGE_REGEXP='((\\d\\D{0,10}){10})',
)
@pytest.mark.redis_store(
    [
        'set',
        'Order:ChatInfo:$$taxichat:123',
        json.dumps(
            {
                'ChatId': '$$taxichat:123',
                'OrderId': '1234567890',
                'DriverId': 'driver',
                'DbId': '1488',
                'NewestMessageId': '3',
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'message',
    [
        ('Здравствуйте стою между 61 б и 61 в',),
        ('Какой дом 9 корпус 1',),
        ('Здравствуйте 00-0 00-0 просто 00 нет',),
        'У меня в стране 0 водосток 00 00 00 0 дома ',
        ('до 0 будет +000р к сумме. Тариф +00 для 00. Багаж + 00р',),
    ],
)
def test_external_chat_message_no_filter(
        taxi_driver_protocol, mockserver, driver_authorizer_service, message,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/chat/1.0/chat/$$taxichat:123/add_update')
    def mock_add_update(request):
        return mockserver.make_response(json.dumps({'message_id': '8'}), 201)

    response = taxi_driver_protocol.get(
        'driver/chat/add?db=1488&session=qwerty',
        params={'channel': '$$taxichat:123', 'msg': message},
    )
    assert response.status_code == 200


@pytest.mark.redis_store(
    [
        'set',
        'Order:ChatInfo:$$taxichat:123',
        json.dumps(
            {
                'ChatId': '$$taxichat:123',
                'OrderId': '1234567890',
                'DriverId': 'driver',
                'DbId': '1488',
                'NewestMessageId': '3',
            },
        ),
    ],
)
def test_external_chat_translate_ok(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/chat/1.0/chat/$$taxichat:123/add_update')
    def mock_add_update(request):
        data = json.loads(request.get_data())
        data.pop('created_date')
        data['message'].pop('id')
        assert data == {
            'message': {
                'metadata': {
                    'language_hint': {
                        'app_language': 'en',
                        'keyboard_languages': ['ru'],
                        'system_languages': ['en', 'de'],
                    },
                },
                'sender': {'id': '1488_driver', 'role': 'driver'},
                'text': 'Я обожаю внешние чаты',
            },
            'newest_message_id': '3',
        }
        return mockserver.make_response(json.dumps({'message_id': '8'}), 201)

    response = taxi_driver_protocol.get(
        'driver/chat/add?db=1488&session=qwerty',
        params={
            'channel': '$$taxichat:123',
            'msg': 'Я обожаю внешние чаты',
            'language_hint': json.dumps(
                {
                    'keyboard_languages': ['ru'],
                    'app_language': 'en',
                    'system_languages': ['en', 'de'],
                },
            ),
        },
    )
    assert response.status_code == 200
    assert response.json()['msg_id'] == '8'


def test_message_banned(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.get(
        'driver/chat/add?db=1488&session=qwerty',
        params={
            'channel': 'PRIVATE',
            'msg': (
                'Ты видел чё б@@@ь с ней творят? Лови ссылочку '
                'pornolab.net/forum/viewtopic.php?t=2103249'
            ),
        },
    )
    assert response.status_code == 200
    assert not response.text


@pytest.mark.redis_store(
    ['hmset', 'ChatBlock:Items', {'999:888': 'Неадекват какой-то'}],
)
def test_blocked(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('666', 'qwerty', 'driver')
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    response = taxi_driver_protocol.post(
        'driver/chat/add?db=666&session=qwerty',
        'channel=paramparamparam&msg=У нас всех чат отключен',
    )
    assert response.status_code == 400

    response = taxi_driver_protocol.post(
        'driver/chat/add?db=999&session=qwerty',
        'channel=usual&msg=Да вы знаете кто я, хватит меня блочить, уроды',
    )
    assert response.status_code == 400


def test_driver_not_found(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('1488', 'qwerty', 'Anonim')

    response = taxi_driver_protocol.get(
        'driver/chat/add?db=1488&session=qwerty',
        params={
            'channel': 'usual',
            'msg': 'Не ищи меня вконтакте, ищи меня в клубе',
        },
    )
    assert response.status_code == 404


def test_driver_add_params_transfer(
        mockserver,
        taxi_driver_protocol,
        client_notify,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    params = {'db': '1488', 'session': 'qwerty'}
    parks_params = {'park_id': '1488', 'driver_profile_id': 'driverSS'}

    @mockserver.json_handler('/parks/driver-profiles/photo')
    def mock_callback(request):
        return {'photos': []}

    response = taxi_driver_protocol.post(
        'driver/chat/add',
        'channel=PRIVATE&msg=Я нечаянно заехал в реку. Проплываю мимо парка '
        'Горького.&tag=SOS',
        params=params,
    )

    assert mock_callback.times_called == 1
    assert mock_callback.next_call()['request'].args.to_dict() == parks_params
    assert response.status_code == 200
    client_notify.mock_client_notify.wait_call()


@pytest.mark.parametrize(
    'parks_response,expected_code,expected_response',
    [
        (
            {'error': {'text': 'some wrong parameter'}},
            400,
            {'error': {'text': 'some wrong parameter'}},
        ),
        ('some error', 500, None),
    ],
)
def test_driver_add_error_transfer(
        mockserver,
        taxi_driver_protocol,
        parks_response,
        expected_code,
        expected_response,
        client_notify,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    @mockserver.json_handler('/parks/driver-profiles/photo')
    def mock_callback(request):
        return mockserver.make_response(
            json.dumps(parks_response), expected_code,
        )

    response = taxi_driver_protocol.post(
        'driver/chat/add?db=1488&session=qwerty',
        'channel=PRIVATE&msg=Я нечаянно заехал в реку. Проплываю мимо парка '
        'Горького.&tag=SOS',
    )
    assert response.status_code == expected_code
    if expected_response:
        assert response.json() == expected_response


@pytest.mark.parametrize(
    'parks_response,stored_message_part',
    [
        ({'photos': []}, {}),
        (
            {
                'photos': [
                    {
                        'href': (
                            'https://storage.mds.yandex.net/get-taximeter/'
                            '3325/6a255a958d234fa497d99c21b4a1f166_large.jpg'
                        ),
                        'scale': 'large',
                        'type': 'driver',
                    },
                    {
                        'href': (
                            'https://storage.mds.yandex.net/get-taximeter/'
                            'original/driver.jpg'
                        ),
                        'scale': 'original',
                        'type': 'driver',
                    },
                    {
                        'href': (
                            'https://storage.mds.yandex.net/get-taximeter/'
                            'left.jpg'
                        ),
                        'scale': 'original',
                        'type': 'left',
                    },
                    {
                        'href': (
                            'https://storage.mds.yandex.net/get-taximeter/'
                            'front.jpg'
                        ),
                        'scale': 'original',
                        'type': 'front',
                    },
                    {
                        'href': (
                            'https://storage.mds.yandex.net/get-taximeter/'
                            'salon.jpg'
                        ),
                        'scale': 'original',
                        'type': 'salon',
                    },
                ],
            },
            {
                'icon': (
                    'https://storage.mds.yandex.net/get-taximeter/'
                    '3325/6a255a958d234fa497d99c21b4a1f166_large.jpg'
                ),
            },
        ),
    ],
)
def test_driver_add_ok(
        mockserver,
        redis_store,
        taxi_driver_protocol,
        parks_response,
        stored_message_part,
        client_notify,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    @mockserver.json_handler('/parks/driver-profiles/photo')
    def mock_callback(request):
        return parks_response

    response = taxi_driver_protocol.post(
        'driver/chat/add?db=1488&session=qwerty',
        'channel=PRIVATE&msg=Я нечаянно заехал в реку. Проплываю мимо парка '
        'Горького.&tag=SOS',
    )
    assert response.status_code == 200
    assert len(response.json()['msg_id']) == 32

    assert redis_store.exists('Chat:Messages:PRIVATE:1488:driverSS')
    stored_message = json.loads(
        redis_store.lrange('Chat:Messages:PRIVATE:1488:driverSS', 0, -1)[0],
    )

    assert ('icon' in stored_message) == ('icon' in stored_message_part)
    if 'icon' in stored_message_part:
        assert stored_message['icon'] == stored_message_part['icon']

    client_notify.mock_client_notify.wait_call()


@pytest.mark.parametrize('add_phone', [True, False])
def test_driver_chat_add_phone_append(
        mockserver,
        redis_store,
        taxi_driver_protocol,
        driver_authorizer_service,
        client_notify,
        add_phone,
        config,
):
    @mockserver.json_handler('/parks/driver-profiles/photo')
    def mock_callback(request):
        return {'photos': []}

    config.set_values(
        dict(DRIVER_PROTOCOL_APPEND_DRIVER_PHONE_TO_DISPATCHER_CHAT=add_phone),
    )
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    response = taxi_driver_protocol.post(
        'driver/chat/add?db=1488&session=qwerty',
        'channel=PRIVATE&msg=Я нечаянно заехал в реку. Проплываю мимо парка '
        'Горького.&tag=SOS',
    )
    assert response.status_code == 200

    record = next(iter(redis_store.hgetall('Chat:Dispather:1488').values()))
    message = json.loads(record)['msg']

    assert ('+7 (921) 765-23-31' in message) == add_phone
    assert ('+7 (903) 123-45-67' in message) == add_phone
