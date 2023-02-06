import json

import pytest


def get_actual_metrics(metrics_before_test, metrics_after_test):
    actual_metrics = {}
    for metric in metrics_after_test.keys():
        if metric in metrics_before_test.keys():
            actual_metrics[metric] = (
                metrics_after_test[metric] - metrics_before_test[metric]
            )
        else:
            actual_metrics[metric] = metrics_after_test[metric]
    return actual_metrics


def get_access_control_usage(enabled: bool, dry_run: bool, strict_rule: bool):
    return pytest.mark.experiments3(
        name='eats_restapp_authproxy_access_control_usage',
        consumers=['eats-restapp-authproxy/ac_usage'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'enabled': enabled,
                    'dry_run': dry_run,
                    'strict_rule': strict_rule,
                },
            },
        ],
        is_config=True,
    )


async def request_proxy(taxi_eats_authproxy, token, url):
    await taxi_eats_authproxy.invalidate_caches()

    headers = {}
    if token is not None:
        headers['X-Token'] = token
    extra = {'headers': headers}
    return await taxi_eats_authproxy.post(url, data=json.dumps({}), **extra)


@pytest.mark.parametrize(
    'status_code,url,expected_metrics',
    [
        pytest.param(
            200,
            '/4.0/restapp-front/api/v1/client/orders/search',
            {
                'proxy401': 0,
                'auth-ok': 0,
                'auth-fail-no-prefix': 0,
                'auth-fail-access-denied': 0,
                'auth-fail-unexpected-error': 0,
            },
            marks=get_access_control_usage(False, False, False),
            id='all disabled',
        ),
        pytest.param(
            200,
            '/4.0/restapp-front/api/v1/client/orders/search',
            {
                'proxy401': 0,
                'auth-ok': 1,
                'auth-fail-no-prefix': 0,
                'auth-fail-access-denied': 0,
                'auth-fail-unexpected-error': 0,
            },
            marks=get_access_control_usage(True, False, False),
            id='enabled',
        ),
        pytest.param(
            401,
            '/4.0/restapp-front/api/v1/client/orders/change',
            {
                'proxy401': 0,
                'auth-ok': 0,
                'auth-fail-no-prefix': 0,
                'auth-fail-access-denied': 0,
                'auth-fail-unexpected-error': 1,
            },
            marks=get_access_control_usage(True, False, False),
            id='access denied',
        ),
        pytest.param(
            200,
            '/4.0/restapp-front/api/v1/client/orders/change',
            {
                'proxy401': 0,
                'auth-ok': 1,
                'auth-fail-no-prefix': 0,
                'auth-fail-access-denied': 0,
                'auth-fail-unexpected-error': 0,
            },
            marks=get_access_control_usage(True, True, False),
            id='dry run',
        ),
        pytest.param(
            401,
            '/4.0/restapp-front/api/v1/client/restaurants',
            {
                'proxy401': 0,
                'auth-ok': 0,
                'auth-fail-no-prefix': 1,
                'auth-fail-access-denied': 0,
                'auth-fail-unexpected-error': 0,
            },
            marks=get_access_control_usage(True, False, True),
            id='different prefix with strict rule check and not dry run',
        ),
        pytest.param(
            200,
            '/4.0/restapp-front/api/v1/client/restaurants',
            {
                'proxy401': 0,
                'auth-ok': 1,
                'auth-fail-no-prefix': 0,
                'auth-fail-access-denied': 0,
                'auth-fail-unexpected-error': 0,
            },
            marks=get_access_control_usage(True, False, False),
            id='different prefix without strict rule check and not dry run',
        ),
        pytest.param(
            200,
            '/4.0/restapp-front/api/v1/client/restaurants',
            {
                'proxy401': 0,
                'auth-ok': 1,
                'auth-fail-no-prefix': 0,
                'auth-fail-access-denied': 0,
                'auth-fail-unexpected-error': 0,
            },
            marks=get_access_control_usage(True, True, True),
            id='different prefix with strict rule check and dry run',
        ),
    ],
)
async def test_auth_with_token(
        taxi_eats_restapp_authproxy,
        taxi_eats_restapp_authproxy_monitor,
        mockserver,
        mock_eats_restapp_authorizer,
        mock_access_control,
        mock_return_partner_info_200,
        status_code,
        url,
        expected_metrics,
):
    @mockserver.json_handler(url)
    def _mock_backend(request):
        assert request.headers['X-YaEda-PartnerId'] == '41'
        return mockserver.make_response(status=200, json={'status': 'success'})

    metrics_before_test = await taxi_eats_restapp_authproxy_monitor.get_metric(
        'proxy',
    )

    response = await request_proxy(
        taxi_eats_restapp_authproxy, token='token', url=url,
    )
    assert response.status_code == status_code

    metrics_after_test = await taxi_eats_restapp_authproxy_monitor.get_metric(
        'proxy',
    )

    actual_metrics = get_actual_metrics(
        metrics_before_test['auth-result'], metrics_after_test['auth-result'],
    )

    assert actual_metrics == expected_metrics
