import copy

import pytest

from tests_shortcuts import consts

SHORTCUT_IDS = ['id1', 'id2', 'id3', 'id4', 'id5']
OVERLAYS = [
    {
        'attributed_text': {
            'items': [
                {'text': '25 мин', 'type': 'text'},
                {'text': '  •  ', 'type': 'text'},
                {
                    'color': '#ffffff',
                    'image_tag': 'shortcuts_badge_rating_icon',
                    'type': 'image',
                    'vertical_alignment': 'center',
                    'width': 14,
                },
                {'text': ' 4.9 ', 'type': 'text'},
            ],
        },
        'background': {'color': '#42413E'},
        'shape': 'corner_text',
        'text': 'shop',
        'text_color': '#FFFFFF',
    },
]


def build_request(cells_count=1):
    default_cell = {
        'height': 2,
        'width': 2,
        'shortcut': consts.DEFAULT_SCREEN_SHOPS_SHORTCUT,
    }
    cells = []
    blocks = []
    if cells_count is not None:
        for i in range(cells_count):
            cell = copy.deepcopy(default_cell)
            cell['shortcut']['id'] = SHORTCUT_IDS[i]
            cells.append(cell)

        blocks = [
            {
                'id': '46095517619a465db0a738a2ab1dfd86',
                'shortcut_ids': SHORTCUT_IDS[:cells_count],
                'slug': 'eats_shops',
            },
        ]

    payload = {
        'for_shops_screen': True,
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
            'supported_sections': [
                {'type': 'header_linear_grid'},
                {'type': 'items_linear_grid'},
                {'type': 'buttons_container'},
            ],
        },
        'grid': {'id': 'id', 'width': 6, 'cells': cells, 'blocks': blocks},
    }

    return payload


async def check_post(
        taxi_shortcuts,
        cells_count,
        expect_typed_header=True,
        expect_overlays=True,
        title='',
):
    request = build_request(cells_count)

    response = await taxi_shortcuts.post(consts.SCREEN_SHOPS_URL, request)
    assert response.status_code == 200
    data = response.json()

    default_item = {
        'action': {
            'deeplink': (
                'yandextaxi://external?service=shop&href=standalone/shop/'
                'avdaily_2ya_frunzenskaya_10'
            ),
        },
        'background': {
            'color': '#F5F4F2',
            'image_tag': 'shortcuts_shop_ab_daily_shortcut',
        },
        'height': 2,
        'title': title,
        'type': 'deeplink',
        'width': 2,
    }
    if not title:
        default_item['background']['alt_text'] = 'АВ Daily'
    if expect_overlays:
        default_item['overlays'] = OVERLAYS

    items = []
    expected_sections = []

    if cells_count is not None:
        expected_sections.append(
            {
                'shortcut_ids': SHORTCUT_IDS[:cells_count],
                'type': 'items_linear_grid',
            },
        )

        for i in range(cells_count):
            item = copy.deepcopy(default_item)
            item['shortcut_id'] = SHORTCUT_IDS[i]
            items.append(item)
    else:
        expected_sections.append(
            {'shortcut_ids': [], 'type': 'items_linear_grid'},
        )

    expected_data = {
        'layout': {'grid_id': 'id', 'type': 'linear_grid', 'width': 6},
        'offers': {'items': items},
        'sections': expected_sections,
    }

    if expect_typed_header:
        expected_data['sections'][0]['typed_header'] = {
            'lead': {
                'icon_tag': 'shortcuts_goods_header_icon',
                'title': {'text': 'Продукты'},
                'type': 'app_title',
            },
            'type': 'list_item',
        }

    assert data == expected_data


@pytest.mark.parametrize('cells_count', [None, 0, 1, 5])
@pytest.mark.translations(
    client_messages={
        'shortcuts_eats_delivery_time_template': {
            'ru': '%(delivery_time)s мин',
        },
    },
)
@pytest.mark.config(SHORTCUTS_CUSTOMIZATION_ALLOWED_SCENARIOS=['eats_shop'])
@pytest.mark.experiments3(filename='experiments3_for_shops_screen.json')
async def test_usual_case(taxi_shortcuts, add_config, cells_count):
    add_config(
        'shortcuts_sections_settings',
        {'order': ['other', 'buttons', 'header']},
    )

    await check_post(taxi_shortcuts, cells_count)


@pytest.mark.parametrize(
    'scenarios_without_title, title', [([], 'АВ Daily'), (['eats_shop'], '')],
)
@pytest.mark.translations(
    client_messages={
        'shortcuts_eats_delivery_time_template': {
            'ru': '%(delivery_time)s мин',
        },
    },
)
@pytest.mark.config(SHORTCUTS_CUSTOMIZATION_ALLOWED_SCENARIOS=['eats_shop'])
@pytest.mark.experiments3(filename='experiments3_for_shops_screen.json')
async def test_title(
        taxi_shortcuts,
        add_config,
        add_experiment,
        scenarios_without_title,
        title,
):
    add_config(
        'shortcuts_sections_settings',
        {'order': ['other', 'buttons', 'header']},
    )
    add_experiment(
        'shortcuts_screen_settings',
        {
            'shops': {
                'suggest_mode': 'shop',
                'scenarios_without_title': scenarios_without_title,
            },
        },
    )

    await check_post(taxi_shortcuts, 3, False, title=title)


@pytest.mark.parametrize('cells_count', [0, 3])
@pytest.mark.parametrize('with_typed_header', [True, False])
@pytest.mark.translations(
    client_messages={
        'shortcuts_eats_delivery_time_template': {
            'ru': '%(delivery_time)s мин',
        },
    },
)
@pytest.mark.config(SHORTCUTS_CUSTOMIZATION_ALLOWED_SCENARIOS=['eats_shop'])
@pytest.mark.experiments3(filename='experiments3_for_shops_screen.json')
async def test_typed_header(
        taxi_shortcuts,
        add_config,
        add_experiment,
        cells_count,
        with_typed_header,
):
    add_config(
        'shortcuts_sections_settings',
        {'order': ['other', 'buttons', 'header']},
    )
    exp_value = {
        'shops': {
            'scenarios_without_title': ['eats_shop'],
            'suggest_mode': 'shop',
        },
    }
    if with_typed_header:
        exp_value['shops']['typed_header'] = {
            'lead': {
                'type': 'app_title',
                'title': {'text': {'text': 'Продукты'}},
                'icon_tag': 'shortcuts_goods_header_icon',
            },
            'type': 'list_item',
        }
    add_experiment('shortcuts_screen_settings', exp_value)

    await check_post(taxi_shortcuts, cells_count, with_typed_header)


@pytest.mark.parametrize('cells_count', [0, 3])
@pytest.mark.translations(
    client_messages={
        'shortcuts_eats_delivery_time_template': {
            'ru': '%(delivery_time)s мин',
        },
    },
)
async def test_null_screen_settings_exp(taxi_shortcuts, cells_count):
    await check_post(taxi_shortcuts, cells_count, False, False, 'АВ Daily')
