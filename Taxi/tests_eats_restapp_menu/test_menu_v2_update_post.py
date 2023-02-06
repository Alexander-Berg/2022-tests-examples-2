PARTNER_ID = '777'
PLACE_ID = '109151'
INVALID_REVISION = '123'
VALID_REVISION = 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla'


async def test_menu_update_post_no_access(
        taxi_eats_restapp_menu, mock_write_access_403, load_json,
):
    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v2/menu/update',
        params={'place_id': PLACE_ID, 'revision': INVALID_REVISION},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
        json={'menu': {'categories': [], 'items': []}},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Access to place is denied',
    }

    assert mock_write_access_403.times_called == 1


async def test_menu_update_post_basic(
        taxi_eats_restapp_menu, mock_write_access_200,
):
    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v2/menu/update',
        params={'place_id': PLACE_ID, 'revision': VALID_REVISION},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
        json={'menu': {'categories': [], 'items': []}},
    )

    assert response.status_code == 200
    assert mock_write_access_200.times_called == 1
