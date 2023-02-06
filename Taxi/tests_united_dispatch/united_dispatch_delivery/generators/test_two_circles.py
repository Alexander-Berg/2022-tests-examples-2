import pytest


@pytest.mark.parametrize(
    """points,
    pickup_bias,
    dropoff_bias,
    min_batch_size,
    max_batch_size,
    segments_packs_num""",
    [
        pytest.param(
            [
                [[37.332375, 55.958991], [37.480100, 55.844100]],
                [[37.332375, 55.958992], [37.480200, 55.844200]],
                [[37.332375, 55.958993], [37.480300, 55.844300]],
                [[37.332375, 55.958994], [37.480400, 55.844400]],
                [[37.332375, 55.958995], [37.480500, 55.844500]],
                [[37.332375, 55.958996], [37.480500, 60.844500]],
                [[37.332375, 60.958991], [37.332375, 60.858991]],
            ],
            0,
            0,
            3,
            6,
            7,
        ),
        pytest.param(
            [
                [[37.332375, 55.958991], [37.480100, 55.844100]],
                [[37.332375, 55.958991], [37.480200, 55.844200]],
                [[37.332375, 55.958991], [37.480300, 55.844300]],
                [[37.332375, 55.958991], [37.480400, 55.844400]],
                [[37.332355, 55.958991], [37.480400, 55.844400]],
                [[37.332355, 55.958991], [37.480400, 55.844400]],
            ],
            0,
            0,
            3,
            6,
            4,
        ),
        pytest.param(
            [
                [[37.332375, 55.958991], [37.480100, 55.844100]],
                [[37.332375, 55.958992], [37.480200, 55.844200]],
                [[37.332375, 55.958993], [37.480300, 55.844300]],
                [[37.332375, 55.958994], [37.480400, 55.844400]],
                [[37.332375, 55.958995], [37.480500, 55.844500]],
                [[37.332375, 55.958996], [37.480500, 60.844500]],
                [[37.332375, 60.958991], [37.332375, 60.844591]],
            ],
            0,
            0,
            3,
            3,
            4,
        ),
        pytest.param(
            [
                [[37.444629, 55.719156], [37.436553, 55.717822]],
                [[37.477965, 55.706939], [37.535763, 55.732945]],
                [[37.444629, 55.719156], [37.436553, 55.717822]],
                [[37.477965, 55.706939], [37.535763, 55.732945]],
                [[37.444629, 55.719156], [37.436553, 55.717822]],
                [[37.477965, 55.706939], [37.535763, 55.732945]],
            ],
            0.5,
            0,
            2,
            2,
            1,
        ),
        pytest.param(
            [
                [[37.332375, 55.958991], [37.480100, 55.844100]],
                [[37.332375, 55.958991], [37.480200, 55.844200]],
                [[37.332375, 55.958991], [37.480300, 55.844300]],
                [[37.332375, 55.958991], [37.480400, 55.844400]],
                [[37.332355, 55.958991], [37.480400, 55.844400]],
                [[37.332355, 55.958991], [37.480400, 55.844400]],
            ],
            0.2,
            0.2,
            3,
            6,
            4,
        ),
    ],
)
async def test_two_circles_batch_generator(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        create_segment,
        testpoint,
        state_waybill_proposed,
        points,
        pickup_bias,
        dropoff_bias,
        min_batch_size,
        max_batch_size,
        segments_packs_num,
):
    for i, point in enumerate(points):
        pickup, dropoff = point
        create_segment(
            pickup_coordinates=pickup,
            dropoff_coordinates=dropoff,
            segment_id=str(i),
            corp_client_id='b010d898a6ef4a3ea75d0e12e6ea51ef',
            zone_id='himki',
        )

    @testpoint('two_circles_batch_generator::segments_packs_num')
    def check_batched_routes(data):
        assert data['segments_packs_num'] >= segments_packs_num

    await exp_delivery_gamble_settings(generators=['two-circles-batch'])
    await exp_delivery_generators_settings(
        pickup_radius_mult=2,
        pickup_radius_bias=pickup_bias,
        dropoff_radius_mult=50,
        dropoff_radius_bias=dropoff_bias,
        min_batch_size=min_batch_size,
        max_batch_size=max_batch_size,
    )
    await exp_delivery_configs(
        delivery_gamble_settings=False, delivery_generators_settings=False,
    )
    await state_waybill_proposed()
    assert check_batched_routes.times_called


def _get_route_meta(routes, key):
    return list(
        map(
            lambda path: list(map(lambda point: point[key], path)),
            list(map(lambda route: route['points'], routes)),
        ),
    )


async def test_batch_visit_order(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        create_segment,
        testpoint,
        state_waybill_proposed,
):
    point_1 = [[37.0001, 55.0001], [37.0005, 55.0005]]
    point_2 = [[37.0002, 55.0002], [37.0004, 55.0004]]
    point_3 = [[37.0003, 55.0003], [37.0006, 55.0006]]
    for i, (pickup, dropoff) in enumerate([point_1, point_2, point_3]):
        create_segment(
            pickup_coordinates=pickup,
            dropoff_coordinates=dropoff,
            segment_id=str(i + 1),
        )

    @testpoint('delivery_planner::pre_routes')
    def check_batched_routes(data):
        segments_ids = _get_route_meta(data['routes'], 'segment_id')
        routes_types = _get_route_meta(data['routes'], 'type')
        visit_order = dict()

        is_path_valid = False
        for segment_ids in segments_ids:
            is_path_valid |= ['1', '2', '3', '2', '1', '3'] == segment_ids[0:6]
        assert is_path_valid

        is_path_valid = False
        for segment_ids, route_types in zip(segments_ids, routes_types):
            is_route_valid = True
            for segment_id, route_type in zip(segment_ids, route_types):
                if segment_id not in visit_order:
                    if route_type != 'pickup':
                        is_route_valid = False
                        continue
                    visit_order[segment_id] = 0
                else:
                    if route_type == 'dropoff':
                        if (
                                segment_id not in visit_order
                                or visit_order[segment_id] != 0
                        ):
                            is_route_valid = False
                            continue
                        else:
                            visit_order[segment_id] = 1
                    elif route_type == 'return':
                        if (
                                segment_id not in visit_order
                                or visit_order[segment_id] != 1
                        ):
                            is_route_valid = False
                            continue
                        else:
                            visit_order[segment_id] = 2
            is_path_valid |= is_route_valid
        assert is_path_valid

    await exp_delivery_gamble_settings(generators=['two-circles-batch'])
    await exp_delivery_generators_settings(
        pickup_radius_mult=5,
        pickup_radius_bias=0.5,
        dropoff_radius_mult=1000,
        dropoff_radius_bias=0,
        min_batch_size=3,
        max_batch_size=3,
        num_best_routes_route_finder=1,
    )
    await exp_delivery_configs(
        delivery_gamble_settings=False, delivery_generators_settings=False,
    )
    await state_waybill_proposed()
    assert check_batched_routes.times_called
