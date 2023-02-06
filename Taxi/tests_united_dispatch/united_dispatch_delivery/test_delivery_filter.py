import pytest


async def test_corp_clients_threshold(
        exp_delivery_configs,
        create_segment,
        testpoint,
        state_waybill_proposed,
):
    pickup_coordinates = [37.4005, 55.7002]
    dropoff_coordinates = [37.4003, 55.7004]

    create_segment(
        pickup_coordinates=pickup_coordinates,
        dropoff_coordinates=dropoff_coordinates,
        corp_client_id=None,
    )

    create_segment(
        pickup_coordinates=pickup_coordinates,
        dropoff_coordinates=dropoff_coordinates,
        corp_client_id='wrong_corp_id',
    )
    create_segment(
        pickup_coordinates=pickup_coordinates,
        dropoff_coordinates=dropoff_coordinates,
        corp_client_id='test_corp_id_0m',
    )
    create_segment(
        pickup_coordinates=pickup_coordinates,
        dropoff_coordinates=dropoff_coordinates,
        corp_client_id='test_corp_id_10m',
    )

    expected_results = {
        '__no_corp_client_id__': 24000,
        'wrong_corp_id': 12000,
        'test_corp_id_0m': 0,
        'test_corp_id_10m': 600,
    }

    @testpoint('delivery_planner::segment_diff')
    def check_segment_diff(data):
        assert data['segment_diff'] == expected_results[data['corp_client_id']]

    await exp_delivery_configs()
    await state_waybill_proposed()

    assert check_segment_diff.times_called


@pytest.mark.parametrize(
    """pre_filtered_routes_num,
    diff_pre_filtration,
    ratio_pre_filtration""",
    [
        pytest.param(0, -1e9, 2),
        pytest.param(2, -1e9, 0.5),
        pytest.param(0, 0, 2),
        pytest.param(0, 0, 0.5),
    ],
)
async def test_pre_filtered_routes(
        exp_delivery_configs,
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        create_segment,
        testpoint,
        state_waybill_proposed,
        pre_filtered_routes_num,
        diff_pre_filtration,
        ratio_pre_filtration,
):
    pickup_coordinates = [[37.611330, 55.748982], [37.611330, 55.748982]]
    dropoff_coordinates = [[37.775214, 55.781453], [37.425441, 55.720568]]
    for pickup, dropoff in zip(pickup_coordinates, dropoff_coordinates):
        create_segment(
            pickup_coordinates=pickup,
            dropoff_coordinates=dropoff,
            corp_client_id='b010d898a6ef4a3ea75d0e12e6ea51ef',
            zone_id='himki',
        )

    @testpoint('delivery_planner::pre_filtered_routes')
    def check_routes_len(data):
        assert len(data['routes']) >= pre_filtered_routes_num

    await exp_delivery_configs(
        delivery_gamble_settings=False, delivery_generators_settings=False,
    )
    await exp_delivery_gamble_settings(generators=['two-circles-batch'])
    await exp_delivery_generators_settings(
        pickup_radius_mult=10,
        pickup_radius_bias=0,
        dropoff_radius_mult=10,
        dropoff_radius_bias=0,
        min_batch_size=2,
        max_batch_size=6,
        batch_size2_goodness_diff_pre_filtration=diff_pre_filtration,
        batch_size2_goodness_ratio_pre_filtration=ratio_pre_filtration,
    )
    await state_waybill_proposed()
    assert check_routes_len.times_called


@pytest.mark.parametrize(
    (
        'max_batches_per_segment',
        'max_mean_batches_per_segment',
        'input_segments',
        'expecting_batches',
    ),
    [
        pytest.param(1, 1, 2, 2),
        pytest.param(1, 1, 3, 3),
        pytest.param(2, 2, 2, 3),
        pytest.param(2, 1, 2, 2),
        pytest.param(2, 2, 3, 4),
        pytest.param(2, 1, 3, 3),
    ],
)
async def test_batches_filter_limit(
        exp_delivery_configs,
        exp_delivery_generators_settings,
        testpoint,
        create_segment,
        state_waybill_proposed,
        max_batches_per_segment,
        max_mean_batches_per_segment,
        input_segments,
        expecting_batches,
):
    assert input_segments in [2, 3]

    create_segment(
        pickup_coordinates=[37.4, 55.7], dropoff_coordinates=[37.4, 55.71],
    )
    create_segment(
        pickup_coordinates=[37.4, 55.7], dropoff_coordinates=[37.4, 55.711],
    )
    if input_segments == 3:
        create_segment(
            pickup_coordinates=[37.4, 55.7],
            dropoff_coordinates=[37.4, 55.709],
        )

    @testpoint('delivery_planner::filter_routes')
    def check_output_contain_one_batch(data):
        batches = list()

        for route in data['routes']:
            batches.append(route)

        assert len(batches) == expecting_batches

    await exp_delivery_configs(delivery_generators_settings=False)
    await exp_delivery_generators_settings(
        max_batches_per_segment=max_batches_per_segment,
        max_mean_batches_per_segment=max_mean_batches_per_segment,
        batch_size2_goodness_ratio=1,
    )
    await state_waybill_proposed()
    assert check_output_contain_one_batch.times_called


@pytest.mark.parametrize(
    'max_batches_per_segment,input_segments,expecting_batches',
    [
        pytest.param(1, 2, 3),
        pytest.param(1, 3, 10),
        pytest.param(2, 2, 3),
        pytest.param(2, 3, 10),
    ],
)
async def test_batches_filter(
        exp_delivery_configs,
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        testpoint,
        create_segment,
        state_waybill_proposed,
        max_batches_per_segment,
        input_segments,
        expecting_batches,
):
    assert input_segments in [2, 3]
    create_segment(
        pickup_coordinates=[37.4, 55.7], dropoff_coordinates=[37.4, 55.71],
    )
    create_segment(
        pickup_coordinates=[37.4, 55.7], dropoff_coordinates=[37.4, 55.711],
    )
    if input_segments == 3:
        create_segment(
            pickup_coordinates=[37.4, 55.7],
            dropoff_coordinates=[37.4, 55.709],
        )
    batches = list()

    @testpoint('delivery_planner::pre_routes')
    def check_no_batches(data):
        batches.extend(data['routes'])

    await exp_delivery_configs(
        delivery_gamble_settings=False, delivery_generators_settings=False,
    )

    await exp_delivery_gamble_settings(generators=['two-circles-batch'])
    await exp_delivery_generators_settings(
        batch_size2_goodness_diff=2,
        batch_size2_goodness_ratio=1.9,
        distance_of_arrival=10,
        max_batches_per_segment=max_batches_per_segment,
    )

    await state_waybill_proposed()

    assert check_no_batches.times_called
    assert len(batches) >= expecting_batches


@pytest.mark.parametrize(
    (
        'validate_all_transport_types',
        'num_expected_routes',
        'transport_types_for_validation',
    ),
    [
        (False, 2, []),
        (True, 1, []),
        (False, 1, ['car', 'filler']),
        (False, 2, ['filler']),
    ],
)
async def test_live_batches_satisfy(
        exp_delivery_configs,
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        mockserver,
        testpoint,
        load_json,
        create_segment,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        validate_all_transport_types,
        num_expected_routes,
        transport_types_for_validation,
):
    candidates_json = load_json('candidates.json')
    candidate_coordinates = candidates_json['candidates'][0]['position']

    return_candidates = True

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(_):
        if return_candidates:
            return candidates_json
        return {'candidates': []}

    @mockserver.json_handler('/candidates/order-satisfy')
    def _order_satisfy(request, body_json):
        if (
                return_candidates
                or len(body_json['order']['request']['destinations']) == 1
        ):
            return candidates_json
        return None

    @mockserver.json_handler('/driver-trackstory/positions')
    def _driver_position(request):
        result = []
        for driver_id in request.json['driver_ids']:
            result.append(
                {
                    'position': {
                        'lon': candidate_coordinates[0],
                        'lat': candidate_coordinates[1],
                        'timestamp': 10,
                    },
                    'type': 'adjusted',
                    'driver_id': driver_id,
                },
            )

        return {'results': result}

    @testpoint('delivery_planner::filter_routes')
    def _check_output_contain_one_batch(data):
        if not return_candidates:
            assert len(data['routes']) == num_expected_routes

    generators = ['single-segment', 'live-batch']
    await exp_delivery_gamble_settings(
        generators=generators,
        validate_all_transport_types=validate_all_transport_types,
        transport_types_for_validation=transport_types_for_validation,
    )
    await exp_delivery_generators_settings(can_change_next_point_in_path=True)
    await exp_delivery_configs(
        delivery_gamble_settings=False, delivery_generators_settings=False,
    )

    create_segment()
    await state_waybill_proposed()
    await state_taxi_order_performer_found(performer_tariff='courier')

    # no more candidates for the second segment
    return_candidates = False

    create_segment()
    await state_waybill_proposed()
