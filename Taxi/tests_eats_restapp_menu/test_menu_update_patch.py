import json

import pytest

PARTNER_ID = '777'
PLACE_ID = '109151'
INVALID_REVISION = '123'
VALID_REVISION = 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla'
NEW_REVISION = 'MS4xNjA5NTAyNDAwMDAwLmVCMFZvSTlOWmRlUVBOYjhCR1AxaGc'


async def test_menu_update_patch_no_access(
        taxi_eats_restapp_menu, mock_write_access_403, load_json,
):
    response = await taxi_eats_restapp_menu.patch(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/update',
        params={'place_id': PLACE_ID, 'revision': INVALID_REVISION},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
        json={'menu': load_json('add_data.json')},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Access to place is denied',
    }

    assert mock_write_access_403.times_called == 1


@pytest.mark.now('2021-01-01T12:00:00Z')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data.sql',))
async def test_menu_update_patch_basic(
        taxi_eats_restapp_menu,
        mock_write_access_200,
        load_json,
        stq,
        testpoint,
        pg_get_revisions,
        pg_get_menu_content,
):
    @testpoint('DuplicateAdd')
    def duplicate_add(arg):
        pass

    response = await taxi_eats_restapp_menu.patch(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/update',
        params={'place_id': PLACE_ID, 'revision': VALID_REVISION},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
        json={'menu': load_json('add_data.json')},
    )

    assert response.status_code == 200
    assert response.json() == {
        'revision': NEW_REVISION,
        'status': 'processing',
        'status_type': 'intermediate',
    }

    assert duplicate_add.times_called == 0
    assert mock_write_access_200.times_called == 1
    assert stq.eats_restapp_menu_update_menu.times_called == 1

    assert len(pg_get_revisions()) == 2
    db_data = pg_get_menu_content()
    assert len(db_data) == 2

    assert json.loads(pg_get_menu_content()[0]['menu_json']) == load_json(
        'expected.json',
    )
