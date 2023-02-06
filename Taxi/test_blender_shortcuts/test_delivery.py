import pytest

from tests_shortcuts import consts
from tests_shortcuts import helpers


@pytest.mark.parametrize('expect_buttons', [True, False])
@pytest.mark.parametrize('delivery_available', [True, False])
@pytest.mark.parametrize('prefer_native_brick', [True, False])
@pytest.mark.parametrize('is_native_brick_supported_by_client', [True, False])
async def test_delivery_availability(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        delivery_available,
        prefer_native_brick,
        is_native_brick_supported_by_client,
        expect_buttons,
):
    # delivery is special: it is controlled by experiment for now, and its
    # availability detection should be moved elsewhere
    add_experiment(
        consts.DELIVERY_AVAILABILITY_EXPERIMENT,
        {
            'available': delivery_available,
            'prefer_native_brick': prefer_native_brick,
        },
    )

    add_appearance_experiments()

    available_scenarios = helpers.ScenarioSupport(
        available_scenarios=[
            helpers.Scenarios.taxi_route_input,
            helpers.Scenarios.eats_based_eats,
            helpers.Scenarios.header_delivery,
            helpers.Scenarios.taxi_header_delivery,
        ],
    )

    header_params_exp_value = available_scenarios.to_header_params_experiment()
    if expect_buttons:
        header_params_exp_value['buttons']['show_from'] = 1
    add_experiment(consts.HEADER_PARAMS_EXPERIMENT, header_params_exp_value)

    env = helpers.EnvSetup()
    client_support_exceptions = {helpers.Scenarios.eats_based_pharmacy}
    if not is_native_brick_supported_by_client:
        client_support_exceptions.add(helpers.Scenarios.taxi_header_delivery)

    payload = helpers.build_header_request(
        client_support=helpers.ScenarioSupport(
            helpers.Scenarios.get_all_except(client_support_exceptions),
        ).to_client_support(),
        availability_support=env.availability_support,
        supported_actions=env.all_supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offers = response.json()['offers']

    # derive resulting types from client types

    if expect_buttons:
        assert offers.get('header') is None
        result_buttons = {
            btn['id'].split(':')[0] for btn in offers.get('buttons', [])
        }
        expected_buttons = {'eats_based_eats', 'taxi_route_input'}
        if delivery_available:
            expected_buttons.add('header_delivery')

        assert result_buttons == expected_buttons
        return

    assert offers.get('buttons') is None
    result_bricks = {brick['type'] for brick in offers.get('header', [])}
    expected_bricks = {'taxi:route-input', 'eats-based:superapp'}

    if delivery_available:
        delivery_brick = (
            'taxi:header-summary-redirect'
            if prefer_native_brick and is_native_brick_supported_by_client
            else 'header-deeplink'
        )
        expected_bricks.add(delivery_brick)
    assert result_bricks == expected_bricks


@pytest.mark.parametrize('expect_buttons', [True, False])
@pytest.mark.parametrize(
    'native_brick_params',
    [
        {'vertical': 'vertical', 'class': 'class', 'state': 'expanded'},
        {'vertical': 'vertical', 'class': 'class'},
        {},
    ],
)
@pytest.mark.parametrize('append_service_delivery', [True, False])
async def test_native_delivery(
        taxi_shortcuts,
        taxi_config,
        add_experiment,
        add_appearance_experiments,
        native_brick_params,
        append_service_delivery,
        expect_buttons,
):
    taxi_config.set_values(
        {'SHORTCUTS_APPEND_SERVICE_DELIVERY': append_service_delivery},
    )
    # delivery is special: it is controlled by experiment for now, and its
    # availability detection should be moved elsewhere
    add_experiment(
        consts.DELIVERY_AVAILABILITY_EXPERIMENT,
        {'available': True, 'prefer_native_brick': True},
    )

    available_scenarios = helpers.ScenarioSupport(
        available_scenarios=[
            helpers.Scenarios.eats_based_eats,
            helpers.Scenarios.header_delivery,
            helpers.Scenarios.taxi_header_delivery,
            helpers.Scenarios.discovery_scooters,
        ],
    )

    appearances = {}
    for scenario in available_scenarios.ordered_available_scenarios:
        add_fields = (
            native_brick_params
            if scenario == helpers.Scenarios.taxi_header_delivery
            else {}
        )
        appearance = helpers.generate_brick_appearance(overrides=add_fields)
        if scenario == helpers.Scenarios.taxi_header_delivery:
            del appearance['deeplink']
        appearances[scenario.name] = appearance
    add_appearance_experiments(appearances)

    header_params_exp_value = available_scenarios.to_header_params_experiment()
    if expect_buttons:
        header_params_exp_value['buttons']['show_from'] = 1
    add_experiment(consts.HEADER_PARAMS_EXPERIMENT, header_params_exp_value)

    env = helpers.EnvSetup()
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
        actions = [
            (button['service'], button['action'])
            for button in sorted(buttons, key=lambda button: button['service'])
        ]
        assert actions == [
            (
                'delivery',
                {
                    'type': 'taxi:summary-redirect',
                    'state': 'collapsed',  # at least should be state
                    **native_brick_params,
                },
            ),
            ('eats', {'deeplink': 'default_deeplink', 'type': 'deeplink'}),
            ('scooters', {'deeplink': 'default_deeplink', 'type': 'deeplink'}),
        ]
    else:
        assert bricks is not None and buttons is None
        native_delivery_brick = [
            brick
            for brick in bricks
            if brick['type'] == 'taxi:header-summary-redirect'
        ][0]
        assert native_delivery_brick['action'] == {
            'state': 'collapsed',  # at least should be state
            **native_brick_params,
        }
