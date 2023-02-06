import json

import pytest


def test_no_channel(taxi_driver_protocol):
    response = taxi_driver_protocol.post('service/chat/messages')
    assert response.status_code == 400

    response = taxi_driver_protocol.post('service/chat/messages?db=1')
    assert response.status_code == 400

    response = taxi_driver_protocol.post('service/chat/messages?db=777')
    assert response.status_code == 400


@pytest.mark.now('2017-11-11T11:11:11+1111')
def test_disabled(taxi_driver_protocol):
    response = taxi_driver_protocol.post(
        'service/chat/messages?db=666',
        json={'md5': 'abcdef', 'channel': 'Index'},
    )
    assert response.status_code == 200
    items = response.json()['items']
    assert len(items) == 1
    assert items[0]['msg'] == 'Yandex.Uber.Alles'
    assert items[0]['db'] == 'SUPPORT'
    assert items[0]['date'] == '2017-11-11T00:00:00+0000'


@pytest.mark.redis_store(['set', 'Chat:Md5:PRIVATE:1488:NotDriver', 'abcdef'])
def test_no_new_messages(taxi_driver_protocol):
    response = taxi_driver_protocol.post(
        'service/chat/messages?db=1488',
        json={'md5': 'abcdef', 'channel': 'PRIVATE:1488:NotDriver'},
    )
    assert response.status_code == 200
    assert not response.text


@pytest.mark.redis_store(
    ['set', 'Chat:Md5:PRIVATE:1488:NotDriver', 'abcd'],
    [
        'lpush',
        'Chat:Messages:PRIVATE:1488:NotDriver',
        json.dumps({'msg': 'Hello'}),
        json.dumps({'msg': 'World'}),
    ],
)
def test_chat_messages(taxi_driver_protocol):
    response = taxi_driver_protocol.post(
        'service/chat/messages?db=1488',
        json={'md5': 'abcdef', 'channel': 'PRIVATE:1488:NotDriver'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['md5'] == 'abcd'
    assert len(body['items']) == 2


@pytest.mark.redis_store(['set', 'Chat:Md5:PRIVATE:1488:NotDriver', 'abcd'])
def test_chat_empty_messages(taxi_driver_protocol):
    response = taxi_driver_protocol.post(
        'service/chat/messages?db=1488',
        json={'md5': 'abcdef', 'channel': 'PRIVATE:1488:NotDriver'},
    )
    assert response.status_code == 200
    assert response.json()['items'] == []
