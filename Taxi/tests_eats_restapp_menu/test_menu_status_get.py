import pytest

PARTNER_ID = '777'
PLACE_ID = '109151'
INVALID_REVISION = 'MS4xNTc3OTA5NzAxMDAwLlRFU1RfU1RSSU5H'
VALID_REVISION = 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla'


@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data.sql',))
async def test_menu_status_get_no_access(
        taxi_eats_restapp_menu, mock_place_access_400, load_json,
):
    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/status',
        params={'place_id': PLACE_ID, 'revision': INVALID_REVISION},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Access to place is denied',
    }

    assert mock_place_access_400.times_called == 1


@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data.sql',))
async def test_menu_status_get_no_data(
        taxi_eats_restapp_menu, mock_place_access_200, load_json,
):
    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/status',
        params={'place_id': PLACE_ID, 'revision': INVALID_REVISION},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': f'Menu with revision {INVALID_REVISION} not found',
    }

    assert mock_place_access_200.times_called == 1


@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data.sql',))
async def test_menu_status_get_basic(
        taxi_eats_restapp_menu, mock_place_access_200, load_json,
):
    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/status',
        params={'place_id': PLACE_ID, 'revision': VALID_REVISION},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 200
    assert response.json() == {
        'revision': VALID_REVISION,
        'status': 'applied',
        'status_type': 'success',
        'created_at': '2020-04-04T04:04:04+00:00',
    }

    assert mock_place_access_200.times_called == 1
