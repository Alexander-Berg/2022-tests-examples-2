import pytest

from tests_shortcuts import consts
from tests_shortcuts import helpers

CITY_MODE_ACTION_FOR_EXP = {
    'action': {
        'mode': 'city',
        'type': 'city_mode',
        'screen_name': 'city-mode',
        'layers_context': {
            'type': 'multi',
            'objects': [{'type': 'provider_filter'}],
        },
    },
}

CITY_MODE_ACTION_EXPECTED = {
    'action': {
        'mode': 'city',
        'type': 'city_mode',
        'screen_name': 'city-mode',
        'layers_context': {
            'type': 'multi',
            'objects': [
                {
                    'enabled_providers': ['drive', 'stops', 'scooters'],
                    'type': 'provider_filter',
                },
            ],
        },
    },
}

CITY_MODE_TOP_SCREEN_OBJECT = {
    'id': 'some_button',
    'type': 'round_button',
    'title': {
        'items': [
            {
                'type': 'image',
                'width': 25,
                'image_tag': 'superapp_city_mode_icon',
                'vertical_alignment': 'center',
            },
            {
                'text': '  В город',
                'type': 'text',
                'color': '#21201F',
                'font_size': 16,
                'font_style': 'normal',
                'font_weight': 'light',
            },
        ],
    },
}
DISCOVERY_MASSTRANSIT_TOP_SCREEN_OBJECT = {
    'id': 'some_button',
    'type': 'round_button',
    'title': {
        'items': [
            {
                'text': '  Транспорт',
                'type': 'text',
                'color': '#21201F',
                'font_size': 16,
                'font_style': 'normal',
                'font_weight': 'light',
            },
        ],
    },
    'action': {'mode': 'masstransit', 'type': 'discovery'},
}
DISCOVERY_SCOOTERS_TOP_SCREEN_OBJECT = {
    'id': 'some_button',
    'type': 'round_button',
    'title': {
        'items': [
            {
                'text': '  Самокаты',
                'type': 'text',
                'color': '#21201F',
                'font_size': 16,
                'font_style': 'normal',
                'font_weight': 'light',
            },
        ],
    },
    'action': {'mode': 'scooters', 'type': 'discovery'},
}
SCOOTERS_QR_SCAN_TOP_SCREEN_OBJECT = {
    'id': 'some_button',
    'type': 'icon_button',
    'icon': 'scooters_qr_scan',
    'action': {'type': 'scooters_qr_scan'},
}
SUPPORTED_ACTIONS = [
    {'type': 'deeplink'},
    {'type': 'taxi:summary-redirect'},
    {'type': 'taxi:route-input'},
    {'type': 'shortcuts_screen'},
]
CITY_MODE_SUPPORTED_ACTION = {
    'type': 'city_mode',
    'modes': ['drive', 'masstransit', 'scooters'],
}
DISCOVERY_SUPPORTED_ACTION = {
    'type': 'discovery',
    'modes': ['masstransit', 'drive', 'scooters'],
}
SCOOTERS_QR_SCAN_SUPPORTED_ACTION = {'type': 'scooters_qr_scan'}
EXTRA_SUPPORTED_ACTIONS = [
    CITY_MODE_SUPPORTED_ACTION,
    SCOOTERS_QR_SCAN_SUPPORTED_ACTION,
    DISCOVERY_SUPPORTED_ACTION,
]
CITY_MODE_SCENARIOS = [
    'discovery_scooters',
    'discovery_drive',
    'discovery_masstransit',
]


def build_request(extra_supported_actions, available_services=None):
    env = helpers.EnvSetup(available_services=available_services)
    payload = {
        'shortcuts': {
            'supported_features': [
                {'type': 'header-deeplink', 'prefetch_strategies': []},
                {
                    'type': 'eats-based:superapp',
                    'services': ['eats', 'grocery', 'pharmacy'],
                    'prefetch_strategies': [],
                },
                {
                    'prefetch_strategies': [],
                    'services': [],
                    'type': 'header-action-driven',
                },
                {
                    'prefetch_strategies': [],
                    'services': [],
                    'type': 'drive:fixpoint-offers',
                },
                {
                    'prefetch_strategies': [],
                    'services': [],
                    'type': 'action-driven',
                },
            ],
            'supported_sections': env.all_supported_sections,
            'supported_actions': SUPPORTED_ACTIONS + extra_supported_actions,
        },
        'grid': {'id': 'id', 'width': 6, 'cells': []},
        'services_availability': env.availability_support,
    }
    return payload


@pytest.mark.parametrize(
    'available_services, expected_count_at_top_screen',
    [
        (None, 1),
        (
            {
                'taxi',
                'grocery',
                'shop',
                'masstransit',
                'market',
                'pharmacy',
                'drive',
            },
            0,
        ),
    ],
)
@pytest.mark.parametrize(
    'extra_supported_actions, top_screen_object, '
    'expected_top_screen_object, covered_scenarios',
    [
        (
            [SCOOTERS_QR_SCAN_SUPPORTED_ACTION],
            SCOOTERS_QR_SCAN_TOP_SCREEN_OBJECT,
            SCOOTERS_QR_SCAN_TOP_SCREEN_OBJECT,
            [],
        ),
    ],
)
async def test_top_screen_qr_scan_disable(
        taxi_shortcuts,
        add_experiment,
        extra_supported_actions,
        top_screen_object,
        expected_top_screen_object,
        covered_scenarios,
        available_services,
        expected_count_at_top_screen,
):
    exp_value = {
        'enabled': True,
        'city_mode_scenarios_with_priority': CITY_MODE_SCENARIOS,
    }
    exp_value['top_screen_objects'] = [top_screen_object]
    add_experiment(consts.CITY_MODE_PARAMS_EXP, exp_value)

    extra_supported_actions = extra_supported_actions

    request = build_request(
        extra_supported_actions=extra_supported_actions,
        available_services=available_services,
    )

    response = await taxi_shortcuts.post(consts.URL, request)

    assert response.status_code == 200
    data = response.json()
    assert 'top_screen_objects' in data
    length = len(data['top_screen_objects'])
    assert length == expected_count_at_top_screen
    if length != 0:
        assert 'id' in data['top_screen_objects'][0]
        assert (
            data['top_screen_objects'][0]['id'].split(':')[0]
            == expected_top_screen_object['id']
        )
        data['top_screen_objects'][0]['id'] = expected_top_screen_object['id']
        assert data['top_screen_objects'][0] == expected_top_screen_object


@pytest.mark.parametrize('support_action', [True, False])
@pytest.mark.parametrize(
    'extra_supported_actions, top_screen_object, '
    'expected_top_screen_object, covered_scenarios',
    [
        (
            [CITY_MODE_SUPPORTED_ACTION, DISCOVERY_SUPPORTED_ACTION],
            {**CITY_MODE_TOP_SCREEN_OBJECT, **CITY_MODE_ACTION_FOR_EXP},
            {**CITY_MODE_TOP_SCREEN_OBJECT, **CITY_MODE_ACTION_EXPECTED},
            ['city_mode'],
        ),
        (
            [SCOOTERS_QR_SCAN_SUPPORTED_ACTION],
            SCOOTERS_QR_SCAN_TOP_SCREEN_OBJECT,
            SCOOTERS_QR_SCAN_TOP_SCREEN_OBJECT,
            [],
        ),
        (
            [DISCOVERY_SUPPORTED_ACTION],
            DISCOVERY_MASSTRANSIT_TOP_SCREEN_OBJECT,
            DISCOVERY_MASSTRANSIT_TOP_SCREEN_OBJECT,
            ['discovery_masstransit'],
        ),
        (
            [DISCOVERY_SUPPORTED_ACTION],
            DISCOVERY_SCOOTERS_TOP_SCREEN_OBJECT,
            DISCOVERY_SCOOTERS_TOP_SCREEN_OBJECT,
            ['discovery_scooters'],
        ),
    ],
)
@pytest.mark.parametrize('with_top_screen_object', [True, False])
async def test_top_screen_objects(
        taxi_shortcuts,
        add_experiment,
        support_action,
        add_appearance_experiments,
        extra_supported_actions,
        top_screen_object,
        expected_top_screen_object,
        with_top_screen_object,
        covered_scenarios,
):
    add_appearance_experiments()
    env = helpers.EnvSetup()
    env.header_params_experiment['buttons']['show_from'] = 0
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT, env.header_params_experiment,
    )

    exp_value = {
        'enabled': True,
        'city_mode_scenarios_with_priority': CITY_MODE_SCENARIOS,
    }
    if with_top_screen_object:
        exp_value['top_screen_objects'] = [top_screen_object]

    add_experiment(consts.CITY_MODE_PARAMS_EXP, exp_value)

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

    extra_supported_actions = extra_supported_actions
    if not support_action:
        extra_supported_actions = []

    request = build_request(extra_supported_actions=extra_supported_actions)
    if not support_action:
        request['shortcuts']['supported_actions'].remove({'type': 'deeplink'})
    response = await taxi_shortcuts.post(consts.URL, request)
    assert response.status_code == 200
    data = response.json()

    offers = data['offers']
    buttons = offers.get('buttons')
    assert buttons is not None
    button_scenarios = {item['id'].split(':')[0] for item in buttons}

    if with_top_screen_object and support_action:
        assert 'top_screen_objects' in data
        assert len(data['top_screen_objects']) == 1
        assert 'id' in data['top_screen_objects'][0]
        assert (
            data['top_screen_objects'][0]['id'].split(':')[0]
            == expected_top_screen_object['id']
        )

        data['top_screen_objects'][0]['id'] = expected_top_screen_object['id']
        assert data['top_screen_objects'][0] == expected_top_screen_object

        for scenario in covered_scenarios:
            assert scenario not in button_scenarios
    else:
        if not with_top_screen_object:
            assert 'top_screen_objects' not in data

            if support_action:
                for scenario in covered_scenarios:
                    assert scenario in button_scenarios
        elif not support_action:
            assert 'top_screen_objects' in data
            assert not data['top_screen_objects']


async def test_without_exp(taxi_shortcuts):
    request = build_request(extra_supported_actions=EXTRA_SUPPORTED_ACTIONS)

    response = await taxi_shortcuts.post(consts.URL, request)
    assert response.status_code == 200
    data = response.json()

    assert 'top_screen_objects' not in data
