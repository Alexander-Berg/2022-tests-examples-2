from typing import List
from typing import Optional

import pytest


PA_HEADERS = {
    'X-YaTaxi-UserId': 'user_id',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=iphone',
    'X-AppMetrica-DeviceId': 'DeviceId',
}
WEATHER_ICON = 'overcast'
TRAFFIC_ICON = 'traffic_icon'


def get_widget(
        balance: int,
        trend_time_delta_sec: Optional[int] = None,
        icons_to_remove: Optional[List[str]] = None,
):
    icons = ['aico-normal', 'aico-to-replace', WEATHER_ICON, TRAFFIC_ICON]
    if icons_to_remove:
        icons = [icon for icon in icons if icon not in icons_to_remove]
    result: dict = {
        'type': 'test',
        'content': {
            'additional_icons': icons,
            'balance': {
                'leading_icon': 'surge_widget_leading_icon_default',
                'trail_icon': 'surge_widget_trail_icon_default',
                'value_icon': 'surge_widget_value_icon_default',
                'color': '#E0DEDA',
                'balance': balance,
            },
        },
        'accessibility_info': {
            'hint': 'Это виджет',
            'label': 'Это надпись виджета',
            'value': 'Это значение виджета',
        },
        'payload': {
            'balance': balance,
            'surge_color': '#E0DEDA',
            'traffic': {'icon': 'traffic_icon', 'traffic_score': 10},
            'weather': {'condition': 'overcast', 'icon': 'overcast'},
            'trend_type': 'good_trend',
        },
    }

    if trend_time_delta_sec:
        result['payload']['trend_time_delta_sec'] = trend_time_delta_sec

    return result


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.experiments3(filename='exp_surge_widget.json')
@pytest.mark.translations(
    client_messages={
        'surge_widget_hint': {'ru': 'Это виджет'},
        'surge_widget_label': {'ru': 'Это надпись виджета'},
        'surge_widget_value': {'ru': 'Это значение виджета'},
    },
)
async def test_plugin_widget(
        taxi_routestats, mockserver, experiments3, load_json,
):
    experiments3.add_config(**load_json('cfg_widget.json'))
    experiments3.add_config(**load_json('cfg_widget_weather.json'))
    await taxi_routestats.invalidate_caches()

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response.json'),
        }

    @mockserver.json_handler('/weather/graphql/query')
    def _weather(request):
        assert request.json['query'] == (
            '{weatherByPoint(request: { lat: 55.733393, lon: 37.587569 }) {'
            ' now { condition icon(format: PNG_128) } } }'
        )
        return {
            'data': {
                'weatherByPoint': {
                    'now': {
                        'condition': 'overcast',
                        'icon': (
                            'https://yastatic.net/weather/i/icons/funky'
                            '/png/dark/128/ovc.png'
                        ),
                    },
                },
            },
        }

    response = await taxi_routestats.post(
        'v1/routestats', load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200

    surges = [
        sl['paid_options']['value'] if 'paid_options' in sl else None
        for sl in response.json()['service_levels']
    ]
    assert surges == [None, 1.3, 1.4, 1.5, 1.3, None, None, 0.9, None]

    widgets = [sl['widget'] for sl in response.json()['service_levels']]

    expected_widgets = [
        get_widget(0),
        get_widget(
            50,
            # trend for class 'econom' from internal data
            # services/routestats/testsuite/tests_routestats/static/default/internal_data.json
            99,
        ),
        # For case below special clause in exp with priority for weather
        get_widget(50, icons_to_remove=[TRAFFIC_ICON]),
        # For case below special clause in exp with priority for traffic
        get_widget(51, icons_to_remove=[WEATHER_ICON]),
        get_widget(50),
        get_widget(0),
        get_widget(0),
        get_widget(33),
        get_widget(0),
    ]

    for widget, expected_widget in zip(widgets, expected_widgets):
        assert widget == expected_widget

    alternative_opt = response.json()['alternatives']['options'][0]
    assert alternative_opt['type'] == 'explicit_antisurge'
    alt_widget = alternative_opt['service_levels'][0]['widget']
    assert alt_widget == get_widget(50, 99, icons_to_remove=[TRAFFIC_ICON])
