import itertools
import urllib.parse

import pytest


@pytest.mark.now('2019-10-31T11:30:00+0300')
@pytest.mark.config(
    PORTAL_AUTH_PHONE_CONFIRMATION_PERIODS_SECONDS={'__default__': 315360000},
)
@pytest.mark.experiments3(filename='exp3_cashback_for_plus_by_app.json')
@pytest.mark.experiments3(filename='conf3_plus_by_app.json')
@pytest.mark.parametrize(
    'has_ya_plus, app, expected_has_ya_plus, expected_has_cashback_plus',
    [
        (True, 'iphone', True, True),
        (False, 'iphone', False, True),
        (True, 'uber_iphone', False, False),
        (False, 'uber_iphone', False, False),
    ],
)
async def test_phonish_plus_by_phone(
        taxi_zalogin,
        mockserver,
        has_ya_plus,
        app,
        expected_has_ya_plus,
        expected_has_cashback_plus,
):
    @mockserver.json_handler('/user-api/user_phones')
    def mock_user_api_user_phones(request):
        return {
            'id': '000000000000000000000000',
            'phone': '+72222222222',
            'type': 'yandex',
            'personal_phone_id': 'my-personal-id',
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
            'stat': {
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0,
                'fake': 0,
                'total': 0,
            },
        }

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        query_params = {
            key: value
            for key, value in itertools.chain(
                urllib.parse.parse_qsl(request.query_string.decode()),
                request.form.items(),
            )
        }
        if query_params['method'] == 'user_ticket':
            assert query_params == {
                'method': 'user_ticket',
                'format': 'json',
                'dbfields': 'subscription.suid.669',
                'aliases': 'all',
                'user_ticket': 'my-user-ticket',
                'getphones': 'bound',
                'attributes': '1015,1025',
                'phone_attributes': '102,107,4,108',
            }
            return {
                'users': [
                    {
                        'uid': {'value': '12345'},
                        'aliases': {'10': 'phonish-account'},
                        'dbfields': {'subscription.suid.669': ''},
                        'attributes': {'1015': '', '1025': '1'},
                        'phones': [
                            {
                                'id': '2222',
                                'attributes': {
                                    '102': '+72222222222',
                                    '107': '1',
                                    '4': '1556681858',
                                },
                            },
                        ],
                    },
                ],
            }
        if query_params['method'] == 'check_has_plus':
            assert query_params == {
                'method': 'check_has_plus',
                'format': 'json',
                'phone_number': '72222222222',
            }
            return {'has_plus': has_ya_plus}
        pytest.fail('Unexpected blackbox method: %s' % query_params['method'])
        return {}

    @mockserver.json_handler('/user-api/v3/users/create')
    def mock_user_api_users_create(request):
        assert request.json == {
            'application': app,
            'application_version': '4.90.0',
            'authorized': True,
            'token_only': True,
            'has_ya_plus': expected_has_ya_plus,
            'has_cashback_plus': expected_has_cashback_plus,
            'yandex_staff': False,
            'yandex_uid': '12345',
            'yandex_uid_type': 'phonish',
            'phone_id': '000000000000000000000000',
            'yandex_uuid': 'my0yandex0uuid000000000000000000',
        }
        return {'id': 'my-new-user-id-11111111111111111'}

    response = await taxi_zalogin.post(
        'v1/launch/auth',
        params={'uuid': 'my0yandex0uuid000000000000000000'},
        headers={
            'X-Yandex-UID': '12345',
            'X-Ya-User-Ticket': 'my-user-ticket',
            'X-YaTaxi-Pass-Flags': 'credentials=token-bearer',
            'X-Request-Application': (
                'app_name=' + app + ',app_ver1=4,app_ver2=90'
            ),
            'X-Remote-Ip': '::ffff:5.255.245.107',
        },
        json={'allow_full_account': True},
    )
    assert response.status_code == 200
    req_resp = {
        'id': 'my-new-user-id-11111111111111111',
        'authorization_confirmed': True,
        'authorized': True,
        'token_valid': True,
        'loyal': False,
        'phone_id': '000000000000000000000000',
        'phone': '+72222222222',
        'phones': {'+72222222222': True},
        'uuid': 'my0yandex0uuid000000000000000000',
        'personal_phone_id': 'my-personal-id',
    }
    if expected_has_ya_plus:
        req_resp['has_ya_plus'] = expected_has_ya_plus
    if expected_has_cashback_plus:
        req_resp['has_cashback_plus'] = expected_has_cashback_plus
    assert response.json() == req_resp

    # fore some reason for uber we call BB just once
    if app == 'uber_iphone':
        assert mock_blackbox.times_called == 1
    else:
        assert mock_blackbox.times_called == 2
    assert mock_user_api_user_phones.times_called == 1
    assert mock_user_api_users_create.times_called == 1


@pytest.mark.now('2019-10-31T11:30:00+0300')
@pytest.mark.config(
    PORTAL_AUTH_PHONE_CONFIRMATION_PERIODS_SECONDS={'__default__': 315360000},
)
@pytest.mark.parametrize('has_ya_plus', [True, False])
@pytest.mark.experiments3(filename='conf3_plus_by_app.json')
async def test_portal_plus_by_phone(taxi_zalogin, mockserver, has_ya_plus):
    @mockserver.json_handler('/social/api/special/who_shares_taxi_data_v2')
    def mock_social(request):
        return {'status': 'ok'}

    @mockserver.json_handler('/user-api/user_phones')
    def mock_user_api_user_phones(request):
        return {
            'id': '000000000000000000000000',
            'phone': '+72222222222',
            'type': 'yandex',
            'personal_phone_id': 'my-personal-id',
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
            'stat': {
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0,
                'fake': 0,
                'total': 0,
            },
        }

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        query_params = {
            key: value
            for key, value in itertools.chain(
                urllib.parse.parse_qsl(request.query_string.decode()),
                request.form.items(),
            )
        }
        if query_params['method'] == 'user_ticket':
            assert query_params == {
                'method': 'user_ticket',
                'format': 'json',
                'dbfields': 'subscription.suid.669',
                'aliases': 'all',
                'user_ticket': 'my-user-ticket',
                'getphones': 'bound',
                'attributes': '1015,1025',
                'phone_attributes': '102,107,4,108',
            }
            return {
                'users': [
                    {
                        'uid': {'value': '12345'},
                        'aliases': {'1': 'portal-account'},
                        'dbfields': {'subscription.suid.669': ''},
                        'attributes': {'1015': '', '1025': '1'},
                        'phones': [
                            {
                                'id': '1111',
                                'attributes': {
                                    '102': '+71111111111',
                                    '4': '1556681850',
                                },
                            },
                            {
                                'id': '2222',
                                'attributes': {
                                    '102': '+72222222222',
                                    '107': '1',
                                    '4': '1556681858',
                                },
                            },
                        ],
                    },
                ],
            }
        if query_params['method'] == 'check_has_plus':
            assert query_params == {
                'method': 'check_has_plus',
                'format': 'json',
                'phone_number': '72222222222',
            }
            return {'has_plus': has_ya_plus}
        pytest.fail('Unexpected blackbox method: %s' % query_params['method'])
        return {}

    @mockserver.json_handler('/user-api/v3/users/create')
    def mock_user_api_users_create(request):
        assert request.json == {
            'application': 'iphone',
            'application_version': '4.90.0',
            'authorized': True,
            'token_only': True,
            'has_ya_plus': has_ya_plus,
            'has_cashback_plus': False,
            'yandex_staff': False,
            'yandex_uid': '12345',
            'yandex_uid_type': 'portal',
            'phone_id': '000000000000000000000000',
            'yandex_uuid': 'my0yandex0uuid000000000000000000',
        }
        return {'id': 'my-new-user-id-11111111111111111'}

    response = await taxi_zalogin.post(
        'v1/launch/auth',
        params={'uuid': 'my0yandex0uuid000000000000000000'},
        headers={
            'X-Yandex-UID': '12345',
            'X-Ya-User-Ticket': 'my-user-ticket',
            'X-YaTaxi-Pass-Flags': 'credentials=token-bearer',
            'X-Request-Application': 'app_name=iphone,app_ver1=4,app_ver2=90',
            'X-Remote-Ip': '::ffff:5.255.245.107',
        },
        json={'allow_full_account': True},
    )
    assert response.status_code == 200
    req_resp = {
        'id': 'my-new-user-id-11111111111111111',
        'authorization_confirmed': True,
        'authorized': True,
        'token_valid': True,
        'loyal': False,
        'phone_id': '000000000000000000000000',
        'phone': '+72222222222',
        'phones': {'+71111111111': True, '+72222222222': True},
        'uuid': 'my0yandex0uuid000000000000000000',
        'personal_phone_id': 'my-personal-id',
    }
    if has_ya_plus:
        req_resp['has_ya_plus'] = has_ya_plus
    assert response.json() == req_resp

    assert mock_blackbox.times_called == 2
    assert mock_social.times_called == 1
    assert mock_user_api_user_phones.times_called == 1
    assert mock_user_api_users_create.times_called == 1
