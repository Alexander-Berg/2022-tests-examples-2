import json

import pytest


def test_no_park(taxi_driver_protocol):
    response = taxi_driver_protocol.post('service/chat/dispatcher/messages')
    assert response.status_code == 404

    response = taxi_driver_protocol.post(
        'service/chat/dispatcher/messages?db=1',
    )
    assert response.status_code == 404


@pytest.mark.redis_store(['set', 'Chat:DispatherMd5:1488', 'abcdef'])
def test_no_new_messages(taxi_driver_protocol):
    response = taxi_driver_protocol.post(
        'service/chat/dispatcher/messages?db=1488', json={'md5': 'abcdef'},
    )
    assert response.status_code == 200
    assert not response.text


@pytest.mark.now('2017-11-28T12:30:00Z')
@pytest.mark.redis_store(
    ['set', 'Chat:DispatherMd5:1488', 'abcdef'],
    [
        'hmset',
        'Chat:Dispather:1488',
        {
            '111': json.dumps({'date': '2017-11-28T12:11:11Z', 'msg': '1'}),
            '222': json.dumps({'date': '2017-11-28T12:00:00Z', 'msg': '2'}),
            '333': json.dumps({'date': '2017-11-28T11:59:59Z', 'msg': '3'}),
            '444': json.dumps({'date': '2017-11-28T12:20:00Z', 'msg': '4'}),
            '555': json.dumps({'date': '2017-11-28T12:15:00Z', 'msg': '5'}),
            '666': json.dumps({'msg': '6'}),
            '777': json.dumps({}),
        },
    ],
)
def test_dispatcher_messages(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.post(
        'service/chat/dispatcher/messages?db=1488', json={'md5': 'ab'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('answer.json')
