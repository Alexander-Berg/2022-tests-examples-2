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

METADATA_CHECK = """
    SELECT is_visible, red_button_cancelling
    FROM logistic_supply_conductor.workshift_metadata
    WHERE rule_id = 2
    """


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
async def test_big_red_button(taxi_logistic_supply_conductor, pgsql):
    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/stop',
        json={
            'workshift_rule_id': 'af31c824-066d-46df-0001-000000000002',
            'metadata_revision': 1,
        },
        params={'dry_run': True},
    )
    assert response.status_code == 200

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(METADATA_CHECK)
    assert list(cursor) == [(True, False)]

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/stop',
        json={
            'workshift_rule_id': 'af31c824-066d-46df-0001-000000000002',
            'metadata_revision': 1,
        },
    )
    assert response.status_code == 200

    await taxi_logistic_supply_conductor.invalidate_caches()

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(METADATA_CHECK)
    assert list(cursor) == [(False, True)]

    response = await taxi_logistic_supply_conductor.post(
        'internal/v1/offer/reservation/check-creation',
        json={
            'contractor_id': {
                'park_id': PARK_ID,
                'driver_profile_id': DRIVER_ID,
            },
            'items': [
                {
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                    'rule_version': 2,
                },
            ],
            'contractor_position': {'lat': 63, 'lon': 53},
            'check_reason': 'reservation',
        },
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 409
