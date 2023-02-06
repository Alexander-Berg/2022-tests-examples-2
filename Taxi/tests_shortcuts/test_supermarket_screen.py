import copy

import pytest

from tests_shortcuts import consts

SHORTCUT_IDS = ['id1', 'id2', 'id3', 'id4', 'id5']
MARKET_SEARCH_URL = '/search'
LAYOUT_OPTIONS = [[6], [5, 1]]

TRAIL = {
    'type': 'subtitle',
    'title': {
        'attributed_text': {
            'items': [
                {
                    'type': 'text',
                    'text': 'Маркет',
                    'font_size': 20,
                    'font_weight': 'bold',
                    'font_style': 'normal',
                    'color': '#21201F',
                },
            ],
        },
    },
}

SEARCH_SHORTCUT = {
    'color': '#F7F6F5',
    'default_url': '/search',
    'height': 1,
    'image_tag': 'shortcuts_market_search',
    'width': 6,
}
CART_SHORTCUT = {
    'color': '#F7F6F5',
    'default_url': '/cart',
    'image_tag': 'shortcuts_market_cart',
}


def build_request(
        cells_count=1,
        market_search_shortcut=None,
        market_cart_size=None,
        additional_sections=None,
        supported_sections=None,
):
    default_cell = {
        'height': 2,
        'width': 2,
        'shortcut': consts.DEFAULT_MARKET_CATEGORY_SHORTCUT,
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
                {
                    'prefetch_strategies': [],
                    'items': [
                        {'type': 'info'},
                        {'type': 'rating'},
                        {'type': 'thumb'},
                    ],
                    'type': 'vertical_stack_item',
                },
            ],
            'supported_sections': supported_sections or [
                {'type': 'header_linear_grid'},
                {'type': 'items_linear_grid'},
                {'type': 'buttons_container'},
                {'type': 'horizontal_stack_section'},
            ],
        },
        'grid': {'id': 'id', 'width': 6, 'cells': cells, 'blocks': blocks},
    }

    if market_search_shortcut:
        payload['market_search_url'] = MARKET_SEARCH_URL
    if market_cart_size is not None:
        payload['market_cart_size'] = market_cart_size
    if additional_sections:
        payload['additional_sections'] = additional_sections

    return payload


async def check_post(
        taxi_shortcuts,
        cells_count,
        expect_typed_header=True,
        market_search_shortcut=None,
        market_cart_shortcut=None,
        top_block_size=None,
        cart_overlays=None,
):
    market_cart_size = 321 if market_cart_shortcut else None
    request = build_request(
        cells_count, market_search_shortcut, market_cart_size,
    )

    response = await taxi_shortcuts.post(
        consts.SCREEN_SUPERMARKET_URL, request,
    )
    assert response.status_code == 200
    data = response.json()

    default_item = {
        'action': {
            'deeplink': (
                'yandextaxi://external?service=market'
                '&href=%2Fyandex-go%2Fsearch%3Fnid%3D21448850'
                '%26gps%3D37.69558289806989%252C55.7278709834352%26lr%3D213'
            ),
        },
        'background': {
            'color': '#00FFFF',
            'image_tag': 'shortcuts_market_category_21448850',
        },
        'height': 2,
        'title': 'Бытовая химия',
        'type': 'deeplink',
        'width': 2,
    }

    items = []
    expected_sections = []

    if market_search_shortcut and market_cart_shortcut:
        assert data is not None
        assert 'sections' in data
        assert data['sections'] is not None
        assert data['sections'][0]['shortcut_ids'] is not None
        assert len(data['sections'][0]['shortcut_ids']) == top_block_size
        expected_sections.append(
            {
                'shortcut_ids': data['sections'][0]['shortcut_ids'],
                'type': 'items_linear_grid',
            },
        )
        layout = LAYOUT_OPTIONS[top_block_size - 1]
        search_url = 'yandextaxi://external?service=market&href=%2Fsearch'
        items.append(
            {
                'action': {'deeplink': search_url},
                'background': {
                    'color': '#F7F6F5',
                    'image_tag': 'shortcuts_market_search',
                },
                'height': 1,
                'shortcut_id': data['sections'][0]['shortcut_ids'][0],
                'title': '',
                'type': 'deeplink',
                'width': layout[0],
            },
        )
        items.append(
            {
                'action': {
                    'deeplink': (
                        'yandextaxi://external?service=market&href=%2Fcart'
                    ),
                },
                'background': {
                    'color': '#F7F6F5',
                    'image_tag': 'shortcuts_market_cart',
                },
                'height': 1,
                'overlays': [
                    {
                        'shape': 'label',
                        'text': str(market_cart_size),
                        'background': {'color': '#fe5739'},
                    },
                ],
                'shortcut_id': data['sections'][0]['shortcut_ids'][1],
                'title': '',
                'type': 'deeplink',
                'width': layout[1],
            },
        )
        if cart_overlays:
            items[-1]['overlays'] = cart_overlays

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
                'icon_tag': 'shortcuts_market_header_icon',
                'title': {'text': 'Маркет Express'},
                'type': 'app_title',
            },
            'trail': TRAIL,
            'type': 'list_item',
        }

    assert data == expected_data


@pytest.mark.parametrize('cells_count', [None, 0, 1, 5])
@pytest.mark.experiments3(filename='experiments3_for_supermarket_screen.json')
async def test_usual_case(taxi_shortcuts, add_config, cells_count):
    add_config(
        'shortcuts_sections_settings',
        {'order': ['other', 'buttons', 'header']},
    )

    await check_post(taxi_shortcuts, cells_count)


@pytest.mark.parametrize('cells_count', [0, 3])
@pytest.mark.parametrize('with_typed_header', [True, False])
@pytest.mark.experiments3(filename='experiments3_for_supermarket_screen.json')
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
    exp_value = {'supermarket': {'suggest_mode': 'market'}}
    if with_typed_header:
        exp_value['supermarket']['typed_header'] = {
            'lead': {
                'type': 'app_title',
                'title': {'text': {'text': 'Маркет Express'}},
                'icon_tag': 'shortcuts_market_header_icon',
            },
            'trail': TRAIL,
            'type': 'list_item',
        }
    add_experiment('shortcuts_screen_settings', exp_value)

    await check_post(taxi_shortcuts, cells_count, with_typed_header)


@pytest.mark.parametrize('cells_count', [0, 3])
async def test_null_screen_settings_exp(taxi_shortcuts, cells_count):
    await check_post(taxi_shortcuts, cells_count, False)


OVERLAYS = {
    'overlays': [
        {
            'text': 'superapp.market.cart_size',
            'shape': 'label',
            'background': {'color': 'white'},
        },
    ],
}


@pytest.mark.parametrize(
    'search_shortcut, cart_shortcut, block_size',
    [
        (None, None, 0),
        (None, CART_SHORTCUT, 1),
        (SEARCH_SHORTCUT, None, 1),
        (SEARCH_SHORTCUT, CART_SHORTCUT, 2),
    ],
)
@pytest.mark.experiments3(filename='experiments3_for_supermarket_screen.json')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='supermarket_cart_appearance',
    consumers=['shortcuts/shortcuts'],
    clauses=[],
    default_value=OVERLAYS,
)
@pytest.mark.translations(
    client_messages={'superapp.market.cart_size': {'ru': '(%(count)s)'}},
)
async def test_top_block(
        taxi_shortcuts,
        add_config,
        add_experiment,
        search_shortcut,
        cart_shortcut,
        block_size,
):
    add_config(
        'shortcuts_sections_settings',
        {'order': ['other', 'buttons', 'header']},
    )
    exp_value = {'layout_options': [[6], [5, 1]]}
    if search_shortcut:
        exp_value['search_shortcut'] = search_shortcut
    if cart_shortcut:
        exp_value['cart_shortcut'] = cart_shortcut
    add_experiment('superapp_supermarket_settings', exp_value)

    await check_post(
        taxi_shortcuts,
        3,
        True,
        search_shortcut,
        cart_shortcut,
        block_size,
        cart_overlays=[
            {
                'text': '(321)',
                'shape': 'label',
                'background': {'color': 'white'},
            },
        ],
    )


ADDITIONAL_SECTIONS = [
    {
        'slug': 'as0',
        'section': {'type': 'buttons_container', 'button_ids': []},
    },
    {
        'slug': 'as1',
        'section': {'type': 'horizontal_stack_section', 'stack_item_ids': []},
    },
]


@pytest.mark.parametrize(
    'additional_sections, sections_order, supported_sections, expected_types',
    [
        pytest.param(None, None, None, ['items_linear_grid'], id='default'),
        pytest.param(
            ADDITIONAL_SECTIONS,
            None,
            None,
            [
                'items_linear_grid',
                'buttons_container',
                'horizontal_stack_section',
            ],
            id='additions',
        ),
        pytest.param(
            ADDITIONAL_SECTIONS,
            None,
            [{'type': 'items_linear_grid'}],
            ['items_linear_grid'],
            id='filtered',
        ),
        pytest.param(
            ADDITIONAL_SECTIONS,
            ['as1', 'eats_shops', 'as0'],
            None,
            [
                'horizontal_stack_section',
                'items_linear_grid',
                'buttons_container',
            ],
            id='ordering',
        ),
    ],
)
async def test_sections_order(
        taxi_shortcuts,
        add_config,
        additional_sections,
        sections_order,
        supported_sections,
        expected_types,
):
    add_config('shortcuts_sections_settings', {'order': sections_order})

    request = build_request(
        additional_sections=additional_sections,
        supported_sections=supported_sections,
    )

    response = await taxi_shortcuts.post(
        consts.SCREEN_SUPERMARKET_URL, request,
    )
    assert response.status_code == 200
    data = response.json()
    sections_types = [s['type'] for s in data['sections']]
    assert sections_types == expected_types
