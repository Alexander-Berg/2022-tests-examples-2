import pytest

SLOT_ID_1 = 'f111100f-10f0-11ff-f0f0-111f00000000'
SLOT_ID_2 = 'a278134c-49f2-48bc-b9b6-941c76650508'


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
        'pg_descriptive_items_for_offers.sql',
    ],
)
@pytest.mark.parametrize(
    'rule_version, slot_id, response_code, expected_response',
    [
        pytest.param(2, SLOT_ID_1, 404, None, id='not existing slot'),
        pytest.param(
            2,
            SLOT_ID_2,
            200,
            {
                'workshift_rule_id': 'af31c824-066d-46df-0001-000000000002',
                'workshift_rule_version': 2,
            },
            id='existing slot',
        ),
        pytest.param(
            1,
            SLOT_ID_2,
            404,
            None,
            id='wrong rule_version for existing slot_id',
        ),
    ],
)
async def test_workshift_by_slot(
        taxi_logistic_supply_conductor,
        rule_version,
        slot_id,
        response_code,
        expected_response,
):
    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/by-slot',
        json={'slot_id': slot_id, 'rule_version': rule_version},
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == response_code

    if response_code == 200:
        assert response.json() == expected_response
