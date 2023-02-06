import copy

import pytest

from tests_shortcuts import consts
from tests_shortcuts import helpers


def make_eats_payload(shortcuts):
    payload = helpers.make_payload_with_shortcuts(shortcuts)
    payload.update({'eats_places': consts.EATS_PLACES_DELIVERY_TIME})
    return payload


def build_request(supported_features, cells_count, shortcut_ids=None):
    default_cell = {
        'height': 2,
        'width': 2,
        'shortcut': consts.DEFAULT_TAXI_SHORTCUT,
    }
    cells = [default_cell] * cells_count

    if shortcut_ids is not None:
        assert len(shortcut_ids) == cells_count
        cells = []
        for shortcut_id in shortcut_ids:
            cell = copy.deepcopy(default_cell)
            cell['shortcut']['id'] = shortcut_id
            cells.append(cell)

    payload = {
        'shortcuts': {
            'supported_features': [
                {
                    'type': consts.TAXI_EXPECTED_DEST_TYPE,
                    'prefetch_strategies': supported_features,
                },
                {'type': 'taxi:route-input', 'prefetch_strategies': []},
                {'type': 'header-deeplink', 'prefetch_strategies': []},
                {
                    'type': 'eats-based:superapp',
                    'services': ['eats', 'grocery', 'pharmacy'],
                    'prefetch_strategies': [],
                },
            ],
        },
        'grid': {'id': 'id', 'width': 6, 'cells': cells},
    }
    return payload


@pytest.mark.servicetest
async def test_shortcuts_healthcheck(taxi_shortcuts):
    response = await taxi_shortcuts.post(
        consts.URL, helpers.make_default_payload(),
    )
    assert response.status_code == 200
    data = response.json()
    assert data['layout'] == consts.DEFAULT_LAYOUT
    assert data['offers']['items'] == []


@pytest.mark.servicetest
@pytest.mark.translations(
    client_messages={consts.DELIVERY_TIME_KEY: consts.DELIVERY_TIME_TEMPLATES},
)
async def test_shortcuts_only(taxi_shortcuts):
    payload = helpers.make_payload_with_shortcuts(
        [
            consts.DEFAULT_TAXI_SHORTCUT,
            consts.DEFAULT_EATS_SHORTCUT,
            consts.DEFAULT_GROCERY_SHORTCUT,
            consts.DEFAULT_MEDIA_SHORTCUT,
            consts.DEFAULT_PROMO_SHORTCUT,
            consts.DEFAULT_INVITE_SHORTCUT,
            consts.DEFAULT_REFERRAL_SHORTCUT,
            consts.DEFAULT_MAAS_SHORTCUT,
            consts.DEFAULT_DEEPLINK_PARAMS_SHORTCUT,
            consts.DEFAULT_DRIVE_SHORTCUT,
        ],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    assert data['layout'] == consts.DEFAULT_LAYOUT
    assert data['offers']['items'] == [
        {
            'shortcut_id': 'taxi_shortcut_id',
            'attributed_title': {
                'items': [{'type': 'text', 'text': 'attr text'}],
            },
            'title': 'Работа',
            'type': consts.TAXI_EXPECTED_DEST_TYPE,
            'width': 2,
            'height': 2,
            'background': {'color': '#F5F2E4'},
            'action': {
                'position': [1.0, 2.0],
                'log': 'some-log',
                'uri': 'some-uri',
            },
        },
        {
            'shortcut_id': 'eats_shortcut_id',
            'title': 'eats_title',
            'type': consts.DEEPLINK_TYPE,
            'width': 2,
            'height': 2,
            'background': {'color': '#F5F2E4'},
            'action': {
                'deeplink': (
                    'yandextaxi://external?'
                    'service=eats&href=restaurant/slug'
                ),
            },
        },
        {
            'shortcut_id': 'grocery_shortcut_id',
            'title': 'grocery_title',
            'type': consts.DEEPLINK_TYPE,
            'width': 2,
            'height': 2,
            'background': {'color': '#F5F2E4'},
            'action': {
                'deeplink': (
                    'yandextaxi://external?service=grocery&href=?category=1'
                ),
            },
        },
        {
            'shortcut_id': consts.DEFAULT_MEDIA_SHORTCUT['id'],
            'title': consts.DEFAULT_MEDIA_SHORTCUT['content']['title'],
            'type': consts.MEDIA_STORIES_TYPE,
            'width': 2,
            'height': 2,
            'background': {
                'image_url': consts.DEFAULT_MEDIA_SHORTCUT['content'][
                    'image_url'
                ],
                'color': consts.DEFAULT_MEDIA_SHORTCUT['content']['color'],
            },
            'action': {
                'media': {
                    'promo_id': consts.DEFAULT_MEDIA_SHORTCUT[
                        'scenario_params'
                    ]['media_stories_params']['promo_id'],
                },
            },
        },
        {
            'shortcut_id': consts.DEFAULT_PROMO_SHORTCUT['id'],
            'title': consts.DEFAULT_PROMO_SHORTCUT['content']['title'],
            'type': consts.MEDIA_STORIES_TYPE,
            'width': 2,
            'height': 2,
            'background': {
                'image_url': consts.DEFAULT_PROMO_SHORTCUT['content'][
                    'image_url'
                ],
                'color': consts.DEFAULT_PROMO_SHORTCUT['content']['color'],
            },
            'action': {
                'media': {
                    'promo_id': consts.DEFAULT_PROMO_SHORTCUT[
                        'scenario_params'
                    ]['promo_stories_params']['promo_id'],
                },
            },
        },
        {
            'shortcut_id': consts.DEFAULT_INVITE_SHORTCUT['id'],
            'title': consts.DEFAULT_INVITE_SHORTCUT['content']['title'],
            'type': consts.INVITES_TYPE,
            'width': 2,
            'height': 2,
            'background': {
                'color': consts.DEFAULT_INVITE_SHORTCUT['content']['color'],
            },
            'text_style': {
                'color': consts.DEFAULT_INVITE_SHORTCUT['content'][
                    'text_color'
                ],
            },
            'action': consts.DEFAULT_INVITE_SHORTCUT['scenario_params'][
                'invites_params'
            ]['content'],
        },
        {
            'shortcut_id': consts.DEFAULT_REFERRAL_SHORTCUT['id'],
            'title': consts.DEFAULT_REFERRAL_SHORTCUT['content']['title'],
            'subtitle': consts.DEFAULT_REFERRAL_SHORTCUT['content'][
                'subtitle'
            ],
            'type': consts.DEEPLINK_TYPE,
            'width': 2,
            'height': 2,
            'background': {
                'color': consts.DEFAULT_REFERRAL_SHORTCUT['content']['color'],
                'image_tag': consts.DEFAULT_REFERRAL_SHORTCUT['content'][
                    'image_tag'
                ],
            },
            'text_style': {
                'color': consts.DEFAULT_REFERRAL_SHORTCUT['content'][
                    'text_color'
                ],
            },
            'action': consts.DEFAULT_REFERRAL_SHORTCUT['scenario_params'][
                'referral_params'
            ],
        },
        {
            'shortcut_id': consts.DEFAULT_MAAS_SHORTCUT['id'],
            'title': consts.DEFAULT_MAAS_SHORTCUT['content']['title'],
            'subtitle': consts.DEFAULT_MAAS_SHORTCUT['content']['subtitle'],
            'type': consts.ACTION_DRIVEN_TYPE,
            'width': 2,
            'height': 2,
            'background': {
                'color': consts.DEFAULT_MAAS_SHORTCUT['content']['color'],
                'image_tag': consts.DEFAULT_MAAS_SHORTCUT['content'][
                    'image_tag'
                ],
            },
            'overlays': consts.DEFAULT_MAAS_SHORTCUT['content']['overlays'],
            'text_style': {
                'color': consts.DEFAULT_MAAS_SHORTCUT['content']['text_color'],
            },
            'action': {
                'type': 'deeplink',
                'deeplink': consts.DEFAULT_MAAS_SHORTCUT['scenario_params'][
                    'maas_params'
                ]['deeplink'],
            },
        },
        {
            'shortcut_id': consts.DEFAULT_DEEPLINK_PARAMS_SHORTCUT['id'],
            'title': consts.DEFAULT_DEEPLINK_PARAMS_SHORTCUT['content'][
                'title'
            ],
            'subtitle': consts.DEFAULT_DEEPLINK_PARAMS_SHORTCUT['content'][
                'subtitle'
            ],
            'type': consts.DEEPLINK_TYPE,
            'width': 2,
            'height': 2,
            'background': {
                'color': consts.DEFAULT_DEEPLINK_PARAMS_SHORTCUT['content'][
                    'color'
                ],
                'image_tag': consts.DEFAULT_DEEPLINK_PARAMS_SHORTCUT[
                    'content'
                ]['image_tag'],
            },
            'text_style': {
                'color': consts.DEFAULT_DEEPLINK_PARAMS_SHORTCUT['content'][
                    'text_color'
                ],
            },
            'action': consts.DEFAULT_DEEPLINK_PARAMS_SHORTCUT[
                'scenario_params'
            ]['deeplink_params'],
            'overlays': [{'shape': 'bubble'}],
        },
        {
            'shortcut_id': consts.DEFAULT_DRIVE_SHORTCUT['id'],
            'title': consts.DEFAULT_DRIVE_SHORTCUT['content']['title'],
            'subtitle': consts.DEFAULT_DRIVE_SHORTCUT['content']['subtitle'],
            'type': consts.DRIVE_FIXPOINT_OFFERS_TYPE,
            'width': 2,
            'height': 2,
            'background': {
                'color': consts.DEFAULT_DRIVE_SHORTCUT['content']['color'],
            },
            'action': {
                'layers_context': consts.DEFAULT_DRIVE_SHORTCUT[
                    'scenario_params'
                ]['drive_fixpoint_offers_params']['layers_context'],
            },
            'overlays': consts.DEFAULT_DRIVE_SHORTCUT['scenario_params'][
                'drive_fixpoint_offers_params'
            ]['overlays'],
        },
    ]


@pytest.mark.servicetest
@pytest.mark.parametrize('destination_support', [True, False])
async def test_action_driven_destination_support(
        taxi_shortcuts, destination_support,
):
    payload = helpers.make_payload_with_shortcuts(
        [consts.DEFAULT_REDIRECT_DRIVE_SHORTCUT],
        supported_actions=[
            {
                'type': 'taxi:summary-redirect',
                'destination_support': destination_support,
            },
        ],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    action = {
        'type': 'taxi:summary-redirect',
        'class': 'drive_cargo',
        'state': 'collapsed',
        'vertical': 'drive',
        'vertical_trap': True,
    }
    if destination_support:
        action.update(
            {
                'destination': {
                    'log': 'log',
                    'position': [37.211375, 55.577065],
                    'uri': 'uri',
                },
            },
        )
    assert data['offers']['items'] == [
        {
            'shortcut_id': consts.DEFAULT_REDIRECT_DRIVE_SHORTCUT['id'],
            'title': consts.DEFAULT_REDIRECT_DRIVE_SHORTCUT['content'][
                'title'
            ],
            'subtitle': consts.DEFAULT_REDIRECT_DRIVE_SHORTCUT['content'][
                'subtitle'
            ],
            'type': 'action-driven',
            'width': 2,
            'height': 2,
            'background': {
                'color': consts.DEFAULT_REDIRECT_DRIVE_SHORTCUT['content'][
                    'color'
                ],
            },
            'action': action,
            'overlays': (
                consts.DEFAULT_REDIRECT_DRIVE_SHORTCUT['content']['overlays']
            ),
        },
    ]


@pytest.mark.servicetest
@pytest.mark.parametrize('summary_context_support', [True, False])
async def test_action_driven_summary_context_support(
        taxi_shortcuts, summary_context_support,
):
    shortcut = copy.deepcopy(consts.DEFAULT_REDIRECT_DRIVE_SHORTCUT)
    action = {
        'type': 'taxi:summary-redirect',
        'class': 'drive_cargo',
        'state': 'collapsed',
        'vertical': 'drive',
        'vertical_trap': True,
    }
    if summary_context_support:
        summary_context = {
            'summary_context': {
                'class': 'drive',
                'payload': {
                    'selected_offer_id': 'offer_id',
                    'previous_offer_ids': ['offer_id'],
                },
            },
        }
        action.update(summary_context)
        shortcut['scenario_params']['taxi_summary_redirect_params'].update(
            summary_context,
        )

    payload = helpers.make_payload_with_shortcuts(
        [shortcut], supported_actions=[{'type': 'taxi:summary-redirect'}],
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()

    assert data['offers']['items'] == [
        {
            'shortcut_id': shortcut['id'],
            'title': shortcut['content']['title'],
            'subtitle': shortcut['content']['subtitle'],
            'type': 'action-driven',
            'width': 2,
            'height': 2,
            'background': {'color': shortcut['content']['color']},
            'action': action,
            'overlays': (shortcut['content']['overlays']),
        },
    ]


@pytest.mark.servicetest
@pytest.mark.parametrize('summary_context_support', [True, False])
async def test_shuttle_summary_context_support(
        taxi_shortcuts, summary_context_support,
):
    shortcut = copy.deepcopy(consts.DEFAULT_REDIRECT_SHUTTLE_SHORTCUT)
    action = {
        'type': 'taxi:summary-redirect',
        'class': 'shuttle',
        'state': 'collapsed',
        'vertical': 'taxi',
        'vertical_trap': True,
        'maybe_wait_for_routestats': True,
    }
    if summary_context_support:
        summary_context = {
            'summary_context': {
                'class': 'shuttle',
                'payload': {
                    'backend_generated_context': {
                        'shortcut_offer_id': 'shuttle_offer_id',
                    },
                },
            },
        }
        action.update(summary_context)
        shortcut['scenario_params']['taxi_summary_redirect_params'].update(
            summary_context,
        )

    payload = helpers.make_payload_with_shortcuts(
        [shortcut], supported_actions=[{'type': 'taxi:summary-redirect'}],
    )

    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()

    assert data['offers']['items'] == [
        {
            'shortcut_id': shortcut['id'],
            'title': shortcut['content']['title'],
            'subtitle': shortcut['content']['subtitle'],
            'type': 'action-driven',
            'width': 2,
            'height': 2,
            'background': {'color': shortcut['content']['color']},
            'action': action,
            'overlays': (shortcut['content']['overlays']),
        },
    ]


@pytest.mark.experiments3(filename='experiment_sdc_shortcut_type.json')
@pytest.mark.parametrize(
    'user_id, shortcut_type',
    [
        ('some_user_id', 'sdc:route-selection'),
        ('aseppar_user_id', 'action-driven'),
    ],
)
@pytest.mark.servicetest
async def test_sdc_route_selection(taxi_shortcuts, user_id, shortcut_type):
    shortcut = copy.deepcopy(consts.DEFAULT_SDC_ROUTE_SELECTION_SHORTCUT)
    action = {
        'type': 'sdc:route-selection',
        'tariff_class': 'selfdriving',
        'mode': 'sdc',
        'onboarding_promo_id': 'sdc_onboarding_promo',
        'unavailable_reason_fullscreen_id': (
            'emergency_disabled_sdc_onboarding_promo'
        ),
        'selection_screens': [
            {
                'type': 'a',
                'text': 'Выберите точку А',
                'subtitle_text': 'беспилотник там вас подберет',
                'button': {
                    'text': 'далее',
                    'color': '#ABCABC',
                    'background_color': '#FFF000',
                },
            },
            {
                'type': 'b',
                'text': 'Выберите точку Б',
                'subtitle_text': 'беспилотник вас там высадит',
                'button': {
                    'text': 'Готово',
                    'color': '#000FFF',
                    'background_color': '#CABCAB',
                },
            },
        ],
    }

    payload = helpers.make_payload_with_shortcuts([shortcut])

    response = await taxi_shortcuts.post(
        consts.URL, payload, headers={'X-YaTaxi-UserId': user_id},
    )
    assert response.status_code == 200
    data = response.json()

    assert data['offers']['items'] == [
        {
            'shortcut_id': shortcut['id'],
            'title': shortcut['content']['title'],
            'subtitle': shortcut['content']['subtitle'],
            'type': shortcut_type,
            'width': 2,
            'height': 2,
            'background': {'color': shortcut['content']['color']},
            'action': action,
            'overlays': (shortcut['content']['overlays']),
        },
    ]


async def test_custom_deeplink_prefix(taxi_shortcuts, add_experiment):
    add_experiment('deeplink_settings', {'prefix': 'yandexyango'})
    payload = helpers.make_payload_with_shortcuts(
        [consts.DEFAULT_EATS_SHORTCUT, consts.DEFAULT_GROCERY_SHORTCUT],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    assert data['layout'] == consts.DEFAULT_LAYOUT
    for shortcut in data['offers']['items']:
        assert shortcut['action']['deeplink'].startswith('yandexyango')


@pytest.mark.servicetest
@pytest.mark.parametrize('revisions_enabled', [True, False])
async def test_shortcuts_with_image_tag_revision(
        taxi_shortcuts, load_json, taxi_config, revisions_enabled,
):
    taxi_config.set(SHORTCUTS_IMAGE_TAGS_REVISIONS_ENABLED=revisions_enabled)
    await taxi_shortcuts.invalidate_caches()

    payload = helpers.make_payload_with_shortcuts(
        [
            consts.MEDIA_SHORTCUT_CLASS_VIP_ICON_TAG,
            consts.MEDIA_SHORTCUT_CLASS_ECONOM_ICON_TAG,
            consts.MEDIA_SHORTCUT_CLASS_BUSINESS_ICON_TAG,
            consts.MEDIA_SHORTCUT_TAG_NOT_IN_CACHE,
        ],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    assert (
        response.json()
        == load_json('shortcuts_revisions_response_ok.json')[
            'enabled' if revisions_enabled else 'disabled'
        ]
    )


@pytest.mark.servicetest
@pytest.mark.translations(
    client_messages={
        consts.DELIVERY_TIME_KEY: consts.DELIVERY_TIME_TEMPLATES,
        consts.SUBTITLE_KEY: consts.SUBTITLE_TEMPLATES,
    },
)
@pytest.mark.parametrize(
    'locale, expected_text',
    [('en', '5 min'), ('ru', '5 мин'), ('fr', '5 мин')],  # fallback - RU
)
async def test_shortcuts_translations(
        taxi_shortcuts, add_experiment, locale, expected_text,
):
    add_experiment(
        consts.CONTENT_SETTINGS_EXPERIMENT,
        {'subtitle': {'eats:place': {'tanker_key': consts.SUBTITLE_KEY}}},
    )
    response = await taxi_shortcuts.post(
        consts.URL,
        helpers.make_payload_with_shortcuts([consts.DEFAULT_EATS_SHORTCUT]),
        headers={'X-Request-Language': locale},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['layout'] == consts.DEFAULT_LAYOUT
    assert data['offers']['items'] == [
        {
            'shortcut_id': 'eats_shortcut_id',
            'title': 'eats_title',
            'subtitle': expected_text,
            'type': consts.DEEPLINK_TYPE,
            'width': 2,
            'height': 2,
            'background': {'color': '#F5F2E4'},
            'action': {
                'deeplink': (
                    'yandextaxi://external?'
                    'service=eats&href=restaurant/slug'
                ),
            },
        },
    ]


@pytest.mark.servicetest
async def test_respect_blender_height(taxi_shortcuts):
    payload = helpers.make_default_payload(
        cells=[
            {
                'height': 4,
                'width': 2,
                'shortcut': consts.DEFAULT_TAXI_SHORTCUT,
            },
            {'width': 2, 'shortcut': consts.DEFAULT_EATS_SHORTCUT},
            # use default height=2 when not specified
        ],
    )
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    offers_heigths = [s['height'] for s in data['offers']['items']]
    assert offers_heigths == [4, 2]


@pytest.mark.config(SHORTCUTS_SUBTITLE_ETA_FORMAT='like-routestats')
@pytest.mark.translations(
    client_messages={
        'shortcuts.route_eta.round.hours_minutes': {
            'ru': '%(hours).0f ч %(minutes).0f мин',
        },
    },
)
async def test_routestats_like_subtitle_format(taxi_shortcuts, add_experiment):
    add_experiment(
        consts.CONTENT_SETTINGS_EXPERIMENT,
        {
            'delivery_times': {'grocery': 100},
            'subtitle': {'grocery:category': {'text': '{eta}'}},
        },
    )
    response = await taxi_shortcuts.post(
        consts.URL,
        helpers.make_payload_with_shortcuts([consts.DEFAULT_GROCERY_SHORTCUT]),
    )
    assert response.status_code == 200
    data = response.json()
    shortcuts = data['offers']['items']
    assert len(shortcuts) == 1
    assert shortcuts[0]['subtitle'] == '1 ч 40 мин'


@pytest.mark.parametrize(
    'payload,experiment_value,expected',
    [
        pytest.param(
            build_request(
                ['route_eta', 'routestats'],
                2,
                shortcut_ids=['taxi_shortcut_id_1', 'taxi_shortcut_id_2'],
            ),
            {
                consts.TAXI_EXPECTED_DEST_TYPE: [
                    {'strategy': 'route_eta', 'count': 1},
                    {'strategy': 'routestats', 'count': 1},
                ],
            },
            {
                'taxi_shortcut_id_1': 'route_eta',
                'taxi_shortcut_id_2': 'routestats',
            },
            id='Test with enough strategies in experiment',
        ),
        pytest.param(
            build_request(
                ['routestats'],
                2,
                shortcut_ids=['taxi_shortcut_id_1', 'taxi_shortcut_id_2'],
            ),
            {
                consts.TAXI_EXPECTED_DEST_TYPE: [
                    {'strategy': 'route_eta', 'count': 1},
                    {'strategy': 'routestats', 'count': 1},
                ],
            },
            {'taxi_shortcut_id_1': 'routestats', 'taxi_shortcut_id_2': None},
            id='Test with not enough strategies in experiment',
        ),
        pytest.param(
            build_request(
                ['routestats'],
                2,
                shortcut_ids=['taxi_shortcut_id_1', 'taxi_shortcut_id_2'],
            ),
            {
                consts.TAXI_EXPECTED_DEST_TYPE: [
                    {'strategy': 'route_eta', 'count': 1},
                    {'strategy': 'routestats', 'count': 0},
                ],
            },
            {'taxi_shortcut_id_1': None, 'taxi_shortcut_id_2': None},
            id='Test with count=0 for a strategy',
        ),
    ],
)
async def test_prefetch_strategy(
        taxi_shortcuts, add_experiment, payload, experiment_value, expected,
):
    add_experiment(consts.PREFETCH_EXPERIMENT, experiment_value)
    response = await taxi_shortcuts.post(consts.URL, payload)
    assert response.status_code == 200
    data = response.json()
    prefetches = {
        item['shortcut_id']: item['action'].get('prefetch')
        for item in data['offers']['items']
    }
    assert prefetches == expected


@pytest.mark.parametrize('use_sleep', [True, False])
async def test_shortcuts_can_sleep(
        taxi_shortcuts, testpoint, add_experiment, use_sleep,
):
    @testpoint('sleep_test_point')
    def sleep_test_point(data):
        pass

    add_experiment(
        consts.SLEEP_EXPERIMENT, {'enabled': use_sleep, 'sleep_ms': 1},
    )
    response = await taxi_shortcuts.post(
        consts.URL, make_eats_payload([consts.DEFAULT_EATS_SHORTCUT]),
    )
    assert response.status_code == 200
    assert sleep_test_point.has_calls == use_sleep


async def test_shortcuts_non_json_request(taxi_shortcuts):
    # Make sure we've properly handling non-json request in
    # GetRequestBodyForLogging
    response = await taxi_shortcuts.post(
        consts.URL, 'non-json-string-should-not-core-service',
    )
    assert response.status_code == 400


async def test_animated_background(taxi_shortcuts):
    response = await taxi_shortcuts.post(
        consts.URL,
        helpers.make_payload_with_shortcuts(
            [consts.DEFAULT_ANIMATED_TAXI_SHORTCUT],
        ),
    )
    data = response.json()
    offers = data.get('offers', {}).get('items', {})
    assert len(offers) == 1
    background = offers[0].get('background')
    assert background is not None
    assert background == {
        'animation': {
            'count': 3,
            'delay': 2.0,
            'id': 'sdc_onboarding_animation',
            'source': {
                'anchor': {'point': {'x': 0.5, 'y': 0.0}, 'shape': 'bubble'},
                'delay_per_circle': 100,
                'circle_count': 3,
                'color': '#FFFFFF',
                'duration': 3000.0,
            },
            'type': 'pulse_circles',
        },
        'image_tag': 'referral_image_tag',
        'color': '#F2E7E7',
    }
