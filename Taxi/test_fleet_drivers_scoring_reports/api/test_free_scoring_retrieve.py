import aiohttp.web
import pytest


@pytest.mark.config(
    TAXI_FLEET_EXCLUDE_COUNTRY_CODES=['usa'],
    FLEET_DRIVERS_SCORING_REPORTS_LICENSE_COUNTRIES={
        'countries': [{'code': 'rus', 'key': 'license_country_rus'}],
        'i18n_keyset': 'opteum_scoring',
    },
)
@pytest.mark.translations(
    opteum_scoring={'license_country_rus': {'ru': 'Россия'}},
)
async def test_success(
        web_app_client,
        headers,
        mockserver,
        mock_fleet_drivers_scoring,
        mock_personal_single_license,
        load_json,
):
    stub = load_json('success.json')

    driver_license = '86ЕК868672'
    expected_driver_license = stub['scoring_request']['query']['driver'][
        'license_pd_id'
    ]

    @mockserver.json_handler('/territories/v1/countries/list')
    async def _territories(request, **kwargs):
        return aiohttp.web.json_response(
            load_json('response_territories.json'),
        )

    mock_personal_single_license(driver_license, expected_driver_license)

    @mock_fleet_drivers_scoring('/v1/drivers/scoring/retrieve')
    async def _scoring_retrieve(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/scoring/retrieve',
        headers=headers,
        json={'license': driver_license},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


@pytest.mark.config(
    TAXI_FLEET_EXCLUDE_COUNTRY_CODES=['usa'],
    FLEET_DRIVERS_SCORING_REPORTS_LICENSE_COUNTRIES={
        'countries': [{'code': 'rus', 'key': 'license_country_rus'}],
        'i18n_keyset': 'opteum_scoring',
    },
)
@pytest.mark.translations(
    opteum_scoring={'license_country_rus': {'ru': 'Россия'}},
)
async def test_success_affiliated_has_debt(
        web_app_client,
        headers,
        mockserver,
        mock_fleet_drivers_scoring,
        mock_personal_single_license,
        load_json,
):
    stub = load_json('success_affiliated_has_debt.json')

    driver_license = '86ЕК868672'
    expected_driver_license = stub['scoring_request']['query']['driver'][
        'license_pd_id'
    ]

    @mockserver.json_handler('/territories/v1/countries/list')
    async def _territories(request, **kwargs):
        return aiohttp.web.json_response(
            load_json('response_territories.json'),
        )

    mock_personal_single_license(driver_license, expected_driver_license)

    @mock_fleet_drivers_scoring('/v1/drivers/scoring/retrieve')
    async def _scoring_retrieve(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/scoring/retrieve',
        headers=headers,
        json={'license': driver_license},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


@pytest.mark.config(
    TAXI_FLEET_EXCLUDE_COUNTRY_CODES=['rus'],
    FLEET_DRIVERS_SCORING_REPORTS_LICENSE_COUNTRIES={
        'countries': [{'code': 'rus', 'key': 'license_country_rus'}],
        'i18n_keyset': 'opteum_scoring',
    },
)
@pytest.mark.translations(
    opteum_scoring={'license_country_rus': {'ru': 'Россия'}},
)
async def test_success_license_country_eng(
        web_app_client,
        headers,
        mockserver,
        mock_fleet_drivers_scoring,
        mock_personal_single_license,
        load_json,
):
    stub = load_json('success.json')

    driver_license = '86ЕК868672'
    expected_driver_license = stub['scoring_request']['query']['driver'][
        'license_pd_id'
    ]

    @mockserver.json_handler('/territories/v1/countries/list')
    async def _territories(request, **kwargs):
        return aiohttp.web.json_response(
            load_json('response_territories.json'),
        )

    mock_personal_single_license(driver_license, expected_driver_license)

    @mock_fleet_drivers_scoring('/v1/drivers/scoring/retrieve')
    async def _scoring_retrieve(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/scoring/retrieve',
        headers=headers,
        json={'license': driver_license},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
