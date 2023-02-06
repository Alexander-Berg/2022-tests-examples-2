import copy

import pytest

from tests_shortcuts import consts
from tests_shortcuts import helpers


@pytest.mark.servicetest
async def test_taxi_badges(taxi_shortcuts, add_experiment):
    add_experiment(
        consts.CONTENT_SETTINGS_EXPERIMENT,
        {
            'badges': {
                'taxi:poi': {
                    '__default__': {
                        'image_tag': 'base_tag',
                        'background': {'color': 'red'},
                        'shape': 'poi',
                    },
                },
            },
        },
    )
    badge_properties = {
        'image_tag': 'superapp_badge_poi_work',
        'background': {'color': '#C4BFA7'},
    }
    shortcut = copy.deepcopy(consts.DEFAULT_TAXI_SHORTCUT)
    shortcut['content']['overlays'] = [{'shape': 'bubble'}]
    shortcut['scenario_params']['taxi_expected_destination_params'].update(
        {'icon': badge_properties},
    )
    response = await taxi_shortcuts.post(
        consts.URL, helpers.make_payload_with_shortcuts([shortcut]),
    )
    assert response.status_code == 200
    data = response.json()
    shortcuts = data['offers']['items']
    assert len(shortcuts) == 1

    assert shortcuts[0]['overlays'] == [
        {**badge_properties, 'shape': 'poi'},
        {'shape': 'bubble'},
    ]


@pytest.mark.servicetest
@pytest.mark.translations(
    client_messages={consts.TANKER_KEY: {'ru': 'badge_text'}},
)
@pytest.mark.parametrize(
    'exp_badge_key, shortcut',
    [
        ('eats:place', consts.DEFAULT_EATS_SHORTCUT),
        ('grocery:category', consts.DEFAULT_GROCERY_SHORTCUT),
    ],
)
@pytest.mark.parametrize(
    'badge_properties',
    [
        pytest.param(
            {
                '__default__': helpers.make_default_badge(
                    shape='bubble', text='badge_text',
                ),
            },
            id='Test with default text',
        ),
        pytest.param(
            {
                '__default__': helpers.make_default_badge(
                    tanker_key=consts.TANKER_KEY,
                ),
            },
            id='Test with default tanker key',
        ),
        pytest.param(
            {
                '__default__': helpers.make_default_badge(
                    text='incorrect_text', tanker_key=consts.TANKER_KEY,
                ),
            },
            id='Test with default text and tanker key',
        ),  # default key has a higher priority than default text
        pytest.param(
            {
                'overrides': helpers.make_overridden_badge(text='badge_text'),
                '__default__': helpers.make_default_badge(),
            },
            id='Test with text in override',
        ),
        pytest.param(
            {
                '__default__': helpers.make_default_badge(
                    text='incorrect_text',
                ),
                'overrides': helpers.make_overridden_badge(
                    tanker_key=consts.TANKER_KEY,
                ),
            },
            id='Test with tanker key in override',
        ),
        pytest.param(
            {
                'overrides': helpers.make_overridden_badge(text='badge_text'),
                '__default__': helpers.make_default_badge(
                    text='incorrect_text',
                ),
            },
            id='Test with text in both default and override',
        ),  # overridden text has a higher priority than default text
        pytest.param(
            {
                'overrides': helpers.make_overridden_badge(
                    text='incorrect_text', tanker_key=consts.TANKER_KEY,
                ),
                '__default__': helpers.make_default_badge(),
            },
            id='Test with overriden tanker key '
            'and text and no text in default',
        ),  # overridden key has a higher priority than overridden text
        pytest.param(
            {
                '__default__': helpers.make_default_badge(
                    tanker_key='incorrect_key',
                ),
                'overrides': helpers.make_overridden_badge(text='badge_text'),
            },
            id='Test with tanker key in default and text in override',
        ),  # overridden text has a higher priority than default key
        pytest.param(
            {
                '__default__': helpers.make_default_badge(
                    tanker_key='incorrect_key',
                ),
                'overrides': helpers.make_overridden_badge(
                    text='incorrect_text', tanker_key=consts.TANKER_KEY,
                ),
            },
            id='Test with tanker key in default and override',
        ),
        pytest.param(
            {
                '__default__': helpers.make_default_badge(),
                'overrides': helpers.make_overridden_badge(
                    text='badge_text',
                    text_color='badge_text_color',
                    background_color='badge_background_color',
                ),
            },
            id='Test with other fields in override',
        ),
        pytest.param(
            {
                'overrides': helpers.make_overridden_badge(
                    text='badge_text',
                    text_color='badge_text_color',
                    background_color='badge_background_color',
                    shape='bubble',
                ),
            },
            id='Test with only overrides',
        ),
    ],
)
async def test_badges_default_overrides_priority(
        taxi_shortcuts,
        add_experiment,
        exp_badge_key,
        shortcut,
        badge_properties,
):
    add_experiment(
        consts.CONTENT_SETTINGS_EXPERIMENT,
        {'badges': {exp_badge_key: badge_properties}},
    )
    response = await taxi_shortcuts.post(
        consts.URL, helpers.make_payload_with_shortcuts([shortcut]),
    )
    assert response.status_code == 200
    data = response.json()
    shortcuts = data['offers']['items']
    assert len(shortcuts) == 1

    assert shortcuts[0]['overlays'][0] == {
        'text': 'badge_text',
        'text_color': 'badge_text_color',
        'background': {'color': 'badge_background_color'},
        'shape': 'bubble',
    }


@pytest.mark.translations(
    client_messages={consts.TANKER_KEY: {'ru': 'badge_text2'}},
)
@pytest.mark.parametrize(
    'exp_badge_key, shortcut',
    [
        ('eats:place', consts.DEFAULT_EATS_SHORTCUT),
        ('grocery:category', consts.DEFAULT_GROCERY_SHORTCUT),
    ],
)
@pytest.mark.parametrize(
    'badge_properties, expected_overlays',
    [
        pytest.param(
            {
                '__default__': helpers.make_default_badge(text='default_text'),
                'overrides': helpers.make_overridden_badge(
                    text='overriden_text',
                ),
                'items': [helpers.make_default_badge(text='badge_text')],
            },
            [
                {
                    'text': 'overriden_text',
                    'text_color': 'badge_text_color',
                    'background': {'color': 'badge_background_color'},
                    'shape': 'bubble',
                },
            ],
            id='Test with default, overrides and badges',
        ),
        pytest.param(
            {
                '__default__': helpers.make_default_badge(text='default_text'),
                'items': [helpers.make_default_badge(text='badge_text')],
            },
            [
                {
                    'text': 'badge_text',
                    'text_color': 'badge_text_color',
                    'background': {'color': 'badge_background_color'},
                    'shape': 'bubble',
                },
            ],
            id='Test with default and badges',
        ),
        pytest.param(
            {
                'overrides': helpers.make_overridden_badge(
                    text='overriden_text',
                    text_color='badge_text_color',
                    background_color='badge_background_color',
                    shape='bubble',
                ),
                'items': [helpers.make_default_badge(text='badge_text')],
            },
            [
                {
                    'text': 'overriden_text',
                    'text_color': 'badge_text_color',
                    'background': {'color': 'badge_background_color'},
                    'shape': 'bubble',
                },
            ],
            id='Test with overrides and badges',
        ),
        pytest.param(
            {
                'items': [
                    helpers.make_default_badge(text='badge_text1'),
                    helpers.make_default_badge(tanker_key=consts.TANKER_KEY),
                ],
            },
            [
                {
                    'text': 'badge_text1',
                    'text_color': 'badge_text_color',
                    'background': {'color': 'badge_background_color'},
                    'shape': 'bubble',
                },
                {
                    'text': 'badge_text2',
                    'text_color': 'badge_text_color',
                    'background': {'color': 'badge_background_color'},
                    'shape': 'bubble',
                },
            ],
            id='Test with multiple badges',
        ),
    ],
)
async def test_badges_multiple_badges(
        taxi_shortcuts,
        add_experiment,
        exp_badge_key,
        shortcut,
        badge_properties,
        expected_overlays,
):
    add_experiment(
        consts.CONTENT_SETTINGS_EXPERIMENT,
        {'badges': {exp_badge_key: badge_properties}},
    )
    response = await taxi_shortcuts.post(
        consts.URL, helpers.make_payload_with_shortcuts([shortcut]),
    )
    assert response.status_code == 200
    data = response.json()
    shortcuts = data['offers']['items']
    assert len(shortcuts) == 1

    assert shortcuts[0]['overlays'] == expected_overlays


@pytest.mark.translations(
    client_messages={
        'drive.text': {'ru': 'Драйв!'},
        'drive.item_text': {'ru': 'Го!'},
    },
)
@pytest.mark.parametrize(
    'service, scenario', [('eats', helpers.Scenarios.eats_based_eats)],
)
@pytest.mark.parametrize('offers_key', ['header', 'buttons'])
async def test_overlays_from_experiment(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        load_json,
        service,
        scenario,
        offers_key,
):
    scenario_support = helpers.ScenarioSupport(
        available_scenarios=[scenario], available_services=[service],
    )

    add_appearance_experiments()
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT,
        scenario_support.to_header_params_experiment(
            show_from=1 if offers_key == 'buttons' else 2,
        ),
    )

    add_experiment(
        consts.SHORTCUTS_OVERLAYS_EXPERIMENT,
        load_json('superapp_overlays_experiment.json'),
        predicates=[
            helpers.exp_create_contains_predicate(
                'eats_promo_tags', 'new-user',
            ),
        ],
    )

    payload = helpers.build_header_request(
        client_support=scenario_support.to_client_support(),
        availability_support=scenario_support.to_services_availability(),
        supported_actions=helpers.EnvSetup().all_supported_actions,
        eats_promo_tags=['asdfgh', 'new-user'],
    )

    response = await taxi_shortcuts.post(
        consts.URL, headers={'X-Request-Language': 'ru'}, json=payload,
    )

    assert response.status_code == 200

    offers = response.json()['offers']
    assert offers_key in offers

    assert len(offers[offers_key]) == 1
    assert offers[offers_key][0]['service'] == service
    assert offers[offers_key][0]['overlays'] == load_json(
        'superapp_expected_overlays.json',
    )


@pytest.mark.translations(
    client_messages={
        'drive.text': {'ru': 'Драйв!'},
        'drive.item_text': {'ru': 'Го!'},
    },
)
@pytest.mark.parametrize(
    'service, scenario', [('grocery', helpers.Scenarios.eats_based_grocery)],
)
@pytest.mark.parametrize('offers_key', ['header', 'buttons'])
async def test_overlays_from_experiment_for_lavka(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        load_json,
        service,
        scenario,
        offers_key,
):
    scenario_support = helpers.ScenarioSupport(
        available_scenarios=[scenario], available_services=[service],
    )

    add_appearance_experiments()
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT,
        scenario_support.to_header_params_experiment(
            show_from=1 if offers_key == 'buttons' else 2,
        ),
    )

    add_experiment(
        consts.SHORTCUTS_OVERLAYS_EXPERIMENT,
        load_json('superapp_overlays_experiment.json'),
        predicates=[
            helpers.exp_create_contains_predicate(
                'lavka_promo_tags', 'lavka-new-user',
            ),
        ],
    )

    payload = helpers.build_header_request(
        client_support=scenario_support.to_client_support(),
        availability_support=scenario_support.to_services_availability(),
        supported_actions=helpers.EnvSetup().all_supported_actions,
        lavka_promo_tags=['lavka-new-user'],
    )

    response = await taxi_shortcuts.post(
        consts.URL, headers={'X-Request-Language': 'ru'}, json=payload,
    )

    assert response.status_code == 200

    offers = response.json()['offers']
    assert offers_key in offers

    assert len(offers[offers_key]) == 1
    assert offers[offers_key][0]['service'] == service
    assert offers[offers_key][0]['overlays'] == load_json(
        'superapp_expected_overlays.json',
    )


@pytest.mark.translations(
    client_messages={
        'drive.text': {'ru': 'Драйв!'},
        'drive.item_text': {'ru': 'Го!'},
    },
)
@pytest.mark.parametrize(
    'service, scenario', [('market', helpers.Scenarios.market)],
)
@pytest.mark.parametrize('offers_key', ['buttons'])
async def test_overlays_from_experiment_for_market(
        taxi_shortcuts,
        add_experiment,
        add_appearance_experiments,
        load_json,
        service,
        scenario,
        offers_key,
):
    scenario_support = helpers.ScenarioSupport(
        available_scenarios=[scenario], available_services=[service],
    )

    add_appearance_experiments()
    add_experiment(
        consts.HEADER_PARAMS_EXPERIMENT,
        scenario_support.to_header_params_experiment(
            show_from=1 if offers_key == 'buttons' else 2,
        ),
    )

    add_experiment(
        consts.SHORTCUTS_OVERLAYS_EXPERIMENT,
        load_json('superapp_overlays_experiment.json'),
        predicates=[
            helpers.exp_create_contains_predicate(
                'market_promo_tags', 'market-go-new-user',
            ),
        ],
    )

    payload = helpers.build_header_request(
        client_support=scenario_support.to_client_support(),
        availability_support=scenario_support.to_services_availability(),
        supported_actions=helpers.EnvSetup().all_supported_actions,
        market_promo_tags=['market-go-new-user'],
    )

    response = await taxi_shortcuts.post(
        consts.URL, headers={'X-Request-Language': 'ru'}, json=payload,
    )

    assert response.status_code == 200

    offers = response.json()['offers']
    assert offers_key in offers

    assert len(offers[offers_key]) == 1
    assert offers[offers_key][0]['service'] == service
    assert offers[offers_key][0]['overlays'] == load_json(
        'superapp_expected_overlays.json',
    )
