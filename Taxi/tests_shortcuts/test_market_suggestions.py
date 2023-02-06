import copy

import pytest

from tests_shortcuts import consts

SHORTCUT_IDS = ['id1', 'id2', 'id3', 'id4', 'id5']


def build_request(
        cells_count=1, market_suggestions=None, geobase_city_id=None,
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
            'supported_sections': [
                {'type': 'header_linear_grid'},
                {'type': 'items_linear_grid'},
                {'type': 'buttons_container'},
                {'type': 'horizontal_stack_section'},
            ],
        },
        'grid': {'id': 'id', 'width': 6, 'cells': cells, 'blocks': blocks},
    }

    if market_suggestions is not None:
        payload['market_suggestions'] = market_suggestions
    if geobase_city_id is not None:
        payload['geobase_city_id'] = geobase_city_id

    return payload


@pytest.mark.experiments3(
    filename='experiments3_for_supermarket_suggestions.json',
)
@pytest.mark.parametrize(
    'url, geobase_city_id',
    [
        pytest.param(consts.URL, 213, id='default'),
        pytest.param(consts.SCREEN_SUPERMARKET_URL, 213, id='supermarket'),
        pytest.param(consts.URL, None, id='!geobase_city_id'),
    ],
)
async def test_market_suggestions(
        taxi_shortcuts, add_config, load_yaml, url, geobase_city_id,
):
    add_config(
        'shortcuts_sections_settings',
        {
            'order': [
                'market-suggestions:cCa',
                'eats_shops',
                'market-suggestions:cBa',
            ],
        },
    )

    request = build_request(
        market_suggestions=load_yaml('suggestion_items_request.yaml'),
        geobase_city_id=geobase_city_id,
    )

    response = await taxi_shortcuts.post(url, request)
    assert response.status_code == 200
    data = response.json()
    if geobase_city_id is None:
        assert data['sections'] == [
            {'type': 'items_linear_grid', 'shortcut_ids': ['id1']},
            {'stack_item_ids': ['qwe'], 'type': 'horizontal_stack_section'},
        ]
        assert data['offers']['stack_items'] == [
            {
                'alignment_top_items': [
                    {'qwe': ['rty'], 'type': 'unknown'},
                    {'type': 'thumb'},
                ],
                'id': 'qwe',
                'type': 'vertical_stack_item',
            },
        ]
        return
    assert data['sections'] == load_yaml('suggestion_sections_response.yaml')
    assert data['offers']['stack_items'] == load_yaml(
        'suggestion_items_response.yaml',
    )
