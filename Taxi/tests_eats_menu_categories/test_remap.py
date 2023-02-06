import dataclasses

import pytest

from tests_eats_menu_categories import models


@pytest.mark.now('2021-12-10T01:16:00+03:00')
@pytest.mark.yt(
    dyn_table_data=[
        {
            'path': '//home/eda-dwh/raw/bigfood/place_menu_items/2021',
            'values': [
                {
                    'id': 1,
                    'doc': dataclasses.asdict(
                        models.YtMenuItem(
                            item_legacy_id=1,
                            place_id=100,
                            name='Menu Item 1',
                            updated_at='2021-02-16 10:51:24.000000',
                        ),
                    ),
                },
                {'id': 2, 'doc': {'invalid': []}},
                {
                    'id': 3,
                    'doc': dataclasses.asdict(
                        models.YtMenuItem(
                            item_legacy_id=3,
                            place_id=100,
                            name='Menu Item 3',
                            updated_at='2021-12-10T01:16:00+03:00',
                        ),
                    ),
                },
                {
                    'id': 4,
                    'doc': dataclasses.asdict(
                        models.YtMenuItem(
                            item_legacy_id=4,
                            place_id=103,
                            name='Menu Item 4',
                            updated_at='',
                        ),
                    ),
                },
            ],
        },
    ],
)
async def test_force_remap(taxi_eats_menu_categories, yt_apply, testpoint):

    messages = []

    @testpoint('TaskManager::RemapMenuItems::task')
    def send_task(msg):
        messages.append(msg)

    response = await taxi_eats_menu_categories.post(
        '/internal/eats-menu-categories/v1/menu-items/remap',
        headers={'x-yandex-login': 'testsuite'},
        json={'menu_items': ['1', '2', '4']},
    )

    assert response.status_code == 204
    assert send_task.times_called == 2 and len(messages) == 2

    messages.sort(key=lambda item: item['item_legacy_id'])

    assert messages == [
        {
            'item_legacy_id': 1,
            'place_id': 100,
            'name': 'Menu Item 1',
            'updated_at': '2021-02-16 10:51:24.000000',
        },
        {
            'item_legacy_id': 4,
            'place_id': 103,
            'name': 'Menu Item 4',
            'updated_at': '',
        },
    ]
