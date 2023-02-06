import pytest


@pytest.mark.parametrize(
    'expected_quotas',
    [
        pytest.param([]),
        pytest.param(
            [
                {
                    'data': {'quota': 1001},
                    'quota_id': 'af31c824-066d-46df-0001-100000000001',
                },
                {
                    'data': {'quota': 1002},
                    'quota_id': 'af31c824-066d-46df-0001-100000000002',
                },
                {
                    'data': {'quota': 1003},
                    'quota_id': 'af31c824-066d-46df-0001-100000000003',
                },
            ],
            marks=pytest.mark.pgsql(
                'logistic_supply_conductor', files=['pg_workshift_quotas.sql'],
            ),
        ),
    ],
)
@pytest.mark.now('2020-07-07T00:00:00Z')
async def test_quotas_update(taxi_logistic_supply_conductor, expected_quotas):
    response = await taxi_logistic_supply_conductor.post(
        'internal/v1/caches/quotas/updates',
        params={'consumer': 'test'},
        json={},
    )
    assert response.status_code == 200
    response_json = response.json()

    for actual, expected in zip(response_json['quotas'], expected_quotas):
        assert actual['quota_id'] == expected['quota_id']
        assert actual['data']['quota'] == expected['data']['quota']


@pytest.mark.parametrize(
    'expected_quotas',
    [
        pytest.param(
            [
                {
                    'data': {'quota': 1001},
                    'quota_id': 'af31c824-066d-46df-0001-100000000001',
                },
                {
                    'data': {'quota': 1003},
                    'quota_id': 'af31c824-066d-46df-0001-100000000003',
                },
                {
                    'data': {'quota': 10},
                    'quota_id': 'af31c824-066d-46df-0001-100000000002',
                },
            ],
            marks=pytest.mark.pgsql(
                'logistic_supply_conductor', files=['pg_workshift_quotas.sql'],
            ),
        ),
    ],
)
@pytest.mark.now('2020-07-07T00:00:00Z')
async def test_quotas_update_modify(
        taxi_logistic_supply_conductor, expected_quotas,
):
    update_response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/quota/update',
        json={
            'quotas': [
                {
                    'revision': 1,
                    'quota': 10,
                    'siblings_id': 1,
                    'week_day': 'friday',
                },
            ],
        },
    )
    assert update_response.status_code == 200

    await taxi_logistic_supply_conductor.invalidate_caches()

    response = await taxi_logistic_supply_conductor.post(
        'internal/v1/caches/quotas/updates',
        params={'consumer': 'test'},
        json={},
    )
    assert response.status_code == 200
    response_json = response.json()

    for actual, expected in zip(response_json['quotas'], expected_quotas):
        assert actual['quota_id'] == expected['quota_id']
        assert actual['data']['quota'] == expected['data']['quota']
