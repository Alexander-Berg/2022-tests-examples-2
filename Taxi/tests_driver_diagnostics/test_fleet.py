import pytest

from tests_driver_diagnostics import utils


FLEET_HEADERS = {
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'login',
    'X-Yandex-UID': '123',
    'X-Park-ID': 'park_id1',
    'Accept-Language': 'ru',
}

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


REASONS = {
    'efficiency/driver_weariness': ['blocked till 2020-01-02T20:10:00.0+0000'],
}

DETAILS = {
    'partners/fetch_exams_classes': ['econom by exams: exam1, exam2'],
    'efficiency/fetch_tags_classes': ['econom by tags: tag1, tag2'],
    'infra/fetch_profile_classes': [
        'econom by grade',
        'comfortplus by requirements: req1, req2',
    ],
    'infra/fetch_final_classes': ['econom by final result'],
}


def response_key_func(arg: dict):
    key = ''
    block_reasons = arg.get('block_reasons', [])
    for reason in block_reasons:
        key += reason['text']
    return key


@pytest.mark.parametrize(
    'driver_id,status_code,response_key',
    [('driver_id1', 200, 'all_good'), ('driver_id2', 404, 'not_found')],
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
async def test_fleet_handle(
        taxi_driver_diagnostics,
        candidates,
        mock_fleet_parks_list,
        driver_categories_api,
        load_json,
        driver_profiles,
        qc_cpp,
        driver_id,
        status_code,
        response_key,
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
    candidates.set_response_reasons(REASONS, DETAILS)
    driver_categories_api.set_categories(
        ['econom', 'comfortplus', 'maybach', 'comfort'],
    )

    response = await taxi_driver_diagnostics.get(
        'fleet/driver-diagnostics/v1/restrictions',
        headers=FLEET_HEADERS,
        params={'driver_id': driver_id},
    )

    assert response.status_code == status_code

    response_json = response.json()
    if isinstance(response_json.get('tariffs', None), list):
        response_json['tariffs'].sort(key=response_key_func)
        print(response_json)

    expected_json = load_json('fleet_response.json')[response_key]
    if isinstance(expected_json.get('tariffs', None), list):
        expected_json['tariffs'].sort(key=response_key_func)
        print(expected_json)

    assert response_json == expected_json
