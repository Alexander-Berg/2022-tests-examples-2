import json

import pytest
import pytz


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


async def request_proxy(taxi_eats_authproxy, token, url):
    await taxi_eats_authproxy.invalidate_caches()

    headers = {}
    if token is not None:
        headers['X-Token'] = token
    extra = {'headers': headers}
    return await taxi_eats_authproxy.post(url, data=json.dumps({}), **extra)


async def request_proxy_wo_cache_inval(taxi_eats_authproxy, token, url):
    headers = {}
    if token is not None:
        headers['X-Token'] = token
    extra = {'headers': headers}
    return await taxi_eats_authproxy.post(url, data=json.dumps({}), **extra)


async def request_proxy_with_locale(
        taxi_eats_authproxy, accept_language, x_language, url,
):
    headers = {}
    headers['X-Token'] = 'token'
    if accept_language is not None:
        headers['Accept-Language'] = accept_language
    if x_language is not None:
        headers['X-Language'] = x_language
    extra = {'headers': headers}
    return await taxi_eats_authproxy.post(url, data=json.dumps({}), **extra)


@pytest.mark.parametrize(
    'places,personal_email_id',
    [
        pytest.param([123, 234, 343], '999', id='multiple places'),
        pytest.param([123], '999', id='single place'),
        pytest.param([], '999', id='empty places'),
        pytest.param([123, 234, 343], None, id='no personal_email_id'),
    ],
)
async def test_headers_with_200_response_from_eats_partners(
        taxi_eats_restapp_authproxy,
        taxi_eats_restapp_authproxy_monitor,
        mockserver,
        mock_eats_restapp_authorizer,
        mock_access_control,
        places,
        personal_email_id,
):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/info')
    def _mock_response_200(request):
        payload = {
            'country_code': 'RU',
            'email': 'partner1@partner.com',
            'id': 1,
            'is_blocked': False,
            'is_fast_food': False,
            'name': 'Партнер1',
            'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6332',
            'places': places,
            'roles': [
                {'id': 1, 'slug': 'ROLE_ADMIN', 'title': 'admin'},
                {'id': 2, 'slug': 'ROLE_LOL', 'title': 'lol'},
            ],
            'timezone': 'Europe/Moscow',
        }
        if personal_email_id:
            payload['personal_email_id'] = personal_email_id
        return mockserver.make_response(status=200, json={'payload': payload})

    @mockserver.json_handler('/4.0/restapp-front/api/v1/client/orders/search')
    def _mock_backend(request):
        assert 'X-Token' not in request.headers
        assert request.headers['X-YaEda-PartnerId'] == '41'
        assert (
            request.headers['X-YaEda-Partner-Uid']
            == '1b9d70ef-d667-4c9c-9b20-c61209ea6332'
        )
        assert request.headers['X-YaEda-Partner-Places'] == ','.join(
            map(str, places),
        )
        assert request.headers['X-YaEda-Partner-Country-Code'] == 'RU'
        if personal_email_id:
            assert (
                request.headers['X-YaEda-Partner-Personal-Email-Id']
                == personal_email_id
            )
        else:
            assert 'X-YaEda-Partner-Personal-Email-Id' not in request.headers

        return mockserver.make_response(status=200, json={'status': 'success'})

    response = await request_proxy(
        taxi_eats_restapp_authproxy,
        token='token',
        url='/4.0/restapp-front/api/v1/client/orders/search',
    )
    assert response.status_code == 200


async def test_headers_with_400_response_from_eats_partners(
        taxi_eats_restapp_authproxy,
        taxi_eats_restapp_authproxy_monitor,
        mockserver,
        mock_eats_restapp_authorizer,
        mock_access_control,
        mock_return_partner_info_400,
):
    metrics_before_test = await taxi_eats_restapp_authproxy_monitor.get_metric(
        'proxy',
    )

    response = await request_proxy(
        taxi_eats_restapp_authproxy,
        token='token',
        url='/4.0/restapp-front/api/v1/client/orders/search',
    )
    assert response.status_code == 500

    metrics_after_test = await taxi_eats_restapp_authproxy_monitor.get_metric(
        'proxy',
    )

    actual_metrics = get_actual_metrics(
        metrics_before_test['auth-result'], metrics_after_test['auth-result'],
    )
    assert not actual_metrics['auth-ok']
    assert not actual_metrics['auth-fail-no-prefix']
    assert not actual_metrics['auth-fail-access-denied']
    assert actual_metrics['auth-fail-unexpected-error'] == 1


@pytest.mark.parametrize(
    'status_code',
    [
        pytest.param(
            401,
            marks=(
                pytest.mark.config(
                    EATS_RESTAPP_AUTHPROXY_ROUTE_RULES=[
                        {
                            'input': {
                                'http-path-prefix': (
                                    '/4.0/restapp-front/api/v1/client/orders'
                                ),
                            },
                            'output': {
                                'tvm-service': 'mock',
                                'upstream': {'$mockserver': ''},
                            },
                            'proxy': {},
                        },
                    ],
                )
            ),
            id='proxy 401 disabled',
        ),
        pytest.param(
            200,
            marks=(
                pytest.mark.config(
                    EATS_RESTAPP_AUTHPROXY_ROUTE_RULES=[
                        {
                            'input': {
                                'http-path-prefix': (
                                    '/4.0/restapp-front/api/v1/client/orders'
                                ),
                            },
                            'output': {
                                'tvm-service': 'mock',
                                'upstream': {'$mockserver': ''},
                            },
                            'proxy': {'proxy-401': True},
                        },
                    ],
                )
            ),
            id='proxy 401 enabled',
        ),
    ],
)
async def test_headers_with_404_response_from_eats_partners(
        taxi_eats_restapp_authproxy,
        taxi_eats_restapp_authproxy_monitor,
        mockserver,
        mock_eats_restapp_authorizer,
        mock_access_control,
        mock_return_partner_info_404,
        status_code,
):
    @mockserver.json_handler('/4.0/restapp-front/api/v1/client/orders/search')
    def _mock_backend(request):
        assert request.headers['X-YaEda-PartnerId'] == '41'
        return mockserver.make_response(status=200, json={'status': 'success'})

    metrics_before_test = await taxi_eats_restapp_authproxy_monitor.get_metric(
        'proxy',
    )

    response = await request_proxy(
        taxi_eats_restapp_authproxy,
        token='token',
        url='/4.0/restapp-front/api/v1/client/orders/search',
    )
    assert response.status_code == status_code

    metrics_after_test = await taxi_eats_restapp_authproxy_monitor.get_metric(
        'proxy',
    )

    actual_metrics = get_actual_metrics(
        metrics_before_test['auth-result'], metrics_after_test['auth-result'],
    )
    assert not actual_metrics['auth-ok']
    assert not actual_metrics['auth-fail-no-prefix']
    assert not actual_metrics['auth-fail-access-denied']
    assert not actual_metrics['auth-fail-unexpected-error']


async def test_headers_with_500_response_from_eats_partners(
        taxi_eats_restapp_authproxy,
        taxi_eats_restapp_authproxy_monitor,
        mockserver,
        mock_eats_restapp_authorizer,
        mock_access_control,
        mock_return_partner_info_500,
):
    metrics_before_test = await taxi_eats_restapp_authproxy_monitor.get_metric(
        'proxy',
    )

    response = await request_proxy(
        taxi_eats_restapp_authproxy,
        token='token',
        url='/4.0/restapp-front/api/v1/client/orders/search',
    )
    assert response.status_code == 500

    metrics_after_test = await taxi_eats_restapp_authproxy_monitor.get_metric(
        'proxy',
    )

    actual_metrics = get_actual_metrics(
        metrics_before_test['auth-result'], metrics_after_test['auth-result'],
    )
    assert not actual_metrics['auth-ok']
    assert not actual_metrics['auth-fail-no-prefix']
    assert not actual_metrics['auth-fail-access-denied']
    assert actual_metrics['auth-fail-unexpected-error'] == 1


ROUTE_RULE_FOR_LOGOUT = [
    {
        'input': {
            'http-path-prefix': '/4.0/restapp-front/api/v1/client/logout',
        },
        'output': {'tvm-service': 'mock', 'upstream': {'$mockserver': ''}},
        'proxy': {'additional-headers-to-proxy': ['X-Token']},
    },
]


@pytest.mark.config(EATS_RESTAPP_AUTHPROXY_ROUTE_RULES=ROUTE_RULE_FOR_LOGOUT)
async def test_headers_x_token_proxying_to_logout(
        taxi_eats_restapp_authproxy,
        taxi_eats_restapp_authproxy_monitor,
        mockserver,
        mock_eats_restapp_authorizer,
        mock_access_control,
        mock_return_partner_info_200,
):
    @mockserver.json_handler('/4.0/restapp-front/api/v1/client/logout')
    def _mock_backend(request):
        assert request.headers['X-YaEda-PartnerId'] == '41'
        assert 'X-Token' in request.headers

        return mockserver.make_response(status=200, json={'status': 'success'})

    response = await request_proxy(
        taxi_eats_restapp_authproxy,
        token='token',
        url='/4.0/restapp-front/api/v1/client/logout',
    )
    assert response.status_code == 200


async def test_partner_info_cache(
        taxi_eats_restapp_authproxy,
        mockserver,
        mocked_time,
        mock_eats_restapp_authorizer,
        mock_access_control,
):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/info')
    def _mock_response_200(request):
        payload = {
            'country_code': 'RU',
            'email': 'partner1@partner.com',
            'personal_email_id': '999',
            'id': 1,
            'is_blocked': False,
            'is_fast_food': False,
            'name': 'Партнер1',
            'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6332',
            'places': [123, 234, 343],
            'roles': [
                {'id': 1, 'slug': 'ROLE_ADMIN', 'title': 'admin'},
                {'id': 2, 'slug': 'ROLE_LOL', 'title': 'lol'},
            ],
            'timezone': 'Europe/Moscow',
        }
        assert request.args['resolve_personal'] == 'false'
        return mockserver.make_response(status=200, json={'payload': payload})

    @mockserver.json_handler('/4.0/restapp-front/api/v1/client/orders/search')
    def _mock_backend(request):
        assert request.headers['X-YaEda-PartnerId'] == '41'
        return mockserver.make_response(status=200, json={'status': 'success'})

    time1 = pytz.utc.localize(mocked_time.now())

    response = await request_proxy_wo_cache_inval(
        taxi_eats_restapp_authproxy,
        token='token',
        url='/4.0/restapp-front/api/v1/client/orders/search',
    )

    assert response.status_code == 200
    assert _mock_response_200.times_called == 1

    mocked_time.sleep(20)
    time2 = pytz.utc.localize(mocked_time.now())

    response = await request_proxy_wo_cache_inval(
        taxi_eats_restapp_authproxy,
        token='token',
        url='/4.0/restapp-front/api/v1/client/orders/search',
    )

    assert time2 != time1
    assert response.status_code == 200
    assert _mock_response_200.times_called == 1

    mocked_time.sleep(41)
    time3 = pytz.utc.localize(mocked_time.now())

    response = await request_proxy_wo_cache_inval(
        taxi_eats_restapp_authproxy,
        token='token',
        url='/4.0/restapp-front/api/v1/client/orders/search',
    )

    assert time3 != time2
    assert response.status_code == 200
    assert _mock_response_200.times_called == 2


@pytest.mark.parametrize(
    'accept_language,x_language,expected_locale',
    [
        pytest.param(None, None, None, id='no locale'),
        pytest.param('kk-KZ', None, 'kk', id='Accept-Language only'),
        pytest.param(None, 'kk', 'kk', id='X-Language only'),
        pytest.param('hy-AM', 'kk', 'kk', id='Accept-Language and X-Language'),
    ],
)
async def test_headers_with_locale(
        taxi_eats_restapp_authproxy,
        mockserver,
        mock_eats_restapp_authorizer,
        mock_access_control,
        accept_language,
        x_language,
        expected_locale,
):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/info')
    def _mock_response_200(request):
        payload = {
            'country_code': 'RU',
            'email': 'partner1@partner.com',
            'id': 1,
            'is_blocked': False,
            'is_fast_food': False,
            'name': 'Партнер1',
            'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6332',
            'places': [123],
            'roles': [
                {'id': 1, 'slug': 'ROLE_ADMIN', 'title': 'admin'},
                {'id': 2, 'slug': 'ROLE_LOL', 'title': 'lol'},
            ],
            'personal_email_id': '999',
            'timezone': 'Europe/Moscow',
        }
        return mockserver.make_response(status=200, json={'payload': payload})

    @mockserver.json_handler('/4.0/restapp-front/api/v1/client/orders/search')
    def _mock_backend(request):
        if not accept_language and not x_language:
            assert 'X-YaEda-Partner-Locale' not in request.headers
        else:
            assert request.headers['X-YaEda-Partner-Locale'] == expected_locale

        return mockserver.make_response(status=200, json={'status': 'success'})

    response = await request_proxy_with_locale(
        taxi_eats_restapp_authproxy,
        accept_language,
        x_language,
        url='/4.0/restapp-front/api/v1/client/orders/search',
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    'roles,expected_permissions',
    [
        pytest.param([], '', id='no roles'),
        pytest.param(
            [{'id': 1, 'slug': 'ROLE_OPERATOR', 'title': 'operator'}],
            'permission.restaurant.functionality,'
            + 'permission.communications.read',
            id='single role',
        ),
        pytest.param(
            [
                {'id': 1, 'slug': 'ROLE_OPERATOR', 'title': 'operator'},
                {'id': 2, 'slug': 'ROLE_MANAGER', 'title': 'manager'},
            ],
            'permission.restaurant.menu,permission.orders.active,'
            + 'permission.restaurant.functionality,'
            + 'permission.communications.read',
            id='multiple roles',
        ),
    ],
)
async def test_headers_with_roles(
        taxi_eats_restapp_authproxy,
        mockserver,
        mock_eats_restapp_authorizer,
        mock_access_control,
        roles,
        expected_permissions,
):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/info')
    def _mock_response_200(request):
        payload = {
            'country_code': 'RU',
            'email': 'partner1@partner.com',
            'id': 1,
            'is_blocked': False,
            'is_fast_food': False,
            'name': 'Партнер1',
            'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6332',
            'places': [123],
            'roles': roles,
            'personal_email_id': '999',
            'timezone': 'Europe/Moscow',
        }
        return mockserver.make_response(status=200, json={'payload': payload})

    @mockserver.json_handler('/4.0/restapp-front/api/v1/client/orders/search')
    def _mock_backend(request):
        assert 'X-YaEda-Partner-Permissions' in request.headers
        assert (
            request.headers['X-YaEda-Partner-Permissions']
            == expected_permissions
        )

        return mockserver.make_response(status=200, json={'status': 'success'})

    response = await request_proxy(
        taxi_eats_restapp_authproxy,
        'token',
        url='/4.0/restapp-front/api/v1/client/orders/search',
    )

    assert response.status_code == 200


async def test_partner_info_personal_flag(
        taxi_eats_restapp_authproxy,
        mockserver,
        mocked_time,
        mock_eats_restapp_authorizer,
        mock_access_control,
):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/info')
    def _mock_response_200(request):
        payload = {
            'country_code': 'RU',
            'email': '',
            'id': 1,
            'is_blocked': False,
            'is_fast_food': False,
            'name': 'Партнер1',
            'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6332',
            'places': [123],
            'roles': [
                {'id': 1, 'slug': 'ROLE_ADMIN', 'title': 'admin'},
                {'id': 2, 'slug': 'ROLE_LOL', 'title': 'lol'},
            ],
            'personal_email_id': '999',
            'timezone': 'Europe/Moscow',
        }

        return mockserver.make_response(status=200, json={'payload': payload})

    @mockserver.json_handler('/4.0/restapp-front/api/v1/client/orders/search')
    def _mock_backend(request):
        assert request.headers['X-YaEda-PartnerId'] == '41'
        return mockserver.make_response(status=200, json={'status': 'success'})

    response = await request_proxy_wo_cache_inval(
        taxi_eats_restapp_authproxy,
        token='token',
        url='/4.0/restapp-front/api/v1/client/orders/search',
    )

    assert response.status_code == 200
    assert _mock_response_200.times_called == 1
