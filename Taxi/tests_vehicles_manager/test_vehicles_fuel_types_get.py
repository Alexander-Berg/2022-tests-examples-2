import pytest

ENDPOINT_URL = '/fleet/vehicles-manager/v1/fuel/type'

PARKS_ALLOWED_FUEL_VALUES = ['petrol', 'methane', 'propane', 'electricity']

TRANSLATIONS = {
    'petrol': {'ru': 'Бензин'},
    'methane': {'ru': 'Метан'},
    'propane': {'ru': 'Пропан'},
    'electricity': {'ru': 'Электричество'},
}

VEHICLES_MANAGER_HEADERS = {'X-Park-ID': '123', 'Accept-Language': 'ru'}


@pytest.mark.translations(backend_vehicles_manager=TRANSLATIONS)
@pytest.mark.config(PARKS_ALLOWED_FUEL_VALUES=PARKS_ALLOWED_FUEL_VALUES)
async def test_get_fuel(taxi_vehicles_manager):
    response = await taxi_vehicles_manager.get(
        ENDPOINT_URL, headers=VEHICLES_MANAGER_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'items': [
            {'value': 'electricity', 'label': 'Электричество'},
            {'value': 'propane', 'label': 'Пропан'},
            {'value': 'methane', 'label': 'Метан'},
            {'value': 'petrol', 'label': 'Бензин'},
        ],
    }
