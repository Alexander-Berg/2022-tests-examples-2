import pytest


PARK_ID = '458f82d8dbf24ecd81d1de2c7826d1b5'
DRIVER_ID = 'e2b66c10ece54751a8db96b3a2039b0f'


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
async def test_slot_subscribers_empty_update(taxi_logistic_supply_conductor):
    response = await taxi_logistic_supply_conductor.post(
        'internal/v1/caches/slot-subscribers/updates',
        params={'consumer': 'test'},
        json={},
    )
    assert response.status_code == 200
    assert response.json()['slot_subscribers'] == []


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata_with_requirements.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
        'pg_workshift_slot_subscribers.sql',
    ],
)
async def test_slot_subscribers_update(taxi_logistic_supply_conductor):
    response = await taxi_logistic_supply_conductor.post(
        'internal/v1/caches/slot-subscribers/updates',
        params={'consumer': 'test'},
        json={},
    )
    assert response.status_code == 200
    response_json = response.json()

    assert (
        response_json['slot_subscribers'][0]['contractor_id']
        == f'{PARK_ID}_{DRIVER_ID}'
    )
    assert (
        response_json['slot_subscribers'][0]['data']['slot_id']
        == '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3'
    )
    assert response_json['slot_subscribers'][0]['data']['version'] == 2


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata_with_requirements.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
        'pg_workshift_slot_subscribers.sql',
    ],
)
async def test_slot_subscribers_retrieve(taxi_logistic_supply_conductor):
    response = await taxi_logistic_supply_conductor.post(
        'internal/v1/caches/slot-subscribers/retrieve',
        params={'consumer': 'test'},
        json={'id_in_set': [f'{PARK_ID}_{DRIVER_ID}']},
    )
    assert response.status_code == 200
    response_json = response.json()

    assert (
        response_json['slot_subscribers'][0]['contractor_id']
        == f'{PARK_ID}_{DRIVER_ID}'
    )
    assert (
        response_json['slot_subscribers'][0]['data']['slot_id']
        == '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3'
    )
    assert response_json['slot_subscribers'][0]['data']['version'] == 2
