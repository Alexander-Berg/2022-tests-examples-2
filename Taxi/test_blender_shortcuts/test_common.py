import pytest

from tests_shortcuts import consts
from tests_shortcuts import helpers


def _state_fields_item(type_, position, log=None):
    result = {'type': type_, 'position': position}
    if log is not None:
        result['log'] = log
    return result


# Testing all combinations would yield O(2^(N * K)) test cases, where
#    N = amount of different bricks
#    K = amount of entities to consider while calculating availability
# For now N = 5 (taxi, eats, pharmacy, grocery, delivery) and K=4
# (client_support, availability_support, layout_support, known_orders).
# Thats 1 million test cases, so we will only test cherry picked ones
@pytest.mark.parametrize('header_elements_enabled', [True, False])
@pytest.mark.parametrize(
    'client_supported_services',
    [
        [],  # client does not support dynamic bricks
        [helpers.Scenarios.taxi_route_input],  # client supports only taxi
        [
            helpers.Scenarios.taxi_route_input,
            helpers.Scenarios.eats_based_eats,
            helpers.Scenarios.eats_based_grocery,
            helpers.Scenarios.eats_based_pharmacy,
        ],
    ],
)
@pytest.mark.parametrize(
    'availability_supported_services',
    [
        # There is no test with [] availability, because taxi availability is
        # hardcoded to True in dynamic bricks logic
        [helpers.Scenarios.taxi_route_input],
        [
            helpers.Scenarios.taxi_route_input,
            helpers.Scenarios.eats_based_eats,
            helpers.Scenarios.eats_based_grocery,
            helpers.Scenarios.eats_based_pharmacy,
        ],
    ],
)
@pytest.mark.parametrize(
    'layout_supported_services',
    [
        [],  # layout experiment has no bricks in it
        [helpers.Scenarios.taxi_route_input],
        [
            helpers.Scenarios.taxi_route_input,
            helpers.Scenarios.eats_based_eats,
            helpers.Scenarios.eats_based_grocery,
            helpers.Scenarios.eats_based_pharmacy,
        ],
    ],
)
async def test_correct_availability_merge(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        header_elements_enabled,
        availability_supported_services,
        client_supported_services,
        layout_supported_services,
):
    target_availability = (
        set(client_supported_services)
        & set(availability_supported_services)
        & set(layout_supported_services)
    )

    add_appearance_experiments()
    env = helpers.EnvSetup()
    header_elements_params = {
        'enabled': header_elements_enabled,
        'priority': [scenario.name for scenario in layout_supported_services],
    }
    env.header_params_experiment['bricks'].update(header_elements_params)
    env.header_params_experiment['buttons'].update(header_elements_params)
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    client_support = helpers.ScenarioSupport(
        available_scenarios=client_supported_services,
    ).to_client_support()
    availability_support = helpers.ScenarioSupport(
        available_scenarios=availability_supported_services,
    ).to_services_availability()
    payload = helpers.build_header_request(
        client_support=client_support,
        availability_support=availability_support,
        supported_actions=env.all_supported_actions
        if target_availability
        else None,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    # if cutout is turned on, there should be no header and no buttons
    if not header_elements_enabled:
        assert all(field not in offers for field in ('header', 'buttons'))
        return

    # if no bricks (buttons) are generated, there should be no header (buttons)
    if target_availability == set():
        assert all(field not in offers for field in ('header', 'buttons'))
        return

    brick_to_scenario_map = {
        ('taxi:route-input', None): helpers.Scenarios.taxi_route_input.name,
        (
            'eats-based:superapp',
            'eats',
        ): helpers.Scenarios.eats_based_eats.name,
        (
            'eats-based:superapp',
            'grocery',
        ): helpers.Scenarios.eats_based_grocery.name,
        (
            'eats-based:superapp',
            'pharmacy',
        ): helpers.Scenarios.eats_based_pharmacy.name,
    }

    button_scenarios = {
        btn['id'].split(':')[0] for btn in offers.get('buttons', [])
    }

    brick_scenarios = {
        brick_to_scenario_map[(brick['type'], brick.get('service'))]
        for brick in offers.get('header', [])
    }

    expected_scenarios = {scenario.name for scenario in target_availability}

    assert brick_scenarios | button_scenarios == expected_scenarios


async def test_layout_width_respected(
        taxi_shortcuts, add_experiment, add_appearance_experiments,
):
    add_appearance_experiments()
    env = helpers.EnvSetup()

    default_height = 1
    eats_width = 4
    taxi_width = 2

    header_elements_params = {
        'priority': [
            helpers.Scenarios.eats_based_eats.name,
            helpers.Scenarios.taxi_route_input.name,
        ],
        'layout_options': {'2': [eats_width, taxi_width]},
    }
    env.header_params_experiment['bricks'].update(header_elements_params)

    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )
    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()

    result_bricks = {
        (header['type'], header['width'], header['height'])
        for header in data['offers']['header']
    }

    # check that priority matters
    assert result_bricks == {
        ('eats-based:superapp', eats_width, default_height),
        ('taxi:route-input', taxi_width, default_height),
    }


@pytest.mark.parametrize(
    'available_services',
    [
        [
            helpers.Scenarios.eats_based_eats,
            helpers.Scenarios.eats_based_grocery,
            helpers.Scenarios.eats_based_pharmacy,
        ],
        [],
    ],
)
@pytest.mark.parametrize('show_disabled', [True, False])
@pytest.mark.parametrize(
    'known_orders_services', [{'eats', 'grocery', 'pharmacy', 'drive'}],
)
@pytest.mark.parametrize(
    'known_order_pattern', [':order_id:version', ':order_id:', ':', ':' * 5],
)
async def test_known_orders(
        taxi_shortcuts,
        add_experiment,
        available_services,
        add_appearance_experiments,
        known_orders_services,
        known_order_pattern,
        show_disabled,
):
    add_appearance_experiments()

    env = helpers.EnvSetup()
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    payload = helpers.build_header_request(
        client_support=helpers.ScenarioSupport(
            available_scenarios=list(helpers.Scenarios),
        ).to_client_support(),
        availability_support=helpers.ScenarioSupport(
            available_scenarios=available_services,
        ).to_services_availability(),
        known_orders=[
            f'{svc}{known_order_pattern}' for svc in known_orders_services
        ],
        supported_actions=env.all_supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    assert 'header' in offers or 'buttons' in offers

    if not show_disabled and not available_services:
        return

    found_services = set()
    for client_brick in offers.get('header', []):
        brick_service_name = client_brick['shortcut_id'].split(':')[0]
        if brick_service_name == 'taxi':
            continue
        found_services.add(brick_service_name)
    for button in offers.get('buttons', []):
        found_services.add(button['id'].split(':')[0])

    expected_services = {
        'taxi_route_input',
        'eats_based_eats',
        'eats_based_grocery',
        'eats_based_pharmacy',
        'discovery_drive',
    }
    assert expected_services == found_services


@pytest.mark.translations(
    client_messages={
        'default_title_key': {'ru': 'default_translated_title'},
        'superapp.taxi.another_car': {'ru': 'translated_another_car'},
    },
)
@pytest.mark.parametrize('active_orders_services', [['taxi'], []])
async def test_active_orders_services(
        taxi_shortcuts, add_experiment, active_orders_services, experiments3,
):
    experiments3.add_experiment(
        name=consts.SUPERAPP_BRICKS_APPEARANCE_EXPERIMENT,
        consumers=['shortcuts/shortcuts'],
        clauses=[
            {
                'value': {
                    'taxi_route_input': {
                        **consts.DEFAULT_APPEARANCE,
                        **{'title_key': 'superapp.taxi.another_car'},
                    },
                },
                'predicate': {
                    'init': {
                        'predicates': [
                            helpers.exp_create_contains_predicate(
                                'active_orders_services', 'taxi',
                            ),
                        ],
                    },
                    'type': 'all_of',
                },
            },
            {
                'value': {'taxi_route_input': consts.DEFAULT_APPEARANCE},
                'predicate': {
                    'init': {'predicates': [{'type': 'true'}]},
                    'type': 'all_of',
                },
            },
        ],
    )

    env = helpers.EnvSetup()
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    scenario_support = helpers.ScenarioSupport()
    payload = helpers.build_header_request(
        client_support=helpers.ScenarioSupport(
            available_scenarios=list(helpers.Scenarios),
        ).to_client_support(),
        availability_support=scenario_support.to_services_availability(),
        supported_actions=env.all_supported_actions,
        state={'active_orders_services': active_orders_services},
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    assert 'header' in offers
    assert offers['header'][0]['type'] == 'taxi:route-input'
    if 'taxi' in active_orders_services:
        assert offers['header'][0]['title'] == 'translated_another_car'
    else:
        assert offers['header'][0]['title'] == 'default_translated_title'


@pytest.mark.parametrize('expect_buttons', [True, False])
@pytest.mark.parametrize(
    'multicolor_support, service_enabled, show_disabled',
    [
        (True, True, False),
        (True, False, True),
        (False, True, False),
        (False, False, True),
    ],
)
async def test_multicolor_service_icons(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        multicolor_support,
        service_enabled,
        show_disabled,
        expect_buttons,
):
    add_appearance_experiments(
        {
            helpers.Scenarios.eats_based_eats.name: (
                helpers.generate_brick_appearance({**consts.DEFAULT_ICON})
            ),
        },
    )

    available_scenarios = helpers.ScenarioSupport(
        available_scenarios=[helpers.Scenarios.eats_based_eats],
    )
    header_params_exp_value = available_scenarios.to_header_params_experiment()
    if expect_buttons:
        header_params_exp_value['buttons']['show_from'] = 1
    add_experiment(consts.HEADER_PARAMS_EXPERIMENT, header_params_exp_value)

    availability_support = helpers.ScenarioSupport(
        available_scenarios=available_scenarios.ordered_available_scenarios
        if service_enabled
        else list(),
        show_disabled_services=['eats'] if show_disabled else [],
    ).to_services_availability()

    env = helpers.EnvSetup()
    payload = helpers.build_header_request(
        client_support=available_scenarios.to_client_support(),
        availability_support=availability_support,
        multicolor_service_icons_supported=multicolor_support,
        supported_actions=env.all_supported_actions,
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    if expect_buttons:
        result_icon_size = offers['buttons'][0]['icon_size']
        assert result_icon_size == 'medium'

    result_icon = (
        [button['icon_tag'] for button in offers['buttons']][0]
        if expect_buttons
        else [brick['icon_tag'] for brick in offers['header']][0]
    )

    expected_tag = ''
    if multicolor_support:
        expected_tag = consts.DEFAULT_ICON['multicolor_icon']
        if service_enabled:
            expected_tag = expected_tag['enabled_tag']
        else:
            expected_tag = expected_tag['disabled_tag']
    else:
        expected_tag = consts.DEFAULT_ICON['icon_tag']
    assert result_icon == expected_tag


@pytest.mark.parametrize('supported_icon_sizes', [['big'], []])
@pytest.mark.parametrize(
    'multicolor_support, try_big_multicolor_icon',
    [(True, True), (True, False), (False, True)],
)
async def test_big_multicolor_icons(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        multicolor_support,
        try_big_multicolor_icon,
        supported_icon_sizes,
):
    big_multicolor_icon = {}
    if try_big_multicolor_icon:
        big_multicolor_icon = {
            'big_multicolor_icon': {
                'enabled_tag': 'big_colored_enabled_tag',
                'disabled_tag': 'big_colored_disabled_tag',
            },
        }
    add_appearance_experiments(
        {
            helpers.Scenarios.eats_based_eats.name: (
                helpers.generate_brick_appearance(
                    {**consts.DEFAULT_ICON, **big_multicolor_icon},
                )
            ),
        },
    )

    available_scenarios = helpers.ScenarioSupport(
        available_scenarios=[helpers.Scenarios.eats_based_eats],
    )
    header_params_exp_value = available_scenarios.to_header_params_experiment()
    header_params_exp_value['buttons']['show_from'] = 1
    add_experiment(consts.HEADER_PARAMS_EXPERIMENT, header_params_exp_value)

    availability_support = helpers.ScenarioSupport(
        available_scenarios=available_scenarios.ordered_available_scenarios,
    ).to_services_availability()

    env = helpers.EnvSetup()
    payload = helpers.build_header_request(
        client_support=available_scenarios.to_client_support(),
        availability_support=availability_support,
        multicolor_service_icons_supported=multicolor_support,
        supported_actions=env.all_supported_actions,
        supported_icon_sizes=supported_icon_sizes,
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    result_icon_size = offers['buttons'][0]['icon_size']
    if (
            multicolor_support
            and try_big_multicolor_icon
            and 'big' in supported_icon_sizes
    ):
        assert result_icon_size == 'big'
    else:
        assert result_icon_size == 'medium'

    result_icon = offers['buttons'][0]['icon_tag']
    expected_tag = ''
    if multicolor_support:
        if try_big_multicolor_icon and 'big' in supported_icon_sizes:
            expected_tag = big_multicolor_icon['big_multicolor_icon']
        else:
            expected_tag = consts.DEFAULT_ICON['multicolor_icon']
        expected_tag = expected_tag['enabled_tag']
    else:
        expected_tag = consts.DEFAULT_ICON['icon_tag']

    assert result_icon == expected_tag


@pytest.mark.config(
    EXTENDED_TEMPLATE_STYLES_MAP={
        'style': {
            'font_size': 20,
            'font_weight': 'bold',
            'meta_color': '#000000',
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'card_title_key': {'ru': 'Тайтл'},
        'card_subtitle_key': {'ru': 'Сабтайтл'},
    },
)
@pytest.mark.experiments3(filename='experiment_superapp_upsell_card.json')
@pytest.mark.parametrize(
    'orders_info',
    [
        [['6c432ba271d8c84f8990c99cd5a54f6f', 'taxi']],
        [['6c432ba271d8c84f8990c99cd5a54f6f', 'eats']],
        [],
        [
            ['7e432ba271d8c84f8990c99cd5a54f6f', 'taxi'],
            ['6c432ba271d8c84f8990c99cd5a54f6f', 'taxi'],
        ],
    ],
)
async def test_card_objects(taxi_shortcuts, add_experiment, orders_info):
    env = helpers.EnvSetup()
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )
    known_orders_info = []
    card_objects_exist = False
    taxi_order_id = ''
    for order in orders_info:
        known_orders_info.append({'orderid': order[0], 'service': order[1]})
        if order[1] == 'taxi':
            card_objects_exist = True
            taxi_order_id = order[0]

    expected_cards = [
        {
            'action': {'deeplink': 'yandextaxi://...', 'type': 'deeplink'},
            'card': {
                'icon_tag': 'some_tag',
                'subtitle': 'Сабтайтл',
                'attributed_title': {
                    'items': [{'text': 'Тайтл', 'type': 'text'}],
                },
            },
            'hide_on_action': True,
            'id': 'unique_id_(grocery)',
            'max_show_count': 10,
            'service': 'taxi',
            'order_id': taxi_order_id,
            'statuses': ['transporting'],
            'type': 'order_card',
        },
        {
            'action': {
                'deeplink': (
                    'yandextaxi://external?service=grocery'
                    '&delivery_lon=37.500000&delivery_lat=55.500000'
                ),
                'type': 'deeplink',
            },
            'card': {
                'icon_tag': 'some_tag',
                'title': 'TTitle',
                'attributed_subtitle': {
                    'items': [
                        {
                            'text': 'TSubTitle',
                            'type': 'text',
                            'font_size': 20,
                            'font_weight': 'bold',
                            'meta_color': '#000000',
                        },
                    ],
                },
            },
            'hide_on_action': False,
            'id': 'unique_id_2',
            'max_show_count': 11,
            'service': 'taxi',
            'order_id': taxi_order_id,
            'statuses': ['transporting', 'riding'],
            'type': 'order_card',
        },
    ]

    scenario_support = helpers.ScenarioSupport()
    payload = helpers.build_header_request(
        client_support=helpers.ScenarioSupport(
            available_scenarios=list(helpers.Scenarios),
        ).to_client_support(),
        availability_support=scenario_support.to_services_availability(),
        supported_actions=env.all_supported_actions,
        state={
            'known_orders_info': known_orders_info,
            'fields': [{'type': 'b', 'position': [37.5, 55.5]}],
        },
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    response_body = response.json()

    if card_objects_exist:
        assert response_body['card_objects'] == expected_cards
    else:
        assert 'card_objects' not in response_body


@pytest.mark.parametrize(
    'log, expected_point_b_tags',
    [
        pytest.param(
            '{"type":"userplace","userplace_id":"work","tags":["a","b"]}',
            ['a', 'b'],
            id='parsable_and_have_tags',
        ),
        pytest.param(
            '{"type":"userplace","userplace_id":"work"}', None, id='no_tags',
        ),
        pytest.param('unknown_log', None, id='not_json_log'),
        pytest.param(None, None, id='no_log'),
    ],
)
async def test_kwarg_point_b(
        taxi_shortcuts,
        add_experiment,
        experiments3,
        log,
        expected_point_b_tags,
):
    experiments3.add_experiment(
        name=consts.SUPERAPP_BRICKS_APPEARANCE_EXPERIMENT,
        consumers=['shortcuts/shortcuts'],
        clauses=[
            {
                'value': {'taxi_route_input': consts.DEFAULT_APPEARANCE},
                'predicate': {
                    'init': {'predicates': [{'type': 'true'}]},
                    'type': 'all_of',
                },
            },
        ],
    )

    env = helpers.EnvSetup()
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )
    scenario_support = helpers.ScenarioSupport()
    payload = helpers.build_header_request(
        client_support=helpers.ScenarioSupport(
            available_scenarios=list(helpers.Scenarios),
        ).to_client_support(),
        availability_support=scenario_support.to_services_availability(),
        state={
            'fields': [
                _state_fields_item(type_='a', position=[37, 55], log='smth'),
                _state_fields_item(type_='b', position=[38, 56], log=log),
            ],
        },
    )

    exp3_recorder = experiments3.record_match_tries(
        consts.SUPERAPP_BRICKS_APPEARANCE_EXPERIMENT,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    if expected_point_b_tags is not None:
        point_b_tags = match_tries[0].kwargs['point_b_tags']
        assert sorted(point_b_tags) == expected_point_b_tags
    else:
        assert 'point_b_tags' not in match_tries[0].kwargs


@pytest.mark.config(
    EXTENDED_COLORS_SETTINGS={
        'semantic_colors_mapping': {
            'text': {'__default__': '#000000', 'ultima': '#111111'},
        },
    },
)
@pytest.mark.parametrize('expect_buttons', [True, False])
@pytest.mark.parametrize(
    'themeable, appearance_mode, expected_colors',
    [
        (None, None, {'background': '#AABBCC', 'text': '#000000'}),
        (None, 'default', {'background': '#AABBCC', 'text': '#000000'}),
        (None, 'ultima', {'background': '#AABBCC', 'text': '#111111'}),
        ('1', None, {'background': '#AABBCC', 'text': 'text'}),
        (
            '2',
            'default',
            {'background': 'd:#FAFAFA;l:#AABBCC', 'text': 'text'},
        ),
        ('3', 'ultima', {'background': 'd:#FAFAFA;l:#AABBCC', 'text': 'text'}),
    ],
)
async def test_color_replacement(
        taxi_shortcuts,
        add_experiment,
        add_config,
        add_appearance_experiments,
        expect_buttons,
        themeable,
        appearance_mode,
        expected_colors,
):
    add_config(
        consts.SHORTCUTS_COLOR_REPLACEMENT_SETTINGS_EXP, {'enabled': True},
    )

    add_appearance_experiments(
        overrides={
            'background_color': 'd:#FAFAFA;l:#AABBCC',
            'active_text_color': 'text',
        },
    )

    env = helpers.EnvSetup()
    scenario_support = helpers.ScenarioSupport(
        available_scenarios=[
            helpers.Scenarios.taxi_route_input,
            helpers.Scenarios.eats_based_eats,
            helpers.Scenarios.eats_based_grocery,
        ],
    )
    header_params_exp = scenario_support.to_header_params_experiment()
    header_params_exp['buttons']['show_from'] = 1 if expect_buttons else 99
    add_experiment(consts.HEADER_PARAMS_EXPERIMENT, header_params_exp)

    state = {'appearance_mode': appearance_mode} if appearance_mode else {}
    payload = helpers.build_header_request(
        client_support=helpers.ScenarioSupport(
            available_scenarios=list(helpers.Scenarios),
        ).to_client_support(),
        availability_support=scenario_support.to_services_availability(),
        supported_actions=env.all_supported_actions,
        state=state,
    )

    await taxi_shortcuts.invalidate_caches()

    headers = {'themeable': themeable} if themeable else {}
    response = await taxi_shortcuts.post(
        consts.URL, headers=headers, json=payload,
    )

    offers = response.json()['offers']
    buttons = offers.get('buttons')
    bricks = offers.get('header')
    entrypoints = None

    if expect_buttons:
        assert buttons is not None and bricks is None
        entrypoints = buttons
    else:
        assert bricks is not None and buttons is None
        entrypoints = bricks

    for item in entrypoints:
        assert item['background']['color'] == expected_colors['background']
        assert item['text_style']['color'] == expected_colors['text']
