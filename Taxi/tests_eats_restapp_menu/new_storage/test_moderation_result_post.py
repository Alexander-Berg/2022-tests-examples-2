import pytest

PLACE_ID = 109151
REVISION = 'Mi4y'
TASK_ID = 'task123'


@pytest.mark.experiments3(filename='transitional_settings.json')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
@pytest.mark.now('2021-01-01T12:00:00Z')
async def test_ns_moderation_result_post_change_data(
        taxi_eats_restapp_menu, load_json, pg_get_menus, pg_get_items,
):

    response = await taxi_eats_restapp_menu.post(
        '/v1/moderation/result',
        json={
            'task_id': TASK_ID,
            'context': {'place_id': str(PLACE_ID)},
            'queue': 'restapp_moderation_item',
            'status': 'approved',
            'actual_payload': {},
            'payload': {
                'id': '1234595',
                'revision': REVISION,
                'value': '{"name": "Поправили имя"}',
            },
        },
    )

    db_menus = pg_get_menus()
    assert len(db_menus) == 3
    assert (
        db_menus[0]['origin'] == 'external'
        and db_menus[0]['items_hash'] == '1231231231231231231231'
        and db_menus[1]['origin'] == 'user_generated'
        and db_menus[1]['items_hash'] == 'cth27DbS0H_aZNL8gq_MGA'
        and db_menus[2]['origin'] == 'moderation'
        and db_menus[2]['items_hash'] == '0KIVHs8E3vkXpY0fSX4adQ'
    )

    assert response.status_code == 200
    assert pg_get_items() == load_json('expected_items.json')


@pytest.mark.experiments3(filename='transitional_settings.json')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': False,
    },
)
@pytest.mark.now('2021-01-01T12:00:00Z')
async def test_ns_moderation_result_post_change_options(
        taxi_eats_restapp_menu, load_json, pg_get_menus, pg_get_items,
):

    response = await taxi_eats_restapp_menu.post(
        '/v1/moderation/result',
        json={
            'task_id': TASK_ID,
            'context': {'place_id': str(PLACE_ID)},
            'queue': 'restapp_moderation_item',
            'status': 'approved',
            'actual_payload': {},
            'payload': {
                'id': '1234595',
                'revision': REVISION,
                'value': (
                    '{"name": "Сметана 20%", "options_groups":'
                    ' [{"origin_id": "2716078", "name": "Поменяли_имя_г'
                    'руппы", "options": [{"origin_id": "26778790", "nam'
                    'e": "XYZ"}]}]}'
                ),
            },
        },
    )

    db_menus = pg_get_menus()
    assert len(db_menus) == 3
    assert (
        db_menus[0]['origin'] == 'external'
        and db_menus[0]['items_hash'] == '1231231231231231231231'
        and db_menus[1]['origin'] == 'user_generated'
        and db_menus[1]['items_hash'] == 'cth27DbS0H_aZNL8gq_MGA'
        and db_menus[2]['origin'] == 'moderation'
        and db_menus[2]['items_hash'] == 'XvjUD4VF59qQdKldHhLCtw'
    )

    assert response.status_code == 200
    assert pg_get_items() == load_json('expected_items_options.json')
