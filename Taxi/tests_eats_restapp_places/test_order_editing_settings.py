import pytest

PARTNER_ID = 1
PLACE_ID = 42

HANDLE_URL = '/4.0/restapp-front/places/v2/order-editing-settings?place_id={}'


@pytest.fixture(name='mock_eats_core_order_editing_settings')
def _mock_eats_core_order_editing_settings(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/order-editing-settings')
    def _mock_core(request):
        return mockserver.make_response(
            status=200,
            json={
                'is_success': True,
                'payload': {
                    'status': 'enabled',
                    'allow_restaurant_expense_changes': True,
                    'allow_client_expense_changes': True,
                    'allow_cancel': True,
                    'time_to_approve_changes': 10,
                },
            },
        )


async def test_order_editing_settings_success(
        taxi_eats_restapp_places,
        mock_eats_core_order_editing_settings,
        mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.get(
        HANDLE_URL.format(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 200


async def test_places_order_editing_settings_403_on_authorizer_403(
        taxi_eats_restapp_places, mock_restapp_authorizer_403,
):
    response = await taxi_eats_restapp_places.get(
        HANDLE_URL.format(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Error: no access to the place or no permissions',
        'details': {
            'errors': [{'code': '403', 'message': 'Forbidden by authorizer'}],
        },
    }


async def test_places_order_editing_settings_400_on_core_400(
        taxi_eats_restapp_places, mock_eats_core_400, mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.get(
        HANDLE_URL.format(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Error: core request failed',
        'details': {'errors': [{'code': '400', 'message': 'error'}]},
    }


async def test_places_order_editing_settings_404_on_core_404(
        taxi_eats_restapp_places, mock_eats_core_404, mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.get(
        HANDLE_URL.format(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Ресторан не найден',
        'details': {'errors': [{'code': '404', 'message': 'place not found'}]},
    }
