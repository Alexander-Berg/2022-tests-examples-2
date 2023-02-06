import pytest


@pytest.mark.parametrize('lookup_flow', ['taxi-dispatch', 'united-dispatch'])
async def test_lookup_flow_exp(
        state_waybill_proposed,
        exp_delivery_gamble_settings,
        exp_delivery_configs,
        get_single_waybill,
        lookup_flow: str,
):
    """
        Check lookup_flow modified via experiment.
    """
    await exp_delivery_gamble_settings(lookup_flow=lookup_flow)
    await exp_delivery_configs(delivery_gamble_settings=False)
    await state_waybill_proposed()

    assert get_single_waybill()['lookup_flow'] == lookup_flow


async def test_repeat_search_candidate_found(
        state_taxi_order_created,
        exp_delivery_gamble_settings,
        exp_delivery_configs,
        performer_for_order,
        get_single_waybill,
        run_single_planner,
):
    """
        Check candidate found on repeat search.
        autoreorder_flow: newway
    """
    # create waybill with lookup_flow: united-dispatch
    await exp_delivery_gamble_settings(lookup_flow='united-dispatch')
    await exp_delivery_configs(delivery_gamble_settings=False)
    await state_taxi_order_created()

    assert get_single_waybill()['candidate'] is not None
    assert get_single_waybill()['waybill'].get('performer') is None

    # drop candidate
    await performer_for_order(version=1)
    await performer_for_order(version=2)
    assert get_single_waybill()['candidate'] is None

    # find candidate
    await run_single_planner()

    assert get_single_waybill()['candidate'] is not None


async def test_repeat_search_candidate_not_found(
        state_taxi_order_created,
        exp_delivery_gamble_settings,
        exp_delivery_configs,
        performer_for_order,
        get_single_waybill,
        run_single_planner,
        mockserver,
):
    """
        Check candidate not found on repeat search.
    """
    # create waybill with lookup_flow: united-dispatch
    await exp_delivery_gamble_settings(lookup_flow='united-dispatch')
    await exp_delivery_configs(delivery_gamble_settings=False)
    await state_taxi_order_created()

    # drop candidate
    await performer_for_order(version=1)
    await performer_for_order(version=2)
    assert get_single_waybill()['candidate'] is None

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        return {'candidates': []}

    # candidate not found, no errors
    await run_single_planner()

    assert get_single_waybill()['candidate'] is None


async def test_scoring_context(
        state_taxi_order_created,
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        performer_for_order,
        create_segment,
        get_single_waybill,
        run_single_planner,
        scoring,
        mock_maps,
):
    # create waybill with lookup_flow: united-dispatch
    await exp_delivery_gamble_settings(
        disable_maps_router=False, lookup_flow='united-dispatch',
    )
    await exp_delivery_generators_settings()
    pickup_coordinates = (82.929395, 55.056471)
    dropoff_coordinates = (82.910909, 55.055010)
    mock_maps.add_route(
        points=[pickup_coordinates, dropoff_coordinates],
        car_time=360,
        car_distance=2500,
        pedestrian_time=960,
        pedestrian_distance=1370,
    )
    await exp_delivery_configs(
        delivery_gamble_settings=False, delivery_generators_settings=False,
    )

    create_segment(
        pickup_coordinates=pickup_coordinates,
        dropoff_coordinates=dropoff_coordinates,
    )

    await state_taxi_order_created()

    # drop candidate
    await performer_for_order(version=1)
    await performer_for_order(version=2)
    assert get_single_waybill()['candidate'] is None

    # find candidate
    await run_single_planner()

    assert get_single_waybill()['candidate'] is not None

    routers_data = scoring.requests[-1].json['requests'][0]['search']['order'][
        'request'
    ]['batch_properties']['batch_aggregates']['routers_data']
    assert routers_data == {
        'car': {'distance': 2500.0, 'time': 360},
        'pedestrian': {'distance': 1370.0, 'time': 960},
    }


@pytest.mark.parametrize('exclude_rejected_candidates', [False, True])
async def test_exclude_rejected_candidate(
        state_segments_replicated,
        exp_delivery_gamble_settings,
        exp_delivery_configs,
        exp_rejected_candidates_load_settings,
        run_single_planner,
        mockserver,
        create_segment,
        add_rejected_candidate,
        exclude_rejected_candidates: bool,
):
    """
        Check request to candidates for rejected candidate.
    """
    await exp_delivery_gamble_settings(
        exclude_rejected_candidates=exclude_rejected_candidates,
    )
    await exp_delivery_configs(delivery_gamble_settings=False)
    await exp_rejected_candidates_load_settings()

    seg = create_segment()
    add_rejected_candidate(segment=seg, candidate_id='some_id')

    await state_segments_replicated()

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        assert request.json['order']['request']['rejected_candidates']
        if exclude_rejected_candidates:
            assert 'excluded_contractor_ids' in request.json
        else:
            assert 'excluded_contractor_ids' not in request.json
        return {'candidates': []}

    await run_single_planner()

    assert _order_search.times_called


async def test_repeat_waybills_count(
        state_taxi_order_created,
        exp_delivery_gamble_settings,
        exp_delivery_configs,
        get_single_waybill,
        run_single_planner,
        mark_waybill_rebuilt,
):
    """
        Check rebuilt waybills count
    """
    # create waybill with lookup_flow: united-dispatch
    await exp_delivery_gamble_settings(lookup_flow='united-dispatch')
    await exp_delivery_configs(delivery_gamble_settings=False)
    await state_taxi_order_created()

    stats = await run_single_planner()
    assert (
        stats.find_metric(
            {'distlock_worker_alias': 'input-rebuilt-waybills'},
        ).value
        == 0
    )

    waybill = get_single_waybill()
    mark_waybill_rebuilt(waybill['id'])
    stats = await run_single_planner()
    assert (
        stats.find_metric(
            {'distlock_worker_alias': 'input-rebuilt-waybills'},
        ).value
        == 1
    )


async def test_repeat_search_reorder_oldway(
        state_taxi_order_performer_found,
        exp_delivery_gamble_settings,
        exp_delivery_configs,
        performer_for_order,
        get_single_waybill,
        run_single_planner,
):
    """
        Check repeat search happy path for autoreorder_flow: oldway.
    """
    # create waybill with lookup_flow: united-dispatch
    await exp_delivery_gamble_settings(lookup_flow='united-dispatch')
    await exp_delivery_configs(delivery_gamble_settings=False)
    await state_taxi_order_performer_found()

    assert get_single_waybill()['candidate'] is not None
    assert get_single_waybill()['waybill']['performer']

    # drop candidate
    await performer_for_order(version=1)
    await performer_for_order(version=2)
    assert get_single_waybill()['candidate'] is None

    # find candidate
    await run_single_planner()

    assert get_single_waybill()['candidate'] is not None
