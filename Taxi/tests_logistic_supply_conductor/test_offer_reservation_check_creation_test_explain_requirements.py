import pytest

PARK_ID = '458f82d8dbf24ecd81d1de2c7826d1b5'
DRIVER_ID_1 = 'e2b66c10ece54751a8db96b3a2039b0f'
DRIVER_ID_2 = '40295b99f56a46f1b309d940715a15dd'


DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'Timezone': 'Europe/Moscow',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', f'{PARK_ID}_{DRIVER_ID_1}', 'foo1'),
        ('dbid_uuid', f'{PARK_ID}_{DRIVER_ID_1}', 'bar2'),
        ('dbid_uuid', f'{PARK_ID}_{DRIVER_ID_2}', 'foo1'),
    ],
)
@pytest.mark.config(TAGS_INDEX={'enabled': True})
@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_OFFER_DISPLAY_SETTINGS={
        'siblings_max_time_before_end': 2000000000,
    },
)
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
        'pg_descriptive_items_for_offers.sql',
    ],
)
@pytest.mark.parametrize(
    'init_sql, driver_id, response_code, expected_response',
    [
        pytest.param(
            """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true, visibility_duration = '90 years'::interval
            WHERE rule_id = 2
            """,
            DRIVER_ID_2,
            200,
            {
                'items': [
                    {
                        'offer_identity': {
                            'rule_version': 2,
                            'slot_id': '76a3176e-f759-44bc-8fc7-43ea091bd68b',
                        },
                        'short_info': {
                            'quota_id': 'af31c824-066d-46df-0001-100000000001',
                            'time_range': {
                                'begin': '2033-04-06T08:00:00+00:00',
                                'end': '2033-04-06T20:00:00+00:00',
                            },
                            'allowed_transport_types': [
                                'pedestrian',
                                'auto',
                                'bicycle',
                            ],
                        },
                        'check_not_pass_reason': (
                            'Failed requirements: foo, bar'
                        ),
                    },
                    {
                        'offer_identity': {
                            'rule_version': 2,
                            'slot_id': 'a278134c-49f2-48bc-b9b6-941c76650508',
                        },
                        'short_info': {
                            'quota_id': 'af31c824-066d-46df-0001-100000000002',
                            'time_range': {
                                'begin': '2033-04-08T08:00:00+00:00',
                                'end': '2033-04-08T20:00:00+00:00',
                            },
                            'allowed_transport_types': [
                                'pedestrian',
                                'auto',
                                'bicycle',
                            ],
                        },
                        'check_not_pass_reason': (
                            'Failed requirements: foo, bar'
                        ),
                    },
                    {
                        'offer_identity': {
                            'rule_version': 2,
                            'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                        },
                        'short_info': {
                            'quota_id': 'af31c824-066d-46df-0001-100000000003',
                            'time_range': {
                                'begin': '2033-04-10T08:00:00+00:00',
                                'end': '2033-04-10T20:00:00+00:00',
                            },
                            'allowed_transport_types': [
                                'pedestrian',
                                'auto',
                                'bicycle',
                            ],
                        },
                        'check_not_pass_reason': (
                            'Failed requirements: foo, bar'
                        ),
                    },
                ],
            },
            id='test ExplainCourierRequirements courier_requirements',
        ),
    ],
)
async def test_offer_reservation_check_creation_test_validate_requirements(
        taxi_logistic_supply_conductor,
        pgsql,
        init_sql,
        driver_id,
        response_code,
        expected_response,
        testpoint,
):
    @testpoint('explain_requirements_cache_miss')
    def explain_requirements_new_value(data):
        value = data['requirement_name']
        if explain_requirements_new_value.times_called == 1:
            assert value == 'bar'
        if explain_requirements_new_value.times_called == 2:
            assert value == 'foo'

    if init_sql is not None:
        cursor = pgsql['logistic_supply_conductor'].cursor()
        cursor.execute(init_sql)

    await taxi_logistic_supply_conductor.invalidate_caches()

    response = await taxi_logistic_supply_conductor.post(
        'internal/v1/offer/reservation/check-creation',
        json={
            'contractor_id': {
                'park_id': PARK_ID,
                'driver_profile_id': driver_id,
            },
            'items': [
                {
                    'rule_version': 2,
                    'slot_id': '76a3176e-f759-44bc-8fc7-43ea091bd68b',
                },
                {
                    'rule_version': 2,
                    'slot_id': 'a278134c-49f2-48bc-b9b6-941c76650508',
                },
                {
                    'rule_version': 2,
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
            ],
            'check_reason': 'reservation',
        },
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == response_code

    if response_code == 200:
        assert response.json() == expected_response

    assert explain_requirements_new_value.times_called == 2
