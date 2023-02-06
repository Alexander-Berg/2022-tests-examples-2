import pytest

PARTNER_ID = '777'
PLACE_ID = '109151'
INVALID_REVISION = '123'
VALID_REVISION = 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla'
NEW_REVISION = 'MS4xNjA5NTAyNDAwMDAwLlFCOVlobWg5R2dQS0FEYmlzLUY0dFE'


async def test_menu_update_post_no_access(
        taxi_eats_restapp_menu, mock_write_access_403, load_json,
):
    response = await taxi_eats_restapp_menu.post(
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
        'url_prefix': 'http://avatars.mdst.yandex.net/get-eda',
        'image_postfix': '/orig',
        'thumbnail_postfix': '/80x80',
        'image_processing_enabled': True,
    },
)
async def test_menu_update_post_basic(
        taxi_eats_restapp_menu,
        mock_write_access_200,
        load_json,
        stq,
        testpoint,
):
    @testpoint('DuplicateAdd')
    def duplicate_add(arg):
        pass

    response = await taxi_eats_restapp_menu.post(
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


@pytest.mark.now('2021-01-01T12:00:00Z')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'http://avatars.mdst.yandex.net/get-eda',
        'image_postfix': '/orig',
        'thumbnail_postfix': '/80x80',
        'image_processing_enabled': True,
    },
)
async def test_menu_update_post_duplicate(
        taxi_eats_restapp_menu,
        mock_write_access_200,
        load_json,
        stq,
        testpoint,
        pg_get_revisions,
):
    @testpoint('DuplicateAdd')
    def duplicate_add(arg):
        assert arg == NEW_REVISION

    response = await taxi_eats_restapp_menu.post(
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

    response = await taxi_eats_restapp_menu.post(
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

    assert len(pg_get_revisions()) == 2
    assert duplicate_add.times_called == 1
    assert mock_write_access_200.times_called == 2
    assert stq.eats_restapp_menu_update_menu.times_called == 1
