import copy
import datetime

import pytest

from tests_plus_sweet_home import constants

# pylint: disable=invalid-name
pytestmark = [pytest.mark.experiments3(filename='experiments3_defaults.json')]

HEADERS = {
    'X-SDK-Client-ID': 'taxi.test',
    'X-SDK-Version': '10.10.10',
    'X-Yandex-UID': '111111',
    'X-YaTaxi-Pass-Flags': 'portal,cashback-plus',
    'X-Request-Language': 'ru',
    'X-Remote-IP': '185.15.98.233',
}

SUBSCRIPTION_WITH_SUCCESS_SCREEN = 'ya_plus_rus_v2'


@pytest.mark.parametrize(
    'subscription_id, is_success_screen_expected',
    [
        (SUBSCRIPTION_WITH_SUCCESS_SCREEN, True),
        ('ya_plus_rus_v2_trial', False),
    ],
)
@pytest.mark.experiments3(filename='exp3-success_screen.json')
async def test_success_screen(
        taxi_plus_sweet_home,
        mockserver,
        load_json,
        subscription_id: str,
        is_success_screen_expected: bool,
):
    @mockserver.json_handler('/fast-prices/billing/transitions')
    def _mock_transitions(request):
        product = constants.SUBSCRIPTION_TO_PRODUCT_MAPPING[subscription_id]
        return {
            'transitions': [
                {
                    'available': True,
                    'product': {'id': product, 'vendor': 'YANDEX'},
                    'transitionType': 'SUBMIT',
                },
            ],
        }

    headers = copy.deepcopy(HEADERS)
    headers['X-Yandex-UID'] = 'yandex_uid:success_screen_enabled'

    response = await taxi_plus_sweet_home.post(
        '/4.0/sweet-home/v2/sdk-state',
        json={'include': ['state']},
        headers=headers,
    )

    assert response.status_code == 200
    content = response.json()

    if not is_success_screen_expected:
        assert 'typed_experiments' not in content
        return

    assert 'typed_experiments' in content
    typed_experiments = content['typed_experiments']
    assert typed_experiments['version'] == 10

    assert len(typed_experiments['items']) == 1
    success_screen_value = load_json('expected_success_screen_value.json')
    assert typed_experiments['items'][0] == success_screen_value


@pytest.mark.parametrize('locale', ['en', ''])
@pytest.mark.experiments3(filename='exp3-success_screen.json')
async def test_locale(
        taxi_plus_sweet_home, mockserver, load_json, locale: str,
):
    @mockserver.json_handler('/fast-prices/billing/transitions')
    def _mock_transitions(request):
        product = constants.SUBSCRIPTION_TO_PRODUCT_MAPPING[
            SUBSCRIPTION_WITH_SUCCESS_SCREEN
        ]
        return {
            'transitions': [
                {
                    'available': True,
                    'product': {'id': product, 'vendor': 'YANDEX'},
                    'transitionType': 'SUBMIT',
                },
            ],
        }

    headers = copy.deepcopy(HEADERS)
    headers['X-Yandex-UID'] = 'yandex_uid:success_screen_enabled'
    headers['X-Request-Language'] = locale

    response = await taxi_plus_sweet_home.post(
        '/4.0/sweet-home/v2/sdk-state',
        json={'include': ['state']},
        headers=headers,
    )

    assert response.status_code == 200
    content = response.json()

    assert 'typed_experiments' in content
    typed_experiments = content['typed_experiments']
    assert typed_experiments['version'] == 10

    assert len(typed_experiments['items']) == 1

    if locale == 'en':
        success_screen_value = load_json(
            'expected_success_screen_value_en.json',
        )
        assert typed_experiments['items'][0] == success_screen_value
        return

    success_screen_value = load_json('expected_success_screen_value.json')
    assert typed_experiments['items'][0] == success_screen_value


@pytest.mark.parametrize(
    'end_subscription,is_experiment_expected,order_type',
    [
        (
            (
                datetime.datetime.utcnow() + datetime.timedelta(days=40)
            ).strftime('%Y-%m-%dT%H:%M:%SZ'),
            False,
            'native-auto-subscription',
        ),
        ('2021-06-22T13:11:15Z', True, 'native-auto-subscription'),
        ('2021-06-22T13:11:15Z', False, 'some_order_type'),
    ],
)
@pytest.mark.experiments3(
    filename='exp3-sweet_home_subscription_unbinding_card.json',
)
async def test_sweet_home_subscription_unbinding_card(
        taxi_plus_sweet_home,
        mockserver,
        load_json,
        end_subscription,
        is_experiment_expected,
        order_type,
):
    @mockserver.json_handler('/fast-prices-notify/billing/user/state')
    def _mock_transitions(request):
        return {
            'uid': 111111,
            'activeIntervals': [
                {
                    'featureBundle': 'new-plus',
                    'orderType': order_type,
                    'end': end_subscription,
                },
            ],
        }

    headers = copy.deepcopy(HEADERS)
    headers['X-Yandex-UID'] = 'yandex_uid:success_screen_enabled'
    headers['X-YaTaxi-Pass-Flags'] = 'portal,cashback-plus,ya-plus'

    response = await taxi_plus_sweet_home.post(
        '/4.0/sweet-home/v2/sdk-state',
        json={
            'include': ['state'],
            'geo_state': {'accuracy': 0, 'location': [37.5, 55.8]},  # Moscow
        },
        headers=headers,
    )

    assert response.status_code == 200
    content = response.json()

    if not is_experiment_expected:
        assert 'typed_experiments' not in content
        return

    assert 'typed_experiments' in content
    typed_experiments = content['typed_experiments']
    assert typed_experiments['version'] == 10

    assert len(typed_experiments['items']) == 1
    subscription_unbinding_card_value = load_json(
        'expected_unbinding_card_value.json',
    )

    assert typed_experiments['items'][0] == subscription_unbinding_card_value
