import pytest

import utils

AM_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/test',
            'priority': 100,
            'rule_name': '/test',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/test',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'session',
            'cookie_webview_enabled': False,
            'passport_scopes': [],
            'proxy_cookie': [],
            'personal': {
                'eater_id': True,
                'eater_uuid': True,
                'email_id': True,
                'phone_id': True,
            },
            'proxy_401': False,
        },
        'rule_type': 'eats-authproxy',
    },
]


@pytest.mark.passport_token(token={'uid': '100', 'scope': 'eats:all'})
@pytest.mark.eater_session(outer={'inner': 'in'})
@pytest.mark.eater(
    u100={
        'id': '100',
        'personal_phone_id': 'p100',
        'personal_email_id': 'e100',
    },
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
@pytest.mark.parametrize(
    ['error_type', 'expected_metric_value'],
    [
        pytest.param('InternalServerError', 1, id='internal'),
        pytest.param('std::exception', 1, id='unknown'),
        pytest.param('Unauthorized', 0, id='unauthorized'),
        pytest.param('Timeout', 0, id='timeout'),
    ],
)
async def test_internal_error(
        taxi_eats_authproxy,
        mockserver,
        mock_eater_authorizer,
        mock_core_eater,
        blackbox_service,
        request_proxy,
        testpoint,
        taxi_eats_authproxy_monitor,
        error_type,
        expected_metric_value,
):
    await taxi_eats_authproxy.tests_control(reset_metrics=True)

    @testpoint('internal_error_test')
    def _mytp(data):
        return {'value': error_type}

    @mockserver.json_handler('test/123')
    def _mock_backend(request):
        if error_type == 'Timeout':
            raise mockserver.TimeoutError()

    @mockserver.json_handler('/eater-authorizer/v1/eater/sessions/login')
    def _mock_login(request):
        return 'ok'

    await request_proxy('token', headers={'Origin': 'yandex.ru'})
    metrics = await taxi_eats_authproxy_monitor.get_metric(
        'eap-router-metrics',
    )

    utils.check_metrics(
        metrics, {'internal_errors_counter': expected_metric_value},
    )
