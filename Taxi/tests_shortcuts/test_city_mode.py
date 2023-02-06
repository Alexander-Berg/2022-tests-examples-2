# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_shortcuts import consts
from tests_shortcuts import helpers

MASSTRANSIT_ELEM = {
    'action': consts.TYPED_MASSTRANSIT_ACTION,
    'service': 'masstransit',
    'shortcut_id': 'discovery_masstransit',
}
DRIVE_ELEM = {
    'action': consts.TYPED_DRIVE_ACTION,
    'service': 'drive',
    'shortcut_id': 'discovery_drive',
}
SCOOTERS_ELEM = {
    'action': consts.TYPED_SCOOTERS_ACTION,
    'service': 'scooters',
    'shortcut_id': 'discovery_scooters',
}
SCENARIO_TO_ELEM = {
    helpers.Scenarios.discovery_masstransit: MASSTRANSIT_ELEM,
    helpers.Scenarios.discovery_drive: DRIVE_ELEM,
    helpers.Scenarios.discovery_scooters: SCOOTERS_ELEM,
}
DEFAULT_SCENARIOS = [
    helpers.Scenarios.discovery_masstransit,
    helpers.Scenarios.discovery_drive,
    helpers.Scenarios.discovery_scooters,
]
LAYOUT_OPTIONS = [[6], [3, 3], [6, 3, 3], [3, 3, 3, 3], [4, 3, 3, 3, 3]]


def build_request(
        add_experiment,
        add_appearance_experiments=None,
        overrides=None,
        supported_features=None,
        supported_actions=None,
        deathflag_services=None,
        available_services=None,
):
    if overrides is None:
        overrides = {}
    if add_appearance_experiments is not None:
        add_appearance_experiments(overrides=overrides)
    basic_scenarios = [
        helpers.Scenarios.taxi_route_input,
        helpers.Scenarios.eats_based_eats,
        helpers.Scenarios.eats_based_grocery,
        helpers.Scenarios.eats_based_pharmacy,
        helpers.Scenarios.discovery_masstransit,
        helpers.Scenarios.discovery_drive,
        helpers.Scenarios.discovery_scooters,
        helpers.Scenarios.discovery_restaurants,
        helpers.Scenarios.discovery_contacts,
    ]

    env = helpers.EnvSetup()
    header_elements_params = {
        'enabled': True,
        'priority': [scenario.name for scenario in basic_scenarios],
    }
    env.header_params_experiment['bricks'].update(header_elements_params)
    env.header_params_experiment['buttons'].update(header_elements_params)
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    client_support = helpers.ScenarioSupport(
        available_scenarios=basic_scenarios,
    ).to_client_support()

    availability_support = helpers.ScenarioSupport(
        available_scenarios=basic_scenarios,
        deathflag_services=deathflag_services,
        available_services=available_services,
    ).to_services_availability()
    payload = {
        'zone_name': 'moscow',
        'services_availability': availability_support,
        'shortcuts': {
            'supported_actions': (
                supported_actions
                if supported_actions is not None
                else env.all_supported_actions
            ),
            'supported_features': (
                supported_features
                if supported_features is not None
                else client_support
            ),
            'supported_sections': env.all_supported_sections,
        },
    }
    return payload


def check_response(data, city_mode_scenarios, expected_layouts):
    if expected_layouts is None:
        assert 'header' not in data['offers']
    else:
        header_elems = []
        if city_mode_scenarios:
            assert 'header' in data['offers']
            for elem in data['offers']['header']:
                assert 'action' in elem
                assert 'service' in elem
                assert 'width' in elem
                assert 'height' in elem
                header_elems.append(
                    {
                        'shortcut_id': elem['shortcut_id'].split(':')[0],
                        'action': elem['action'],
                        'service': elem['service'],
                        'width': elem['width'],
                        'height': elem['height'],
                    },
                )

            assert 'sections' in data
            assert len(data['sections']) == 1
            assert 'shortcut_ids' in data['sections'][0]
            shortcut_ids = [
                elem.split(':')[0]
                for elem in data['sections'][0]['shortcut_ids']
            ]
            assert shortcut_ids == [
                scenario.name for scenario in city_mode_scenarios
            ]

        expected_header_elems = []
        assert len(city_mode_scenarios) == len(expected_layouts)
        bricks_size = len(city_mode_scenarios)
        for i in range(bricks_size):
            expected_header_elems.append(
                {
                    **SCENARIO_TO_ELEM[city_mode_scenarios[i]],
                    'width': expected_layouts[i],
                    'height': 1,
                },
            )

        assert header_elems == expected_header_elems


@pytest.mark.parametrize(
    'is_available, supported_features, supported_actions,'
    'expected_offer_type, expected_offer_action',
    [
        (
            True,
            [{'prefetch_strategies': [], 'type': 'header-action-driven'}],
            [
                {
                    'type': 'discovery',
                    'modes': ['masstransit', 'drive', 'scooters'],
                },
            ],
            'header-action-driven',
            {
                'type': 'discovery',
                'mode': 'scooters',
                'layers_context': {'param_1': 'xxxx'},
            },
        ),
        (
            False,
            [{'prefetch_strategies': [], 'type': 'header-action-driven'}],
            [
                {
                    'type': 'discovery',
                    'modes': ['masstransit', 'drive', 'scooters'],
                },
            ],
            'header-action-driven',
            None,
        ),
        (
            False,
            [{'prefetch_strategies': [], 'type': 'header-action-driven'}],
            [
                {
                    'type': 'discovery',
                    'modes': ['masstransit', 'drive', 'scooters'],
                },
                {'type': 'deeplink'},
            ],
            'header-action-driven',
            {'deeplink': 'smt..', 'type': 'deeplink'},
        ),
        (
            False,
            [{'prefetch_strategies': [], 'type': 'header-deeplink'}],
            [
                {
                    'type': 'discovery',
                    'modes': ['masstransit', 'drive', 'scooters'],
                },
                {'type': 'deeplink'},
            ],
            None,
            None,
        ),
        (
            False,
            [{'prefetch_strategies': [], 'type': 'header-action-driven'}],
            [{'type': 'deeplink'}],
            'header-action-driven',
            {'deeplink': 'smt..', 'type': 'deeplink'},
        ),
        (
            False,
            [
                {
                    'prefetch_strategies': [],
                    'services': ['scooters'],
                    'type': 'header-action-driven',
                },
            ],
            [{'type': 'deeplink'}],
            'header-action-driven',
            {'deeplink': 'smt..', 'type': 'deeplink'},
        ),
    ],
)
@pytest.mark.experiments3(filename='experiments3_for_city_mode.json')
async def test_city_mode_scooters_offers(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        is_available,
        supported_features,
        supported_actions,
        expected_offer_type,
        expected_offer_action,
):
    add_experiment(
        consts.CITY_MODE_PARAMS_EXP,
        {
            'enabled': True,
            'city_mode_scenarios_with_priority': [
                helpers.Scenarios.discovery_scooters.name,
            ],
            'layout_options': LAYOUT_OPTIONS,
        },
    )
    if is_available:
        deathflag_services = {}
        available_services = {'scooters'}
    else:
        deathflag_services = {'scooters'}
        available_services = {}

    request = build_request(
        add_experiment,
        add_appearance_experiments,
        available_services=available_services,
        deathflag_services=deathflag_services,
        supported_features=supported_features,
        supported_actions=supported_actions,
    )

    response = await taxi_shortcuts.post(consts.CITY_MODE_URL, request)
    assert response.status_code == 200

    data = response.json()

    if expected_offer_type:
        assert 'header' in data['offers'] and data['offers']['header'] != []
        assert data['offers']['header'][0]['type'] == expected_offer_type
        if expected_offer_action:
            assert (
                data['offers']['header'][0]['action'] == expected_offer_action
            )
        else:
            assert 'action' not in data['offers']['header'][0]
    else:
        assert 'header' not in data['offers'] or data['offers']['header'] == []


@pytest.mark.experiments3(filename='experiments3_for_city_mode.json')
async def test_city_mode_contacts(
        taxi_shortcuts, add_experiment, add_appearance_experiments,
):
    deathflag_services = {}
    available_services = {'contacts'}

    request = build_request(
        add_experiment,
        add_appearance_experiments,
        available_services=available_services,
        deathflag_services=deathflag_services,
        supported_features=[
            {'prefetch_strategies': [], 'type': 'header-action-driven'},
        ],
        supported_actions=[
            {
                'type': 'discovery',
                'modes': ['masstransit', 'drive', 'scooters', 'contacts'],
            },
        ],
    )

    response = await taxi_shortcuts.post(consts.CITY_MODE_URL, request)
    assert response.status_code == 200

    data = response.json()

    assert 'header' in data['offers'] and data['offers']['header']
    assert data['offers']['header'][0]['type'] == 'header-action-driven'
    assert data['offers']['header'][0]['action'] == {
        'type': 'discovery',
        'mode': 'contacts',
        'layers_context': {'param_1': 'xxxx'},
    }


@pytest.mark.parametrize(
    'city_mode_scenarios, expected_layouts',
    [
        ([], []),
        ([helpers.Scenarios.discovery_masstransit], [6]),
        ([helpers.Scenarios.discovery_drive], [6]),
        ([helpers.Scenarios.discovery_scooters], [6]),
        (
            [
                helpers.Scenarios.discovery_masstransit,
                helpers.Scenarios.discovery_drive,
            ],
            [3, 3],
        ),
        (
            [
                helpers.Scenarios.discovery_drive,
                helpers.Scenarios.discovery_scooters,
            ],
            [3, 3],
        ),
        (
            [
                helpers.Scenarios.discovery_masstransit,
                helpers.Scenarios.discovery_scooters,
            ],
            [3, 3],
        ),
        (
            [
                helpers.Scenarios.discovery_masstransit,
                helpers.Scenarios.discovery_drive,
                helpers.Scenarios.discovery_scooters,
            ],
            [6, 3, 3],
        ),
    ],
)
@pytest.mark.config(SHORTCUTS_METRICS_ENABLED=True)
@pytest.mark.experiments3(filename='experiments3_for_city_mode.json')
async def test_city_mode_scenarios_from_exp(
        taxi_shortcuts,
        taxi_shortcuts_monitor,
        city_mode_scenarios,
        expected_layouts,
        add_experiment,
        add_appearance_experiments,
):
    add_experiment(
        consts.CITY_MODE_PARAMS_EXP,
        {
            'enabled': True,
            'city_mode_scenarios_with_priority': [
                scenario.name for scenario in city_mode_scenarios
            ],
            'layout_options': LAYOUT_OPTIONS,
        },
    )

    request = build_request(add_experiment, add_appearance_experiments)

    async with metrics_helpers.MetricsCollector(
            taxi_shortcuts_monitor,
            sensor='shortcuts_entrypoints_product_metrics',
    ) as collector:
        response = await taxi_shortcuts.post(consts.CITY_MODE_URL, request)

    assert response.status_code == 200
    data = response.json()

    check_response(data, city_mode_scenarios, expected_layouts)

    metrics = sorted(
        collector.collected_metrics, key=lambda it: it.labels['scenario'],
    )

    expected_metrics = []
    for scenario in city_mode_scenarios:
        expected_metrics.append(
            metrics_helpers.Metric(
                labels={
                    'sensor': 'shortcuts_entrypoints_product_metrics',
                    'zone': 'moscow',
                    'scenario': scenario.name,
                    'entrypoint': 'bricks',
                    'screen': 'city-mode',
                },
                value=1,
            ),
        )
    expected_metrics = sorted(
        expected_metrics, key=lambda it: it.labels['scenario'],
    )

    assert metrics == expected_metrics


@pytest.mark.parametrize(
    'city_mode_scenarios, overrides, expected_action, '
    'expected_offer_type, supported_actions',
    [
        (
            [helpers.Scenarios.discovery_masstransit],
            {'deathbrick_deeplink': 'mydeeplink'},
            {
                'layers_context': {'param_1': 'xxxx'},
                'mode': 'masstransit',
                'type': 'discovery',
            },
            'header-action-driven',
            None,
        ),
        (
            [helpers.Scenarios.discovery_scooters],
            {'deathbrick_deeplink': 'mydeeplink'},
            {'deeplink': 'mydeeplink', 'type': 'deeplink'},
            'header-action-driven',
            None,
        ),
        (
            [helpers.Scenarios.discovery_scooters],
            None,
            {
                'layers_context': {'param_1': 'xxxx'},
                'mode': 'scooters',
                'type': 'discovery',
            },
            'header-action-driven',
            None,
        ),
        (
            [helpers.Scenarios.discovery_restaurants],
            {},
            {
                'layers_context': {'param_1': 'xxxx'},
                'type': 'discovery',
                'mode': 'restaurants',
            },
            'header-action-driven',
            [
                {
                    'type': 'discovery',
                    'modes': [
                        'masstransit',
                        'drive',
                        'scooters',
                        'restaurants',
                    ],
                },
            ],
        ),
    ],
)
@pytest.mark.experiments3(filename='experiments3_for_city_mode.json')
async def test_city_mode_deathbrick_deeplink(
        taxi_shortcuts,
        taxi_shortcuts_monitor,
        city_mode_scenarios,
        expected_offer_type,
        expected_action,
        add_experiment,
        add_appearance_experiments,
        overrides,
        supported_actions,
):
    add_experiment(
        consts.CITY_MODE_PARAMS_EXP,
        {
            'enabled': True,
            'city_mode_scenarios_with_priority': [
                scenario.name for scenario in city_mode_scenarios
            ],
            'layout_options': LAYOUT_OPTIONS,
        },
    )
    request = build_request(
        add_experiment,
        add_appearance_experiments,
        overrides,
        supported_actions=supported_actions,
    )

    response = await taxi_shortcuts.post(consts.CITY_MODE_URL, request)

    assert response.status_code == 200
    data = response.json()
    for header in data['offers']['header']:
        assert header['action'] == expected_action
        assert header['type'] == expected_offer_type


@pytest.mark.parametrize(
    'layout_options', [None, [[6], [3, 3]], [[6], [3, 3], [6, 3]]],
)
@pytest.mark.experiments3(filename='experiments3_for_city_mode.json')
async def test_layout_options_errors(
        taxi_shortcuts,
        layout_options,
        add_experiment,
        add_appearance_experiments,
):
    city_mode_scenarios = [
        helpers.Scenarios.discovery_masstransit,
        helpers.Scenarios.discovery_drive,
        helpers.Scenarios.discovery_scooters,
    ]
    city_mode_exp_value = {
        'enabled': True,
        'city_mode_scenarios_with_priority': [
            scenario.name for scenario in city_mode_scenarios
        ],
    }
    if layout_options:
        city_mode_exp_value['layout_options'] = layout_options
    add_experiment(consts.CITY_MODE_PARAMS_EXP, city_mode_exp_value)

    request = build_request(add_experiment, add_appearance_experiments)
    response = await taxi_shortcuts.post(consts.CITY_MODE_URL, request)
    assert response.status_code == 200
    data = response.json()

    check_response(data, city_mode_scenarios, None)


@pytest.mark.experiments3(filename='experiments3_for_city_mode.json')
async def test_none_city_mode_params_exp(
        taxi_shortcuts, add_experiment, add_appearance_experiments,
):
    add_experiment(consts.CITY_MODE_PARAMS_EXP, None)

    request = build_request(add_experiment, add_appearance_experiments)
    response = await taxi_shortcuts.post(consts.CITY_MODE_URL, request)
    assert response.status_code == 200
    data = response.json()

    assert 'header' not in data['offers']
    assert len(data['sections']) == 1
    assert data['sections'][0] == {
        'shortcut_ids': [],
        'type': 'items_linear_grid',
        'typed_header': {
            'lead': {'title': {'text': 'В городе'}, 'type': 'subtitle'},
            'type': 'list_item',
        },
    }


@pytest.mark.parametrize(
    'has_typed_header, tanker_key',
    [(True, None), (True, consts.CITY_SCREEN_TITLE_TANKER_KEY), (False, None)],
)
@pytest.mark.translations(
    client_messages={
        consts.CITY_SCREEN_TITLE_TANKER_KEY: {'ru': 'Город (localized)'},
    },
)
@pytest.mark.experiments3(filename='experiments3_for_city_mode.json')
async def test_typed_header(
        taxi_shortcuts,
        has_typed_header,
        tanker_key,
        add_experiment,
        add_appearance_experiments,
):
    expected_text = 'Город'
    screen_settings_value = {}
    localized_text = {'text': 'Город'}
    if tanker_key:
        localized_text['tanker_key'] = tanker_key
        expected_text = 'Город (localized)'
    if has_typed_header:
        screen_settings_value['city_mode'] = {
            'typed_header': {
                'lead': {
                    'type': 'subtitle',
                    'title': {'text': localized_text},
                },
                'type': 'list_item',
            },
        }
    add_experiment('shortcuts_screen_settings', screen_settings_value)

    request = build_request(add_experiment, add_appearance_experiments)

    response = await taxi_shortcuts.post(consts.CITY_MODE_URL, request)
    assert response.status_code == 200
    data = response.json()

    assert 'sections' in data
    assert len(data['sections']) == 1

    if has_typed_header:
        assert 'typed_header' in data['sections'][0]
        assert data['sections'][0]['typed_header'] == {
            'lead': {'type': 'subtitle', 'title': {'text': expected_text}},
            'type': 'list_item',
        }
    else:
        assert 'typed_header' not in data['sections'][0]
