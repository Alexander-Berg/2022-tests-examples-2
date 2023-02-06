import copy

import pytest


URL = 'v1/widgets'


def get_headers(locale='ru', app_name=None):
    if app_name is None:
        app_name = 'android'
    return {
        'X-Yandex-Uid': '4003514353',
        'X-Remote-IP': '127.0.0.1',
        'X-Request-Language': locale,
        'X-Request-Application': f'app_name={app_name}',
    }


DEFAULT_WIDGETS = [
    {
        'id': '94a60c5ec82947c0a7252fa2c1c254ef',
        'title': 'Домой',
        'subtitle': '',
        'background': {'color': 'F5F2E4'},
        'overlays': [
            {
                'shape': 'poi',
                'image_tag': 'custom_shortcut_home_userplace_tag',
                'background': {'color': 'C4BFA7'},
            },
        ],
        'action': {
            'type': 'deeplink',
            'deeplink': (
                'yandextaxi://route?end-lat=55.793024&end-lon=37.971913'
            ),
        },
    },
]
DEFAULT_USER_STATE = {'selected_class': 'econom'}
DEFAULT_PRICE_INFO = {
    'categories': {
        'econom': {
            'fixed_price': True,
            'user': {
                'price': {'total': 3111.0},
                'trip_information': {'time': 600.0},
            },
            'currency': {'name': 'RUB', 'symbol': '₽', 'fraction_digits': 0},
        },
    },
}

DEFAULT_WIDGET = {
    'action': {
        'deeplink': 'yandextaxi://route?end-lat=55.793024&end-lon=37.971913',
        'type': 'deeplink',
    },
    'background': {'color': 'F5F2E4'},
    'id': '94a60c5ec82947c0a7252fa2c1c254ef',
    'overlays': [
        {
            'background': {'color': 'C4BFA7'},
            'image_tag': 'custom_shortcut_home_userplace_tag',
            'shape': 'poi',
        },
    ],
    'subtitle': '~3111 $SIGN$$CURRENCY$, 10 мин',
    'title': 'Домой',
}

DEFAULT_WIDGET_WITHOUT_PRICE = copy.deepcopy(DEFAULT_WIDGET)
DEFAULT_WIDGET_WITHOUT_PRICE['subtitle'] = ''


def _make_request(widgets, price_info):
    request = {'state': DEFAULT_USER_STATE}
    if price_info is not None:
        request['pricing_info'] = price_info
    if widgets is not None:
        request['widgets'] = widgets

    return request


def _make_expected_response(widgets):
    return {
        'currency_rules': {
            'code': 'RUB',
            'sign': '₽',
            'template': '$VALUE$ $SIGN$$CURRENCY$',
            'text': 'руб.',
        },
        'typed_experiments': {'items': [], 'version': 0},
        'widgets': widgets,
    }


@pytest.mark.parametrize(
    'request_body, expected_status, expected_response',
    [
        (
            _make_request(
                widgets=DEFAULT_WIDGETS, price_info=DEFAULT_PRICE_INFO,
            ),
            200,
            _make_expected_response(widgets=[DEFAULT_WIDGET]),
        ),
        (
            _make_request(widgets=[], price_info=DEFAULT_PRICE_INFO),
            200,
            _make_expected_response(widgets=[]),
        ),
        (
            _make_request(
                widgets=DEFAULT_WIDGETS, price_info={'categories': {}},
            ),
            200,
            _make_expected_response(widgets=[DEFAULT_WIDGET_WITHOUT_PRICE]),
        ),
        (
            _make_request(widgets=DEFAULT_WIDGETS, price_info=None),
            200,
            _make_expected_response(widgets=[DEFAULT_WIDGET_WITHOUT_PRICE]),
        ),
    ],
)
@pytest.mark.translations(
    tariff={'currency_with_sign.default': {'en': '$VALUE$ $SIGN$$CURRENCY$'}},
    client_messages={
        'shortcuts.route_eta.round.hours_minutes': {
            'ru': '%(hours).0f ч %(minutes).0f мин',
        },
        'shortcuts.route_eta.round.hours': {'ru': '%(value).0f ч'},
        'shortcuts.route_eta.round.tens_minutes': {'ru': '%(value).0f мин'},
    },
)
@pytest.mark.config(SHORTCUTS_SUBTITLE_ETA_FORMAT='like-routestats')
async def test_v1_widgets_simple_request(
        taxi_shortcuts, request_body, expected_status, expected_response,
):
    locale = 'ru'
    response = await taxi_shortcuts.post(
        URL, request_body, headers=get_headers(locale),
    )
    assert response.status_code == expected_status
    if expected_status != 200:
        return

    data = response.json()
    assert data == expected_response
