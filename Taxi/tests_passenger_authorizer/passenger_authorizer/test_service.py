# flake8: noqa
# pylint: disable=import-error,wildcard-import
from passenger_authorizer_plugins.generated_tests import *
# Feel free to write your own implementation to override generated tests


async def test_check_nodata(taxi_passenger_authorizer, blackbox_service):
    response = await taxi_passenger_authorizer.post('check')
    assert response.status_code == 200
    assert not response.json()['authorized']


async def test_check_token_ok(taxi_passenger_authorizer, blackbox_service):
    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        'check',
        data='{}',
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'authorized': True,
        'is_timed_out': False,
        'phone-id': '102610261026102610261026',
        'token': {
            'login': 'login',
            'login_id': 'login_id',
            'pdd': False,
            'phonish': True,
            'portal': False,
            'uid': '100',
            'ya_plus': False,
            'cashback_plus': False,
        },
    }


async def test_check_session_ok(taxi_passenger_authorizer, blackbox_service):
    blackbox_service.set_sessionid_info('session_id_cookie', uid='100')

    response = await taxi_passenger_authorizer.post(
        'check',
        data='{}',
        headers={
            'Cookie': 'Session_id=session_id_cookie',
            'X-YaTaxi-UserId': '12345',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'authorized': True,
        'is_timed_out': False,
        'phone-id': '102610261026102610261026',
        'sid': {'login': 'login', 'uid': '100'},
    }


async def test_check_session_and_token_ok(
        taxi_passenger_authorizer, blackbox_service,
):
    blackbox_service.set_sessionid_info('session_id_cookie', uid='100')
    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        'check',
        data='{}',
        bearer='test_token',
        headers={
            'Cookie': 'Session_id=session_id_cookie',
            'X-YaTaxi-UserId': '12345',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'authorized': True,
        'is_timed_out': False,
        'phone-id': '102610261026102610261026',
        'token': {
            'login': 'login',
            'login_id': 'login_id',
            'phonish': True,
            'portal': False,
            'pdd': False,
            'uid': '100',
            'ya_plus': False,
            'cashback_plus': False,
        },
        'sid': {'login': 'login', 'uid': '100'},
    }


async def test_check_token_userid_mismatch(
        taxi_passenger_authorizer, blackbox_service,
):
    # Invalid uid
    blackbox_service.set_token_info('test_token', uid='101')

    response = await taxi_passenger_authorizer.post(
        'check',
        data='{}',
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 200
    assert not response.json()['authorized']


async def test_userid_changed(
        taxi_passenger_authorizer, blackbox_service, mongodb, mockserver,
):
    @mockserver.json_handler('/4.0/')
    async def _test(request):
        return {}

    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '/4.0/',
        data='{}',
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 200

    mongodb.users.update({'_id': '12345'}, {'$set': {'yandex_uid': '101'}})

    blackbox_service.set_token_info('test_token2', uid='101')

    response = await taxi_passenger_authorizer.post(
        '/4.0/',
        data='{}',
        bearer='test_token2',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 200


async def test_check_session_userid_mismatch(
        taxi_passenger_authorizer, blackbox_service,
):
    blackbox_service.set_sessionid_info('session_id_cookie', uid='102')

    response = await taxi_passenger_authorizer.post(
        'check',
        data='{}',
        headers={
            'Cookie': 'Session_id=session_id_cookie',
            'X-YaTaxi-UserId': '100',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'authorized': False, 'is_timed_out': False}


async def test_check_session_and_token_userids_mismatch(
        taxi_passenger_authorizer, blackbox_service,
):
    blackbox_service.set_sessionid_info('session_id_cookie', uid='102')
    blackbox_service.set_token_info('test_token', uid='101')

    response = await taxi_passenger_authorizer.post(
        'check',
        data='{}',
        bearer='test_token',
        headers={
            'Cookie': 'Session_id=session_id_cookie',
            'X-YaTaxi-UserId': '100',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'authorized': False, 'is_timed_out': False}


async def test_check_token_nouser(taxi_passenger_authorizer, blackbox_service):
    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        'check',
        data='{}',
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '1245'},  # no such user
    )
    assert response.status_code == 200
    assert not response.json()['authorized']


async def test_check_badtoken(taxi_passenger_authorizer, blackbox_service):
    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        'check',
        data='{}',
        bearer='bad_token',
        headers={'X-YaTaxi-UserId': '100'},
    )
    assert response.status_code == 200
    assert not response.json()['authorized']


async def test_check_passport_timeout(taxi_passenger_authorizer, mockserver):
    @mockserver.json_handler('/blackbox')
    async def _passport_timeout(request):
        raise mockserver.TimeoutError

    response = await taxi_passenger_authorizer.post(
        'check',
        data='{}',
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '12345'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'authorized': False,
        'is_timed_out': True,
        'phone-id': '102610261026102610261026',
    }
