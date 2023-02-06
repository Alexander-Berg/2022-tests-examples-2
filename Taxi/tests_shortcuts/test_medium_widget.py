# pylint: disable=too-many-lines
import pytest

from tests_shortcuts import consts
from tests_shortcuts import helpers


@pytest.mark.translations(
    client_messages={'default_title_key': {'ru': 'default_translated_title'}},
)
async def test_medium_widget(
        taxi_shortcuts, add_experiment, add_appearance_experiments,
):
    add_appearance_experiments(with_attributed_title=False)
    add_experiment(
        consts.SUPERAPP_MEDIUM_WIDGET_OVERRIDES,
        {
            'taxi:route-input': {
                'deeplink': 'yandextaxi://route?expandingState=expanded',
            },
            'taxi:expected-destination': {
                'icon_tag': 'custom_shortcut_default_tag',
            },
            'taxi:expected-destination_userplace_home': {
                'icon_tag': 'custom_shortcut_userplace_home_tag',
            },
            'taxi:expected-destination_icon_app_shortcut_poi_airport': {
                'icon_tag': 'custom_shortcut_airport_tag',
            },
            'market': {
                'deeplink': 'yandextaxi://market',
                'icon_tag': 'market_override_icon_tag',
            },
        },
    )

    env = helpers.EnvSetup()
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT,
        {
            'bricks': {
                'enabled': True,
                'priority': ['taxi_route_input'],
                'layout_options': {'1': [6]},
            },
            'buttons': {
                'enabled': True,
                'priority': [
                    'eats_based_grocery',
                    'eats_based_eats',
                    'discovery_scooters',
                    'market',
                ],
                'show_from': 1,
            },
        },
    )

    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
        supported_actions=env.all_supported_actions,
    )

    payload['grid'] = helpers.make_payload_with_shortcuts(
        [
            consts.DEFAULT_TAXI_SHORTCUT,
            consts.DEFAULT_EATS_SHORTCUT,
            consts.DEFAULT_TAXI_USERLACE_HOME_SHORTCUT,
            consts.DEFAULT_TAXI_AIRPORT_SHORTCUT,
            consts.DEFAULT_GROCERY_SHORTCUT,
        ],
    )['grid']

    response = await taxi_shortcuts.post(consts.MEDIUM_WIDGET_URL, payload)
    assert response.status_code == 200
    response_body = response.json()

    expected_response_body = {
        'header': {
            'deeplink': 'yandextaxi://route?expandingState=expanded',
            'icon_tag': 'default_icon_tag',
            'title': 'default_translated_title',
        },
        'services': [
            {
                'deeplink': 'default_deeplink',
                'icon_tag': 'default_icon_tag',
                'service': 'grocery',
                'title': 'default_translated_title',
            },
            {
                'deeplink': 'default_deeplink',
                'icon_tag': 'default_icon_tag',
                'service': 'eats',
                'title': 'default_translated_title',
            },
            {
                'deeplink': 'yandextaxi://market',
                'icon_tag': 'market_override_icon_tag',
                'service': 'market',
                'title': 'default_translated_title',
            },
        ],
        'shortcuts': [
            {
                'deeplink': (
                    'yandextaxi://route?end-lat=2.000000&end-lon=1.000000'
                ),
                'icon_tag': 'custom_shortcut_default_tag',
                'title': 'Работа',
            },
            {
                'deeplink': (
                    'yandextaxi://route?end-lat=55.500000&end-lon=37.500000'
                ),
                'icon_tag': 'custom_shortcut_userplace_home_tag',
                'title': 'Home',
            },
            {
                'deeplink': (
                    'yandextaxi://route?end-lat=56.000000&end-lon=38.000000'
                ),
                'icon_tag': 'custom_shortcut_airport_tag',
                'title': 'Airport',
            },
        ],
    }

    assert response_body == expected_response_body
