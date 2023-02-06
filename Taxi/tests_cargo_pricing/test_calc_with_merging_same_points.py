import copy

import pytest

from tests_cargo_pricing import utils


def _add_mergable_points(v1_calc_creator):
    waypoints = v1_calc_creator.payload['waypoints']
    assert len(waypoints) == 3
    # additional pickup waypoint (almost the same as first)
    assert waypoints[0]['type'] == 'pickup'
    waypoints.insert(1, copy.deepcopy(waypoints[0]))
    waypoints[1]['position'][0] = waypoints[0]['position'][0] + 0.00001
    waypoints[1]['id'] = 'clone_waypoint_1'
    # two additional dropoff waypoint (almost the same as second)
    assert waypoints[2]['type'] == 'dropoff'
    waypoints.insert(3, copy.deepcopy(waypoints[2]))
    waypoints[3]['position'][1] = waypoints[2]['position'][1] - 0.00001
    waypoints[3]['id'] = 'clone_waypoint_2'
    waypoints.insert(4, copy.deepcopy(waypoints[2]))
    waypoints[4]['id'] = 'clone_waypoint_3'
    return waypoints


@pytest.fixture(name='get_request_fake_middle_points')
def _get_request_fake_middle_points(v1_calc_creator):
    def _get():
        recalc_req = v1_calc_creator.mock_recalc.request
        user_fake_mid_pnts = utils.fake_middle_point_count(
            recalc_req['user']['trip_details']['user_options'],
        )
        driver_fake_mid_pnts = utils.fake_middle_point_count(
            recalc_req['driver']['trip_details']['user_options'],
        )
        return (user_fake_mid_pnts, driver_fake_mid_pnts)

    return _get


async def test_calc_with_merging_same_points_with_default_config(
        v1_calc_creator, get_request_fake_middle_points,
):
    _add_mergable_points(v1_calc_creator)

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_fake_mid_pnts, driver_fake_mid_pnts = get_request_fake_middle_points()
    assert user_fake_mid_pnts == 4
    assert driver_fake_mid_pnts == 4

    prepare_req = v1_calc_creator.mock_prepare.request
    waypoints = v1_calc_creator.payload['waypoints']
    assert prepare_req['waypoints'] == [
        waypoints[0]['position'],
        waypoints[2]['position'],
        waypoints[3]['position'],
        waypoints[4]['position'],
        waypoints[5]['position'],
    ]


async def test_calc_with_merging_same_points(
        v1_calc_creator,
        setup_merge_waypoints_config,
        get_request_fake_middle_points,
):
    _add_mergable_points(v1_calc_creator)

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_fake_mid_pnts, driver_fake_mid_pnts = get_request_fake_middle_points()
    assert user_fake_mid_pnts == 2
    assert driver_fake_mid_pnts == 2

    prepare_req = v1_calc_creator.mock_prepare.request
    waypoints = v1_calc_creator.payload['waypoints']
    assert prepare_req['waypoints'] == [
        waypoints[0]['position'],
        waypoints[2]['position'],
        waypoints[5]['position'],
    ]


async def test_calc_with_merging_same_points_and_previous_calc_id(
        v1_calc_creator,
        setup_merge_waypoints_config,
        get_request_fake_middle_points,
):
    _add_mergable_points(v1_calc_creator)

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    previous_calc_id = response.json()['calc_id']

    second_payload = utils.get_default_calc_request()
    second_payload['previous_calc_id'] = previous_calc_id

    v1_calc_creator.payload = second_payload
    _add_mergable_points(v1_calc_creator)
    second_response = await v1_calc_creator.execute()
    assert second_response.status_code == 200

    user_fake_mid_pnts, driver_fake_mid_pnts = get_request_fake_middle_points()
    assert user_fake_mid_pnts == 2
    assert driver_fake_mid_pnts == 2

    prepare_req = v1_calc_creator.mock_prepare.request
    waypoints = v1_calc_creator.payload['waypoints']
    assert prepare_req['waypoints'] == [
        waypoints[0]['position'],
        waypoints[2]['position'],
        waypoints[5]['position'],
    ]


@pytest.mark.config(
    CARGO_PRICING_ENABLE_BATCH_MULTIPLIER={
        'source_point_visited': False,
        'source_point_completed': True,
        'destination_point_visited': True,
        'destination_point_completed': False,
        'return_point_visited': False,
        'return_point_completed': True,
    },
)
async def test_composite_pricing_multiplication_config(
        v1_calc_creator, setup_merge_waypoints_config,
):
    _add_mergable_points(v1_calc_creator)
    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    waypoints = response.json()['details']['waypoints']
    assert waypoints[0]['merged_points_number'] == 2
    assert waypoints[1]['merged_points_number'] == 3
    assert waypoints[2]['merged_points_number'] == 1
    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['composite_pricing__source_point_visited'] == 1
    assert user_options['composite_pricing__source_point_completed'] == 2
    assert user_options['composite_pricing__destination_point_visited'] == 3
    assert user_options['composite_pricing__destination_point_completed'] == 1
    assert user_options['composite_pricing__return_point_visited'] == 1
    assert user_options['composite_pricing__return_point_completed'] == 1


async def _calc_price_without_free_waiting(
        v1_calc_creator, price_for='performer',
):
    prepare_response = v1_calc_creator.mock_prepare.categories
    tariff = prepare_response['cargocorp']['tariff_info']
    tariff['point_a_free_waiting_time'] = 0
    tariff['point_b_free_waiting_time'] = 0

    v1_calc_creator.payload['price_for'] = price_for
    create_resp = await v1_calc_creator.execute()
    return create_resp


def _relative_time(minutes):
    return utils.from_start(minutes=minutes)


def _get_request_waitings(v1_calc_creator):
    recalc_req = v1_calc_creator.mock_recalc.request
    user_trip_details = recalc_req['user']['trip_details']
    user_waiting = user_trip_details['waiting_time']

    driver_trip_details = recalc_req['driver']['trip_details']
    driver_waiting = driver_trip_details['waiting_time']
    return (user_waiting, driver_waiting)


async def test_calc_with_merging_same_points_waiting(v1_calc_creator):
    _add_mergable_points(v1_calc_creator)
    waypoints = v1_calc_creator.payload['waypoints']
    waypoints[0]['first_time_arrived_at'] = _relative_time(minutes=1)
    waypoints[0]['resolution_info']['resolved_at'] = _relative_time(minutes=5)
    waypoints[1]['first_time_arrived_at'] = _relative_time(minutes=3)
    waypoints[1]['resolution_info']['resolved_at'] = _relative_time(minutes=6)

    response = await _calc_price_without_free_waiting(v1_calc_creator)
    assert response.status_code == 200

    user_waiting, driver_waiting = _get_request_waitings(v1_calc_creator)
    assert user_waiting == 5 * 60
    assert driver_waiting == 5 * 60


async def test_calc_with_merging_same_points_waiting_with_eta(v1_calc_creator):
    _add_mergable_points(v1_calc_creator)
    waypoints = v1_calc_creator.payload['waypoints']
    waypoints[0]['first_time_arrived_at'] = _relative_time(minutes=1)
    waypoints[0]['resolution_info']['resolved_at'] = _relative_time(minutes=5)
    waypoints[0]['eta'] = _relative_time(minutes=4)
    waypoints[1]['first_time_arrived_at'] = _relative_time(minutes=3)
    waypoints[1]['resolution_info']['resolved_at'] = _relative_time(minutes=6)
    waypoints[1]['eta'] = _relative_time(minutes=5)

    response = await _calc_price_without_free_waiting(
        v1_calc_creator, price_for='performer',
    )
    assert response.status_code == 200

    user_waiting, driver_waiting = _get_request_waitings(v1_calc_creator)
    assert user_waiting == 2 * 60
    assert driver_waiting == 2 * 60


async def test_calc_with_merging_same_points_waiting_with_due(v1_calc_creator):
    _add_mergable_points(v1_calc_creator)
    waypoints = v1_calc_creator.payload['waypoints']
    waypoints[0]['first_time_arrived_at'] = _relative_time(minutes=1)
    waypoints[0]['resolution_info']['resolved_at'] = _relative_time(minutes=5)
    waypoints[0]['due'] = _relative_time(minutes=4)
    waypoints[1]['first_time_arrived_at'] = _relative_time(minutes=3)
    waypoints[1]['resolution_info']['resolved_at'] = _relative_time(minutes=6)
    waypoints[1]['due'] = _relative_time(minutes=5)

    response = await _calc_price_without_free_waiting(
        v1_calc_creator, price_for='client',
    )
    assert response.status_code == 200

    user_waiting, driver_waiting = _get_request_waitings(v1_calc_creator)
    assert user_waiting == 1 * 60
    assert driver_waiting == 1 * 60


def _add_batched_waypoints(v1_calc_creator):
    base_point = v1_calc_creator.payload['waypoints'][1]
    arrived_at = base_point['first_time_arrived_at']
    resolved_at = base_point['resolution_info']['resolved_at']
    v1_calc_creator.payload['waypoints'] = [
        {
            'claim_id': 'claim1',
            'id': 'waypoint2',
            'type': 'dropoff',
            'position': [37.5447415, 55.9061769],
            'first_time_arrived_at': arrived_at,
            'resolution_info': {
                'resolved_at': resolved_at,
                'resolution': 'delivered',
            },
        },
        {
            'claim_id': 'claim2',
            'id': 'waypoint_copy1',
            'type': 'dropoff',
            'position': [32.5447415, 55.9061769],
            'first_time_arrived_at': arrived_at,
            'resolution_info': {
                'resolved_at': resolved_at,
                'resolution': 'delivered',
            },
        },
        {
            'claim_id': 'claim3',
            'id': 'waypoint_copy2',
            'type': 'dropoff',
            'position': [37.5447415, 58.9061769],
            'first_time_arrived_at': arrived_at,
            'resolution_info': {
                'resolved_at': resolved_at,
                'resolution': 'delivered',
            },
        },
    ]
    return v1_calc_creator


async def test_composite_pricing_points_limitation(
        v1_calc_creator,
        setup_merge_waypoints_config,
        setup_composite_pricing_point_limits_config,
):
    v1_calc_creator = _add_batched_waypoints(v1_calc_creator)
    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['composite_pricing__destination_point_visited'] == 2


async def test_composite_pricing_points_limitation_unbatched(
        v1_calc_creator,
        setup_merge_waypoints_config,
        setup_composite_pricing_point_limits_config,
):
    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['composite_pricing__destination_point_visited'] == 1
