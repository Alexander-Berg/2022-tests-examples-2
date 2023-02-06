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
    ],
)
@pytest.mark.parametrize(
    'init_sql, request_json, response_code',
    [
        pytest.param(
            None,
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'cancellation_offer': {
                    'fine_value': {'value': '123', 'currency_code': 'mnt'},
                },
                'actual_offer': {
                    'rule_version': 1,
                    'slot_id': '00000000000000000000000000000000',
                },
                'last_accepted_offer': {
                    'rule_version': 1,
                    'slot_id': '00000000000000000000000000000000',
                },
            },
            404,
            id='incorrect slot',
        ),
        pytest.param(
            None,
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'cancellation_offer': {
                    'fine_value': {'value': '123', 'currency_code': 'mnt'},
                },
                'actual_offer': {
                    'rule_version': 1,
                    'slot_id': '57079d82-fabd-4e70-9961-09a4733bbc57',
                },
                'last_accepted_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
            },
            400,
            id='actual offer older than last accepted offer',
        ),
        pytest.param(
            None,
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'cancellation_offer': {
                    'fine_value': {'value': '123', 'currency_code': 'mnt'},
                },
                'actual_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
                'last_accepted_offer': {
                    'rule_version': 1,
                    'slot_id': 'a4e20684-fd40-490c-b6ac-faf0ee074b89',
                },
            },
            400,
            id='rule_id mismatch',
        ),
        pytest.param(
            None,
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'cancellation_offer': {
                    'fine_value': {'value': '123', 'currency_code': 'mnt'},
                },
                'actual_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
                'last_accepted_offer': {
                    'rule_version': 1,
                    'slot_id': '57079d82-fabd-4e70-9961-09a4733bbc57',
                },
            },
            409,
            id='not accepted slot, paid cancellation',
        ),
        pytest.param(
            None,
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'cancellation_offer': {
                    'fine_value': {'value': '0', 'currency_code': 'rub'},
                },
                'actual_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
                'last_accepted_offer': {
                    'rule_version': 1,
                    'slot_id': '57079d82-fabd-4e70-9961-09a4733bbc57',
                },
            },
            200,
            id='not accepted slot, free cancellation',
        ),
        pytest.param(
            None,
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'cancellation_offer': {
                    'fine_value': {'value': '123', 'currency_code': 'mnt'},
                },
                'actual_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
                'last_accepted_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
            },
            409,
            id='accepted slot, paid cancellation but config is empty',
        ),
        pytest.param(
            None,
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'cancellation_offer': {
                    'fine_value': {'value': '0', 'currency_code': 'rub'},
                },
                'actual_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
                'last_accepted_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
            },
            200,
            id='accepted slot, free cancellation due to empty config',
        ),
        pytest.param(
            None,
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'cancellation_offer': {
                    'fine_value': {'value': '1000', 'currency_code': 'rub'},
                },
                'actual_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
                'last_accepted_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
            },
            200,
            id='accepted slot, paid cancellation',
            marks=pytest.mark.config(
                LOGISTIC_SUPPLY_CONDUCTOR_CANCELLATION_SETTINGS_BY_COUNTRY={
                    'ru': {
                        'cancelation_offer_ttl': 300,
                        'penalties': [
                            {
                                'time_left_until_workshift_start': 1000000000,
                                'fine_value': '1000',
                            },
                            {
                                'time_left_until_workshift_start': 1000,
                                'fine_value': '2000',
                            },
                        ],
                        'currency_code': 'RUB',
                    },
                },
            ),
        ),
        pytest.param(
            None,
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'cancellation_offer': {
                    'fine_value': {'value': '2000', 'currency_code': 'rub'},
                },
                'actual_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
                'last_accepted_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
            },
            409,
            id='accepted slot, paid cancellation, wrong price',
            marks=pytest.mark.config(
                LOGISTIC_SUPPLY_CONDUCTOR_CANCELLATION_SETTINGS_BY_COUNTRY={
                    'ru': {
                        'cancelation_offer_ttl': 300,
                        'penalties': [
                            {
                                'time_left_until_workshift_start': 1000000000,
                                'fine_value': '1000',
                            },
                            {
                                'time_left_until_workshift_start': 1000,
                                'fine_value': '2000',
                            },
                        ],
                        'currency_code': 'RUB',
                    },
                },
            ),
        ),
        pytest.param(
            None,
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'cancellation_offer': {
                    'fine_value': {'value': '0', 'currency_code': 'rub'},
                },
                'actual_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
                'last_accepted_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
            },
            200,
            id='accepted slot, free cancellation due to time left',
            marks=pytest.mark.config(
                LOGISTIC_SUPPLY_CONDUCTOR_CANCELLATION_SETTINGS_BY_COUNTRY={
                    'ru': {
                        'cancelation_offer_ttl': 300,
                        'penalties': [
                            {
                                'time_left_until_workshift_start': 1000,
                                'fine_value': '1000',
                            },
                        ],
                        'currency_code': 'RUB',
                    },
                },
            ),
        ),
        pytest.param(
            None,
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'cancellation_offer': {
                    'fine_value': {'value': '1000', 'currency_code': 'rub'},
                },
                'actual_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
                'last_accepted_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
            },
            409,
            id='accepted slot, paid cancellation but too much time left',
            marks=pytest.mark.config(
                LOGISTIC_SUPPLY_CONDUCTOR_CANCELLATION_SETTINGS_BY_COUNTRY={
                    'ru': {
                        'cancelation_offer_ttl': 300,
                        'penalties': [
                            {
                                'time_left_until_workshift_start': 1000,
                                'fine_value': '1000',
                            },
                        ],
                        'currency_code': 'RUB',
                    },
                },
            ),
        ),
        pytest.param(
            None,
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'cancellation_offer': {
                    'fine_value': {'value': '1000', 'currency_code': 'rub'},
                },
                'actual_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
                'last_accepted_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
            },
            409,
            id='accepted slot, paid cancellation but offer is outdated',
            marks=[
                pytest.mark.config(
                    LOGISTIC_SUPPLY_CONDUCTOR_CANCELLATION_SETTINGS_BY_COUNTRY={  # noqa: E501
                        'ru': {
                            'cancelation_offer_ttl': 300,
                            'penalties': [
                                {
                                    'time_left_until_workshift_start': (
                                        1000000000
                                    ),
                                    'fine_value': '1000',
                                },
                                {
                                    'time_left_until_workshift_start': 1000,
                                    'fine_value': '2000',
                                },
                            ],
                            'currency_code': 'RUB',
                        },
                    },
                ),
                pytest.mark.now('2035-09-17T10:31:00+00:00'),
            ],
        ),
        pytest.param(
            None,
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'cancellation_offer': {
                    'fine_value': {'value': '2000', 'currency_code': 'rub'},
                },
                'actual_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
                'last_accepted_offer': {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
            },
            200,
            id='accepted slot, paid cancellation with 2nd time range',
            marks=[
                pytest.mark.config(
                    LOGISTIC_SUPPLY_CONDUCTOR_CANCELLATION_SETTINGS_BY_COUNTRY={  # noqa: E501
                        'ru': {
                            'cancelation_offer_ttl': 300,
                            'penalties': [
                                {
                                    'time_left_until_workshift_start': (
                                        1000000000
                                    ),
                                    'fine_value': '1000',
                                },
                                {
                                    'time_left_until_workshift_start': 1000,
                                    'fine_value': '2000',
                                },
                            ],
                            'currency_code': 'RUB',
                        },
                    },
                ),
                pytest.mark.now('2035-09-17T10:31:00+00:00'),
            ],
        ),
    ],
)
async def test_cancellation(
        taxi_logistic_supply_conductor,
        pgsql,
        init_sql,
        request_json,
        response_code,
):
    if init_sql is not None:
        cursor = pgsql['logistic_supply_conductor'].cursor()
        cursor.execute(init_sql)

    await taxi_logistic_supply_conductor.invalidate_caches()

    response = await taxi_logistic_supply_conductor.post(
        'internal/v1/offer/reservation/check-cancellation',
        json=request_json,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == response_code
