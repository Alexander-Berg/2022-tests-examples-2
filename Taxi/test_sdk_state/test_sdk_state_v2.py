import pytest

from tests_plus_sweet_home import constants

HEADERS = {
    'X-SDK-Client-ID': 'taxi.test',
    'X-SDK-Version': '10.10.10',
    'X-Yandex-UID': '111111',
    'X-YaTaxi-Pass-Flags': 'portal,cashback-plus',
    'X-Request-Language': 'ru',
    'X-Remote-IP': '185.15.98.233',
}


@pytest.mark.tariff_settings(filename='tariff_settings.json')
@pytest.mark.experiments3(filename='necessary_exps3.json')
@pytest.mark.parametrize(
    'remote_ip, is_exp_enabled, expected_curr_rules',
    [
        # exp disabled
        ('185.15.98.233', False, {'code': 'RUB', 'text': 'руб.'}),
        ('37.151.221.0', False, {'code': 'RUB', 'text': 'руб.'}),
        ('74.68.76.35', False, {'code': 'RUB', 'text': 'руб.'}),
        # exp enabled
        ('185.15.98.233', True, {'code': 'KZT', 'text': 'т'}),
        ('37.151.221.0', True, {'code': 'KZT', 'text': 'т'}),
        ('74.68.76.35', True, {'code': 'KZT', 'text': 'т'}),
    ],
)
async def test_enable_plus_sweet_home_under_cashback_international_experiment(
        taxi_plus_sweet_home,
        load_json,
        experiments3,
        remote_ip,
        is_exp_enabled,
        expected_curr_rules,
):
    zone_name = 'astana'  # Kazakhstan
    geo_point = [37.5, 55.8]  # Moscow

    body = {
        'include': ['menu'],
        'geo_state': {
            'accuracy': 10,
            'location': geo_point,
            'zone_name': zone_name,
        },
        'supported_features': [{'type': 'qr'}],
    }

    HEADERS['X-Remote-IP'] = remote_ip

    if is_exp_enabled:
        experiments3.add_experiments_json(
            load_json('exp3-cashback-for-plus-international.json'),
        )
        await taxi_plus_sweet_home.invalidate_caches()

    response = await taxi_plus_sweet_home.post(
        '/4.0/sweet-home/v2/sdk-state', headers=HEADERS, json=body,
    )

    assert response.status_code == 200

    context = response.json()

    menu_context = context.get('menu')
    assert menu_context

    currency_rules = menu_context.get('currency_rules')
    assert currency_rules

    curr_rules_to_assert = {
        'code': currency_rules['code'],
        'text': currency_rules['text'],
    }
    assert curr_rules_to_assert == expected_curr_rules


@pytest.mark.tariff_settings(filename='tariff_settings.json')
@pytest.mark.experiments3(filename='necessary_exps3.json')
@pytest.mark.experiments3(filename='exp3-cashback-for-plus-international.json')
@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={
        'ru': ['ya_plus_rus_v2'],
        'kz': ['ya_plus_rus_v2'],
    },
)
@pytest.mark.parametrize(
    'remote_ip, zone, is_divergence, is_v2',
    [
        # /4.0/sweet-home/v1/sdk-state
        ('185.15.98.233', 'astana', True, True),
        ('37.151.221.0', 'astana', False, True),
        ('74.68.76.35', 'moscow', True, True),
        ('185.15.98.233', 'moscow', False, True),
        # /4.0/sweet-home/v2/sdk-state
        ('185.15.98.233', 'astana', True, False),
        ('37.151.221.0', 'astana', False, False),
        ('74.68.76.35', 'moscow', True, False),
        ('185.15.98.233', 'moscow', False, False),
    ],
)
async def test_hide_action_button(
        taxi_plus_sweet_home, remote_ip, zone, is_divergence, is_v2,
):
    body = {
        'include': ['menu'],
        'geo_state': {'accuracy': 10, 'zone_name': zone},
    }

    if is_v2:
        body['supported_features'] = [{'type': 'inapp_purchases:plus'}]

    HEADERS['X-Remote-IP'] = remote_ip
    url = (
        '/4.0/sweet-home/v2/sdk-state'
        if is_v2
        else '/4.0/sweet-home/v1/sdk-state'
    )

    response = await taxi_plus_sweet_home.post(url, headers=HEADERS, json=body)

    assert response.status_code == 200

    context = response.json()

    menu_context = context.get('menu')
    assert menu_context

    action_button = menu_context.get('action_button')

    if is_divergence:
        assert not action_button
    else:
        assert action_button


@pytest.mark.experiments3(filename='necessary_exps3.json')
@pytest.mark.parametrize(
    'remote_ip, zone, is_forcing, is_mismatch',
    [
        # forcing enabled
        ('185.15.98.233', 'astana', True, True),
        ('37.151.221.0', 'astana', True, False),
        ('37.151.221.0', 'moscow', True, True),
        ('185.15.98.233', 'moscow', True, False),
        # forcing disabled
        ('185.15.98.233', 'astana', False, True),
        ('37.151.221.0', 'astana', False, False),
        ('37.151.221.0', 'moscow', False, True),
        ('185.15.98.233', 'moscow', False, False),
    ],
)
async def test_forcing_native_home(
        taxi_plus_sweet_home,
        taxi_config,
        remote_ip,
        zone,
        is_forcing,
        is_mismatch,
):
    body = {
        'include': ['menu'],
        'geo_state': {'accuracy': 10, 'zone_name': zone},
    }
    HEADERS['X-Remote-IP'] = remote_ip

    taxi_config.set_values(
        {
            'SWEET_HOME_MENU_GLOBAL_CONFIG': {
                'enabled': True,
                'menu_type': 'WEBVIEW',
                'webview_params': {
                    'url': 'https://plus-test.yandex.ru/home-sdk-test/?',
                    'need_authorization': True,
                },
                'force_native_on_country_mismatch': is_forcing,
            },
        },
    )

    response = await taxi_plus_sweet_home.post(
        '/4.0/sweet-home/v2/sdk-state', headers=HEADERS, json=body,
    )

    assert response.status_code == 200

    context = response.json()
    menu = context.get('menu')
    assert menu

    assert (
        context['menu_type'] == 'NATIVE'
        if is_forcing and is_mismatch
        else 'WEBVIEW'
    )


@pytest.mark.experiments3(filename='necessary_exps3.json')
async def test_rounding_factor(taxi_plus_sweet_home, mockserver):
    @mockserver.json_handler('/plus-wallet/v1/balances')
    def _mock_balances(request):
        req_query = request.query
        rounding_factor = req_query.get('rounding_factor')

        assert rounding_factor
        assert rounding_factor == 'wallet_show_balance'

        return {
            'balances': [
                {
                    'balance': constants.DEFAULT_BALANCE,
                    'currency': constants.DEFAULT_CURRENCY,
                    'wallet_id': constants.DEFAULT_WALLET_ID,
                },
            ],
        }

    body = {'include': ['state']}

    response = await taxi_plus_sweet_home.post(
        '/4.0/sweet-home/v2/sdk-state', headers=HEADERS, json=body,
    )

    assert response.status_code == 200

    context = response.json()
    state = context.get('state')
    assert state
