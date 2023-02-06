import pytest


@pytest.mark.translations(
    tariff={
        'name.econom': {'ru': 'Эконом'},
        'name.comfort': {'ru': 'Комфорт'},
        'name.comfortplus': {'ru': 'Комфорт+'},
        'name.business': {'ru': 'Бизнес'},
        'name.minivan': {'ru': 'Минивэн'},
    },
)
def test_vehicles_classes(taxi_marketplace_api):
    response = taxi_marketplace_api.post(
        '/v1/vehicles/classes',
        headers={
            'Accept-Language': 'ru',
            'X-YaTaxi-API-Key': 'marketplace_api_key',
        },
        json={'zone_name': 'moscow'},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['classes']) == 5
    assert sorted(data['classes'], key=lambda cl: cl['class']) == [
        {'class': 'business', 'name': 'Комфорт'},
        {'class': 'comfortplus', 'name': 'Комфорт+'},
        {'class': 'econom', 'name': 'Эконом'},
        {'class': 'minivan', 'name': 'Минивэн'},
        {'class': 'vip', 'name': 'Бизнес'},
    ]
