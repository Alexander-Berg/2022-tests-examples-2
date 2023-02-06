import pytest


PARK_ID = '458f82d8dbf24ecd81d1de2c7826d1b5'
DRIVER_ID = 'e2b66c10ece54751a8db96b3a2039b0f'

DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'Timezone': 'Europe/Moscow',
    'X-Remote-IP': '12.34.56.78',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata_with_requirements.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
        'pg_courier_requirements.sql',
    ],
)
@pytest.mark.parametrize(
    'request_dict, response_code, response_json',
    [
        (
            {
                'offer_identities': [
                    {
                        'slot_id': 'a278134c-49f2-48bc-b9b6-941c76650508',
                        'rule_version': 2,
                    },
                ],
            },
            200,
            {
                'polygons': [
                    {
                        'offer_identity': {
                            'rule_version': 2,
                            'slot_id': 'a278134c-49f2-48bc-b9b6-941c76650508',
                        },
                        'polygon': {
                            'coordinates': [
                                [
                                    {'lat': 62.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 54.0},
                                ],
                            ],
                        },
                    },
                ],
            },
        ),
        (
            {
                'offer_identities': [
                    {
                        'slot_id': 'a278134c-49f2-48bc-b9b6-941c76650508',
                        'rule_version': 2,
                    },
                    {
                        'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                        'rule_version': 2,
                    },
                ],
            },
            200,
            {
                'polygons': [
                    {
                        'offer_identity': {
                            'rule_version': 2,
                            'slot_id': 'a278134c-49f2-48bc-b9b6-941c76650508',
                        },
                        'polygon': {
                            'coordinates': [
                                [
                                    {'lat': 62.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 54.0},
                                ],
                            ],
                        },
                    },
                    {
                        'offer_identity': {
                            'rule_version': 2,
                            'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                        },
                        'polygon': {
                            'coordinates': [
                                [
                                    {'lat': 62.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 54.0},
                                ],
                            ],
                        },
                    },
                ],
            },
        ),
        (
            {
                'offer_identities': [
                    {
                        'slot_id': 'a278134c-49f2-48bc-b9b6-404404404404',
                        'rule_version': 2,
                    },
                ],
            },
            404,
            [],
        ),
        (
            {
                'offer_identities': [
                    {
                        'slot_id': 'a278134c-49f2-48bc-b9b6-941c76650508',
                        'rule_version': 42,
                    },
                ],
            },
            404,
            [],
        ),
    ],
)
async def test_offer_geoarea_by_slot(
        taxi_logistic_supply_conductor,
        request_dict,
        response_code,
        response_json,
):
    await taxi_logistic_supply_conductor.invalidate_caches()

    response = await taxi_logistic_supply_conductor.post(
        '/internal/v1/offer/geoarea-by-slot',
        json=request_dict,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == response_code

    if response.status_code == 200:
        print(response.json())
        assert response.json() == response_json
