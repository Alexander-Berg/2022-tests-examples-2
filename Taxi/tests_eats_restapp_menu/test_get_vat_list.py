import pytest


async def request_proxy_get_vat_list(taxi_eats_restapp_menu, country):
    url = (
        '/4.0/restapp-front/eats-restapp-menu/v1/places/vat-list'
        '?country={}'.format(country)
    )

    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}

    return await taxi_eats_restapp_menu.get(url, **extra)


@pytest.mark.config(
    EATS_RESTAPP_MENU_CLIENT_VAT_LIST=[
        {
            'country': 'RUS',
            'values': [
                {'value': 10, 'description': '10%'},
                {'value': 20, 'description': '20%'},
            ],
        },
    ],
)
async def test_get_vat_list(taxi_eats_restapp_menu, taxi_config):
    country = 'RUS'

    response = await request_proxy_get_vat_list(
        taxi_eats_restapp_menu, country,
    )

    assert response.status_code == 200
    assert len(response.json()['values']) == 2
    assert response.json()['values'][0]['value'] == 10
    assert response.json()['values'][0]['description'] == '10%'
    assert response.json()['values'][1]['value'] == 20
    assert response.json()['values'][1]['description'] == '20%'


async def test_get_vat_list_404(taxi_eats_restapp_menu):
    country = 'RUS'
    response = await request_proxy_get_vat_list(
        taxi_eats_restapp_menu, country,
    )
    assert response.status_code == 404
    assert response.json()['code'] == '404'
