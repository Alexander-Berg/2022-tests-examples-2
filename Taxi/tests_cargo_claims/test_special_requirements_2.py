import pytest


_EXPERIMENTS_MERGE_BY_TAG = [
    {
        'consumer': 'cargo-claims/special-requirements',
        'merge_method': 'dicts_recursive_merge',
        'tag': 'claims_special_requirements',
    },
]


@pytest.fixture(name='exp_cargo_weight_bike_special_requirements')
async def _exp_cargo_weight_bike_special_requirements(
        experiments3, taxi_cargo_claims,
):
    async def wrapper(weight=25.0):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_weight_for_bike_couriers_special_requirements',
            consumers=['cargo-claims/special-requirements'],
            clauses=[
                {
                    'title': 'too-heavy',
                    'predicate': {
                        'init': {
                            'value': weight,
                            'arg_name': 'weight',
                            'arg_type': 'double',
                        },
                        'type': 'gte',
                    },
                    'value': {
                        'too_heavy_for_bike_courier': {
                            'special_requirements': ['without_bike_couriers'],
                        },
                    },
                },
            ],
            default_value={},
            merge_values_by=_EXPERIMENTS_MERGE_BY_TAG,
        )
        await taxi_cargo_claims.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.mark.parametrize(
    'clause_weight, req_exists', [[25, True], [36, False]],
)
async def test_weight_for_bike_couriers_special_requirement(
        taxi_cargo_claims,
        create_claim_with_performer,
        exp_cargo_weight_bike_special_requirements,
        clause_weight,
        req_exists,
):
    # items_weight = 35.6 for created segment
    await exp_cargo_weight_bike_special_requirements(weight=clause_weight)
    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'cargo'}],
            'cargo_ref_id': create_claim_with_performer.claim_id,
        },
    )
    assert response.status_code == 200
    tariff = response.json()['virtual_tariffs'][0]
    assert tariff['class'] == 'cargo'
    if req_exists:
        assert {'id': 'without_bike_couriers'} in tariff[
            'special_requirements'
        ]
    else:
        assert {'id': 'without_bike_couriers'} not in tariff[
            'special_requirements'
        ]
