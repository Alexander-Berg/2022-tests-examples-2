import copy

import pytest

from tests_shortcuts import consts

SHORTCUT_IDS = ['id1', 'id2', 'id3', 'id4', 'id5']


def build_request(cells_count=0, shortcut=None):
    default_cell = {
        'height': 2,
        'width': 3,
        'shortcut': shortcut or consts.DEFAULT_SCOOTERS_SHORTCUT,
    }
    cells = []
    blocks = []
    if cells_count:
        for i in range(cells_count):
            cell = copy.deepcopy(default_cell)
            cell['shortcut']['id'] = SHORTCUT_IDS[i]
            cells.append(cell)

        blocks = [
            {
                'id': '46095517619a465db0a738a2ab1dfd86',
                'shortcut_ids': SHORTCUT_IDS[:cells_count],
                'slug': 'scooters_shortcuts',
            },
        ]

    payload = {
        'shortcuts': {
            'supported_features': [
                {'type': 'header-deeplink', 'prefetch_strategies': []},
                {
                    'prefetch_strategies': [],
                    'services': [],
                    'type': 'header-action-driven',
                },
                {
                    'prefetch_strategies': [],
                    'services': [],
                    'type': 'action-driven',
                },
            ],
            'supported_actions': [{'type': 'scooters_qr_scan'}],
            'supported_sections': [
                {'type': 'header_linear_grid'},
                {'type': 'items_linear_grid'},
            ],
        },
        'grid': {'id': 'id', 'width': 6, 'cells': cells, 'blocks': blocks},
    }

    return payload


DEFAULT_ITEM_QR_SCAN = {
    'title': 'Сканировать',
    'subtitle': 'QR-код на руле самоката',
    'type': 'action-driven',
    'height': 2,
    'width': 3,
    'background': {'color': '#F1F0ED'},
    'action': {'type': 'scooters_qr_scan'},
    'overlays': [
        {'shape': 'bottom_right', 'image_tag': 'app_shortcut_poi_airport'},
    ],
}


async def check_post(
        taxi_shortcuts,
        cells_count,
        expect_typed_header=True,
        shortcut=None,
        default_item=None,
):
    request = build_request(cells_count, shortcut)

    response = await taxi_shortcuts.post(consts.SCREEN_SCOOTERS_URL, request)
    assert response.status_code == 200
    data = response.json()

    items = []
    expected_sections = [
        {
            'shortcut_ids': SHORTCUT_IDS[:cells_count],
            'type': 'items_linear_grid',
        },
    ]

    for i in range(cells_count):
        item = copy.deepcopy(default_item or DEFAULT_ITEM_QR_SCAN)
        item['shortcut_id'] = SHORTCUT_IDS[i]
        items.append(item)

    if expect_typed_header:
        expected_sections[0]['typed_header'] = {
            'type': 'list_item',
            'lead': {
                'type': 'app_title',
                'icon_tag': 'shortcuts_button_scooters:7d1d49',
                'title': {'text': 'Самокаты'},
            },
        }

    expected_data = {
        'layout': {'grid_id': 'id', 'type': 'linear_grid', 'width': 6},
        'offers': {'items': items},
        'sections': expected_sections,
    }

    assert data == expected_data


@pytest.mark.parametrize('cells_count', [0, 1, 5])
@pytest.mark.experiments3(filename='exp3_for_scooters_screen.json')
@pytest.mark.translations(
    client_messages={
        'scooters.screens.shortcuts.header.title': {'ru': 'Самокаты'},
    },
)
async def test_scooters_screen(taxi_shortcuts, add_config, cells_count):
    add_config(
        'shortcuts_sections_settings',
        {'order': ['other', 'buttons', 'header']},
    )

    await check_post(taxi_shortcuts, cells_count)


@pytest.mark.experiments3(filename='exp3_for_scooters_screen.json')
@pytest.mark.translations(
    client_messages={
        'scooters.screens.shortcuts.header.title': {'ru': 'Самокаты'},
    },
)
async def test_any_action(taxi_shortcuts, add_config):
    add_config(
        'shortcuts_sections_settings',
        {'order': ['other', 'buttons', 'header']},
    )

    await check_post(
        taxi_shortcuts,
        1,
        shortcut=consts.DEFAULT_ANYACTION_SHORTCUT,
        default_item={
            'type': 'action-driven',
            'shortcut_id': 'id1',
            'title': 'Подписка',
            'action': consts.WEBAPP_ACTION,
            'width': 3,
            'height': 2,
            'background': {'color': '#00FFFF'},
        },
    )
