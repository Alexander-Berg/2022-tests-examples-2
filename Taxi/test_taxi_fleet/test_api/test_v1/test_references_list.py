import aiohttp.web
import pytest


FLEET_COUNTRY_PROPERTIES = {
    'deu': {
        'car_license_types': [
            {'id': 'taxi', 'tanker_key': 'CarLicenseType.Standard'},
            {'id': 'phv', 'tanker_key': 'CarLicenseType.PrivateHireVehicle'},
        ],
    },
}


OPTEUM_ENUMS = {
    'CarLicenseType.PrivateHireVehicle': {'ru': 'PHV'},
    'CarLicenseType.Standard': {'ru': 'Стандартная'},
    'DriverStatus.Not_Working': {'ru': 'Не работает'},
    'DriverStatus.Working': {'ru': 'Работает'},
    'DriverStatus.Fired': {'ru': 'Уволен'},
    'OrderCategory.None': {'ru': '-'},
    'OrderCategory.ComfortPlus': {'ru': 'КомфортПлюс'},
    'OrderCategory.ChildTariff': {'ru': 'Детский'},
    'TransactionType.Payment': {'ru': 'Платеж'},
    'TransactionType.Refund': {'ru': 'Возврат'},
    'TransactionType.Chargeback': {'ru': 'Возвратные'},
}


OPTEUM_PARK_SPECIFICATION_CATEGORIES = {
    'taxi': ['comfort_plus', 'child_tariff'],
}


@pytest.mark.config(
    FLEET_COUNTRY_PROPERTIES=FLEET_COUNTRY_PROPERTIES,
    OPTEUM_PARK_SPECIFICATION_CATEGORIES=OPTEUM_PARK_SPECIFICATION_CATEGORIES,
)
@pytest.mark.translations(opteum_enums=OPTEUM_ENUMS)
async def test_success(web_app_client, mock_parks, headers, load_json):
    references_list = load_json('response.json')
    response = await web_app_client.post(
        '/api/v1/references/list',
        headers=headers,
        json={'references': list(references_list.keys())},
    )

    assert response.status == 200, response.text
    assert await response.json() == references_list


@pytest.mark.config(
    FLEET_COUNTRY_PROPERTIES=FLEET_COUNTRY_PROPERTIES,
    OPTEUM_PARK_SPECIFICATION_CATEGORIES=OPTEUM_PARK_SPECIFICATION_CATEGORIES,
)
@pytest.mark.translations(opteum_enums=OPTEUM_ENUMS)
async def test_success_deu(web_app_client, mock_parks_deu, headers, load_json):
    references_list = load_json('response_deu.json')
    response = await web_app_client.post(
        '/api/v1/references/list',
        headers=headers,
        json={'references': list(references_list.keys())},
    )

    assert response.status == 200, response.text
    assert await response.json() == references_list


@pytest.mark.config(TAXI_FLEET_EXCLUDE_COUNTRY_CODES=['usa'])
async def test_success_countries(
        web_app_client, mock_parks, headers, mockserver, load_json,
):
    @mockserver.json_handler('/territories/v1/countries/list')
    async def _territories(request, **kwargs):
        return aiohttp.web.json_response(
            load_json('response_territories.json'),
        )

    response = await web_app_client.post(
        '/api/v1/references/list',
        headers=headers,
        json={
            'references': [
                'driver_license_countries',
                'driver_passport_countries',
            ],
        },
    )

    assert response.status == 200, response.text
    assert await response.json() == {
        'driver_license_countries': [
            {'id': 'blr', 'name_en': 'Belarus', 'name_ru': 'Беларусь'},
            {'id': 'rus', 'name_en': 'Russia', 'name_ru': 'Россия'},
        ],
        'driver_passport_countries': [
            {'id': 'blr', 'name_en': 'Belarus', 'name_ru': 'Беларусь'},
            {'id': 'rus', 'name_en': 'Russia', 'name_ru': 'Россия'},
        ],
    }
