import pytest


@pytest.fixture
def client_notify(mockserver):
    class Handlers:
        @mockserver.json_handler('/client_notify/v2/push')
        def mock_client_notify(request):
            return {'notification_id': '123123'}

    return Handlers()


def test_no_message(taxi_driver_protocol):
    response = taxi_driver_protocol.post('service/chat/add')
    assert response.status_code == 200
    assert not response.text

    response = taxi_driver_protocol.post(
        'service/chat/add?db=1488', json={'yandex': False, 'user_id': 'abcde'},
    )
    assert response.status_code == 200
    assert not response.text

    response = taxi_driver_protocol.post(
        'service/chat/add', json={'yandex': 'False'},
    )
    assert response.status_code == 200
    assert not response.text


def test_not_valid_channel(taxi_driver_protocol):
    response = taxi_driver_protocol.post(
        'service/chat/add?db=1',
        json={'channel': 'Index', 'msg': 'Chop is dish'},
    )
    assert response.status_code == 404

    response = taxi_driver_protocol.post(
        'service/chat/add?db=777', json={'msg': 'Chop is dish'},
    )
    assert response.status_code == 500


def test_chat_disabled(taxi_driver_protocol):
    response = taxi_driver_protocol.post(
        'service/chat/add?db=666', json={'channel': 'usual', 'msg': 'lalala'},
    )
    assert response.status_code == 400


def test_chat_add(taxi_driver_protocol, client_notify, mockserver):
    response = taxi_driver_protocol.post(
        'service/chat/add?db=1488',
        json={
            'channel': 'PRIVATE:1488:Driver',
            'driver': 'Driver',
            'user_id': '123456',
            'yandex': True,
            'user_login': 'olegvp',
            'msg': 'Testing message',
        },
    )
    assert response.status_code == 200
    client_notify.mock_client_notify.wait_call()


def test_empty_locale(taxi_driver_protocol, client_notify):
    response = taxi_driver_protocol.post(
        'service/chat/add',
        json={'channel': 'usual', 'msg': 'lalala', 'user_id': 'qwerty123456'},
    )
    assert response.status_code == 200
    client_notify.mock_client_notify.wait_call()
