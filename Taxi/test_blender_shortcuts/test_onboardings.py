import datetime

import pytest

from tests_shortcuts import consts
from tests_shortcuts import helpers


@pytest.mark.parametrize(
    'service, scenario', [('eats', helpers.Scenarios.eats_based_eats)],
)
@pytest.mark.parametrize('offers_key', ['header', 'buttons'])
@pytest.mark.now('2020-09-25T16:50:00+0000')
async def test_new_user_kwargs(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        load_json,
        mocked_time,
        service,
        scenario,
        offers_key,
):
    scenario_support = helpers.ScenarioSupport(
        available_scenarios=[scenario], available_services=[service],
    )

    reg_timestamp = datetime.datetime.fromisoformat('2020-09-20T00:00:00')
    user_phone_info = helpers.create_user_phone_info(
        created=reg_timestamp.isoformat() + '+0000', total=1,
    )

    add_appearance_experiments(
        predicates=[
            helpers.exp_create_eq_predicate(
                'user_registration_timestamp',
                user_phone_info['created'],
                arg_type='timepoint',
            ),
            helpers.exp_create_eq_predicate(
                'user_hours_count_since_registration',
                (mocked_time.now() - reg_timestamp).total_seconds() // 3600,
                arg_type='int',
            ),
            helpers.exp_create_eq_predicate(
                'user_total_orders_count',
                user_phone_info['stat']['total'],
                arg_type='int',
            ),
        ],
    )
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT,
        scenario_support.to_header_params_experiment(
            # if (offers_key == buttons) return response['offers']['buttons']
            # if (offers_key == header) return response['offers']['header']
            show_from=1
            if offers_key == 'buttons'
            else 2,
        ),
    )

    add_experiment(
        consts.SHORTCUTS_OVERLAYS_EXPERIMENT,
        load_json('superapp_overlays_experiment.json'),
    )

    payload = helpers.build_header_request(
        client_support=scenario_support.to_client_support(),
        availability_support=scenario_support.to_services_availability(),
        supported_actions=helpers.EnvSetup().all_supported_actions,
        user_phone_info=user_phone_info,
    )

    response = await taxi_shortcuts.post(
        consts.URL, headers={'X-Request-Language': 'ru'}, json=payload,
    )

    assert response.status_code == 200

    offers = response.json()['offers']
    assert offers_key in offers

    assert len(offers[offers_key]) == 1
    assert offers[offers_key][0]['service'] == service


@pytest.mark.parametrize(
    'service, scenario', [('eats', helpers.Scenarios.eats_based_eats)],
)
@pytest.mark.parametrize(
    'seen', [[], [{'id': 'counter_id', 'status': 'complete'}]],
)
@pytest.mark.parametrize('enable_in_bricks', [None, True, False])
async def test_buttons_onboardings(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        service,
        scenario,
        seen,
        enable_in_bricks,
):
    scenario_support = helpers.ScenarioSupport(
        available_scenarios=[scenario], available_services=[service],
    )
    counter_id = 'counter_id'
    onboarding = helpers.create_onboarding(counter_id, enable_in_bricks)

    add_appearance_experiments()
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT,
        scenario_support.to_header_params_experiment(show_from=1),
    )
    add_experiment(consts.ONBOARDINGS_EXP, {scenario.name: onboarding})

    payload = helpers.build_header_request(
        client_support=scenario_support.to_client_support(),
        availability_support=scenario_support.to_services_availability(),
        supported_actions=helpers.EnvSetup().all_supported_actions,
        seen=seen,
    )

    has_onboarding = all(
        counter['id'] != counter_id or counter['status'] != 'complete'
        for counter in seen
    )

    response = await taxi_shortcuts.post(consts.URL, json=payload)

    assert response.status_code == 200

    offers = response.json()['offers']
    assert 'buttons' in offers
    assert len(offers['buttons']) == 1

    button = offers['buttons'][0]

    onboarding['type'] = 'media-stories'
    onboarding.pop('enable_in_bricks', None)

    if has_onboarding:
        assert 'onboarding' in button
        assert button['onboarding'] == onboarding
    else:
        assert 'onboarding' not in button


@pytest.mark.parametrize(
    'service, scenario', [('eats', helpers.Scenarios.eats_based_eats)],
)
@pytest.mark.parametrize(
    'seen', [[], [{'id': 'counter_id', 'status': 'complete'}]],
)
@pytest.mark.parametrize('enable_in_bricks', [None, True, False])
async def test_bricks_onboardings(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        service,
        scenario,
        seen,
        enable_in_bricks,
):
    scenario_support = helpers.ScenarioSupport(
        available_scenarios=[scenario], available_services=[service],
    )
    counter_id = 'counter_id'
    onboarding = helpers.create_onboarding(counter_id, enable_in_bricks)

    add_appearance_experiments()
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT,
        scenario_support.to_header_params_experiment(show_from=99),
    )
    add_experiment(consts.ONBOARDINGS_EXP, {scenario.name: onboarding})

    payload = helpers.build_header_request(
        client_support=scenario_support.to_client_support(),
        availability_support=scenario_support.to_services_availability(),
        supported_actions=helpers.EnvSetup().all_supported_actions,
        seen=seen,
    )

    has_onboarding = (
        all(
            counter['id'] != counter_id or counter['status'] != 'complete'
            for counter in seen
        )
        and enable_in_bricks
    )

    response = await taxi_shortcuts.post(consts.URL, json=payload)

    assert response.status_code == 200

    offers = response.json()['offers']
    assert 'header' in offers
    assert len(offers['header']) == 1

    brick = offers['header'][0]

    onboarding['type'] = 'media-stories'
    onboarding.pop('enable_in_bricks', None)

    if has_onboarding:
        assert 'onboarding' in brick
        assert brick['onboarding'] == onboarding
    else:
        assert 'onboarding' not in brick
