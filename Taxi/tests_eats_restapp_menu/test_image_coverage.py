import math

import pytest


PARTNER_ID = '777'
PLACE_ID = '109151'
PLACE_ID_2 = '109152'
MENU_REVISION = 'MS4xNjA5NDU5MjAwMDAwLlh0dWlHWUUzeE96cER1WDN0dndkeFE'


@pytest.mark.experiments3(filename='moderation_flow_settings.json')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
async def test_menu_count_percent(
        taxi_eats_restapp_menu,
        mock_place_access_200,
        mockserver,
        load_json,
        pgsql,
):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def mock_place_menu(request):
        return load_json('base_data.json')

    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/active',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 200
    assert mock_place_menu.times_called == 1

    cursor = pgsql['eats_restapp_menu'].dict_cursor()

    cursor.execute('SELECT * FROM eats_restapp_menu.picture_coverage;')
    coverage = cursor.fetchall()
    assert len(coverage) == 2
    assert (
        math.isclose(float(coverage[1]['menu_picture_cover_percentage']), 100)
        and coverage[1]['menu_items_cnt'] == 2
        and coverage[1]['menu_item_with_pictures_cnt'] == 2
        and math.isclose(
            float(coverage[0]['menu_picture_cover_percentage']), 85.5556,
        )
        and coverage[0]['menu_items_cnt'] == 100
        and coverage[0]['menu_item_with_pictures_cnt'] == 85
    )


async def test_menu_get_percent(taxi_eats_restapp_menu):
    response = await taxi_eats_restapp_menu.get(
        '/v1/menu/picture_coverage', params={'place_id': PLACE_ID_2},
    )

    assert response.status_code == 200
    assert response.json()['percent'] == '85.56'


async def test_menu_front_get_percent(
        taxi_eats_restapp_menu, mock_place_access_200,
):
    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/picture_coverage',
        params={'place_id': PLACE_ID_2},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 200
    assert response.json()['percent'] == '85.56'


async def test_menu_front_get_percent_access_fail(
        taxi_eats_restapp_menu, mock_place_access_400,
):
    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/picture_coverage',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 403
