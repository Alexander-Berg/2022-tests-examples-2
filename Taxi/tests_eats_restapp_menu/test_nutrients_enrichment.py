import pytest


PARTNER_ID = '777'
PLACE_ID = '109151'
MENU_REVISION = 'MS4xNjA5NDU5MjAwMDAwLm44dUR3bkF4Q0tLYUxQLUxERG44Rnc'
NEW_REVISION = 'MS4xNjA5NTAyNDAwMDAwLkpNSFd6eXUzWGVvcmFSeGJldVZDV1E'


@pytest.mark.now('2021-01-01T12:00:00Z')
@pytest.mark.config(
    EATS_RESTAPP_MENU_NUTRIENTS_VALIDATION={
        'enabled': False,
        'deviation_percent': 20,
        'max_calories': 100000,
    },
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
async def test_nutrients_enrichment_no_check(
        taxi_eats_restapp_menu, mock_write_access_200, load_json,
):
    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/update',
        params={'place_id': PLACE_ID, 'revision': MENU_REVISION},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
        json={'menu': load_json('add_data_invalid.json')},
    )

    assert response.status_code == 200
    assert response.json() == {
        'revision': NEW_REVISION,
        'status': 'processing',
        'status_type': 'intermediate',
    }

    assert mock_write_access_200.times_called == 1
