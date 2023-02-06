import copy

import pytest

from tests_shortcuts import consts
from tests_shortcuts import helpers


CONTENT_CUSTOMIZATION_CONSUMER = 'shortcuts/content_customization'


@pytest.fixture(autouse=True)
def set_allowed_scenarios(taxi_config):
    taxi_config.set(
        SHORTCUTS_CUSTOMIZATION_ALLOWED_SCENARIOS=[
            'drive_fixpoint_offers',
            'eats_place',
            'grocery_category',
        ],
    )


@pytest.mark.translations(
    client_messages={consts.DELIVERY_TIME_KEY: consts.DELIVERY_TIME_TEMPLATES},
)
@pytest.mark.config(
    SHORTCUTS_CUSTOMIZATION_MAX_COUNT=5, SHORTCUTS_CUSTOMIZATION_MATCH_LIMIT=5,
)
@pytest.mark.parametrize(
    'shortcut, subtitle_template, expected_subtitle',
    [
        (
            consts.DEFAULT_EATS_SHORTCUT,
            'Время: {eta}, рейтинг: {rating}',
            'Время: 5 мин, рейтинг: 4.2',
        ),
        (consts.DEFAULT_GROCERY_SHORTCUT, 'Время: {eta}', 'Время: 5 мин'),
    ],
)
async def test_customize_subtitle(
        taxi_shortcuts,
        add_experiment,
        shortcut,
        subtitle_template,
        expected_subtitle,
):
    add_experiment(
        consts.CONTENT_CUSTOMIZATION_MARK_EXPERIMENT,
        {'enabled': True, 'limit': 5, 'mark_group': 1},
    )

    add_experiment(
        consts.CONTENT_CUSTOMIZATION_EXPERIMENT,
        {'subtitle': {'text': subtitle_template}},
        consumers=[CONTENT_CUSTOMIZATION_CONSUMER],
    )
    add_experiment(
        consts.CONTENT_SETTINGS_EXPERIMENT, {'delivery_times': {'grocery': 5}},
    )
    payload = helpers.make_payload_with_shortcuts([shortcut])
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offer = response.json()['offers']['items'][0]
    assert offer['subtitle'] == expected_subtitle


@pytest.mark.config(
    SHORTCUTS_CUSTOMIZATION_MAX_COUNT=5, SHORTCUTS_CUSTOMIZATION_MATCH_LIMIT=5,
)
@pytest.mark.parametrize(
    'shortcut, payload_shortcut, should_customize',
    [
        (consts.DEFAULT_EATS_SHORTCUT, consts.DEFAULT_EATS_SHORTCUT, True),
        (consts.DEFAULT_GROCERY_SHORTCUT, consts.DEFAULT_EATS_SHORTCUT, True),
        (consts.DEFAULT_DRIVE_SHORTCUT, consts.DEFAULT_DRIVE_SHORTCUT, True),
        (consts.DEFAULT_MEDIA_SHORTCUT, consts.DEFAULT_EATS_SHORTCUT, False),
    ],
)
async def test_customize_badge(
        taxi_shortcuts,
        add_experiment,
        shortcut,
        payload_shortcut,
        should_customize,
):
    add_experiment(
        consts.CONTENT_CUSTOMIZATION_MARK_EXPERIMENT,
        {'enabled': True, 'limit': 5, 'mark_group': 1},
    )

    add_experiment(
        consts.CONTENT_CUSTOMIZATION_EXPERIMENT,
        {'badges': [{'text_color': '#AABBCC'}]},
        consumers=[CONTENT_CUSTOMIZATION_CONSUMER],
    )
    payload = helpers.make_payload_with_shortcuts([payload_shortcut])
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offer = response.json()['offers']['items'][0]
    if should_customize:
        overlay = offer['overlays'][0]
        assert overlay['text_color'] == '#AABBCC'


@pytest.mark.config(
    SHORTCUTS_CUSTOMIZATION_MAX_COUNT=5, SHORTCUTS_CUSTOMIZATION_MATCH_LIMIT=5,
)
async def test_customize_badge_with_content_settings(
        taxi_shortcuts, add_experiment,
):
    add_experiment(
        consts.CONTENT_SETTINGS_EXPERIMENT,
        {'badges': {'eats:place': {'__default__': {'text_color': '#CCBBAA'}}}},
    )
    add_experiment(
        consts.CONTENT_CUSTOMIZATION_MARK_EXPERIMENT,
        {'enabled': True, 'limit': 5, 'mark_group': 1},
    )

    add_experiment(
        consts.CONTENT_CUSTOMIZATION_EXPERIMENT,
        {'badges': [{'text_color': '#AABBCC'}]},
        consumers=[CONTENT_CUSTOMIZATION_CONSUMER],
    )
    payload = helpers.make_payload_with_shortcuts(
        [consts.DEFAULT_EATS_SHORTCUT],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    offer = response.json()['offers']['items'][0]
    overlays = offer['overlays']
    assert len(overlays) == 1
    overlay = overlays[0]
    assert overlay['text_color'] == '#AABBCC'


async def _check_customization(
        taxi_shortcuts, add_experiment, expected_customized_count,
):
    add_experiment(
        consts.CONTENT_CUSTOMIZATION_EXPERIMENT,
        {'badges': [{'text_color': '#AABBCC'}]},
        consumers=[CONTENT_CUSTOMIZATION_CONSUMER],
    )
    shortcuts = [
        {**copy.deepcopy(consts.DEFAULT_EATS_SHORTCUT), 'id': str(i)}
        for i in range(3)
    ]
    payload = helpers.make_payload_with_shortcuts(shortcuts)
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200

    customized_badges_count = 0
    for offer in response.json()['offers']['items']:
        overlays = offer.get('overlays')
        if not overlays:
            continue

        badge = overlays[0]
        if badge.get('text_color') == '#AABBCC':
            customized_badges_count += 1

    assert customized_badges_count == expected_customized_count


@pytest.mark.parametrize(
    (
        'experiment_settings_limit,'
        'customization_max_count,'
        'customization_match_limit,'
        'expected_customized_count'
    ),
    [
        pytest.param(
            1,
            2,
            3,
            1,
            id='Test with experiment limit lower than config limit',
        ),
        pytest.param(
            10,
            2,
            3,
            2,
            id='Test with experiment limit higher than config limit',
        ),
        pytest.param(
            8,
            5,
            2,
            2,
            id=(
                'Test with config customization limit'
                ' higher than config match limit'
            ),
        ),
        pytest.param(
            6, 5, 10, 3, id='Test with customization limit not reached',
        ),
    ],
)
async def test_respect_config_limits(
        taxi_shortcuts,
        taxi_config,
        add_experiment,
        experiment_settings_limit,
        customization_max_count,
        customization_match_limit,
        expected_customized_count,
):
    taxi_config.set(
        SHORTCUTS_CUSTOMIZATION_MAX_COUNT=customization_max_count,
        SHORTCUTS_CUSTOMIZATION_MATCH_LIMIT=customization_match_limit,
    )
    add_experiment(
        consts.CONTENT_CUSTOMIZATION_MARK_EXPERIMENT,
        {'enabled': True, 'limit': experiment_settings_limit, 'mark_group': 1},
    )

    await _check_customization(
        taxi_shortcuts, add_experiment, expected_customized_count,
    )


@pytest.mark.config(
    SHORTCUTS_CUSTOMIZATION_MAX_COUNT=5, SHORTCUTS_CUSTOMIZATION_MATCH_LIMIT=5,
)
@pytest.mark.parametrize(
    'customization_enabled, expected_customized_count',
    [(True, 3), (False, 0)],
)
async def test_respect_enabled_setting(
        taxi_shortcuts,
        add_experiment,
        customization_enabled,
        expected_customized_count,
):
    add_experiment(
        consts.CONTENT_CUSTOMIZATION_MARK_EXPERIMENT,
        {'enabled': customization_enabled, 'limit': 5, 'mark_group': 1},
    )
    await _check_customization(
        taxi_shortcuts, add_experiment, expected_customized_count,
    )


@pytest.mark.config(
    SHORTCUTS_CUSTOMIZATION_MAX_COUNT=5, SHORTCUTS_CUSTOMIZATION_MATCH_LIMIT=5,
)
async def test_no_customization_without_mark(taxi_shortcuts, add_experiment):
    await _check_customization(taxi_shortcuts, add_experiment, 0)
