import datetime
import hashlib

import pytest

TOKEN = '49ad7845b979409abf57ec556e980153'


@pytest.mark.parametrize(
    'application, build_type, token_type',
    [
        ('iphone', 'inhouse-dev', 'apns'),
        ('android', None, 'hms'),
        ('android', None, 'fcm'),
    ],
)
@pytest.mark.now('2020-06-26T14:00:00Z')
async def test_user_notification_subscribe(
        taxi_ucommunications,
        mockserver,
        stq,
        application,
        build_type,
        token_type,
):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _subscribe_app(request, *args, **kwargs):
        return mockserver.make_response('OK', 200)

    data = {'user_id': 'user_id', 'application': application}
    expected_apns_token = ''
    expected_gcm_token = ''
    expected_hms_token = ''
    if token_type == 'apns':
        data['apns_token'] = TOKEN
        expected_apns_token = TOKEN
    elif token_type == 'fcm':
        data['gcm_token'] = TOKEN
        expected_gcm_token = TOKEN
    elif token_type == 'hms':
        data['hms_token'] = TOKEN
        expected_hms_token = TOKEN
    else:
        assert False, 'bad token type'

    if token_type == 'hms':
        data['token_type'] = token_type
    if build_type:
        data['build_type'] = build_type

    response = await taxi_ucommunications.post(
        'user/notification/subscribe', json=data,
    )
    assert response.status_code == 200
    assert stq.user_notification_subscription.times_called == 1
    call = stq.user_notification_subscription.next_call()
    call.pop('id')
    link = call['kwargs']['log_extra']['_link']
    assert link
    assert isinstance(link, str)
    result_build_type = call['kwargs'].pop('build_type')
    if build_type:
        assert result_build_type == 'inhouse-dev'
    expected_type = 'hms' if token_type == 'hms' else ''
    assert call == {
        'args': [],
        'eta': datetime.datetime(2020, 6, 26, 14, 0),
        'kwargs': {
            'log_extra': {'_link': link},
            'token': TOKEN,
            'token_type': expected_type,
            'push_tokens_hash': {
                'apns_token_hash': hashlib.md5(
                    expected_apns_token.encode(),
                ).hexdigest(),
                'gcm_token_hash': hashlib.md5(
                    expected_gcm_token.encode(),
                ).hexdigest(),
                'hms_token_hash': hashlib.md5(
                    expected_hms_token.encode(),
                ).hexdigest(),
            },
            'user_id': 'user_id',
            'application': application,
        },
        'queue': 'user_notification_subscription',
    }


@pytest.mark.now('2020-06-26T14:00:00Z')
async def test_tags(taxi_ucommunications, mockserver, stq):
    response = await taxi_ucommunications.post(
        'user/notification/subscribe',
        json={
            'user_id': 'user_1',
            'push_tokens': {
                'apns_token': 'token',
                'gcm_token': '',
                'hms_token': '',
            },
            'push_settings': {
                'included_tags': ['new_feats', 'taxi_promocodes'],
                'excluded_tags': ['lavka_news', 'eats_discounts'],
                'enabled_by_system': True,
            },
            'application': 'iphone',
            'build_type': 'inhouse-distr',
        },
    )
    assert response.status_code == 200
    call = stq.user_notification_subscription.next_call()
    call.pop('id')
    link = call['kwargs']['log_extra']['_link']

    assert call == {
        'args': [],
        'eta': datetime.datetime(2020, 6, 26, 14, 0),
        'kwargs': {
            'log_extra': {'_link': link},
            'build_type': 'inhouse-distr',
            'token': 'token',
            'token_type': '',
            'push_tokens_hash': {
                'apns_token_hash': hashlib.md5('token'.encode()).hexdigest(),
                'gcm_token_hash': hashlib.md5(''.encode()).hexdigest(),
                'hms_token_hash': hashlib.md5(''.encode()).hexdigest(),
            },
            'user_id': 'user_1',
            'application': 'iphone',
            'push_settings': {
                'enabled_by_system': True,
                'excluded_tags': ['lavka_news', 'eats_discounts'],
                'included_tags': ['new_feats', 'taxi_promocodes'],
            },
            'excluded_tags': ['lavka_news', 'eats_discounts'],
        },
        'queue': 'user_notification_subscription',
    }


@pytest.mark.now('2020-06-26T14:00:00Z')
async def test_subscribe_webpush(taxi_ucommunications, stq):
    subscription = {
        'endpoint': 'https://fcm.googleapis.com/fcm/send/id',
        'expirationTime': None,
        'keys': {
            'auth': '9pvIVgPVrXiT2gYizpdS-g222',
            'p256dh': 'BNFGBgNt0dLv4AOJr0ocZfX9U120PyGbfiHZ9smoTTG',
        },
    }
    data = {
        'user_id': 'user_id',
        'application': 'web_turboapp_taxi',
        'subscription': subscription,
    }

    response = await taxi_ucommunications.post(
        'user/notification/subscribe', json=data,
    )
    assert response.status_code == 200

    assert stq.user_notification_subscription.times_called == 1
    call = stq.user_notification_subscription.next_call()

    call.pop('id')
    call['kwargs'].pop('log_extra')

    assert call == {
        'args': [],
        'eta': datetime.datetime(2020, 6, 26, 14, 0),
        'kwargs': {
            'token': '',
            'user_id': 'user_id',
            'application': 'web_turboapp_taxi',
            'web_push_subscription': subscription,
        },
        'queue': 'user_notification_subscription',
    }
