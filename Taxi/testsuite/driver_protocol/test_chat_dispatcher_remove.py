import json

import pytest


def test_bad_request(taxi_driver_protocol):
    response = taxi_driver_protocol.post('service/chat/dispatcher/remove')
    assert response.status_code == 400

    response = taxi_driver_protocol.post(
        'service/chat/dispatcher/remove?db=1488',
    )
    assert response.status_code == 400

    response = taxi_driver_protocol.post(
        'service/chat/dispatcher/remove?id=abc',
    )
    assert response.status_code == 400


@pytest.mark.redis_store(['set', 'Chat:DispatherMd5:1488', 'abcdef'])
def test_no_message(taxi_driver_protocol):
    response = taxi_driver_protocol.post(
        'service/chat/dispatcher/remove?db=1488&id=123',
    )
    assert response.status_code == 200


@pytest.mark.now('2017-12-06T11:11:11+0000')
@pytest.mark.redis_store(
    ['set', 'Chat:DispatherMd5:1488', 'abcdef'],
    ['hmset', 'Chat:Dispather:1488', {'123': json.dumps({'msg': '123'})}],
)
def test_remove(taxi_driver_protocol):
    response = taxi_driver_protocol.post(
        'service/chat/dispatcher/remove?db=1488&id=123',
    )
    assert response.status_code == 200
