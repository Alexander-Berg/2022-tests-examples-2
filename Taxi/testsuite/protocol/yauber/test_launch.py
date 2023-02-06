import base64
import hashlib
import hmac

from protocol.yauber import yauber


def test_basic(taxi_protocol, db, blackbox_service, dummy_feedback):
    response = taxi_protocol.post(
        '/3.0/launch',
        json={'id': '536b24fa2816451b855d9a3e640215c3'},
        bearer='test_token',
        headers=yauber.headers,
    )
    response = response.json()
    user_id = response['id']
    assert response['authorized']
    assert response['phone'] == '+72222222222'
    user = db.users.find_one({'_id': user_id})
    phone_id = user['phone_id']
    user_phone = db.user_phones.find_one({'_id': phone_id})
    assert user_phone['phone'] == '+72222222222'
    assert user_phone['type'] == 'uber'
    assert user_phone['phone_hash'] is not None
    assert user_phone['phone_salt'] is not None
    assert (
        user_phone['phone_hash']
        == hmac.new(
            base64.b64decode(user_phone['phone_salt']) + b'secdist_salt',
            user_phone['phone'].encode(),
            hashlib.sha256,
        ).hexdigest()
    )


def test_invalid_scope(taxi_protocol, db, blackbox_service):
    blackbox_service.set_token_info(
        'test_token', '123', phones=['*+72222222222'], scope='yataxi:write',
    )
    response = taxi_protocol.post(
        '/3.0/launch', json={}, bearer='test_token', headers=yauber.headers,
    )
    response = response.json()
    assert not response['authorized']
    assert not response['token_valid']
