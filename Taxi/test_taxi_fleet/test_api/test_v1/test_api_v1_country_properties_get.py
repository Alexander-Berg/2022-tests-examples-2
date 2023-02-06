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
            {'id': 'taxi', 'tanker_key': 'CarLicenseType.Standard'},
            {'id': 'phv', 'tanker_key': 'CarLicenseType.PrivateHireVehicle'},
        ],
        'medical_rides': {'medical_transport': True},
        'vat_values': ['0', '7', '19'],
    },
    'usa': {
        'car_license_types': [
            {'id': 'taxi', 'tanker_key': 'CarLicenseType.Standard'},
            {'id': 'phv', 'tanker_key': 'CarLicenseType.PrivateHireVehicle'},
        ],
        'medical_rides': {'medical_transport': False},
        'vat_values': ['0', '7', '19'],
    },
}


@pytest.mark.config(FLEET_COUNTRY_PROPERTIES=FLEET_COUNTRY_PROPERTIES)
@pytest.mark.parametrize(
    'park_id, response_200',
    [
        pytest.param(
            '8601e1f8e094424aa70c81b61ffdf00f',
            {
                'car_license_types',
                'vat_values',
                'medical_rides',
                'medical_transport',
            },
            id='correct_request_rus',
        ),
        pytest.param(
            '8601e1f8e094424aa70c81b61ffdf01f',
            {'car_license_types'},
            id='correct_request_deu',
        ),
        pytest.param(
            '8601e1f8e094424aa70c81b61ffdf02f',
            {'car_license_types', 'vat_values', 'medical_rides'},
            id='correct_request_usa',
        ),
        pytest.param(
            '8601e1f8e094424aa70c81b61ffdf03f',
            set(),
            id='correct_request_ukr',
        ),
    ],
)
async def test_response_200(
        web_app_client,
        headers,
        park_id,
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
        '/api/v1/country-properties',
        headers={**headers, 'X-Park-Id': park_id},
    )

    assert response.status == 200

    data = await response.json()
    assert set(data.keys()) == {'available_properties'}
    assert len(data['available_properties']) == len(response_200)
    assert set(data['available_properties']) == response_200
