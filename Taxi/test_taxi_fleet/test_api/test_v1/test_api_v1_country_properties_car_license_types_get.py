import aiohttp.web
import pytest


FLEET_COUNTRY_PROPERTIES = {
    'deu': {
        'car_license_types': [
            {'id': 'taxi', 'tanker_key': 'CarLicenseType.Standard'},
            {'id': 'phv', 'tanker_key': 'CarLicenseType.PrivateHireVehicle'},
        ],
    },
    'rus': {
        'car_license_types': [
            {'id': 'license_id3', 'tanker_key': 'CarLicenseType.LicenseType3'},
        ],
    },
    'usa': {
        'car_license_types': [
            {'id': 'license_id4', 'tanker_key': 'CarLicenseType.LicenseType4'},
            {'id': 'license_id5', 'tanker_key': 'CarLicenseType.LicenseType5'},
            {'id': 'license_id6', 'tanker_key': 'CarLicenseType.LicenseType6'},
        ],
    },
}


@pytest.mark.config(FLEET_COUNTRY_PROPERTIES=FLEET_COUNTRY_PROPERTIES)
@pytest.mark.parametrize(
    'park_id, locale, response_200',
    [
        pytest.param(
            '8601e1f8e094424aa70c81b61ffdf00f',
            'ru, ru',
            [{'id': 'license_id3', 'name': 'Тип лицензии 3'}],
            id='correct_request_rus',
        ),
        pytest.param(
            '8601e1f8e094424aa70c81b61ffdf01f',
            'en',
            [{'id': 'taxi', 'name': 'Standard'}, {'id': 'phv', 'name': 'PHV'}],
            id='correct_request_deu',
        ),
        pytest.param(
            '8601e1f8e094424aa70c81b61ffdf02f',
            'en, ru',
            [
                {'id': 'license_id4', 'name': 'License type 4'},
                {'id': 'license_id5', 'name': 'License type 5'},
                {'id': 'license_id6', 'name': 'License type 6'},
            ],
            id='correct_request_usa',
        ),
        pytest.param(
            '8601e1f8e094424aa70c81b61ffdf03f',
            'ru, en',
            [],
            id='correct_request_ukr',
        ),
    ],
)
@pytest.mark.translations(
    opteum_enums={
        'CarLicenseType.Standard': {'ru': 'Стандартная', 'en': 'Standard'},
        'CarLicenseType.PrivateHireVehicle': {'ru': 'PHV', 'en': 'PHV'},
        'CarLicenseType.LicenseType3': {
            'ru': 'Тип лицензии 3',
            'en': 'License type 3',
        },
        'CarLicenseType.LicenseType4': {
            'ru': 'Тип лицензии 4',
            'en': 'License type 4',
        },
        'CarLicenseType.LicenseType5': {
            'ru': 'Тип лицензии 5',
            'en': 'License type 5',
        },
        'CarLicenseType.LicenseType6': {
            'ru': 'Тип лицензии 6',
            'en': 'License type 6',
        },
    },
)
async def test_response_200(
        web_app_client,
        headers,
        park_id,
        locale,
        response_200,
        mock_fleet_parks,
        load_json,
):
    fleet_parks_stub = load_json('fleet_parks_success.json')

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request):
        assert (
            request.json['query']['park']['ids'][0]
            in fleet_parks_stub['request']
        )
        return aiohttp.web.json_response(
            fleet_parks_stub['response'][
                request.json['query']['park']['ids'][0]
            ],
        )

    response = await web_app_client.get(
        '/api/v1/country-properties/car-license-types',
        headers={**headers, 'X-Park-Id': park_id, 'Accept-Language': locale},
    )

    assert response.status == 200

    data = await response.json()
    assert list(data.keys()) == ['car_license_types']
    assert data['car_license_types'] == response_200
