# pylint: disable=import-error,wildcard-import
import pytest

import utils

AM_ROUTING_RULE = utils.make_rule(
    {
        'input': {'prefix': '/staff_login', 'rule_name': '/staff_login'},
        'proxy': {
            'auth_type': 'oauth-or-session',
            'personal': {'staff_login': True},
        },
        'rule_type': 'passenger-authorizer',
    },
)


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.routing_rules([AM_ROUTING_RULE])
async def test_proxy_pa_staff_login_header(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    blackbox_service.set_token_info(
        'token', uid='100', staff_login='staff_login',
    )

    @mockserver.json_handler('/staff_login')
    def mock_staff_login(request):
        assert request.headers['X-YaTaxi-Staff-Login'] == 'staff_login'
        return {}

    await taxi_passenger_authorizer.post(
        '/staff_login',
        bearer='token',
        headers={
            'Content-Type': 'application/json',
            'Origin': 'localhost',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert mock_staff_login.times_called == 1


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.routing_rules([AM_ROUTING_RULE])
@pytest.mark.passport_token(token={'uid': '100'})
async def test_proxy_pa_staff_login_header_empty_blackbox(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/staff_login')
    def mock_staff_login(request):
        assert request.headers['X-YaTaxi-Staff-Login'] == ''
        return {}

    # blackbox without staff_login parameter
    blackbox_service.set_token_info('token', uid='100')

    await taxi_passenger_authorizer.post(
        '/staff_login',
        bearer='token',
        headers={
            'Content-Type': 'application/json',
            'Origin': 'localhost',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
        },
    )
    assert mock_staff_login.times_called == 1
