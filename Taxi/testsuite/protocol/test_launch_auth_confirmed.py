import json

import pytest


@pytest.fixture(scope='function', autouse=True)
def mock_services(mockserver):
    @mockserver.json_handler('/feedback/1.0/wanted/retrieve')
    def mock_feedback(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert sorted(data.keys()) == ['id', 'newer_than', 'phone_id']
        return {'orders': []}


@pytest.mark.parametrize(
    'user_id, authorized',
    [
        ('11111111111111111111111111111111', False),
        ('11111111111111111111111111111112', True),
    ],
)
@pytest.mark.parametrize('auth_confirmed', ['true', 'True', 'TRUE'])
@pytest.mark.config(TVM_ENABLED=False)
def test_auth_confirmed(
        taxi_protocol, db, user_id, authorized, auth_confirmed,
):
    request_yandex_uuid = '44444444444444444444444444444444'

    user_before = db.users.find_one({'_id': user_id})

    yandex_uuid = user_before['yandex_uuid']

    response = taxi_protocol.post(
        '3.0/launch',
        params={'uuid': request_yandex_uuid},
        headers={'X-Yandex-Auth-Confirmed': auth_confirmed},
        json={'id': user_id},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['id'] == user_id
    assert response_body['authorized'] == authorized
    assert response_body['uuid'] == yandex_uuid

    user_after = db.users.find_one({'_id': user_id})

    assert user_after == user_before


@pytest.mark.parametrize('user_id', ['11111111111111111111111111111112'])
@pytest.mark.config(
    TVM_ENABLED=False,
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'timeout': 100, 'retries': 1},
        'launch': {'use_afs': True, 'timeout': 200, 'retries': 2},
    },
)
def test_is_spammer_device_id(taxi_protocol, mockserver, user_id):
    @mockserver.json_handler('/antifraud/client/user/is_spammer/launch')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': user_id,
            'user_phone_id': '333333333333333333333333',
            'device_id': '4444-444444-44444444-4444444-444444',
        }
        return {'is_spammer': False}

    response = taxi_protocol.post(
        '3.0/launch',
        headers={'X-Yandex-Auth-Confirmed': 'true'},
        json={'id': user_id, 'device_id': 'some_device_id'},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['id'] == user_id


@pytest.mark.config(TVM_ENABLED=False)
def test_auth_confirmed_zuser(taxi_protocol):
    user_id = 'z1111111111111111111111111111111'

    response = taxi_protocol.post(
        '3.0/launch',
        headers={'X-Yandex-Auth-Confirmed': 'true'},
        json={'id': user_id},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['id'] == user_id
    assert not response_body['authorized']
    assert response_body['uuid'] == ''


def test_fake_auth_confirmed(taxi_protocol, db):
    user_id = '11111111111111111111111111111111'
    request_yandex_uuid = '44444444444444444444444444444444'

    user_before = db.users.find_one({'_id': user_id})

    response = taxi_protocol.post(
        '3.0/launch',
        params={'uuid': request_yandex_uuid},
        headers={
            'X-Ya-Service-Ticket': 'ticket',
            'X-Yandex-Auth-Confirmed': 'true',
        },
        json={'id': user_id},
    )
    assert response.status_code == 401

    user_after = db.users.find_one({'_id': user_id})

    assert user_after == user_before
