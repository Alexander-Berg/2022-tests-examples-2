import copy

import pytest

from tests_cargo_pricing import utils


_DEFAULT_ROUTE_LEN = 7082.17578125
_LONG_ROUTE_LEN = 8435.8349609375


@pytest.fixture(name='set_distance_exceeding_exp3_value')
def _set_distance_exceeding_exp3_value(experiments3, taxi_cargo_pricing):
    async def set_distance(value):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_pricing_distance_limits_for_extra_price_setup',
            consumers=['cargo-pricing/v1/taxi/calc'],
            clauses=[],
            default_value={'distance_meters_extra_price_lower_bound': value},
        )
        await taxi_cargo_pricing.invalidate_caches()

    return set_distance


async def test_calc_without_distance_exceeding(
        v1_calc_creator, set_distance_exceeding_exp3_value,
):
    await set_distance_exceeding_exp3_value(_LONG_ROUTE_LEN)
    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert 'distance_exceeding' not in user_options


async def test_calc_with_distance_exceeding(
        v1_calc_creator, set_distance_exceeding_exp3_value,
):
    await set_distance_exceeding_exp3_value(_DEFAULT_ROUTE_LEN)
    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['distance_exceeding'] == 1


async def test_recalc_with_distance_exceeding_if_exp_changes(
        v1_calc_creator, set_distance_exceeding_exp3_value,
):
    await set_distance_exceeding_exp3_value(_DEFAULT_ROUTE_LEN)
    calc_response = await v1_calc_creator.execute()
    assert calc_response.status_code == 200

    await set_distance_exceeding_exp3_value(_LONG_ROUTE_LEN)
    v1_calc_creator.payload['previous_calc_id'] = calc_response.json()[
        'calc_id'
    ]
    recalc_response = await v1_calc_creator.execute()
    assert recalc_response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['distance_exceeding'] == 1


async def test_recalc_with_distance_exceeding_by_differ_route(
        v1_calc_creator, set_distance_exceeding_exp3_value,
):
    await set_distance_exceeding_exp3_value(_LONG_ROUTE_LEN)
    calc_response = await v1_calc_creator.execute()
    assert calc_response.status_code == 200
    calc_user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert 'distance_exceeding' not in calc_user_options

    v1_calc_creator.payload['previous_calc_id'] = calc_response.json()[
        'calc_id'
    ]
    v1_calc_creator.payload['waypoints'].extend(
        copy.deepcopy(v1_calc_creator.payload['waypoints']),
    )

    recalc_response = await v1_calc_creator.execute()
    assert recalc_response.status_code == 200

    recalc_user_options = utils.get_recalc_request_user_options(
        v1_calc_creator,
    )
    assert recalc_user_options['distance_exceeding'] == 1
