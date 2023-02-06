from dateutil import parser
import pytest

from eats_catalog import storage
from . import layout_utils


PLUS_PROMO_TYPE_ID = 102


def create_places(eats_catalog_storage):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='open', place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+00:00'),
                    end=parser.parse('2021-01-01T14:00:00+00:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+00:00'),
                    end=parser.parse('2021-01-02T14:00:00+00:00'),
                ),
            ],
        ),
    )


@pytest.mark.now('2021-01-01T12:00:00+00:00')
async def test_plus_info_actions(
        catalog_for_layout, eats_catalog_storage, mockserver,
):
    create_places(eats_catalog_storage)

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/places-list',
    )
    def _eats_plus(_):
        return {
            'cashback': [
                {
                    'place_id': 1,
                    'cashback': 12,
                    'plus_promo_info_actions': [
                        {
                            'icon_url': 'icon_url',
                            'accent_color': [
                                {'theme': 'dark', 'value': '#bada55'},
                            ],
                            'title': 'title',
                            'description': 'description',
                            'extended': {
                                'title': 'Бесплатные тесты',
                                'content': (
                                    'При написании фичи, тесты в подарок'
                                ),
                                'button': {
                                    'title': 'Посмотреть всё',
                                    'url': 'url',
                                },
                            },
                        },
                    ],
                },
            ],
        }

    response = await catalog_for_layout(
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('open', data)
    place = layout_utils.find_place_by_slug('open', block)
    actions = layout_utils.find_actions('plus_promo', place)

    plus_promo_info_action_id = actions[0]['id']
    assert actions == [
        {
            'id': plus_promo_info_action_id,
            'payload': {
                'accent_color': [{'theme': 'dark', 'value': '#bada55'}],
                'description': 'description',
                'extended': {
                    'button': {'title': 'Посмотреть всё', 'url': 'url'},
                    'content': 'При написании фичи, тесты в подарок',
                    'title': 'Бесплатные тесты',
                },
                'icon_url': 'icon_url',
                'title': 'title',
                'promo_type_id': '102',
            },
            'type': 'plus_promo',
        },
    ]


@pytest.mark.parametrize('empty_info_actions', [False, True])
@pytest.mark.now('2021-01-01T12:00:00+00:00')
async def test_plus_info_actions_promo_type_predicate(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        empty_info_actions,
):
    create_places(eats_catalog_storage)

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/places-list',
    )
    def _eats_plus(_):
        response = {
            'cashback': [
                {
                    'place_id': 1,
                    'cashback': 12,
                    'plus_promo_info_actions': [
                        {
                            'icon_url': 'icon_url',
                            'accent_color': [
                                {'theme': 'dark', 'value': '#bada55'},
                            ],
                            'title': 'title',
                            'description': 'description',
                            'extended': {
                                'title': 'Бесплатные тесты',
                                'content': (
                                    'При написании фичи, тесты в подарок'
                                ),
                                'button': {
                                    'title': 'Посмотреть всё',
                                    'url': 'url',
                                },
                            },
                        },
                    ],
                },
            ],
        }
        if empty_info_actions:
            del response['cashback'][0]['plus_promo_info_actions']
        return response

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'condition': {
                    'type': 'contains',
                    'init': {
                        'arg_name': 'promo_type',
                        'arg_type': 'int',
                        'value': PLUS_PROMO_TYPE_ID,
                    },
                },
            },
        ],
    )

    assert response.status_code == 200

    data = response.json()

    if empty_info_actions:
        layout_utils.assert_no_block_or_empty('open', data)
    else:
        layout_utils.find_block('open', data)
