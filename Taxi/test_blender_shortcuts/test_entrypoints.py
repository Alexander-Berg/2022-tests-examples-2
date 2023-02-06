# pylint: disable=too-many-lines
import copy

import pytest

from tests_shortcuts import consts
from tests_shortcuts import helpers

CITY_MODE_LAYOUT_OPTIONS = [
    [6],
    [3, 3],
    [6, 3, 3],
    [3, 3, 3, 3],
    [4, 3, 3, 3, 3],
]


@pytest.mark.translations(
    client_messages={'default_title_key': {'ru': 'default_translated_title'}},
)
@pytest.mark.parametrize('expect_buttons', [True, False])
@pytest.mark.parametrize('with_attributed_title', [True, False])
async def test_entrypoints_simple(
        taxi_shortcuts, add_experiment, expect_buttons, with_attributed_title,
):
    appearance_values = {
        scenario.name: helpers.generate_brick_appearance(
            scenario=scenario, with_attributed_title=with_attributed_title,
        )
        for scenario in helpers.Scenarios
    }
    add_experiment(
        consts.SUPERAPP_BUTTONS_APPEARANCE_EXPERIMENT,
        {
            **appearance_values,
            'market': {
                **consts.DEFAULT_APPEARANCE,
                'attributed_title': consts.DEFAULT_ATTRIBUTED_TITLE,
                'action': {
                    'name': 'market',
                    'type': 'shortcuts_screen',
                    'restore_state_from_cache': True,
                },
            },
        },
    )
    add_experiment(
        consts.SUPERAPP_BRICKS_APPEARANCE_EXPERIMENT, appearance_values,
    )

    add_experiment(
        consts.DELIVERY_AVAILABILITY_EXPERIMENT,
        {'available': True, 'prefer_native_brick': True},
    )
    add_experiment(consts.ULTIMA_AVAILABILITY_EXPERIMENT, {'available': True})

    env = helpers.EnvSetup()
    if not expect_buttons:
        env.header_params_experiment['buttons']['show_from'] = 20
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
        supported_actions=env.all_supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    buttons = offers.get('buttons')
    bricks = offers.get('header')

    if expect_buttons:
        assert buttons is not None and bricks is None
        entrypoints = buttons
    else:
        assert bricks is not None and buttons is None
        entrypoints = bricks

    expected_scenarios = (
        helpers.Scenarios.taxi_route_input,
        helpers.Scenarios.eats_based_eats,
        helpers.Scenarios.eats_based_grocery,
        helpers.Scenarios.eats_based_shop,
        helpers.Scenarios.taxi_header_delivery,
        helpers.Scenarios.discovery_masstransit,
        helpers.Scenarios.discovery_drive,
        helpers.Scenarios.discovery_shuttle,
        helpers.Scenarios.discovery_scooters,
        helpers.Scenarios.taxi_header_ultima,
        helpers.Scenarios.market,
    )
    expected_services = (
        None,
        'eats',
        'grocery',
        'shop',
        'delivery',
        'masstransit',
        'drive',
        None,
        'scooters',
        None,
        'market',
    )
    if expect_buttons:
        assert len(entrypoints) == len(expected_services)
    else:
        # see market hack below
        assert len(expected_services) - len(entrypoints) == 1
    for (item, scenario, service) in zip(
            entrypoints, expected_scenarios, expected_services,
    ):
        if service == 'market' and not expect_buttons:
            # https://st.yandex-team.ru/TAXIBACKEND-36514
            # skip market brick for now
            continue

        expected_action = copy.deepcopy(
            helpers.get_action_by_scenario(scenario, typed=expect_buttons),
        )
        if service == 'market':
            expected_action = {
                **expected_action,
                'restore_state_from_cache': True,
            }
        assert item.get('action', {}) == expected_action
        assert item['background'] == {'color': 'default_background_color'}
        assert item['text_style'] == {'color': 'default_active_text_color'}
        assert item['icon_tag'] == 'default_icon_tag'
        assert item['title'] == 'default_translated_title'
        if with_attributed_title:
            assert item['attributed_title'] == {
                'items': [
                    {
                        'type': 'text',
                        'text': 'test text',
                        'font_size': 14,
                        'font_weight': 'regular',
                        'font_style': 'normal',
                        'color': '#000000',
                    },
                    {'type': 'image', 'image_tag': 'test_image', 'width': 10},
                ],
            }
        if service is not None:
            assert item['service'] == service
            entrypoint_id = (
                item['id'] if expect_buttons else item['shortcut_id']
            )
            assert service in entrypoint_id


@pytest.mark.parametrize('expect_buttons', [True, False])
async def test_shop_entrypoint(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        expect_buttons,
):
    add_appearance_experiments()
    env = helpers.EnvSetup(show_disabled_services=['shop'])
    if not expect_buttons:
        env.header_params_experiment['buttons']['show_from'] = 10
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
        supported_actions=env.all_supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    if expect_buttons:
        entrypoints = offers.get('buttons')
    else:
        entrypoints = offers.get('header')
    assert entrypoints is not None

    shop_match = [
        entry for entry in entrypoints if entry.get('service', '') == 'shop'
    ]
    assert len(shop_match) == 1

    shop = shop_match[0]
    assert shop.get('action', {}) == helpers.get_action_by_scenario(
        helpers.Scenarios.eats_based_shop, typed=expect_buttons,
    )

    if not expect_buttons:
        assert shop.get('type', '') == 'eats-based:superapp'


@pytest.mark.parametrize('expect_buttons', [True, False])
async def test_priority_matters(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        expect_buttons,
):
    add_appearance_experiments()
    env = helpers.EnvSetup()

    priority = [
        helpers.Scenarios.eats_based_eats.name,
        helpers.Scenarios.taxi_route_input.name,
    ]
    env.header_params_experiment['bricks']['priority'] = priority
    env.header_params_experiment['buttons']['priority'] = priority
    if expect_buttons:
        env.header_params_experiment['buttons']['show_from'] = 1
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
        supported_actions=env.all_supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()

    buttons = [
        (button['id'].split(':')[0], button.get('service'))
        for button in data['offers'].get('buttons', [])
    ]

    bricks = [
        (header['type'], header.get('service'))
        for header in data['offers'].get('header', [])
    ]

    if expect_buttons:
        assert not bricks
        assert buttons == [
            ('eats_based_eats', 'eats'),
            ('taxi_route_input', None),
        ]
    else:
        assert not buttons
        assert bricks == [
            ('eats-based:superapp', 'eats'),
            ('taxi:route-input', None),
        ]


@pytest.mark.parametrize('send_supported_actions', [True, False])
async def test_no_supported_actions(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        send_supported_actions,
):
    add_appearance_experiments()

    add_experiment(consts.ULTIMA_AVAILABILITY_EXPERIMENT, {'available': True})

    env = helpers.EnvSetup()
    env.header_params_experiment['buttons']['show_from'] = 1
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    supported_actions = (
        env.all_supported_actions if send_supported_actions else None
    )
    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
        supported_actions=supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    buttons = offers.get('buttons')
    bricks = offers.get('header')

    if send_supported_actions:
        assert len(buttons) == 10  # taxi, eats, grocery, shop, discovery,
        # drive, scooters, ultima, market, shuttle
        assert bricks is None
    else:
        # do not return discovery bricks
        # because they depend on supported_actions
        assert len(bricks) == 5  # taxi, eats, grocery, shop, ultima
        assert buttons is None


@pytest.mark.parametrize('expect_buttons', [True, False])
@pytest.mark.parametrize('with_optional_params', [True, False])
@pytest.mark.translations(
    client_messages={'tanker_key': {'ru': 'tanker_value'}},
)
async def test_appearance_experiment_matters(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        expect_buttons,
        with_optional_params,
):
    show_disabled_service = 'shop'

    background_color = 'red'
    active_text_color = 'white'
    disabled_text_color = 'blue'
    icon_tag = 'service_icon_tag'
    deeplink = 'yandextaxi://somedeeplink'

    appearances = {}
    for header_scenario in helpers.Scenarios:
        appearances[header_scenario.name] = helpers.generate_brick_appearance(
            {
                'title_key': 'tanker_key',
                'background_color': background_color,
                'active_text_color': active_text_color,
                'disabled_text_color': disabled_text_color,
                'icon_tag': icon_tag,
                'deeplink': deeplink,
            },
        )
    # bricks with no deeplink
    for scenario_name in [
            helpers.Scenarios.taxi_route_input.name,
            helpers.Scenarios.discovery_drive.name,
            helpers.Scenarios.discovery_scooters.name,
            helpers.Scenarios.discovery_masstransit.name,
            helpers.Scenarios.discovery_shuttle.name,
    ]:
        appearances[scenario_name].pop('deeplink')
    # add modes for discovery actions
    appearances[helpers.Scenarios.discovery_drive.name]['mode'] = 'drive'
    appearances[helpers.Scenarios.discovery_shuttle.name]['mode'] = 'shuttle'
    appearances[helpers.Scenarios.discovery_scooters.name]['mode'] = 'scooters'
    appearances[helpers.Scenarios.market.name]['mode'] = 'market'
    appearances[helpers.Scenarios.discovery_masstransit.name][
        'mode'
    ] = 'masstransit'

    if expect_buttons:
        appearances[helpers.Scenarios.eats_based_shop.name].pop('deeplink')
        action = {'name': 'shops', 'type': 'shortcuts_screen'}
        if with_optional_params:
            action['suggest_mode'] = 'shop'
        appearances[helpers.Scenarios.eats_based_shop.name]['action'] = action

    add_appearance_experiments(appearances)
    env = helpers.EnvSetup(
        show_disabled_services=[show_disabled_service],
        disabled_available_scenarios={
            helpers.Scenarios.eats_based_grocery,
            helpers.Scenarios.eats_based_shop,
        },
    )

    env.header_params_experiment['buttons']['show_from'] = (
        1 if expect_buttons else 10
    )
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )
    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
        supported_actions=env.all_supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    buttons = offers.get('buttons')
    bricks = offers.get('header')

    if expect_buttons:
        assert buttons is not None and bricks is None
        entrypoints = buttons
    else:
        assert bricks is not None and buttons is None
        entrypoints = bricks

    def check_button_action(button_type, action):
        expected_action = {'deeplink': deeplink, 'type': 'deeplink'}
        if button_type == 'taxi_route_input':
            expected_action = {'type': 'taxi:route-input'}
        elif button_type == 'discovery_drive':
            expected_action = {'mode': 'drive', 'type': 'discovery'}
        elif button_type == 'discovery_masstransit':
            expected_action = {'mode': 'masstransit', 'type': 'discovery'}
        elif button_type == 'discovery_shuttle':
            expected_action = {'mode': 'shuttle', 'type': 'discovery'}
        elif button_type == 'discovery_scooters':
            expected_action = {'mode': 'scooters', 'type': 'discovery'}
        elif button_type == 'eats_based_shop':
            action = {'name': 'shops', 'type': 'shortcuts_screen'}
            if with_optional_params:
                action['suggest_mode'] = 'shop'
            expected_action = action
        assert action == expected_action

    def check_brick_action(brick_):
        if brick_['type'] == 'taxi:route-input':
            assert 'action' not in brick_
        elif brick_['type'] == 'header-action-driven':
            assert (
                (
                    'mode' in brick_['action']
                    and brick_['action']['mode']
                    in ('drive', 'masstransit', 'scooters', 'shuttle')
                )
                or (
                    'type' in brick_['action']
                    and brick_['action']['type'] == 'deeplink'
                    and 'deeplink' in brick_['action']
                )
            )
        else:
            assert brick_['action']['deeplink'] == deeplink

    buttons = set()
    for item in entrypoints:
        assert item['title'] == 'tanker_value'
        assert item['background']['color'] == background_color
        assert item['icon_tag'] == icon_tag
        if item.get('service') == show_disabled_service:
            assert item['text_style']['color'] == disabled_text_color
        else:
            assert item['text_style']['color'] == active_text_color

        if expect_buttons:
            button_type = item['id'].split(':')[0]
            check_button_action(button_type, item['action'])
            buttons.add(button_type)
        else:
            check_brick_action(item)

    if expect_buttons:
        assert buttons == set(
            [
                'taxi_route_input',
                'discovery_drive',
                'discovery_masstransit',
                'discovery_shuttle',
                'discovery_scooters',
                'eats_based_shop',
                'eats_based_eats',
                'market',
            ],
        )


# build bricks if there is no enough buttons
async def test_bricks_fallback(
        taxi_shortcuts, add_experiment, add_appearance_experiments,
):
    add_appearance_experiments()
    env = helpers.EnvSetup()

    add_experiment(
        consts.DELIVERY_AVAILABILITY_EXPERIMENT, {'available': True},
    )

    # do not include discovery bricks, because they are not supported
    env.header_params_experiment['buttons']['show_from'] = 11
    env.header_params_experiment['bricks'].update(
        {
            'layout_options': {'3': [6, 3, 3]},
            'priority': [
                'taxi_route_input',
                'header_delivery',
                'eats_based_eats',
            ],
        },
    )

    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    # client do not support discovery bricks
    env.client_support.remove(
        {'type': 'header-action-driven', 'prefetch_strategies': []},
    )

    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
        supported_actions=env.all_supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    bricks = data['offers'].get('header', [])

    assert len(bricks) == 3
    assert [brick['width'] for brick in bricks] == [6, 3, 3]


@pytest.mark.parametrize(
    'supported_modes',
    [['masstransit', 'drive', 'shuttle'], ['masstransit'], ['drive'], []],
)
@pytest.mark.parametrize(
    'scenarios',
    [
        [
            helpers.Scenarios.discovery_masstransit,
            helpers.Scenarios.discovery_drive,
            helpers.Scenarios.discovery_shuttle,
        ],
        [helpers.Scenarios.discovery_drive],
        [helpers.Scenarios.discovery_masstransit],
        [],
    ],
)
@pytest.mark.parametrize('expect_buttons', [True, False])
async def test_discovery_modes(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        expect_buttons,
        supported_modes,
        scenarios,
):
    add_appearance_experiments()

    available_scenarios = helpers.ScenarioSupport(
        available_scenarios=scenarios,
    )

    header_params_exp_value = available_scenarios.to_header_params_experiment()
    if expect_buttons:
        header_params_exp_value['buttons']['show_from'] = 1
    add_experiment(consts.HEADER_PARAMS_EXPERIMENT, header_params_exp_value)

    env = helpers.EnvSetup()
    supported_actions = env.all_supported_actions
    discovery_action = [
        action for action in supported_actions if action['type'] == 'discovery'
    ][0]
    discovery_action['modes'] = supported_modes
    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
        supported_actions=supported_actions,
    )

    expected_modes = [
        mode
        for (scenario, mode) in [
            (helpers.Scenarios.discovery_masstransit, 'masstransit'),
            (helpers.Scenarios.discovery_drive, 'drive'),
            (helpers.Scenarios.discovery_shuttle, 'shuttle'),
        ]
        if scenario in scenarios and mode in supported_modes
    ]

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    bricks = offers.get('header')
    buttons = offers.get('buttons')

    if not scenarios or not supported_modes or not expected_modes:
        assert bricks is None and buttons is None
        return

    if expect_buttons:
        assert bricks is None and buttons is not None
        entrypoints = buttons
    else:
        assert buttons is None and bricks is not None
        entrypoints = bricks

    result_modes = [entrypoint['action']['mode'] for entrypoint in entrypoints]
    assert expected_modes == result_modes


@pytest.mark.parametrize(
    'expect_buttons',
    [pytest.param(True, id='buttons'), pytest.param(False, id='bricks')],
)
async def test_entrypoints_use_rtl_icons(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        expect_buttons,
):
    add_appearance_experiments(
        overrides={
            'multicolor_icon_rtl': {
                'enabled_tag': 'rtl_multicolor_enabled_tag',
                'disabled_tag': 'rtl_multicolor_disabled_tag',
            },
        },
    )

    add_experiment(consts.RTL_POLICY_EXPERIMENT, {'use_rtl_icon': True})

    env = helpers.EnvSetup()
    if expect_buttons:
        env.header_params_experiment['buttons']['show_from'] = 1
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    availability_support = helpers.ScenarioSupport(
        available_scenarios=[
            helpers.Scenarios.taxi_route_input,
            helpers.Scenarios.eats_based_eats,
            helpers.Scenarios.eats_based_grocery,
        ],
    ).to_services_availability()

    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=availability_support,
        supported_actions=env.all_supported_actions,
        multicolor_service_icons_supported=True,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    buttons = offers.get('buttons')
    bricks = offers.get('header')

    if expect_buttons:
        assert buttons is not None and bricks is None
        entrypoints = buttons
    else:
        assert bricks is not None and buttons is None
        entrypoints = bricks

    expected_services = (None, 'eats', 'grocery')

    assert len(entrypoints) == len(expected_services)
    for (item, service) in zip(entrypoints, expected_services):
        assert item['icon_tag'] == 'rtl_multicolor_enabled_tag'
        assert item.get('service') == service  # None for taxi_route_input


@pytest.mark.parametrize(
    'service, scenario',
    [
        ('eats', helpers.Scenarios.eats_based_eats),
        ('grocery', helpers.Scenarios.eats_based_grocery),
        ('pharmacy', helpers.Scenarios.eats_based_pharmacy),
    ],
)
@pytest.mark.parametrize('deathflag', [True, False])
async def test_deathbricks(
        taxi_shortcuts,
        add_experiment,
        service,
        scenario,
        deathflag,
        add_appearance_experiments,
):
    scenario_support = helpers.ScenarioSupport(
        available_scenarios=[scenario],
        available_services=[],
        service_to_deathflag_map={service: deathflag},
    )

    add_appearance_experiments()
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT,
        scenario_support.to_header_params_experiment(),
    )

    payload = helpers.build_header_request(
        client_support=scenario_support.to_client_support(),
        availability_support=scenario_support.to_services_availability(),
        supported_actions=helpers.EnvSetup().all_supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)

    assert response.status_code == 200

    offers = response.json()['offers']
    assert 'buttons' not in offers

    if deathflag:
        assert len(offers['header']) == 1
        assert offers['header'][0]['action'] == consts.DEEPLINK_ACTION
        assert offers['header'][0]['service'] == service
    else:
        assert 'header' not in offers


# route_input != 6 -> no brick
# .width = 2 -> layout
# .width = 1 -> layout
@pytest.mark.parametrize(
    'chaos_exp_value,has_appearance,route_input_size,expected_layout',
    [
        (None, True, 6, [{'taxi': 6}]),  # no exp -> no chaos
        (
            {'enabled': False, 'width': 2},
            True,
            6,
            [{'taxi': 6}],
        ),  # disabled -> no chaos
        (
            {'enabled': False, 'width': 2},
            True,
            5,
            [{'taxi': 5}],
        ),  # small route_input -> no chaos
        (
            {'enabled': True, 'width': 2},
            False,
            6,
            [{'taxi': 6}],
        ),  # no appearance -> no chaos
        ({'enabled': True, 'width': 2}, True, 6, [{'taxi': 4}, {'chaos': 2}]),
        ({'enabled': True, 'width': 1}, True, 6, [{'taxi': 5}, {'chaos': 1}]),
    ],
)
async def test_chaotic_brick(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        chaos_exp_value,
        has_appearance,
        route_input_size,
        expected_layout,
):

    if chaos_exp_value is not None:
        add_experiment(consts.CHAOS_BRICK_EXP, chaos_exp_value)

    appearance_ext = None
    if has_appearance:
        appearance_dict = helpers.generate_brick_appearance()
        appearance_dict['background_image_tag'] = 'chaos_image'
        appearance_ext = {'chaos_alert': appearance_dict}
    add_appearance_experiments(appearance_ext=appearance_ext)

    scenario_support = helpers.ScenarioSupport(
        available_scenarios=[helpers.Scenarios.taxi_route_input],
    )  # only taxi is available

    # set single brick width to route_input_size
    # (we know that only taxi is available)
    header_params = scenario_support.to_header_params_experiment(
        layout_options={1: [route_input_size]},
    )

    add_experiment(consts.HEADER_PARAMS_EXPERIMENT, header_params)

    payload = helpers.build_header_request(
        client_support=scenario_support.to_client_support(),
        availability_support=scenario_support.to_services_availability(),
        supported_actions=helpers.EnvSetup().all_supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']['header']
    reality = []
    for offer in offers:
        name = 'chaos'
        if 'taxi' in offer['type']:
            name = 'taxi'
        brick = {name: offer['width']}
        reality.append(brick)

    assert reality == expected_layout

    chaos_bricks = [x for x in offers if x['shortcut_id'].startswith('chaos')]
    if chaos_bricks:
        assert chaos_bricks[0]['background']['image_tag'] == 'chaos_image'


@pytest.mark.parametrize(
    'city_mode_scenarios, expected_providers',
    [
        ([], None),
        (
            ['discovery_masstransit', 'discovery_drive', 'discovery_scooters'],
            ['drive', 'stops', 'scooters'],
        ),
        (['discovery_masstransit'], ['stops']),
        (['discovery_drive'], ['drive']),
        (['discovery_scooters'], ['scooters']),
    ],
)
@pytest.mark.parametrize('enabled', [True, False])
@pytest.mark.parametrize('action_supported', [True, False])
async def test_city_mode_entrypoint(
        taxi_shortcuts,
        add_experiment,
        city_mode_scenarios,
        expected_providers,
        enabled,
        action_supported,
):
    add_experiment(
        consts.CITY_MODE_PARAMS_EXP,
        {
            'enabled': enabled,
            'city_mode_scenarios_with_priority': city_mode_scenarios,
            'layout_options': CITY_MODE_LAYOUT_OPTIONS,
        },
    )

    add_experiment(
        consts.CITY_MODE_LAYERS_CONTEXT_EXP,
        {
            'provider_filter': [
                {'type': 'constant', 'providers': []},
                {'type': 'discovery_drive', 'providers': ['drive']},
                {'type': 'discovery_scooters', 'providers': ['scooters']},
                {'type': 'discovery_masstransit', 'providers': ['stops']},
            ],
        },
    )

    appearance_values = {
        scenario.name: helpers.generate_brick_appearance(scenario=scenario)
        for scenario in helpers.Scenarios
    }

    add_experiment(
        consts.SUPERAPP_BUTTONS_APPEARANCE_EXPERIMENT,
        {
            **appearance_values,
            'city_mode': {
                **consts.DEFAULT_APPEARANCE,
                'action': {
                    'mode': 'city',
                    'type': 'city_mode',
                    'screen_name': 'city-mode',
                    'layers_context': {
                        'type': 'multi',
                        'objects': [{'type': 'provider_filter'}],
                    },
                },
            },
        },
    )

    env = helpers.EnvSetup()
    env.header_params_experiment['buttons']['show_from'] = 0
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    supported_actions = env.all_supported_actions
    if not action_supported:
        supported_actions.remove(
            {
                'type': 'city_mode',
                'modes': ['drive', 'masstransit', 'scooters'],
            },
        )

    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
        supported_actions=supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    buttons = offers.get('buttons')
    assert buttons is not None
    button_scenarios = {item['id'].split(':')[0] for item in buttons}

    city_mode_available = city_mode_scenarios and enabled and action_supported

    if city_mode_available:
        candidates = [
            item for item in buttons if item['id'].split(':')[0] == 'city_mode'
        ]
        assert len(candidates) == 1
        item = candidates[0]

        assert item['service'] == 'city'
        assert item['background'] == {'color': 'default_background_color'}
        assert item['text_style'] == {'color': 'default_active_text_color'}
        assert item['icon_tag'] == 'default_icon_tag'
        assert item['title'] == ''
        assert item['action'] == {
            'mode': 'city',
            'type': 'city_mode',
            'screen_name': 'city-mode',
            'layers_context': {
                'type': 'multi',
                'objects': [
                    {
                        'enabled_providers': expected_providers,
                        'type': 'provider_filter',
                    },
                ],
            },
        }

        for scenario in city_mode_scenarios:
            assert scenario not in button_scenarios
    else:
        for scenario in city_mode_scenarios:
            assert scenario in button_scenarios


@pytest.mark.parametrize(
    'shop_scenario, shop_scenario_expected',
    [
        ('eats_based_shop', 'eats_based_shop'),
        ('native_shop', 'native_shop'),
        (None, 'eats_based_shop'),
    ],
)
async def test_shop_scenario_control(
        taxi_shortcuts,
        add_appearance_experiments,
        add_experiment,
        shop_scenario,
        shop_scenario_expected,
):
    add_appearance_experiments()
    if shop_scenario:
        add_experiment(consts.SHOP_SCENARIO_EXP, {'scenario': shop_scenario})

    env = helpers.EnvSetup()
    env.header_params_experiment['buttons']['show_from'] = 0
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    supported_actions = env.all_supported_actions

    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=env.availability_support,
        supported_actions=supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    buttons = offers.get('buttons')
    assert buttons is not None

    shop_button = None
    for button in buttons:
        if button['id'].split(':')[0] == shop_scenario_expected:
            shop_button = button
            break

    assert shop_button is not None
    assert 'service' in shop_button
    assert shop_button['service'] == 'shop'


@pytest.mark.parametrize(
    'expect_buttons',
    [pytest.param(True, id='buttons'), pytest.param(False, id='bricks')],
)
async def test_bricks_buttons_counters(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        expect_buttons,
):
    counters = {
        'items': [{'id': 'cid', 'max_show_count': 3, 'max_usage_count': 1}],
    }

    add_appearance_experiments(overrides={'counters': counters})

    env = helpers.EnvSetup()
    if expect_buttons:
        env.header_params_experiment['buttons']['show_from'] = 1
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    availability_support = helpers.ScenarioSupport(
        available_scenarios=[
            helpers.Scenarios.taxi_route_input,
            helpers.Scenarios.eats_based_eats,
            helpers.Scenarios.eats_based_grocery,
        ],
    ).to_services_availability()

    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=availability_support,
        supported_actions=env.all_supported_actions,
        multicolor_service_icons_supported=True,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    buttons = offers.get('buttons')
    bricks = offers.get('header')

    if expect_buttons:
        assert buttons is not None and bricks is None
        entrypoints = buttons
    else:
        assert bricks is not None and buttons is None
        entrypoints = bricks

    expected_services = (None, 'eats', 'grocery')

    assert len(entrypoints) == len(expected_services)
    for (item, service) in zip(entrypoints, expected_services):
        assert item.get('counters') == counters
        assert item.get('service') == service  # None for taxi_route_input


@pytest.mark.translations(
    client_messages={'default_title_key': {'ru': 'default_translated_title'}},
)
@pytest.mark.parametrize('expect_buttons', [True, False])
@pytest.mark.parametrize('prefer_native_brick', [True, False])
async def test_delivery_dashboard_action(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        expect_buttons,
        prefer_native_brick,
):
    add_appearance_experiments(
        overrides={'action': {'type': 'delivery_dashboard'}},
        predicates=[
            helpers.exp_create_contains_predicate(
                'supported_features', 'delivery_dashboard',
            ),
        ],
    )
    add_experiment(
        consts.DELIVERY_AVAILABILITY_EXPERIMENT,
        {'available': True, 'prefer_native_brick': prefer_native_brick},
    )

    env = helpers.EnvSetup()
    env.header_params_experiment['buttons']['show_from'] = (
        1 if expect_buttons else 20
    )
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    availability_support = helpers.ScenarioSupport(
        available_scenarios=[
            helpers.Scenarios.header_delivery,
            helpers.Scenarios.taxi_header_delivery,
        ],
    ).to_services_availability()

    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=availability_support,
        supported_actions=env.all_supported_actions,
    )
    payload['shortcuts']['supported_features'].append(
        {'type': 'delivery_dashboard', 'prefetch_strategies': []},
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    buttons = offers.get('buttons')
    bricks = offers.get('header')

    if expect_buttons:
        assert buttons is not None and bricks is None
        entrypoints = buttons
    else:
        assert bricks is not None and buttons is None
        entrypoints = bricks

    assert len(entrypoints) == 2, entrypoints
    assert entrypoints[1]['service'] == 'delivery'
    assert entrypoints[1]['action'] == {'type': 'delivery_dashboard'}


@pytest.mark.parametrize(
    'expect_buttons',
    [pytest.param(True, id='buttons'), pytest.param(False, id='bricks')],
)
async def test_parameterized_deeplink(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        expect_buttons,
):
    add_appearance_experiments(
        overrides={
            'parameterized_deeplink': {
                'default_text': 'yandextaxi://...',
                'parameterized_text': (
                    'yandextaxi://external?service=service'
                    '&delivery_lon={b_lon:f}&delivery_lat={b_lat:f}'
                ),
                'params': ['b_lon', 'b_lat'],
            },
        },
    )

    env = helpers.EnvSetup()
    if expect_buttons:
        env.header_params_experiment['buttons']['show_from'] = 1
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    availability_support = helpers.ScenarioSupport(
        available_scenarios=[
            helpers.Scenarios.taxi_route_input,
            helpers.Scenarios.eats_based_eats,
            helpers.Scenarios.eats_based_grocery,
        ],
    ).to_services_availability()

    payload = helpers.build_header_request(
        client_support=env.client_support,
        availability_support=availability_support,
        supported_actions=env.all_supported_actions,
        multicolor_service_icons_supported=True,
        state={'fields': [{'type': 'b', 'position': [37.5, 55.5]}]},
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    buttons = offers.get('buttons')
    bricks = offers.get('header')

    if expect_buttons:
        assert buttons is not None and bricks is None
        entrypoints = buttons
    else:
        assert bricks is not None and buttons is None
        entrypoints = bricks

    expected_services = (None, 'eats', 'grocery')

    assert len(entrypoints) == len(expected_services)
    for item, service in zip(entrypoints, expected_services):
        assert item.get('service') == service  # None for taxi_route_input
        if service is not None:
            assert 'action' in item
            if expect_buttons:
                assert item['action'].get('type') == 'deeplink'
            assert item['action'].get('deeplink') == (
                'yandextaxi://external?service=service'
                '&delivery_lon=37.500000&delivery_lat=55.500000'
            )
