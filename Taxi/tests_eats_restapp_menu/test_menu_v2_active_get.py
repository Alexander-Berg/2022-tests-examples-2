PARTNER_ID = '777'
PLACE_ID = '109151'


async def test_menu_active_get_no_access(
        taxi_eats_restapp_menu, mock_place_access_400,
):
    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v2/menu/active',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Access to place is denied',
    }

    assert mock_place_access_400.times_called == 1


async def test_menu_active_get_basic(
        taxi_eats_restapp_menu, mock_place_access_200,
):
    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v2/menu/active',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 200
    assert mock_place_access_200.times_called == 1
