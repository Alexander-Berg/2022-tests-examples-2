import pytest

from tests_driver_diagnostics import utils


AUTH_HEADERS = {'Accept-language': 'ru-RU'}

DEFAULT_BODY = utils.get_default_body()

DEFAULT_PARAMS = utils.get_internal_body()['contractor_params']

SELF_EMPLOYED_PARK = {
    'id': 'park_id1',
    'login': 'some_login',
    'name': 'some_name',
    'is_active': True,
    'city_id': 'MSK',
    'locale': 'ru',
    'is_billing_enabled': True,
    'is_franchising_enabled': True,
    'country_id': 'rus',
    'driver_partner_source': 'selfemployed_fns',
    'fleet_type': 'taximeter',
    'provider_config': {'clid': 'park_id1', 'type': 'production'},
    'demo_mode': False,
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
}


@pytest.mark.parametrize(
    'reasons,details',
    [
        (
            {
                'efficiency/driver_weariness': [
                    'blocked till 2020-01-02T20:10:00.0+0000',
                ],
            },
            {
                'partners/fetch_exams_classes': [
                    'econom by exams: exam1, exam2',
                ],
                'efficiency/fetch_tags_classes': [
                    'econom by tags: tag1, tag2',
                ],
                'infra/fetch_profile_classes': [
                    'econom by grade',
                    'comfortplus by requirements: req1, req2',
                ],
                'infra/fetch_final_classes': ['econom by final result'],
            },
        ),
    ],
)
@pytest.mark.config(
    TARIFF_CLASSES_MAPPING={
        'uberx': {'classes': ['econom'], 'requirements': [{'childchair': 3}]},
        'ubernight': {'classes': ['econom']},
    },
    ALL_CATEGORIES=[
        'econom',
        'business',
        'comfortplus',
        'uberx',
        'ubernight',
        'maybach',
        'cargo',
        'comfort',
    ],
)
@pytest.mark.experiments3(filename='diagnostics_admin_settings.json')
async def test_common_handler(
        taxi_driver_diagnostics,
        candidates,
        mock_fleet_parks_list,
        driver_categories_api,
        load_json,
        driver_profiles,
        qc_cpp,
        reasons,
        details,
):
    driver_profiles.set_contractor_data(
        utils.PARK_CONTRACTOR_PROFILE_ID, vehicle_id='12345',
    )
    qc_cpp.set_exams(
        'park_id1_12345',
        [
            {
                'code': 'branding',
                'modified': '2019-02-07T17:28:23.009000Z',
                'present': {'sanctions': ['sticker_off']},
            },
        ],
    )

    mock_fleet_parks_list.set_parks([SELF_EMPLOYED_PARK])
    candidates.set_response_reasons(reasons, details)
    driver_categories_api.set_categories(
        ['econom', 'comfortplus', 'maybach', 'comfort'],
    )

    response = await taxi_driver_diagnostics.post(
        'internal/driver-diagnostics/v1/common/restrictions',
        headers=AUTH_HEADERS,
        json=DEFAULT_BODY,
        params=DEFAULT_PARAMS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('two_levels_common_response.json')
