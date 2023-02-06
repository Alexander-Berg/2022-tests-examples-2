import json

import pytest


@pytest.fixture
def client_notify(mockserver):
    class Handlers:
        @mockserver.json_handler('/client_notify/v2/push')
        def mock_client_notify(request):
            return {'notification_id': '123123'}

    return Handlers()


def test_bad_request(taxi_driver_protocol):
    response = taxi_driver_protocol.post('service/chat/subscription_callback')
    assert response.status_code == 400

    response = taxi_driver_protocol.post(
        'service/chat/subscription_callback?alias_id=',
    )
    assert response.status_code == 400

    response = taxi_driver_protocol.post(
        'service/chat/subscription_callback?alias_id=12345',
    )
    assert response.status_code == 400


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
def test_redis_info_exists(
        taxi_driver_protocol, client_notify, mockserver, redis_store,
):

    # It's ok, don't update
    response = taxi_driver_protocol.post(
        'service/chat/subscription_callback?alias_id=1234567890',
        json={
            'chat_id': '$$taxichat:123',
            'newest_message_id': '3',
            'updated_date': '2018-01-31T14:01:05.379614Z',
        },
    )
    assert response.status_code == 200
    assert (
        json.loads(redis_store.get('Order:ChatInfo:$$taxichat:123'))[
            'NewestMessageId'
        ]
        == '3'
    )

    client_notify.mock_client_notify.wait_call()

    # Let's do it now
    response = taxi_driver_protocol.post(
        'service/chat/subscription_callback?alias_id=1234567890',
        json={
            'chat_id': '$$taxichat:123',
            'newest_message_id': '4',
            'updated_date': '2018-01-31T14:01:05.379614Z',
        },
    )
    assert response.status_code == 200
    assert (
        json.loads(redis_store.get('Order:ChatInfo:$$taxichat:123'))[
            'NewestMessageId'
        ]
        == '4'
    )

    client_notify.mock_client_notify.wait_call()

    @mockserver.json_handler('/chat/1.0/chat/$$taxichat:123')
    def mock_chat(request):
        return mockserver.make_response('Error', 500)

    # Now with bad alias_id and without chat service we should get error
    response = taxi_driver_protocol.post(
        'service/chat/subscription_callback?alias_id=123',
        json={
            'chat_id': '$$taxichat:123',
            'newest_message_id': '4',
            'updated_date': '2018-01-31T14:01:05.379614Z',
        },
    )
    assert response.status_code == 400


@pytest.mark.redis_store(
    [
        'hset',
        'Order:SetCar:Items:1488',
        '1234567890',
        json.dumps({'id': '1234567890', 'client_chat_id': '$$taxichat:123'}),
    ],
    [
        'hset',
        'Order:SetCar:Items:1488',
        '11111',
        json.dumps({'id': '11111', 'client_chat_id': ''}),
    ],
)
def test_redis_info_not_exists(
        taxi_driver_protocol,
        client_notify,
        mockserver,
        load_json,
        redis_store,
):
    @mockserver.json_handler('/chat/1.0/chat/$$taxichat:123')
    def mock_chat(request):
        return load_json('OrderChatInfo.json')

    response = taxi_driver_protocol.post(
        'service/chat/subscription_callback?alias_id=1234567890',
        json={
            'chat_id': '$$taxichat:123',
            'newest_message_id': '6',
            'updated_date': '2018-01-31T14:01:05.379614Z',
        },
    )
    assert response.status_code == 200
    # because of answer from chat service
    assert (
        json.loads(redis_store.get('Order:ChatInfo:$$taxichat:123'))[
            'NewestMessageId'
        ]
        == '4'
    )

    client_notify.mock_client_notify.wait_call()

    # required to change alias_id successfully
    @mockserver.json_handler('/chat/1.0/chat/$$taxichat:123')
    def mock_chat_again(request):
        data = load_json('OrderChatInfo.json')
        data['metadata']['taximeter_order']['alias_id'] = '11111'
        return data

    # request with other alias_id, should be successful
    response = taxi_driver_protocol.post(
        'service/chat/subscription_callback?alias_id=11111',
        json={
            'chat_id': '$$taxichat:123',
            'newest_message_id': '6',
            'updated_date': '2018-01-31T14:01:05.379614Z',
        },
    )
    assert response.status_code == 200
    assert (
        json.loads(redis_store.hget('Order:SetCar:Items:1488', '1234567890'))[
            'client_chat_id'
        ]
        == ''
    )
    assert (
        json.loads(redis_store.hget('Order:SetCar:Items:1488', '11111'))[
            'client_chat_id'
        ]
        == '$$taxichat:123'
    )

    client_notify.mock_client_notify.wait_call()


def test_no_info_at_all(taxi_driver_protocol, mockserver, load_json):
    @mockserver.json_handler('/chat/1.0/chat/$$taxichat:123')
    def mock_chat(request):
        return mockserver.make_response('Error', 500)

    response = taxi_driver_protocol.post(
        'service/chat/subscription_callback?alias_id=1234567890',
        json={
            'chat_id': '$$taxichat:123',
            'newest_message_id': '6',
            'updated_date': '2018-01-31T14:01:05.379614Z',
        },
    )
    assert response.status_code == 400


@pytest.mark.redis_store(
    [
        'hset',
        'Order:SetCar:Items:1488',
        '1234567890',
        json.dumps(
            {
                'id': '1234567890',
                'client_chat_id': '$$taxichat:123',
                'driver_id': 'driver',
            },
        ),
    ],
    ['hset', 'Order:SetCar:Drivers:1488', '1234567890', 'bugaga'],
)
@pytest.mark.now('2018-02-13T00:00:00Z')
def test_check_setcar(
        taxi_driver_protocol,
        client_notify,
        mockserver,
        load_json,
        redis_store,
):
    @mockserver.json_handler('/chat/1.0/chat/$$taxichat:123')
    def mock_chat(request):
        return load_json('OrderChatInfo.json')

    response = taxi_driver_protocol.post(
        'service/chat/subscription_callback?alias_id=1234567890',
        json={
            'chat_id': '$$taxichat:123',
            'newest_message_id': '4',
            'updated_date': '2018-01-31T14:01:05.379614Z',
        },
    )
    assert response.status_code == 200

    setcar_info = json.loads(
        redis_store.hget('Order:SetCar:Items:1488', '1234567890'),
    )
    assert setcar_info['date_create'] == '2018-02-13T00:00:00.000000Z'
    assert setcar_info['date_last_change'] == '2018-02-13T00:00:00.000000Z'
    assert setcar_info['client_chat_id'] == '$$taxichat:123'

    assert redis_store.ttl('Order:SetCar:Items:1488') == 15 * 24 * 60 * 60
    assert redis_store.ttl('Order:SetCar:Drivers:1488') == 15 * 24 * 60 * 60
    md5 = redis_store.get('Order:Driver:CancelRequest:MD5:1488:bugaga')
    assert len(md5) == 32
    assert (
        redis_store.ttl('Order:Driver:CancelRequest:MD5:1488:bugaga')
        == 5 * 24 * 60 * 60
    )
    cancelled = redis_store.lrange(
        'Order:Driver:CancelRequest:Items:1488:bugaga', 0, -1,
    )
    assert len(cancelled) == 1
    assert cancelled[0] == b'1234567890'

    md5 = redis_store.get('Order:SetCar:Driver:Reserv:MD5:1488:driver')
    assert len(md5) == 32
    assert (
        redis_store.ttl('Order:SetCar:Driver:Reserv:MD5:1488:driver')
        == 5 * 24 * 60 * 60
    )

    md5 = redis_store.get('Order:SetCar:MD5:1488')
    assert len(md5) == 32
    assert redis_store.ttl('Order:SetCar:MD5:1488') == 15 * 24 * 60 * 60

    provider = redis_store.hget(
        'Order:SetCar:Items:Providers:1488', '1234567890',
    )
    assert provider == b'0'

    client_notify.mock_client_notify.wait_call()
