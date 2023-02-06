import pytest

ENDPOINT_URL = '/fleet/vehicles-manager/v1/company/list'

VEHICLES_MANAGER_HEADERS = {'X-Park-ID': '123'}

VEHICLES_MANAGER_LEASING_COMPANY = [
    {'code': 'companyA', 'name': 'Компания А'},
    {'code': 'companyB', 'name': 'Компания Б'},
    {'code': 'companyC', 'name': 'Компания С'},
    {'code': 'companyD', 'name': 'Компания Д'},
]

PARKS_LEASING_CONFIG = {
    'available_leasing_companies': ['companyA', 'companyB', 'companyD'],
    'available_leasing_interest_rate': {
        'min_leasing_rate': 0,
        'max_leasing_rate': 100,
    },
    'available_leasing_interest_term': {
        'min_leasing_term': 0,
        'max_leasing_term': 60,
    },
    'available_leasing_start_date_interval': {
        'years_before': 10,
        'years_after': 10,
    },
}


@pytest.mark.config(
    VEHICLES_MANAGER_LEASING_COMPANY=VEHICLES_MANAGER_LEASING_COMPANY,
    PARKS_LEASING_CONFIG=PARKS_LEASING_CONFIG,
)
async def test_get_company(taxi_vehicles_manager):
    response = await taxi_vehicles_manager.get(
        ENDPOINT_URL, headers=VEHICLES_MANAGER_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'items': [
            {'value': 'companyD', 'label': 'Компания Д'},
            {'value': 'companyB', 'label': 'Компания Б'},
            {'value': 'companyA', 'label': 'Компания А'},
        ],
    }
