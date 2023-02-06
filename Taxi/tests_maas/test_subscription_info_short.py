import datetime
from typing import Optional

import pytest

TRANSLATIONS = {
    'maas.menu.title_buy_subscription': {'en': 'buy subscription'},
    'maas.menu.title_view_subscription_info': {'en': 'view subscription'},
    'maas.menu.subscription_expiration_day': {
        'en': 'expired at %(expiration_day)s',
    },
    'maas.subscription_info_ui.trips_info': {'en': '%(trips_left)s trips'},
    'maas.menu.subscription_expired': {'en': 'expired'},
}


def get_expiration_day():
    time = datetime.datetime.now() + datetime.timedelta(days=1)
    return time.strftime('%d.%m.%y')


def get_active_response(trips_count=None):
    response = {
        'coupon_id': 'coupon_id',
        'menu_button': {
            'expiring_info': f'expired at {get_expiration_day()}',
            'title': 'view subscription',
            'webview_url': (
                'https://ya-authproxy.taxi.yandex.ru/webview/maas/info'
            ),
        },
    }
    if trips_count is not None:
        response['menu_button']['trips_info'] = f'{trips_count} trips'
    return response


def get_expired_response():
    return {
        'menu_button': {
            'expiring_info': f'expired',
            'title': 'view subscription',
            'webview_url': (
                'https://ya-authproxy.taxi.yandex.ru/webview/maas/info'
            ),
        },
    }


def get_promotion_response():
    return {
        'menu_button': {
            'title': 'buy subscription',
            'webview_url': (
                'https://ya-authproxy.taxi.yandex.ru/webview/maas/checkout'
            ),
        },
    }


@pytest.fixture(name='make_request')
def _make_request(taxi_maas):
    async def _request(phone_id: str):
        headers = {
            'X-YaTaxi-PhoneId': phone_id,
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-Uid': 'yandex_uid',
            'X-Request-Language': 'en',
        }
        response = await taxi_maas.post(
            '/4.0/maas/v1/subscription/info/short', headers=headers,
        )
        assert response.status_code == 200

        return response

    return _request


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.experiments3(filename='maas_user_promotion_exp.json')
@pytest.mark.parametrize(
    'phone_id, expected_response',
    (
        pytest.param(
            'no_subscription_no_promo', {}, id='no_subscription_no_promo',
        ),
        pytest.param('reserved_id', {}, id='reserved_subscription'),
        pytest.param('canceled_id', {}, id='canceled_subscription'),
        pytest.param(
            'expired_no_promo_id', {}, id='expired_no_promo_subscription',
        ),
        pytest.param(
            'active_expired_no_promo_id',
            {},
            id='expired_no_promo_subscription',
        ),
        pytest.param(
            'expired_id', get_expired_response(), id='expired_subscription',
        ),
        pytest.param(
            'active_expired_id',
            get_expired_response(),
            id='active_expired_subscription',
        ),
        pytest.param(
            'promoted_id',
            get_promotion_response(),
            id='promoted_subscription',
        ),
        pytest.param(
            'promoted_reserved_id',
            get_promotion_response(),
            id='promoted_reserved_subscription',
        ),
        pytest.param(
            'promoted_canceled_id',
            get_promotion_response(),
            id='promoted_canceled_subscription',
        ),
    ),
)
async def test_main(
        make_request, coupon_state_mock, phone_id, expected_response,
):
    coupon_state_mock(phone_id)

    response = await make_request(phone_id)
    assert response.json() == expected_response


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.experiments3(filename='maas_user_promotion_exp.json')
@pytest.mark.parametrize(
    ('trips_count', 'error_code'),
    (
        pytest.param(6, None, id='6 trips'),
        pytest.param(0, None, id='0 trips'),
        pytest.param(None, 404, id='coupons 404 response'),
        pytest.param(None, 429, id='coupons 429 response'),
        pytest.param(None, 500, id='coupons 500 response'),
    ),
)
async def test_active(
        make_request,
        coupon_state_mock,
        trips_count: Optional[int],
        error_code: Optional[int],
):
    phone_id = 'active_id'
    coupon_state_mock(phone_id, trips_count, error_code)

    response = await make_request(phone_id)
    expected_response = get_active_response(trips_count)
    assert response.json() == expected_response
