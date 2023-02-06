import pytest


async def test_angle_distance_generator(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        create_segment,
        testpoint,
        state_waybill_proposed,
):
    points = [
        [[37.332375, 55.958991], [37.480100, 55.844100]],
        [[37.332375, 55.958992], [37.480200, 55.844200]],
        [[37.332375, 55.958993], [37.480300, 55.844300]],
        [[37.332375, 55.958994], [37.480400, 55.844400]],
        [[37.332375, 55.958995], [37.480500, 55.844500]],
        [[37.332375, 55.958996], [37.480500, 60.844500]],
        [[37.332375, 60.958991], [37.332375, 60.858991]],
    ]
    min_batch_size = 3
    max_batch_size = 6
    segments_packs_num = 7
    for i, point in enumerate(points):
        pickup, dropoff = point
        create_segment(
            pickup_coordinates=pickup,
            dropoff_coordinates=dropoff,
            segment_id=str(i),
            corp_client_id='b010d898a6ef4a3ea75d0e12e6ea51ef',
            zone_id='himki',
        )

    @testpoint('angle_distance_batch_generator::segments_packs_num')
    def check_batched_routes(data):
        assert data['segments_packs_num'] >= segments_packs_num

    await exp_delivery_gamble_settings(generators=['angle-distance'])
    await exp_delivery_generators_settings(
        min_batch_size=min_batch_size,
        max_batch_size=max_batch_size,
        max_lookup_radius=0.1,
    )
    await exp_delivery_configs(
        delivery_gamble_settings=False, delivery_generators_settings=False,
    )
    await state_waybill_proposed()
    assert check_batched_routes.times_called


@pytest.mark.parametrize(
    """max_batch_size,
    segments_packs_num""",
    [(2, 2), (3, 3)],
)
async def test_co_directional_segemtns(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        create_segment,
        testpoint,
        state_waybill_proposed,
        max_batch_size,
        segments_packs_num,
):
    points = [
        [[37.332375, 55.958991], [37.480100, 55.844100]],
        [[37.332375, 55.958991], [37.480100, 55.844100]],
        [[37.480100, 55.844100], [37.332375, 55.958991]],
    ]
    min_batch_size = 2
    for i, point in enumerate(points):
        pickup, dropoff = point
        create_segment(
            pickup_coordinates=pickup,
            dropoff_coordinates=dropoff,
            segment_id=str(i),
            corp_client_id='b010d898a6ef4a3ea75d0e12e6ea51ef',
            zone_id='himki',
        )

    @testpoint('angle_distance_batch_generator::segments_packs_num')
    def check_batched_routes(data):
        assert data['segments_packs_num'] >= segments_packs_num

    await exp_delivery_gamble_settings(generators=['angle-distance'])
    await exp_delivery_generators_settings(
        min_batch_size=min_batch_size,
        max_batch_size=max_batch_size,
        max_lookup_radius=0.1,
        num_best_routes_route_finder=1,
    )
    await exp_delivery_configs(
        delivery_gamble_settings=False, delivery_generators_settings=False,
    )
    await state_waybill_proposed()
    assert check_batched_routes.times_called
