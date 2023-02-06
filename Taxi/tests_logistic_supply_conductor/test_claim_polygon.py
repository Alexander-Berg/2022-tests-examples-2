import pytest

FIND_GEOAREA_IDS = """
    SELECT claim_id, stored_geoarea_ids
    FROM logistic_supply_conductor.claim_geoareas
    WHERE claim_id = 'some_id'
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
        'pg_descriptive_items_for_offers.sql',
    ],
)
async def test_claim_polygon(
        taxi_logistic_supply_conductor, stq_runner, pgsql,
):

    await stq_runner.logistic_supply_conductor_match_slots.call(
        task_id='task',
        kwargs={
            'claim_id': 'some_id',
            'claim_points': [
                {
                    'id': 111,
                    'claim_point_id': 1111,
                    'point_type': 'source',
                    'visit_status': 'pending',
                    'coordinates': {'lat': 63.0, 'lon': 53.0},
                },
            ],
        },
        expect_fail=False,
    )

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(FIND_GEOAREA_IDS)
    assert list(cursor) == [('some_id', [1])]
