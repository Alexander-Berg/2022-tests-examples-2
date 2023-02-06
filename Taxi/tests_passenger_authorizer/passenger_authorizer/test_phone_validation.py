# pylint: disable=import-error
import datetime
import json

import pytest

from client_blackbox import mock_blackbox  # noqa: F403 F401, I100, I202


DEFAULT_PHONE = mock_blackbox.make_phone('+111111', default=True)
SECONDARY_PHONE = mock_blackbox.make_phone('+111111', default=False)
DEFAULT_CONFIRMED_PHONE = mock_blackbox.make_phone(
    '+111111', default=True, confirmation_time=datetime.datetime.utcnow(),
)


@pytest.mark.parametrize(
    'expect_flag',
    [
        pytest.param(
            True,
            id='missing_phones',
            marks=[
                pytest.mark.passport_token(
                    token1={'uid': '100', 'phones': []},
                ),
            ],
        ),
        pytest.param(
            True,
            id='without_default_phone',
            marks=[
                pytest.mark.passport_token(
                    token1={'uid': '100', 'phones': [SECONDARY_PHONE]},
                ),
            ],
        ),
        pytest.param(
            True,
            id='unconfirmed',
            marks=[
                pytest.mark.passport_token(
                    token1={'uid': '100', 'phones': [DEFAULT_PHONE]},
                ),
            ],
        ),
        pytest.param(
            False,
            id='confirmed',
            marks=[
                pytest.mark.passport_token(
                    token1={'uid': '100', 'phones': [DEFAULT_CONFIRMED_PHONE]},
                ),
            ],
        ),
        pytest.param(
            False,
            id='confirmed',
            marks=[
                pytest.mark.passport_token(
                    token1={
                        'uid': '100',
                        'phones': [SECONDARY_PHONE, DEFAULT_CONFIRMED_PHONE],
                    },
                ),
            ],
        ),
    ],
)
async def test_proxy_validation_rule(
        taxi_passenger_authorizer, blackbox_service, mockserver, expect_flag,
):
    # assert match_enabled
    called = {'called': 0}

    @mockserver.json_handler('/4.0/phone-validation/proxy')
    def _test(request):
        called['called'] += 1

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert request.headers['X-YaTaxi-UserId'] == '12345'
        has_flag = 'phone_confirmation_required' in (
            request.headers['X-YaTaxi-Pass-Flags']
        )
        assert has_flag if expect_flag else not has_flag

        return {'id': '123'}

    response = await taxi_passenger_authorizer.post(
        '4.0/phone-validation/proxy',
        data=json.dumps({}),
        bearer='token1',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert called['called'] == 1
    assert response.status_code == 200


@pytest.mark.parametrize(
    'expected_code',
    [
        pytest.param(
            401,
            id='missing_phones',
            marks=[
                pytest.mark.passport_token(
                    token1={'uid': '100', 'phones': []},
                ),
            ],
        ),
        pytest.param(
            401,
            id='without_default_phone',
            marks=[
                pytest.mark.passport_token(
                    token1={'uid': '100', 'phones': [SECONDARY_PHONE]},
                ),
            ],
        ),
        pytest.param(
            401,
            id='unconfirmed',
            marks=[
                pytest.mark.passport_token(
                    token1={'uid': '100', 'phones': [DEFAULT_PHONE]},
                ),
            ],
        ),
        pytest.param(
            200,
            id='confirmed',
            marks=[
                pytest.mark.passport_token(
                    token1={'uid': '100', 'phones': [DEFAULT_CONFIRMED_PHONE]},
                ),
            ],
        ),
    ],
)
async def test_strict_validation_rule(
        taxi_passenger_authorizer, blackbox_service, mockserver, expected_code,
):
    # assert match_enabled
    called = {'called': 0}

    @mockserver.json_handler('/4.0/phone-validation/strict')
    def _test(request):
        called['called'] += 1

    response = await taxi_passenger_authorizer.post(
        '4.0/phone-validation/strict',
        data=json.dumps({}),
        bearer='token1',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert called['called'] == 1
    else:
        assert called['called'] == 0


@pytest.mark.passport_token(token1={'uid': '100', 'phones': [SECONDARY_PHONE]})
async def test_invalidate_cache(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    # assert match_enabled
    called = {'called': 0}

    @mockserver.json_handler('/4.0/phone-validation/proxy')
    def _test(request):
        called['called'] += 1

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        has_flag = 'phone_confirmation_required' in (
            request.headers['X-YaTaxi-Pass-Flags']
        )
        assert has_flag if called['called'] == 1 else not has_flag

        return {'id': '123'}

    response = await taxi_passenger_authorizer.post(
        '4.0/phone-validation/proxy',
        data=json.dumps({}),
        bearer='token1',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert called['called'] == 1
    assert response.status_code == 200

    blackbox_service.set_token_info(
        'token1', uid='100', phones=[DEFAULT_CONFIRMED_PHONE],
    )

    response = await taxi_passenger_authorizer.post(
        '4.0/phone-validation/proxy',
        data=json.dumps({}),
        bearer='token1',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert called['called'] == 2
    assert response.status_code == 200


@pytest.mark.parametrize(
    'token,session,phone_attributes',
    [('token1', None, '107,4,109'), (None, 'sessionx', '107,4,108,109')],
)
async def test_blackbox_phone_attributes(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        token,
        session,
        phone_attributes,
):
    # assert match_enabled
    called = {'called': 0}

    @mockserver.json_handler('/blackbox')
    def _test(request):
        called['called'] += 1
        assert request.args['phone_attributes'] == phone_attributes
        assert request.args['getphones'] == 'bound'
        return mockserver.make_response('Invalid', status=400)

    await taxi_passenger_authorizer.tests_control(invalidate_caches=True)

    headers = {'X-YaTaxi-UserId': '12345'}
    if session:
        headers['Cookie'] = 'Session_id=' + session
    extra = {}
    if token:
        extra['bearer'] = token
    await taxi_passenger_authorizer.post(
        '4.0/phone-validation/proxy',
        data=json.dumps({}),
        headers=headers,
        **extra,
    )
    assert called['called'] == 1
