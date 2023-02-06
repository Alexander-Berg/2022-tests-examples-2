import copy

import pytest

from tests_shortcuts import consts
from tests_shortcuts import helpers

VALID_ANIMATION_TAG = 'valid_animation_tag'

EATS_DEFAULT_ANIMATION = {
    'count': 1,
    'delay': 0.5,
    'id': VALID_ANIMATION_TAG,
    'show_policy': {'id': VALID_ANIMATION_TAG, 'max_show_count': 2},
    'source': {'type': 'local', 'name': 'animation_file_name'},
}

LOCAL_SOURCE = {'type': 'local', 'name': 'animation_file_name'}
REMOTE_SOURCE = {'type': 'remote', 'url': 'animation_url'}
DEFAULT_SCENARIO = helpers.Scenarios.eats_based_eats
DEFAULT_SERVICE = 'eats'


def create_appearance(source, animation_id=VALID_ANIMATION_TAG):
    return {
        DEFAULT_SCENARIO.name: {
            **copy.deepcopy(consts.DEFAULT_APPEARANCE),
            'animation': {
                **EATS_DEFAULT_ANIMATION,
                'id': animation_id,
                'source': source,
            },
            'deeplink': 'default_deeplink',
        },
    }


@pytest.mark.parametrize(
    'appearance, tag_is_valid',
    [
        (create_appearance(LOCAL_SOURCE), True),
        (create_appearance(REMOTE_SOURCE), True),
        (create_appearance(LOCAL_SOURCE, 'new_tag'), False),
    ],
)
@pytest.mark.config(SHORTCUTS_BUTTONS_ANIMATION_TAGS=[VALID_ANIMATION_TAG])
async def test_buttons_animations(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        appearance,
        tag_is_valid,
):
    add_appearance_experiments(appearance_ext=appearance)

    scenario_support = helpers.ScenarioSupport(
        available_scenarios=[DEFAULT_SCENARIO],
        available_services=[DEFAULT_SERVICE],
    )
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT,
        scenario_support.to_header_params_experiment(show_from=1),
    )

    payload = helpers.build_header_request(
        client_support=scenario_support.to_client_support(),
        availability_support=scenario_support.to_services_availability(),
        supported_actions=helpers.EnvSetup().all_supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, json=payload)

    assert response.status_code == 200

    offers = response.json()['offers']
    assert 'buttons' in offers
    buttons = offers['buttons']
    assert len(buttons) == 1
    button = buttons[0]
    if tag_is_valid:
        assert (
            button['animation']
            == appearance[DEFAULT_SCENARIO.name]['animation']
        )
    else:
        assert 'animation' not in button


@pytest.mark.config(SHORTCUTS_BUTTONS_ANIMATION_TAGS=[VALID_ANIMATION_TAG])
async def test_animations_threshold(
        taxi_shortcuts, add_experiment, add_appearance_experiments,
):
    available_scenarios = [
        helpers.Scenarios.eats_based_eats,
        helpers.Scenarios.eats_based_grocery,
    ]
    appearance_ext = {}
    for scenario in available_scenarios:
        appearance_ext[scenario.name] = copy.deepcopy(
            consts.DEFAULT_APPEARANCE,
        )
        appearance_ext[scenario.name]['animation'] = copy.deepcopy(
            EATS_DEFAULT_ANIMATION,
        )
        appearance_ext[scenario.name]['deeplink'] = 'default_deeplink'

    add_appearance_experiments(appearance_ext=appearance_ext)

    scenario_support = helpers.ScenarioSupport(
        available_scenarios=available_scenarios,
        available_services=['eats', 'grocery'],
    )
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT,
        scenario_support.to_header_params_experiment(show_from=1),
    )

    payload = helpers.build_header_request(
        client_support=scenario_support.to_client_support(),
        availability_support=scenario_support.to_services_availability(),
        supported_actions=helpers.EnvSetup().all_supported_actions,
    )

    response = await taxi_shortcuts.post(consts.URL, json=payload)

    assert response.status_code == 200

    offers = response.json()['offers']
    assert 'buttons' in offers
    buttons = offers['buttons']
    assert len(buttons) == 2
    for button in buttons:
        assert 'animation' not in button
