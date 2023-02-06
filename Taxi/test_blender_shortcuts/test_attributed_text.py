import copy

import pytest

from tests_shortcuts import consts
from tests_shortcuts import helpers


@pytest.mark.translations(
    client_messages={consts.DELIVERY_TIME_KEY: consts.DELIVERY_TIME_TEMPLATES},
)
async def test_badge_attributed_text(taxi_shortcuts, add_experiment):
    attributed_text = {
        'items': [
            {
                'type': 'text',
                'text': {'text': 'Время: {eta}'},
                'font_size': 12,
                'font_weight': 'regular',
                'font_style': 'italic',
                'color': '#AABBCC',
            },
            {
                'type': 'image',
                'image_tag': 'some_image_tag',
                'width': 50,
                'vertical_alignment': 'center',
                'color': '#BBCCAA',
            },
        ],
    }
    add_experiment(
        consts.CONTENT_SETTINGS_EXPERIMENT,
        {
            'badges': {
                'eats:place': {
                    '__default__': {'attributed_text': attributed_text},
                },
            },
        },
    )
    response = await taxi_shortcuts.post(
        consts.URL,
        helpers.make_payload_with_shortcuts([consts.DEFAULT_EATS_SHORTCUT]),
    )
    assert response.status_code == 200
    data = response.json()
    shortcuts = data['offers']['items']
    assert len(shortcuts) == 1
    badge = shortcuts[0]['overlays'][0]
    attributed_text_text = attributed_text['items'][0]
    attributed_text_text['text'] = 'Время: 5 мин'
    assert badge['attributed_text'] == attributed_text


@pytest.mark.parametrize('has_config', (False, True))
@pytest.mark.parametrize('is_promo', (False, True))
@pytest.mark.parametrize('has_promo_type_id', (False, True))
async def test_badge_promo_image_tag(
        taxi_shortcuts,
        add_experiment,
        taxi_config,
        has_config,
        is_promo,
        has_promo_type_id,
):
    if has_config:
        taxi_config.set(
            SHORTCUTS_PROMO_TYPE_ID_TO_IMAGE_TAG={
                1: 'promo_type_id_1_image_tag',
            },
        )

    attributed_text_image = {
        'type': 'image',
        'image_tag': 'foo',
        'width': 50,
        'vertical_alignment': 'center',
        'color': '#BBCCAA',
    }
    if is_promo is not None:
        attributed_text_image['is_promo'] = is_promo
    attributed_text = {'items': [attributed_text_image]}

    add_experiment(
        consts.CONTENT_SETTINGS_EXPERIMENT,
        {
            'badges': {
                'eats:place': {
                    '__default__': {'attributed_text': attributed_text},
                },
            },
        },
    )
    shortcut = copy.deepcopy(consts.DEFAULT_EATS_SHORTCUT)
    if has_promo_type_id:
        shortcut['scenario_params']['eats_place_params']['promo_type_id'] = 1
    response = await taxi_shortcuts.post(
        consts.URL, helpers.make_payload_with_shortcuts([shortcut]),
    )
    assert response.status_code == 200
    data = response.json()
    shortcuts = data['offers']['items']
    assert len(shortcuts) == 1
    badge = shortcuts[0]['overlays'][0]
    image = badge['attributed_text']['items'][0]
    if has_config and is_promo and has_promo_type_id:
        assert image['image_tag'] == 'promo_type_id_1_image_tag'
    else:
        assert image['image_tag'] == 'foo'
