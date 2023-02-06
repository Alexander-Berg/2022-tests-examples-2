import pytest

from tests_shortcuts import consts
from tests_shortcuts import helpers


URL = '/v1/orders-tracking-widgets'


@pytest.fixture(autouse=True)
def _add_styles_config(taxi_config):
    taxi_config.set(
        EXTENDED_TEMPLATE_STYLES_MAP={
            'style': {
                'font_size': 20,
                'font_weight': 'bold',
                'meta_color': '#000000',
            },
            'order_card_subtitle': {'font_size': 16, 'font_weight': 'regular'},
        },
    )


@pytest.fixture(name='add_settings_exp')
def _add_settings_exp(add_experiment):
    def _wrapper(title_key, orders_selectors=None):
        orders_selectors = orders_selectors or [
            {'services': ['taxi', 'eats', 'market']},
        ]

        add_experiment(
            name='orders_tracking_widgets_settings',
            consumers=['shortcuts/orders_tracking_widgets'],
            value={
                'orders_selectors': orders_selectors,
                'collapse_groups': [
                    {
                        'id': 'eats&market',
                        'title_key': title_key,
                        'min_cards_count_to_collapse': 3,
                        'services': ['market', 'eats'],
                        'max_icons_count': 3,
                        'service_icons': {
                            'eats': 'eats_icon',
                            'market': 'market_icon',
                        },
                        'service_names': {
                            'eats': 'eats_key',
                            'market': 'market_key',
                        },
                    },
                ],
                'widgets_order': ['eats&market', 'taxi', 'market', 'eats'],
                'order_cards': {
                    'eats&market': {
                        'show_header': True,
                        'show_state_timeline': True,
                    },
                    'eats': {
                        'show_header': False,
                        'show_state_timeline': False,
                    },
                    'market': {
                        'show_header': False,
                        'show_state_timeline': True,
                    },
                },
                'long_tracking_overlay': {
                    'text_color': '#001122',
                    'background': {'color': '#FAFAFA'},
                },
            },
            predicates=[
                helpers.exp_create_eq_predicate(
                    'screen_type', 'on_multiorder',
                ),
            ],
        )

    return _wrapper


@pytest.mark.translations(
    client_messages={
        'market_orders_widget_title_key': {
            'ru': '<style>Ваши заказы маркета</style>',
        },
    },
)
async def test_fallback(taxi_shortcuts):
    request_body = {
        'screen_type': 'on_multiorder',
        'orders_info': [
            {'service': 'taxi', 'order_id': 'id1'},
            {'service': 'eats', 'order_id': 'id2'},
            {'service': 'eats', 'order_id': 'id3'},
            {'service': 'market', 'order_id': 'id4'},
            {'service': 'market', 'order_id': 'id5'},
        ],
    }
    response = await taxi_shortcuts.post(URL, request_body)
    assert response.status_code == 200
    response_body = response.json()

    expected_response_body = {
        'widgets': [
            {
                'type': 'order_widget',
                'id': 'id1',
                'payload': {'service': 'taxi', 'order_id': 'id1'},
            },
            {
                'type': 'order_widget',
                'id': 'id2',
                'payload': {'service': 'eats', 'order_id': 'id2'},
            },
            {
                'type': 'order_widget',
                'id': 'id3',
                'payload': {'service': 'eats', 'order_id': 'id3'},
            },
            {
                'type': 'orders_widget',
                'id': 'market_group_id',
                'payload': {
                    'orders': [
                        {'service': 'market', 'order_id': 'id4'},
                        {'service': 'market', 'order_id': 'id5'},
                    ],
                    'title': {
                        'items': [
                            {
                                'font_size': 20,
                                'font_weight': 'bold',
                                'meta_color': '#000000',
                                'text': 'Ваши заказы маркета',
                                'type': 'text',
                            },
                        ],
                    },
                },
            },
        ],
    }

    assert response_body == expected_response_body


@pytest.mark.translations(
    client_messages={
        'title_key': {'ru': '<style>У вас {orders_count} заказа</style>'},
        'market_key': {'ru': 'Маркет'},
        'eats_key': {'ru': 'Еда'},
    },
)
async def test_custom_settings(taxi_shortcuts, add_settings_exp):
    add_settings_exp(title_key='title_key')

    request_body = {
        'screen_type': 'on_multiorder',
        'orders_info': [
            {'service': 'delivery', 'order_id': 'id0'},
            {'service': 'taxi', 'order_id': 'id1'},
            {'service': 'eats', 'order_id': 'id2'},
            {'service': 'eats', 'order_id': 'id3'},
            {'service': 'market', 'order_id': 'id4'},
            {'service': 'market', 'order_id': 'id5'},
        ],
    }

    response = await taxi_shortcuts.post(URL, request_body)
    assert response.status_code == 200
    response_body = response.json()

    expected_response_body = {
        'widgets': [
            {
                'type': 'orders_widget',
                'id': 'eats&market',
                'payload': {
                    'orders': [
                        {
                            'service': 'market',
                            'order_id': 'id4',
                            'icon_tag': 'market_icon',
                            'order_card': {
                                'show_header': True,
                                'show_state_timeline': True,
                            },
                        },
                        {
                            'service': 'market',
                            'order_id': 'id5',
                            'icon_tag': 'market_icon',
                            'order_card': {
                                'show_header': True,
                                'show_state_timeline': True,
                            },
                        },
                        {
                            'service': 'eats',
                            'order_id': 'id2',
                            'icon_tag': 'eats_icon',
                            'order_card': {
                                'show_header': True,
                                'show_state_timeline': True,
                            },
                        },
                        {
                            'service': 'eats',
                            'order_id': 'id3',
                            'order_card': {
                                'show_header': True,
                                'show_state_timeline': True,
                            },
                        },
                    ],
                    'title': {
                        'items': [
                            {
                                'font_size': 20,
                                'font_weight': 'bold',
                                'meta_color': '#000000',
                                'text': 'У вас ',
                                'type': 'text',
                            },
                            {
                                'font_size': 20,
                                'font_weight': 'bold',
                                'meta_color': '#000000',
                                'text': '4',
                                'type': 'text',
                            },
                            {
                                'font_size': 20,
                                'font_weight': 'bold',
                                'meta_color': '#000000',
                                'text': ' заказа',
                                'type': 'text',
                            },
                        ],
                    },
                    'subtitle': {
                        'items': [
                            {
                                'font_size': 16,
                                'font_weight': 'regular',
                                'text': 'Маркет, Маркет, Еда',
                                'type': 'text',
                            },
                        ],
                    },
                },
            },
            {
                'type': 'order_widget',
                'id': 'id1',
                'payload': {'service': 'taxi', 'order_id': 'id1'},
            },
        ],
    }

    assert response_body == expected_response_body


async def test_group_does_not_collapse(taxi_shortcuts, add_settings_exp):
    add_settings_exp(title_key='title_key')

    request_body = {
        'screen_type': 'on_multiorder',
        'orders_info': [
            {'service': 'delivery', 'order_id': 'id0'},
            {'service': 'taxi', 'order_id': 'id1'},
            {'service': 'eats', 'order_id': 'id2'},
            {'service': 'market', 'order_id': 'id4'},
        ],
    }

    response = await taxi_shortcuts.post(URL, request_body)
    assert response.status_code == 200
    response_body = response.json()

    expected_response_body = {
        'widgets': [
            {
                'type': 'order_widget',
                'id': 'id1',
                'payload': {'service': 'taxi', 'order_id': 'id1'},
            },
            {
                'type': 'order_widget',
                'id': 'id4',
                'payload': {
                    'service': 'market',
                    'order_id': 'id4',
                    'order_card': {
                        'show_header': False,
                        'show_state_timeline': True,
                    },
                },
            },
            {
                'type': 'order_widget',
                'id': 'id2',
                'payload': {
                    'service': 'eats',
                    'order_id': 'id2',
                    'order_card': {
                        'show_header': False,
                        'show_state_timeline': False,
                    },
                },
            },
        ],
    }

    assert response_body == expected_response_body


@pytest.mark.translations(
    client_messages={
        'drive.text': {'ru': 'Драйв!'},
        'drive.item_text': {'ru': 'Го!'},
    },
)
@pytest.mark.now('2022-04-01T13:56:22.372+03:00')
async def test_long_tracking(
        taxi_shortcuts,
        add_settings_exp,
        add_experiment,
        add_appearance_experiments,
):
    add_settings_exp(
        title_key='title_key',
        orders_selectors=[
            {
                'services': ['market'],
                'statuses': ['delivery'],
                'max_hours_to_completion': 24,
                'min_hours_to_completion': 0,
            },
            {'services': ['taxi']},
        ],
    )

    request_body = {
        'screen_type': 'on_multiorder',
        'orders_info': [
            {'service': 'taxi', 'order_id': 'id1'},
            {'service': 'eats', 'order_id': 'id2'},
            {
                'service': 'market',
                'order_id': 'id3',
                'status': 'delivery',
                'completion_datetime': '2022-04-03T13:56:22.372+03:00',
            },
            {
                'service': 'market',
                'order_id': 'id4',
                'status': 'ready',
                'completion_datetime': '2022-04-01T15:56:22.372+03:00',
            },
            {
                'service': 'market',
                'order_id': 'id5',
                'status': 'delivery',
                'completion_datetime': '2022-04-01T15:56:22.372+03:00',
            },
            {
                'service': 'market',
                'order_id': 'id6',
                'status': 'delivery',
                'completion_datetime': '2022-04-01T12:56:22.372+03:00',
            },
        ],
    }

    response = await taxi_shortcuts.post(URL, request_body)
    assert response.status_code == 200
    response_body = response.json()

    expected_response_body = {
        'widgets': [
            {
                'type': 'order_widget',
                'id': 'id1',
                'payload': {'service': 'taxi', 'order_id': 'id1'},
            },
            {
                'type': 'order_widget',
                'id': 'id5',
                'payload': {
                    'service': 'market',
                    'order_id': 'id5',
                    'order_card': {
                        'show_header': False,
                        'show_state_timeline': True,
                    },
                },
            },
        ],
    }

    assert response_body == expected_response_body

    add_appearance_experiments()

    env = helpers.EnvSetup()
    env.header_params_experiment['buttons']['show_from'] = 1
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    availability_support = helpers.ScenarioSupport(
        available_scenarios=[
            helpers.Scenarios.taxi_route_input,
            helpers.Scenarios.eats_based_eats,
            helpers.Scenarios.eats_based_grocery,
            helpers.Scenarios.market,
            helpers.Scenarios.header_delivery,
        ],
    ).to_services_availability()

    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=availability_support,
        supported_actions=env.all_supported_actions,
        state={
            'screen_type': 'on_multiorder',
            'known_orders_info': request_body['orders_info'],
        },
    )

    await taxi_shortcuts.invalidate_caches()

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']
    assert 'buttons' in offers

    overlays_expectactions = {'market': '3', 'eats': '1'}

    for button in offers['buttons']:
        service = button.get('service')
        if service in overlays_expectactions:
            assert 'overlays' in button
            assert button['overlays'] == [
                {
                    'text': overlays_expectactions[service],
                    'text_color': '#001122',
                    'background': {'color': '#FAFAFA'},
                },
            ]
        else:
            assert 'overlays' not in button
