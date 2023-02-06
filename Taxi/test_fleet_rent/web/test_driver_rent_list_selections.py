import pytest


@pytest.mark.translations(
    taximeter_backend_fleet_rent={
        'rent_record_list_title.unreacted': {'ru': 'Новые списания'},
        'rent_record_list_title.active': {'ru': 'Активные списания'},
        'rent_record_list_title.finished': {'ru': 'Завершившиеся списания'},
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
    cities={'Москва': {'ru': 'Москва'}},
)
async def test_selections(web_app_client, driver_auth_headers):
    response = await web_app_client.get(
        '/driver/v1/periodic-payments/rent/list-selections',
        headers=driver_auth_headers,
    )
    assert response.status == 200
    data = await response.json()
    assert data == {
        'title': 'Orders',
        'items': [
            {
                'type': 'detail',
                'payload': {
                    'type': 'navigate_rent_selection',
                    'rent_listing_selection': 'unreacted',
                },
                'horizontal_divider_type': 'bottom_gap',
                'title': 'Новые списания',
                'right_icon': 'navigate',
            },
            {
                'type': 'detail',
                'payload': {
                    'type': 'navigate_rent_selection',
                    'rent_listing_selection': 'active',
                },
                'horizontal_divider_type': 'bottom_gap',
                'title': 'Активные списания',
                'right_icon': 'navigate',
            },
            {
                'type': 'detail',
                'payload': {
                    'type': 'navigate_rent_selection',
                    'rent_listing_selection': 'finished',
                },
                'horizontal_divider_type': 'bottom_gap',
                'title': 'Завершившиеся списания',
                'right_icon': 'navigate',
            },
        ],
    }
